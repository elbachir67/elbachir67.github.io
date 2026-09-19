#!/usr/bin/env python3
"""Vérifie qu'aucun reste de LaTeX n'a traversé la conversion jusqu'au site (US-51).

Un `\\\\[2pt]` non converti s'affiche tel quel sur une slide, en clair, devant les étudiants. Le rapport
de conversion ne le voyait pas : il ne signale que ce que le script **sait** ne pas savoir traduire. Ce
contrôle regarde le résultat, qui est le seul juge.

Sont cherchés, dans les pages rendues et **hors des blocs de code** :

- `\\\\`, avec ou sans espacement (`\\\\[2pt]`, `\\\\*`) : un saut de ligne LaTeX ;
- `\\[` : soit le même saut de ligne mal découpé, soit une commande restée entière.

Les blocs de code (`<pre>`, `<code>`) sont retirés avant l'examen : un cours peut montrer du LaTeX,
une chaîne Python avec des barres obliques inverses, ou une commande shell.

Si le site publie un jour des **mathématiques hors ligne** (`\\[ … \\]`, rendues par MathJax), il faudra
les excepter ici : aujourd'hui, le site n'en contient aucune, et les formules en ligne s'écrivent `$…$`.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "_site"
HORS_PERIMETRE = ("site_libs",)

CODE = re.compile(r"<(code|pre|script|style)\b[^>]*>.*?</\1>", re.S | re.I)
RESTES = re.compile(r"\\\\\*?(?:\[[^\]]*\])?|\\\[")
CONTEXTE = 60


def restes_de_la_page(page: Path) -> list[str]:
    """Restes de LaTeX visibles dans une page, avec ce qui les entoure."""
    html = page.read_text(encoding="utf-8", errors="ignore")
    texte = CODE.sub(" ", html)
    trouves = []
    for trouve in RESTES.finditer(texte):
        debut = max(0, trouve.start() - CONTEXTE)
        autour = re.sub(r"\s+", " ", texte[debut:trouve.end() + CONTEXTE])
        trouves.append(f"« {trouve[0]} » dans : …{autour}…")
    return trouves


def main() -> int:
    if not SITE.is_dir():
        print("Site non rendu : lancer python3 scripts/rendre.py.")
        return 1

    pages = [p for p in sorted(SITE.rglob("*.html"))
             if not any(morceau in str(p) for morceau in HORS_PERIMETRE)]
    ecarts = 0
    for page in pages:
        for reste in restes_de_la_page(page):
            print(f"{page.relative_to(RACINE)}: {reste}")
            ecarts += 1

    if ecarts:
        print(f"\nÉCHEC : {ecarts} reste(s) de LaTeX dans le site. Corriger "
              "scripts/importer_chapitre.py, puis rejouer l'import de la séance concernée.")
        return 1
    print(f"OK : aucun reste de LaTeX dans {len(pages)} page(s) de _site/ (hors blocs de code).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
