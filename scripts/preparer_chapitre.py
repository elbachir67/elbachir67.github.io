#!/usr/bin/env python3
"""Prépare une nouvelle séance de cours à partir de son .tex (US-20).

    python3 scripts/preparer_chapitre.py <cours-slug> <fichier.tex> [--alt nom="texte"] …

C'est la partie mécanique de la commande `/importer-chapitre` : elle copie les sources dans le dépôt,
importe la séance, écrit son entrée dans `_sources/import.toml`, puis dit ce qui manque encore.

Elle ne crée ni branche ni PR, et ne rend pas le site : ces étapes appartiennent à la commande, qui
s'arrête pour demander au PO ce que le script ne peut pas inventer.

Codes de sortie : 0 tout est prêt · 2 il manque une entrée du PO (texte alternatif, bloc non converti)
· 1 erreur d'utilisation.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BESOIN_DU_PO = 2


def sans_accent(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(lettre for lettre in decompose if unicodedata.category(lettre) != "Mn")


def identifiant(texte: str) -> str:
    """« Du chaos aux couches : juger… » -> « du-chaos-aux-couches »."""
    debut = re.split(r"[:—–,.]", texte)[0]
    mots = re.findall(r"[a-z0-9]+", sans_accent(debut).lower())
    return "-".join(mots[:6]) or "seance"


def champ(source: str, nom: str) -> str:
    trouve = re.search(rf"\\{nom}\{{(.+?)\}}\s*$", source, re.M)
    return trouve[1].strip() if trouve else ""


def numero_suivant(cours: Path) -> str:
    existants = sorted((cours / "chapitres").glob("[0-9][0-9]-*.qmd"))
    return f"{len(existants) + 1:02d}"


def copier_sources(cours: Path, tex: Path, figures_source: Path | None) -> Path:
    """Copie le .tex, son style et ses figures dans _sources/, sans écraser sans le dire."""
    sources = cours / "_sources"
    sources.mkdir(parents=True, exist_ok=True)
    cible = sources / tex.name
    if cible.is_file() and cible.resolve() == tex.resolve():
        # Relance sur une séance déjà importée : la source est déjà à sa place, rien à copier.
        print(f"Sources déjà dans le dépôt : {cible.relative_to(RACINE)}")
    else:
        if cible.is_file() and cible.read_bytes() != tex.read_bytes():
            print(f"Attention : {cible.relative_to(RACINE)} existait et a été remplacé.")
        shutil.copy2(tex, cible)

    for style in sorted(tex.parent.glob("*.sty")):
        destination = sources / style.name
        if not destination.is_file():
            shutil.copy2(style, destination)

    dossier = figures_source or (tex.parent / "figs")
    if dossier.is_dir():
        (sources / "figs").mkdir(exist_ok=True)
        for figure in sorted(dossier.iterdir()):
            destination = sources / "figs" / figure.name
            # Relance depuis le dépôt : les figures sont déjà à leur place.
            if figure.is_file() and not (destination.is_file()
                                         and destination.resolve() == figure.resolve()):
                shutil.copy2(figure, destination)
    return cible


def ecrire_textes_alternatifs(cours: Path, textes: dict[str, str]) -> Path | None:
    """Range les textes alternatifs fournis par le PO à côté des sources, pour un import rejouable."""
    fichier = cours / "_sources" / "textes-alternatifs.toml"
    if not textes and not fichier.is_file():
        return None
    existants = tomllib.loads(fichier.read_text(encoding="utf-8")) if fichier.is_file() else {}
    existants.update(textes)
    lignes = ["# Textes alternatifs des figures qui n'ont pas de légende dans le .tex, fournis par le PO.",
              ""]
    lignes += [f'{nom} = "{texte}"' for nom, texte in sorted(existants.items())]
    fichier.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return fichier


def ressources_demandees(brutes: list[str]) -> list[dict]:
    """« corrige|_corriges/c1.pdf|Corrigé du Lab 1|2026-10-15 » -> entrée du manifeste.

    La date n'existe que pour un corrigé : c'est le jour où il rejoint le site (US-49).
    """
    ressources = []
    for brute in brutes:
        champs = brute.split("|")
        if len(champs) < 3:
            sys.exit(f"Ressource mal formée : « {brute} » (attendu : type|fichier|titre[|date]).")
        entree = {"type": champs[0], "fichier": champs[1], "titre": champs[2] or champs[1]}
        if len(champs) > 3 and champs[3]:
            entree["date"] = champs[3]
        ressources.append(entree)
    return ressources


def ligne_de_ressource(cours: Path, ressource: dict) -> str:
    """Ce que l'import attend : le type, le fichier dans le dépôt, le titre, et la date d'un corrigé."""
    champs = [ressource["type"], f"cours/{cours.name}/{ressource['fichier']}", ressource["titre"]]
    if ressource.get("date"):
        champs.append(ressource["date"])
    return "|".join(champs)


def entree_existante(cours: Path, tex: str) -> dict | None:
    """Séance déjà décrite par le manifeste : une relance la met à jour, sans en créer une seconde."""
    manifeste = cours / "_sources" / "import.toml"
    if not manifeste.is_file():
        return None
    for chapitre in tomllib.loads(manifeste.read_text(encoding="utf-8")).get("chapitres", []):
        if chapitre["tex"] == tex:
            return chapitre
    return None


def ajouter_au_manifeste(cours: Path, entree: dict) -> None:
    """Écrit la séance dans _sources/import.toml, que la CI rejoue (US-41)."""
    manifeste = cours / "_sources" / "import.toml"
    if not manifeste.is_file():
        manifeste.write_text(
            "# Comment chaque séance de ce cours a été importée (US-41).\n"
            "#\n"
            "# scripts/verifier_conversion.py rejoue ces imports en CI et échoue si le .qmd ou les\n"
            "# figures commités diffèrent. Écrit par la commande /importer-chapitre (US-20).\n"
            "#\n"
            "# Les chemins sont relatifs au dossier du cours.\n", encoding="utf-8")
    texte = manifeste.read_text(encoding="utf-8")
    # Une relance remplace l'entrée de la même séance, **à sa place** : le PO fournit ses textes
    # alternatifs en plusieurs fois, et le manifeste doit décrire le dernier import, pas le premier,
    # sans que les séances se retrouvent dans le désordre.
    avant, apres = texte, ""
    depart = texte.find(f'tex = "{entree["tex"]}"')
    if depart != -1:
        debut = texte.rfind("[[chapitres]]", 0, depart)
        suivant = texte.find("[[chapitres]]", depart)
        avant, apres = texte[:debut], (texte[suivant:] if suivant != -1 else "")
    bloc = ["", "[[chapitres]]"]
    bloc += [f'{cle} = "{valeur}"' for cle, valeur in entree.items()
             if cle not in ("figures_python", "ressources")]
    if entree.get("figures_python"):
        bloc += ["", "[chapitres.figures_python]"]
        bloc += [f'{nom} = "{script}"' for nom, script in entree["figures_python"].items()]
    for ressource in entree.get("ressources", []):
        bloc += ["", "[[chapitres.ressources]]"]
        bloc += [f'{cle} = "{valeur}"' for cle, valeur in ressource.items()]
    ecrit = avant.rstrip("\n") + "\n" + "\n".join(bloc) + "\n"
    if apres.strip():
        ecrit += "\n" + apres.lstrip("\n")
    manifeste.write_text(ecrit, encoding="utf-8")


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("cours", help="dossier du cours sous cours/ (son slug)")
    analyseur.add_argument("tex", type=Path, help="fichier .tex de la séance")
    analyseur.add_argument("--slug", help="nom du fichier produit, sans le numéro (par défaut : "
                                          "déduit du sous-titre du .tex)")
    analyseur.add_argument("--description", help="phrase de référencement (par défaut : titre et sous-titre)")
    analyseur.add_argument("--alt", action="append", default=[], metavar='NOM="texte"',
                           help="texte alternatif d'une figure sans légende, fourni par le PO")
    analyseur.add_argument("--figure-python", action="append", default=[], metavar="NOM=SCRIPT.py",
                           help="figure produite par un bloc Python exécuté, au lieu d'être importée")
    analyseur.add_argument("--video", help="identifiant YouTube de la capsule de la séance (US-19)")
    analyseur.add_argument("--ressource", action="append", default=[], metavar="TYPE|FICHIER|TITRE",
                           help="ressource de la séance : lab, td, notebook ou corrige, le fichier "
                                "relatif au dossier du cours, et son titre (répétable, US-49)")
    analyseur.add_argument("--figures-source", type=Path,
                           help="dossier des figures (par défaut : figs/ à côté du .tex)")
    args = analyseur.parse_args()

    cours = RACINE / "cours" / args.cours
    if not (cours / "cours.yml").is_file():
        print(f"Cours inconnu : {cours.relative_to(RACINE)}/cours.yml est absent.")
        return 1
    if not args.tex.is_file():
        print(f"Fichier introuvable : {args.tex}")
        return 1

    source = args.tex.read_text(encoding="utf-8")
    titre, sous_titre = champ(source, "title"), champ(source, "subtitle")
    precedente = entree_existante(cours, f"_sources/{args.tex.name}")
    if precedente:
        sortie = cours / precedente["sortie"]
        numero, slug = Path(precedente["sortie"]).stem.split("-", 1)
        print(f"Séance déjà décrite par le manifeste : {sortie.relative_to(RACINE)} est remplacée.")
    else:
        slug = args.slug or identifiant(sous_titre or titre)
        numero = numero_suivant(cours)
        sortie = cours / "chapitres" / f"{numero}-{slug}.qmd"
    figures = cours / "figures"

    tex = copier_sources(cours, args.tex, args.figures_source)
    textes = dict(morceau.split("=", 1) for morceau in args.alt)
    alt = ecrire_textes_alternatifs(cours, {nom: texte.strip('"') for nom, texte in textes.items()})

    # Une relance sans --description ne doit pas écraser celle qu'on avait écrite : le manifeste fait foi.
    description = (args.description or (precedente or {}).get("description")
                   or " — ".join(filter(None, [titre, sous_titre])))
    scripts_python = (dict(morceau.split("=", 1) for morceau in args.figure_python)
                      or (precedente or {}).get("figures_python", {}))
    commande = [sys.executable, str(RACINE / "scripts" / "importer_chapitre.py"), str(tex),
                "--sortie", str(sortie), "--figures", str(figures),
                "--rapport", str(cours / "_sources" / f"rapport-{numero}-{slug}.md"),
                "--description", description]
    if alt:
        commande += ["--alt", str(alt)]
    video = args.video or (precedente or {}).get("video", "")
    if video:
        commande += ["--video", video]
    ressources = ressources_demandees(args.ressource) or (precedente or {}).get("ressources", [])
    for ressource in ressources:
        commande += ["--ressource", ligne_de_ressource(cours, ressource)]
    for nom, script in scripts_python.items():
        commande += ["--figure-python", f"{nom}={cours / script}"]

    execution = subprocess.run(commande, capture_output=True, text=True)
    print(execution.stdout.strip())
    if execution.returncode != 0:
        print(execution.stderr.strip())
        return 1

    rapport = (cours / "_sources" / f"rapport-{numero}-{slug}.md").read_text(encoding="utf-8")
    produit = sortie.read_text(encoding="utf-8")
    sans_alt = re.findall(r'alt="TODO\(PO\): [^"]*" *[^>]*>}}', produit)
    manquants = sorted({ligne.split(" :")[0].strip("- ") for ligne in rapport.splitlines()
                        if "TODO(PO)" in ligne and ligne.startswith("- ")})
    non_convertis = [ligne for ligne in rapport.splitlines()
                     if ligne.startswith("- **") and "`" in ligne]

    ajouter_au_manifeste(cours, {
        "tex": str(tex.relative_to(cours)),
        "sortie": str(sortie.relative_to(cours)),
        "figures": str(figures.relative_to(cours)),
        **({"alt": str(alt.relative_to(cours))} if alt else {}),
        "description": description,
        **({"video": video} if video else {}),
        **({"ressources": ressources} if ressources else {}),
        "figures_python": scripts_python,
    })

    print(f"\nSéance préparée : {sortie.relative_to(RACINE)}")
    print(f"Rapport : {(cours / '_sources' / f'rapport-{numero}-{slug}.md').relative_to(RACINE)}")
    if manquants or sans_alt:
        print("\nÀ demander au PO — texte alternatif manquant pour : " + ", ".join(manquants or ["(voir le rapport)"]))
        print("Relancer ensuite la commande avec --alt \"nom=phrase du PO\" : le script n'invente pas de description.")
    if non_convertis:
        print(f"\nÉléments non convertis ({len(non_convertis)}), à soumettre au PO avant toute PR :")
        for ligne in non_convertis:
            print(f"  {ligne}")
    return BESOIN_DU_PO if (manquants or sans_alt or non_convertis) else 0


if __name__ == "__main__":
    sys.exit(main())
