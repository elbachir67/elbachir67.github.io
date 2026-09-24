#!/usr/bin/env python3
"""Compile en PDF un document LaTeX livré sans son PDF (US-67).

    python3 scripts/document_pdf.py _import/DSA/S01_ADTs/Lab_S01.tex --sortie cours/<slug>/ressources

Trois des quatre labs de Structures de Données n'existent qu'en `.tex` : le PO écrit ses énoncés,
et ne garde pas toujours le PDF. Une ressource de séance, elle, se publie en PDF — c'est ce que le
lecteur télécharge.

Ce script fait ce que `figures_tikz.py` fait pour les schémas : il compile **à la préparation**, et
le PDF produit est commité. **La CI ne compile jamais de LaTeX** ; elle rejoue l'import, qui trouve
le PDF à sa place.

Deux passes de `pdflatex`, parce qu'une table des matières ou une référence croisée ne se résout
qu'à la seconde. Le document est compilé dans un dossier temporaire : les fichiers auxiliaires
(`.aux`, `.log`, `.out`) ne touchent jamais le dépôt.

Bibliothèque standard uniquement ; la distribution LaTeX est documentée dans le README, comme pour
`figures_tikz.py`.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PASSES = 2


def derniere_erreur(journal: Path) -> str:
    """La première ligne d'erreur du journal de LaTeX, ou un message par défaut."""
    if not journal.is_file():
        return "pdflatex n'a produit aucun journal"
    for ligne in journal.read_text(encoding="utf-8", errors="ignore").splitlines():
        if ligne.startswith("!"):
            return ligne.lstrip("! ").strip()
    return "pdflatex a échoué sans message reconnaissable"


def compiler(source: Path, cible: Path) -> str | None:
    """Compile `source` en PDF à l'emplacement `cible`. Renvoie l'erreur, ou None."""
    with tempfile.TemporaryDirectory() as travail:
        atelier = Path(travail)
        shutil.copy2(source, atelier / source.name)
        # Les documents du PO incluent parfois un style ou une figure voisine.
        for annexe in source.parent.iterdir():
            if annexe.is_file() and annexe.suffix in (".sty", ".cls", ".pdf", ".png", ".jpg"):
                shutil.copy2(annexe, atelier / annexe.name)
        for _ in range(PASSES):
            # `text=True` ferait échouer la lecture : pdflatex écrit son journal dans l'encodage
            # de la distribution, et non en UTF-8. La sortie ne nous sert pas — le journal, si.
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", source.name],
                           cwd=atelier, capture_output=True)
        produit = atelier / f"{source.stem}.pdf"
        if not produit.is_file():
            return derniere_erreur(atelier / f"{source.stem}.log")
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(produit, cible)
    return None


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("sources", type=Path, nargs="+", help="documents .tex à compiler")
    analyseur.add_argument("--sortie", type=Path, required=True, help="dossier des PDF produits")
    analyseur.add_argument("--nom", help="nom du PDF produit, s'il doit différer de celui du .tex")
    args = analyseur.parse_args()

    if shutil.which("pdflatex") is None:
        print("pdflatex est introuvable : installer une distribution LaTeX (TeX Live, MacTeX).")
        return 1
    if args.nom and len(args.sources) > 1:
        print("--nom ne vaut que pour un seul document.")
        return 1

    echecs = 0
    for source in args.sources:
        if not source.is_file():
            print(f"{source} : ÉCHEC — fichier introuvable")
            echecs += 1
            continue
        cible = args.sortie / (args.nom or f"{source.stem}.pdf")
        faute = compiler(source, cible)
        if faute:
            print(f"{source.name} : ÉCHEC — {faute}")
            echecs += 1
        else:
            print(f"{source.name} -> {cible.name} ({round(cible.stat().st_size / 1024)} Ko)")

    if echecs:
        print(f"\nÉCHEC : {echecs} document(s) sur {len(args.sources)} n'ont pas été compilés.")
        return 1
    print(f"\nOK : {len(args.sources)} document(s) compilé(s) dans {args.sortie}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
