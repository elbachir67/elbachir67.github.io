#!/usr/bin/env python3
"""Échoue si un numéro de téléphone apparaît dans le site rendu (US-10, CLAUDE.md §7).

    python3 scripts/verifier_telephone.py            # analyse _site/
    python3 scripts/verifier_telephone.py chemin/    # analyse un autre dossier

Motifs recherchés :
- indicatif du Sénégal : +221 ou 00221 ;
- numéro de 9 chiffres consécutifs (771234567) ;
- numéro sénégalais écrit par groupes (77 123 45 67, 33.821.00.00, 70-123-45-67).

Fichiers analysés : pages et données (.html, .xml, .json, .txt) et texte des PDF, extrait avec
pdftotext (paquet poppler). site_libs/ est exclu : ce sont des bibliothèques tierces copiées par Quarto,
où des nombres sans rapport (valeurs CSS, tracés de police) déclenchent de faux positifs.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MOTIFS = {
    "indicatif +221": re.compile(r"(?<![\w+])\+\s*221"),
    "indicatif 00221": re.compile(r"(?<!\d)00\s*221"),
    "9 chiffres consécutifs": re.compile(r"(?<![\d.])\d{9}(?!\d)"),
    "numéro par groupes": re.compile(r"(?<![\d/.\-])(?:7[05678]|3[03])[ .\-]\d{3}[ .\-]\d{2}[ .\-]\d{2}(?!\d)"),
}
EXTENSIONS_TEXTE = {".html", ".xml", ".json", ".txt"}
EXCLUS = {"site_libs"}


def texte_du_pdf(fichier: Path) -> str:
    if shutil.which("pdftotext") is None:
        sys.exit(f"pdftotext introuvable : impossible de vérifier {fichier} (installer poppler).")
    resultat = subprocess.run(["pdftotext", str(fichier), "-"], capture_output=True, text=True, check=True)
    return resultat.stdout


def fichiers_a_analyser(racine: Path):
    for fichier in sorted(racine.rglob("*")):
        if not fichier.is_file() or EXCLUS.intersection(fichier.relative_to(racine).parts):
            continue
        if fichier.suffix == ".pdf":
            yield fichier, texte_du_pdf(fichier)
        elif fichier.suffix in EXTENSIONS_TEXTE:
            yield fichier, fichier.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer quarto render d'abord).")
    trouves, analyses = 0, 0
    for fichier, texte in fichiers_a_analyser(racine):
        analyses += 1
        for nom, motif in MOTIFS.items():
            for m in motif.finditer(texte):
                trouves += 1
                ligne = texte.count("\n", 0, m.start()) + 1
                extrait = " ".join(texte[max(0, m.start() - 40):m.end() + 20].split())
                message = f"{nom} : « {m.group(0)} » dans « {extrait} »"
                if os.environ.get("GITHUB_ACTIONS"):
                    print(f"::error file={fichier},line={ligne},title=Numéro de téléphone::{message}")
                print(f"{fichier}:{ligne}: {message}")
    if trouves:
        print(f"ÉCHEC : {trouves} numéro(s) de téléphone possible(s) dans {racine}/.")
        return 1
    print(f"OK : aucun numéro de téléphone dans {analyses} fichier(s) de {racine}/ (hors site_libs/).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
