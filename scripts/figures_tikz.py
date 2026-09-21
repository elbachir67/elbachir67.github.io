#!/usr/bin/env python3
"""Compile les schémas TikZ d'un cours en SVG (US-55).

    python3 scripts/figures_tikz.py _import/c-avance/ch-1/CM_Ch-1_Introduction.tex \\
        --sortie cours/<slug>/figures --prefixe introduction

Chaque `tikzpicture` du document devient `<prefixe>-NN.svg`, dans l'ordre où il apparaît : c'est la
même numérotation que celle de `importer_chapitre.py`, pour que la page et les fichiers se
retrouvent sans table de correspondance.

**Jamais en CI**, comme les figures matplotlib : la compilation demande une distribution LaTeX, et le
résultat est commité. Le contrôle de conversion vérifie ensuite que les SVG sont là et non vides
(US-54).

La chaîne retenue, et pourquoi :

    lualatex --output-format=dvi   puis   dvisvgm --font-format=woff2

- Le **pilote dvisvgm de pgf** (`pgfsys-dvisvgm.def`) écrit des instructions SVG dans le DVI : le
  dessin arrive intact, sans passer par PostScript ni Ghostscript.
- `lualatex` avec `fontspec` compose le schéma **dans la police du site**, Source Sans 3. C'est
  LaTeX qui place alors chaque glyphe avec les bonnes métriques. Substituer la police *après coup*,
  dans le SVG, décale le texte : « UNIX réécrit en C » devenait « UNIX réécriten C ».
- `dvisvgm` garde le texte comme **texte**, sélectionnable — et non comme des tracés, qui donneraient
  une image morte.

Bibliothèque standard uniquement ; les dépendances LaTeX sont documentées dans le README.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Paquets du préambule utiles au dessin. La mise en page de l'article, elle, n'a rien à faire dans
# un schéma autonome — et `inputenc`/`fontenc` sont incompatibles avec fontspec.
GARDES = re.compile(r"\s*\\(usepackage|usetikzlibrary|definecolor|tcbuselibrary|pgfplotsset)")
ECARTES = ("geometry", "hyperref", "inputenc", "fontenc", "babel", "fancyhdr", "titlesec")
POLICE = "Source Sans 3"


def preambule_du_dessin(source: str) -> list[str]:
    """Lignes du préambule à reprendre dans le document autonome."""
    avant = source.split(r"\begin{document}", 1)[0]
    return [ligne for ligne in avant.splitlines()
            if GARDES.match(ligne) and not any(mot in ligne for mot in ECARTES)]


def dessins(source: str) -> list[str]:
    """Chaque `tikzpicture` du corps, dans l'ordre, avec ses options."""
    corps = source.split(r"\begin{document}", 1)[-1]
    trouves, position = [], 0
    while True:
        debut = corps.find(r"\begin{tikzpicture}", position)
        if debut == -1:
            return trouves
        fin = corps.index(r"\end{tikzpicture}", debut) + len(r"\end{tikzpicture}")
        trouves.append(corps[debut:fin])
        position = fin


def document(dessin: str, preambule: list[str]) -> str:
    """Document autonome, réglé pour que dvisvgm reçoive du SVG et la police du site."""
    return "\n".join([
        r"\documentclass[border=2pt,dvisvgm]{standalone}",
        # Sans cette ligne, pgf écrit du PostScript que dvisvgm ne sait pas lire seul.
        r"\def\pgfsysdriver{pgfsys-dvisvgm.def}",
        r"\usepackage{fontspec}",
        rf"\setmainfont{{{POLICE}}}",
        *preambule,
        r"\begin{document}",
        dessin,
        r"\end{document}",
        "",
    ])


def compiler(dessin: str, preambule: list[str], cible: Path) -> str | None:
    """Compile un schéma en SVG. Renvoie le message d'erreur, ou None si tout va bien."""
    with tempfile.TemporaryDirectory() as dossier:
        travail = Path(dossier)
        (travail / "f.tex").write_text(document(dessin, preambule), encoding="utf-8")
        latex = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "--output-format=dvi", "f.tex"],
            cwd=travail, capture_output=True, text=True)
        if not (travail / "f.dvi").is_file():
            fautes = [l for l in (travail / "f.log").read_text(encoding="utf-8", errors="ignore")
                      .splitlines() if l.startswith("!")]
            return fautes[0] if fautes else (latex.stdout or "").strip().splitlines()[-1:][0]

        svg = subprocess.run(
            ["dvisvgm", "--font-format=woff2", "--exact", "--no-styles=false", "-o", "f.svg", "f.dvi"],
            cwd=travail, capture_output=True, text=True)
        if not (travail / "f.svg").is_file():
            return (svg.stderr or svg.stdout).strip().splitlines()[-1:][0]

        contenu = (travail / "f.svg").read_text(encoding="utf-8")
        if "<text" not in contenu and re.search(r"[A-Za-z]", dessin):
            return ("le texte du schéma est sorti en tracés, et non en texte : la figure serait "
                    "illisible aux lecteurs d'écran et non sélectionnable")
        # Le nettoyage des autres figures ne s'applique pas ici, et c'est un choix mesuré :
        #
        # - **la police** est déjà celle du site, posée par LaTeX avec les bonnes métriques. La
        #   remplacer dans le SVG décale chaque glyphe : « UNIX réécrit en C » devient
        #   « UNIXréécritenC », constaté à l'écran ;
        # - **les encres** ne peuvent pas devenir `currentColor` sans casser la lisibilité : le texte
        #   d'un schéma vit souvent dans une boîte de couleur claire, et il deviendrait clair sur
        #   clair en mode sombre.
        #
        # Le schéma garde donc les couleurs que le PO a dessinées, et porte une classe qui permet à
        # la page de le poser sur un fond clair quand elle passe en mode sombre.
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(marquer(contenu), encoding="utf-8")
    return None


def marquer(svg: str) -> str:
    """Ajoute la classe `schema-tikz` à la racine : la page sait alors comment le présenter."""
    return re.sub(r"<svg\b", '<svg class="schema-tikz"', svg, count=1)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("source", type=Path, help="le .tex du chapitre")
    analyseur.add_argument("--sortie", type=Path, required=True, help="dossier des SVG produits")
    analyseur.add_argument("--prefixe", required=True, help="préfixe des noms de figures")
    args = analyseur.parse_args()

    for outil in ("lualatex", "dvisvgm"):
        if shutil.which(outil) is None:
            print(f"{outil} est introuvable : installer une distribution LaTeX (voir README).")
            return 1

    source = args.source.read_text(encoding="utf-8")
    preambule = preambule_du_dessin(source)
    schemas = dessins(source)
    if not schemas:
        print("Aucun schéma TikZ dans ce document.")
        return 0

    echecs = 0
    for numero, dessin in enumerate(schemas, start=1):
        nom = f"{args.prefixe}-{numero:02d}"
        cible = args.sortie / f"{nom}.svg"
        faute = compiler(dessin, preambule, cible)
        if faute:
            print(f"{nom} : ÉCHEC — {faute}")
            echecs += 1
        else:
            poids = round(cible.stat().st_size / 1024)
            print(f"{nom} : {poids} Ko")

    if echecs:
        print(f"\nÉCHEC : {echecs} schéma(s) sur {len(schemas)} n'ont pas été produits.")
        return 1
    print(f"\nOK : {len(schemas)} schéma(s) TikZ compilés dans {args.sortie}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
