#!/usr/bin/env python3
"""Vérifie qu'aucun reste de LaTeX n'a traversé la conversion jusqu'au site (US-51).

Un `\\\\[2pt]` non converti s'affiche tel quel sur une slide, en clair, devant les étudiants. Le rapport
de conversion ne le voyait pas : il ne signale que ce que le script **sait** ne pas savoir traduire. Ce
contrôle regarde le résultat, qui est le seul juge.

Sont cherchés, dans les pages rendues et **hors des blocs de code** :

- `\\\\`, avec ou sans espacement (`\\\\[2pt]`, `\\\\*`) : un saut de ligne LaTeX ;
- `\\[` : soit le même saut de ligne mal découpé, soit une commande restée entière ;
- une barre oblique inverse devant l'un des caractères que LaTeX échappe — `{ } [ ] $ % & _ # ~ ^` ;
- un `$` dans le texte visible : une formule que Quarto n'a pas lue et qui s'affiche en dollars.

Les **blocs** de code (`<pre>`) sont retirés avant l'examen : un cours peut y montrer du LaTeX, une
chaîne Python ou une commande shell. Les **codes en ligne** (`<code>`), eux, sont examinés pour le
dernier motif : c'est justement là que le défaut se logeait — « `\\{ \\}` » s'affichait avec ses
barres obliques, parce qu'un code en ligne rend son contenu littéralement. Aucune de ces onze
séquences n'a de sens dans le Python, le shell ou le texte que ces cours montrent.

Les **mathématiques hors ligne** s'écrivent `$$ … $$` : Quarto les rend dans un `<span class="math
display">`, que MATHS retire avant l'examen. La forme `\\[ … \\]`, elle, n'est pas lue par Quarto et
reste donc cherchée — c'est le défaut qu'a montré la séance 3 du cours de ML.

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
# Les mathématiques sont du LaTeX **voulu** : Quarto laisse `\(x \in \{0,1\}\)` dans la page et
# MathJax le rend dans le navigateur. Les chercher ici ferait échouer tout chapitre qui écrit un
# ensemble ou une accolade — le chapitre 1 du cours de C en compte six.
MATHS = re.compile(r'<span class="math[^"]*"[^>]*>.*?</span>', re.S | re.I)
RESTES = re.compile(r"\\\\\*?(?:\[[^\]]*\])?|\\\[")
# Guillemets de LaTeX laissés en clair. Un double accent grave **ouvre un code en ligne** en
# Markdown : il avalait les barres d'un tableau, qui sortait alors en texte brut (chapitre 2 du
# cours de C, 189 occurrences). Hors des blocs et des codes en ligne, ils n'ont rien à faire ici.
GUILLEMETS = re.compile(r"``|(?<![\w'])''(?!\w)")
# Les caractères que LaTeX échappe : dans une page rendue, la barre oblique n'a rien à faire devant.
ECHAPPES = re.compile(r"\\[{}\[\]$%&_#~^]")
# Un dollar encore visible est une formule que Quarto n'a pas lue. Il refuse d'y voir des
# mathématiques dès qu'une espace touche le dollar ouvrant ou le dollar fermant : « $4 = $ » et
# « $k = $ » s'affichaient en toutes lettres dans la séance 5 et le TP 7 du cours de ML. Les
# formules rendues ayant déjà été retirées avec MATHS, ce qui reste ne peut être que du texte.
# La recherche porte sur le **texte visible** : Quarto recopie le titre d'un encadré dans un
# attribut `title=`, où le `$w$` de la source subsiste sans jamais s'afficher.
DOLLARS = re.compile(r"\$")
BALISES = re.compile(r"<[^>]+>")
CONTEXTE = 60


def autour_de(texte: str, trouve: re.Match[str]) -> str:
    debut = max(0, trouve.start() - CONTEXTE)
    entourage = re.sub(r"\s+", " ", texte[debut:trouve.end() + CONTEXTE])
    return f"« {trouve[0]} » dans : …{entourage}…"


def restes_de_la_page(page: Path) -> list[str]:
    """Restes de LaTeX visibles dans une page, avec ce qui les entoure."""
    html = MATHS.sub(" ", page.read_text(encoding="utf-8", errors="ignore"))
    sans_code = CODE.sub(" ", html)
    trouves = [autour_de(t.string, t) for t in RESTES.finditer(sans_code)]
    trouves += [autour_de(t.string, t) for t in GUILLEMETS.finditer(sans_code)]
    trouves += [autour_de(t.string, t) for t in DOLLARS.finditer(BALISES.sub(" ", sans_code))]
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
