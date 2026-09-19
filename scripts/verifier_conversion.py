#!/usr/bin/env python3
"""Échoue si une page de cours ne correspond plus à ses sources (US-41).

    python3 scripts/verifier_conversion.py

Pour chaque cours qui a des sources (`cours/<slug>/_sources/import.toml`), le script :

1. **rejoue l'import** décrit dans ce fichier, dans un dossier temporaire, et compare au `.qmd` et aux
   figures commités : une conversion oubliée après modification du `.tex` fait échouer la CI ;
2. vérifie que **chaque page à code exécutable a son entrée dans `_freeze/`** : sans elle, la CI — qui
   n'installe pas de dépendance Python (US-18) — tenterait d'exécuter le code et échouerait plus loin,
   avec un message moins clair.

Le `.qmd` produit est comparé **au caractère près** : il ne contient aucune part aléatoire. Les
identifiants de cellule tirés au hasard par Quarto (`::: {#42c6f97f .cell}`) vivent dans
`_freeze/…/execute-results/html.json`, qui n'est pas comparé ici : il change à chaque exécution, sans que
le contenu publié change.

Bibliothèque standard uniquement : ce contrôle n'ajoute aucune dépendance à la CI.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
IMPORTEUR = RACINE / "scripts" / "importer_chapitre.py"


def annoncer(fichier: Path, message: str) -> None:
    chemin = fichier.relative_to(RACINE) if fichier.is_relative_to(RACINE) else fichier
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={chemin},title=Conversion des cours::{message}")
    print(f"{chemin}: {message}")


def rejouer(cours: Path, chapitre: dict, dossier: Path) -> list[tuple[Path, str]]:
    """Rejoue un import dans un dossier temporaire et compare au contenu commité."""
    sortie = cours / chapitre["sortie"]
    figures = cours / chapitre["figures"]
    commande = [
        sys.executable, str(IMPORTEUR), str(cours / chapitre["tex"]),
        "--sortie", str(dossier / "chapitre.qmd"),
        "--figures", str(dossier / "figures"),
        "--description", chapitre.get("description", ""),
        # Les figures sont citées dans le .qmd par un chemin relatif : il doit être celui du fichier
        # commité, et non celui du dossier temporaire.
        "--prefixe-figures", os.path.relpath(figures, sortie.parent),
    ]
    if chapitre.get("alt"):
        commande += ["--alt", str(cours / chapitre["alt"])]
    if chapitre.get("video"):
        commande += ["--video", chapitre["video"]]
    for ressource in chapitre.get("ressources", []):
        commande += ["--ressource",
                     f"{ressource['type']}|cours/{cours.name}/{ressource['fichier']}|{ressource['titre']}"]
    for nom, script in chapitre.get("figures_python", {}).items():
        commande += ["--figure-python", f"{nom}={cours / script}"]

    execution = subprocess.run(commande, capture_output=True, text=True)
    if execution.returncode != 0:
        return [(sortie, "l'import a échoué : " + (execution.stderr.strip().splitlines() or [""])[-1])]

    ecarts = []
    attendu = (dossier / "chapitre.qmd").read_text(encoding="utf-8")
    if not sortie.is_file():
        ecarts.append((sortie, "page absente : lancer l'import (voir README)"))
    elif sortie.read_text(encoding="utf-8") != attendu:
        ecarts.append((sortie, "la page ne correspond plus à ses sources : rejouer l'import "
                               "(scripts/importer_chapitre.py, commande dans _sources/import.toml)"))

    for produite in sorted((dossier / "figures").glob("*.svg")):
        commitee = figures / produite.name
        if not commitee.is_file():
            ecarts.append((commitee, "figure absente : rejouer l'import"))
        elif commitee.read_bytes() != produite.read_bytes():
            ecarts.append((commitee, "figure différente de celle que produit l'import"))
    return ecarts


# Ressources d'une séance (US-49) : les énoncés sont publiés depuis ressources/, les corrigés vivent
# dans _corriges/, que Quarto ne publie pas — le préfixe « _ » est la garantie, pas la vigilance.
DOSSIER_PUBLIE, DOSSIER_CORRIGES = "ressources", "_corriges"


def ressources_mal_rangees(cours: Path, chapitre: dict) -> list[tuple[Path, str]]:
    """Une ressource doit exister, et un corrigé ne doit jamais être publiable."""
    ecarts = []
    for ressource in chapitre.get("ressources", []):
        fichier = cours / ressource["fichier"]
        dossier = Path(ressource["fichier"]).parts[0]
        if not fichier.is_file():
            ecarts.append((fichier, "ressource déclarée dans import.toml mais absente du dépôt"))
        if ressource["type"] == "corrige" and dossier != DOSSIER_CORRIGES:
            ecarts.append((fichier, f"un corrigé doit vivre dans {DOSSIER_CORRIGES}/, que le site ne "
                                    "publie pas : jamais à côté de son énoncé"))
        if ressource["type"] != "corrige" and dossier != DOSSIER_PUBLIE:
            ecarts.append((fichier, f"une ressource publiée doit vivre dans {DOSSIER_PUBLIE}/"))
    return ecarts


def corriges_publies(site: Path) -> list[tuple[Path, str]]:
    """Dernier filet : aucun fichier de _corriges/ ne doit se retrouver dans le site rendu."""
    if not site.is_dir():
        return []
    noms = {fichier.name for corriges in RACINE.glob(f"cours/*/{DOSSIER_CORRIGES}")
            for fichier in corriges.iterdir() if fichier.is_file()}
    return [(publie, "corrigé publié : il doit rester hors du site")
            for publie in site.rglob("*") if publie.is_file() and publie.name in noms]


def gel_manquant(page: Path) -> str | None:
    """Une page à code exécutable doit avoir son résultat gelé dans _freeze/."""
    if "```{python}" not in page.read_text(encoding="utf-8"):
        return None
    relatif = page.relative_to(RACINE).with_suffix("")
    resultats = RACINE / "_freeze" / relatif / "execute-results" / "html.json"
    if resultats.is_file():
        return None
    return (f"bloc exécutable sans résultat gelé : {resultats.relative_to(RACINE)} est absent. "
            "Rendre la page en local, puis commiter _freeze/ (voir README).")


def main() -> int:
    manifestes = sorted(RACINE.glob("cours/*/_sources/import.toml"))
    if not manifestes:
        print("OK : aucun cours n'a de sources à vérifier.")
        return 0

    ecarts: list[tuple[Path, str]] = []
    chapitres = 0
    for manifeste in manifestes:
        cours = manifeste.parent.parent
        for chapitre in tomllib.loads(manifeste.read_text(encoding="utf-8"))["chapitres"]:
            chapitres += 1
            ecarts += ressources_mal_rangees(cours, chapitre)
            with tempfile.TemporaryDirectory() as dossier:
                ecarts += rejouer(cours, chapitre, Path(dossier))

    ecarts += corriges_publies(RACINE / "_site")
    pages = sorted(RACINE.glob("cours/*/chapitres/*.qmd"))
    for page in pages:
        manquant = gel_manquant(page)
        if manquant:
            ecarts.append((page, manquant))

    for fichier, message in ecarts:
        annoncer(fichier, message)
    if ecarts:
        print(f"ÉCHEC : {len(ecarts)} écart(s) entre les cours publiés et leurs sources.")
        return 1
    print(f"OK : {chapitres} chapitre(s) identique(s) à ce que produit l'import, "
          f"et {len(pages)} page(s) de cours avec leur gel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
