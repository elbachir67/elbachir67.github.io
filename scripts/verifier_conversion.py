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

import datetime as dt
import json
import os
import re
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
        # Les schémas TikZ portent le nom du chapitre, et non celui du fichier temporaire.
        "--prefixe-tikz", sortie.stem,
    ]
    if chapitre.get("alt"):
        commande += ["--alt", str(cours / chapitre["alt"])]
    if chapitre.get("langage"):
        commande += ["--langage-code", chapitre["langage"]]
    # Un CM rédigé se rejoue avec sa cible, son titre, son numéro affiché et ses encadrés (US-40).
    if chapitre.get("cible"):
        commande += ["--cible", chapitre["cible"]]
    if chapitre.get("titre"):
        commande += ["--titre", chapitre["titre"]]
    if chapitre.get("numero"):
        commande += ["--numero", chapitre["numero"]]
    for nom, encadre in (chapitre.get("encadres") or {}).items():
        commande += ["--encadre", f"{nom}={encadre}"]
    if chapitre.get("video"):
        commande += ["--video", chapitre["video"]]
    for ressource in chapitre.get("ressources", []):
        champs = [ressource["type"], f"cours/{cours.name}/{ressource['fichier']}", ressource["titre"]]
        if ressource.get("date"):
            champs.append(ressource["date"])
        commande += ["--ressource", "|".join(champs)]
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


# Ressources d'une séance (US-49) : elles vivent toutes dans ressources/, et elles sont toutes
# publiées. Le dossier `_corriges/` et la publication datée n'existent plus : aucun corrigé, aucune
# piste, aucune indication de correction ne vit dans le dépôt (décision du PO).
DOSSIER_PUBLIE = "ressources"


def ressources_mal_rangees(cours: Path, chapitre: dict) -> list[tuple[Path, str]]:
    """Une ressource doit exister, être bien rangée, et ne pas porter de date."""
    ecarts = []
    for ressource in chapitre.get("ressources", []):
        fichier = cours / ressource["fichier"]
        dossier = Path(ressource["fichier"]).parts[0]
        if not fichier.is_file():
            ecarts.append((fichier, "ressource déclarée dans import.toml mais absente du dépôt"))
        if dossier != DOSSIER_PUBLIE:
            ecarts.append((fichier, f"une ressource publiée doit vivre dans {DOSSIER_PUBLIE}/"))
        if ressource.get("date"):
            ecarts.append((fichier, "une ressource ne porte pas de date : la publication datée "
                                    "des corrigés est supprimée"))
    return ecarts


# Lien d'une ressource dans une page rendue : on en veut l'adresse et les attributs.
LIEN_RESSOURCE = re.compile(r'<a\b[^>]*class="[^"]*seance-ressource[^"]*"[^>]*>')
ADRESSE = re.compile(r'href="([^"]*)"')


def ressources_sans_telechargement(site: Path) -> list[tuple[Path, str]]:
    """Un lien de ressource qui n'est pas un PDF doit porter « download ».

    Sans lui, le navigateur ouvre le fichier : un fichier de données s'afficherait en clair, et le
    lien paraîtrait cassé. Deux exceptions, où l'ouverture est justement ce qu'on veut : un **PDF**,
    que la visionneuse affiche, et une **page** — depuis US-50, un notebook a la sienne, avec ses
    deux boutons.
    """
    if not site.is_dir():
        return []
    ecarts = []
    for page in sorted(site.rglob("*.html")):
        if "site_libs" in str(page):
            continue
        for balise in LIEN_RESSOURCE.findall(page.read_text(encoding="utf-8", errors="ignore")):
            adresse = (ADRESSE.search(balise) or [None, ""])[1]
            if adresse.lower().endswith((".pdf", ".html")) or "download" in balise:
                continue
            ecarts.append((page, f"la ressource « {adresse.rsplit('/', 1)[-1]} » n'est pas un PDF "
                                 "et son lien ne porte pas « download » : le navigateur l'ouvrira "
                                 "au lieu de l'enregistrer"))
    return ecarts


def notebooks_illisibles() -> list[tuple[Path, str]]:
    """Un notebook dont une cellule Markdown commence par « --- » fait tomber le rendu (US-50).

    Quarto y lit un bloc de métadonnées YAML. Le coût n'est pas la panne, c'est la **recherche** :
    l'erreur désigne un autre fichier que celui en cause, parce que le rendu parcourt toute la liste
    des entrées. Une heure y est passée une fois ; ce contrôle la rend à qui vient après.

    La correction est mécanique : « *** » est la règle horizontale explicite de Markdown, et
    s'affiche de la même façon dans Jupyter.
    """
    ecarts = []
    for notebook in sorted(RACINE.glob("cours/*/ressources/*.ipynb")):
        try:
            cellules = json.loads(notebook.read_text(encoding="utf-8")).get("cells", [])
        except (json.JSONDecodeError, UnicodeDecodeError) as erreur:
            ecarts.append((notebook, f"notebook illisible : {erreur}"))
            continue
        for numero, cellule in enumerate(cellules, start=1):
            if cellule.get("cell_type") != "markdown":
                continue
            for ligne in cellule.get("source", []):
                if ligne.strip() == "---":
                    ecarts.append((notebook, f"cellule {numero} : un « --- » y sépare des sections, "
                                             "et Quarto y lit un bloc YAML — le rendu du projet "
                                             "entier échoue. Écrire « *** »."))
                    break
    return ecarts


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

    ecarts += ressources_sans_telechargement(RACINE / "_site")
    ecarts += notebooks_illisibles()
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
