#!/usr/bin/env python3
"""Vérifie qu'aucun reste de LaTeX n'a traversé la conversion jusqu'au site (US-51).

Un `\\\\[2pt]` non converti s'affiche tel quel sur une slide, en clair, devant les étudiants. Le rapport
de conversion ne le voyait pas : il ne signale que ce que le script **sait** ne pas savoir traduire. Ce
contrôle regarde le résultat, qui est le seul juge.

Sont cherchés, dans les pages rendues et **hors des blocs de code** :

- `\\\\`, avec ou sans espacement (`\\\\[2pt]`, `\\\\*`) : un saut de ligne LaTeX ;
- `\\[` : soit le même saut de ligne mal découpé, soit une commande restée entière ;
- une barre oblique inverse devant l'un des caractères que LaTeX échappe — `{ } [ ] $ % & _ # ~ ^`.

Les **blocs** de code (`<pre>`) sont retirés avant l'examen : un cours peut y montrer du LaTeX, une
chaîne Python ou une commande shell. Les **codes en ligne** (`<code>`), eux, sont examinés pour le
dernier motif : c'est justement là que le défaut se logeait — « `\\{ \\}` » s'affichait avec ses
barres obliques, parce qu'un code en ligne rend son contenu littéralement. Aucune de ces onze
séquences n'a de sens dans le Python, le shell ou le texte que ces cours montrent.

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
BLOCS = re.compile(r"<(pre|script|style)\b[^>]*>.*?</\1>", re.S | re.I)
RESTES = re.compile(r"\\\\\*?(?:\[[^\]]*\])?|\\\[")
# Les caractères que LaTeX échappe : dans une page rendue, la barre oblique n'a rien à faire devant.
ECHAPPES = re.compile(r"\\[{}\[\]$%&_#~^]")
CONTEXTE = 60


def autour_de(texte: str, trouve: re.Match[str]) -> str:
    debut = max(0, trouve.start() - CONTEXTE)
    entourage = re.sub(r"\s+", " ", texte[debut:trouve.end() + CONTEXTE])
    return f"« {trouve[0]} » dans : …{entourage}…"


def restes_de_la_page(page: Path) -> list[str]:
    """Restes de LaTeX visibles dans une page, avec ce qui les entoure."""
    html = page.read_text(encoding="utf-8", errors="ignore")
    trouves = [autour_de(t.string, t) for t in RESTES.finditer(CODE.sub(" ", html))]
    # Les caractères échappés sont cherchés jusque dans les codes en ligne : c'est là qu'ils se
    # voyaient, un code en ligne rendant son contenu tel quel.
    trouves += [autour_de(t.string, t) for t in ECHAPPES.finditer(BLOCS.sub(" ", html))]
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
