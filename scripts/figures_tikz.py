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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importer_chapitre import identifiants_uniques  # noqa: E402  (même dossier)

# Paquets du préambule utiles au dessin. La mise en page de l'article, elle, n'a rien à faire dans
# un schéma autonome — et `inputenc`/`fontenc` sont incompatibles avec fontspec.
GARDES = re.compile(r"\s*\\(usepackage|usetikzlibrary|definecolor|tcbuselibrary|pgfplotsset)")
ECARTES = ("geometry", "hyperref", "inputenc", "fontenc", "babel", "fancyhdr", "titlesec")
POLICE = "Source Sans 3"


# Mots-clés de TikZ : ils s'écrivent sans barre oblique et ne s'affichent jamais.
MOTS_TIKZ = {"node", "child", "children", "edge", "from", "parent", "draw", "fill", "at", "to",
             "and", "cycle", "foreach", "in", "let", "coordinate", "rectangle", "circle",
             "ellipse", "arc", "grid", "plot", "controls", "pic", "scope", "sin", "cos", "of"}


def porte_du_texte(dessin: str) -> bool:
    """Le schéma affiche-t-il du texte ?

    Le contrôle qui suit — « le texte est sorti en tracés » — cherchait une lettre **n'importe où**
    dans la source. Or un schéma TikZ en contient toujours : ses options (`fill=blue!30`) et ses
    mots-clés (`node`, `child`) en sont faits. Le quatrième schéma de la séance 3 d'Introduction à
    l'IA dessine un arbre de recherche dont **tous les nœuds sont vides** : il n'affiche aucun
    texte, son SVG n'en portait donc aucun, et le contrôle le refusait à tort.

    Restent ici les mots qui s'afficheront : ni commentaire, ni option entre crochets, ni commande,
    ni mot-clé de TikZ.
    """
    texte = re.sub(r"(?<!\\)%.*", "", dessin)
    texte = re.sub(r"\\(?:begin|end)\s*\{[A-Za-z*]+\}", " ", texte)
    # Les options s'imbriquent (`every node/.style={...}` dans le bloc du dessin) : on les retire
    # du plus intérieur au plus extérieur, jusqu'à ce qu'il n'en reste plus.
    while True:
        reduit = re.sub(r"\[[^\[\]]*\]", " ", texte)
        if reduit == texte:
            break
        texte = reduit
    sans_commandes = re.sub(r"\\[A-Za-z]+", " ", texte)
    return any(mot.lower() not in MOTS_TIKZ
               for mot in re.findall(r"[A-Za-zÀ-ÿ]{2,}", sans_commandes))


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
        if "<text" not in contenu and porte_du_texte(dessin):
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
        cible.write_text(marquer(contenu, cible.stem), encoding="utf-8")
    return None


def marquer(svg: str, nom: str) -> str:
    """Classe `schema-tikz` à la racine, et identifiants internes préfixés par le nom du schéma.

    Une page de chapitre porte jusqu'à seize schémas. dvisvgm nomme le sien `page1` — le même pour
    tous —, et un identifiant en double dans une page est un défaut : le navigateur en choisit un, et
    toute référence désigne alors le mauvais. C'est ce qui avait brouillé les figures matplotlib.
    """
    svg = re.sub(r"<svg\b", '<svg class="schema-tikz"', svg, count=1)
    return identifiants_uniques(svg, nom)


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
