#!/usr/bin/env python3
"""Convertit en SVG les figures qu'un cours livre en PDF (US-59).

    python3 scripts/figures_pdf.py _import/c-avance/ch2 --sortie <dossier>

Certains chapitres arrivent avec leurs figures déjà compilées en PDF — vingt pour le seul chapitre 2
du cours de C. Le site, lui, incorpore des SVG : c'est la condition pour que le nettoyage du mode
sombre s'applique (`currentColor`) et pour que le texte de la figure reste du texte.

Au Sprint 5, ces conversions se faisaient **à la main**, figure par figure. Trois figures passaient
encore ; vingt-quatre, non.

`pdftocairo -svg` (poppler) garde le texte comme texte et les tracés comme tracés. Il n'y a pas de
dépendance nouvelle dans le dépôt : c'est un outil système, au même titre que la distribution LaTeX
dont dépend `figures_tikz.py`, et il ne tourne **jamais en CI** — le résultat est commité.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def convertir(source: Path, cible: Path) -> str | None:
    """Convertit un PDF en SVG. Renvoie le message d'erreur, ou None si tout va bien."""
    resultat = subprocess.run(["pdftocairo", "-svg", str(source), str(cible)],
                              capture_output=True, text=True)
    if resultat.returncode != 0 or not cible.is_file():
        return (resultat.stderr or resultat.stdout).strip().splitlines()[-1:][0] or "échec"
    contenu = cible.read_text(encoding="utf-8", errors="ignore")
    # Une figure dont le texte est sorti en tracés est illisible aux lecteurs d'écran et ne suivra
    # pas la police de la page. Mieux vaut le dire ici que le découvrir à l'audit d'accessibilité.
    if "<text" not in contenu and "<use" not in contenu:
        return "le texte de la figure est sorti en tracés, et non en texte"
    return None


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("source", type=Path, help="dossier contenant les figures en PDF")
    analyseur.add_argument("--sortie", type=Path, required=True, help="dossier des SVG produits")
    analyseur.add_argument("--motif", default="*.pdf", help="figures à convertir (défaut : *.pdf)")
    args = analyseur.parse_args()

    if shutil.which("pdftocairo") is None:
        print("pdftocairo est introuvable : installer poppler (brew install poppler).")
        return 1

    figures = sorted(args.source.glob(args.motif))
    if not figures:
        print(f"Aucune figure PDF dans {args.source}.")
        return 0

    args.sortie.mkdir(parents=True, exist_ok=True)
    echecs = 0
    for figure in figures:
        cible = args.sortie / f"{figure.stem}.svg"
        faute = convertir(figure, cible)
        if faute:
            print(f"{figure.stem} : ÉCHEC — {faute}")
            echecs += 1
        else:
            print(f"{figure.stem} : {round(cible.stat().st_size / 1024)} Ko")

    if echecs:
        print(f"\nÉCHEC : {echecs} figure(s) sur {len(figures)} n'ont pas été converties.")
        return 1
    print(f"\nOK : {len(figures)} figure(s) converties dans {args.sortie}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
