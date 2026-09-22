#!/usr/bin/env python3
"""Convertit un chapitre de cours Beamer en slides Quarto revealjs (US-15).

    python3 scripts/importer_chapitre.py cours/<slug>/_sources/cm1_archi_seance1.tex \
        --sortie cours/<slug>/chapitres/01-<slug>.qmd \
        --figures cours/<slug>/figures \
        --rapport cours/<slug>/_sources/rapport-NN-<slug>.md

Une `frame` Beamer donne une slide, une `\\section` donne une slide de section, et les sept encadrés
`ucad*` donnent des callouts Quarto (voir `_specs/contenus/latex-vers-quarto.md`).

Le script ne devine jamais : ce qu'il ne sait pas convertir reste dans la page en commentaire
`<!-- NON CONVERTI: … -->` et figure dans le rapport, pour être traité à la main.

Les figures SVG sont nettoyées pour le mode sombre — encres et gris en `currentColor`, fonds clairs
rendus transparents, police héritée de la page — puis écrites dans le dossier `--figures`. Elles sont
insérées par le shortcode `{{< svg … >}}`, qui les incorpore à la page : c'est la condition pour que
`currentColor` suive la couleur du texte. Rien de tout cela ne tourne en CI : le résultat est commité.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

SVG = "http://www.w3.org/2000/svg"

# Ressources d'une séance (US-49) : libellé par type, dans les deux langues. Un corrigé n'a pas de
# libellé ici : c'est `assets/lua/ressources.lua` qui l'affiche, et seulement à partir de sa date.
RESSOURCES = {
    "lab": {"fr": "Lab", "en": "Lab"},
    "td": {"fr": "TD", "en": "Tutorial"},
    "tp": {"fr": "TP", "en": "Lab"},
    "notebook": {"fr": "Notebook", "en": "Notebook"},
    # Le document du cours lui-même, compilé par LaTeX : une page rédigée n'est pas imprimée
    # depuis le site, c'est ce PDF-là qui fait foi (US-40).
    "pdf": {"fr": "PDF du cours", "en": "Course PDF"},
}
CORRIGE = "corrige"

# Commandes qui ne produisent qu'un caractère. `\textbackslash` apparaît dans ces cours à l'intérieur
# d'un `\texttt{}`, donc dans un code en ligne, où la barre oblique inverse ne s'échappe pas.
CARACTERES = {"oe": "œ", "ldots": "\u2026", "dots": "\u2026", "textbackslash": "\\",
              "textasciitilde": "~", "textasciicircum": "^",
              # Symboles employés **hors** mathématiques dans les CM rédigés : une flèche de prose,
              # une coche de validation. Les laisser passer les faisait signaler comme non convertis.
              "checkmark": "✓", "rightarrow": "→", "leftarrow": "←", "leftrightarrow": "↔",
              "Rightarrow": "⇒", "times": "×", "pm": "±", "bullet": "•", "degree": "°"}

# Styles de `lstlisting` définis par beamerucad.sty : « out » et « err » sont des sorties de
# programme, « sh » une commande shell. Sans style, c'est du code dans le langage du cours.
STYLES_CODE = {"out": "", "err": "", "sh": "bash"}
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")

# Encadrés de beamerucad.sty : type de callout Quarto, classe de couleur, titre par défaut.
ENCADRES = {
    "ucaddef": ("note", "ucad-def", "L'essentiel"),
    "ucadform": ("note", "ucad-form", "Formellement"),
    "ucadex": ("tip", "ucad-ex", "Exemple"),
    "ucadpiege": ("warning", "ucad-piege", "Piège"),
    "ucadret": ("important", "ucad-ret", "À retenir"),
    "ucadrec": ("tip", "ucad-rec", "En pratique"),
    "ucadfront": ("note", "ucad-front", "Pour aller plus loin"),
}

# Commandes de mise en page sans équivalent en HTML : le style s'en charge.
IGNOREES = {"vskip", "vspace", "smallskip", "medskip", "bigskip", "centering", "par", "vfill",
            # Apparitions progressives d'une slide Beamer : une page HTML montre tout d'un coup.
            "pause",
            "toprule", "midrule", "bottomrule", "hline", "addlinespace", "small", "scriptsize", "footnotesize",
            "normalsize", "large", "Large", "raggedright", "noindent", "titlepage", "maketitle"}

# Couleurs d'encre du jeu de figures : elles suivront la couleur du texte de la page.
ENCRES = {"#000", "#000000", "black", "#1a3a5c", "#1A3A5C", "#1c2a33", "#1C2A33",
          "#333", "#333333", "#444", "#444444", "#5a5a5a", "#5A5A5A", "#5a6b75", "#5A6B75",
          # Encre des figures matplotlib du cours de Python (la constante DARK de ses scripts).
          "#0f3a5e", "#0F3A5E"}
# Fonds clairs : transparents, pour rester lisibles en mode sombre comme en projection.
FONDS_CLAIRS = {"#fff", "#ffffff", "white", "#f8f9fb", "#fafafa", "#f7f7f7"}
FORMES = {"rect", "circle", "ellipse", "polygon", "polyline", "path", "line"}


# Lignes de fin de script : elles servent à produire un fichier pour LaTeX. Dans un bloc exécuté, la
# figure est affichée par Quarto, et le choix du moteur graphique lui revient.
EXPORT = re.compile(r"^\s*(matplotlib\.use\(|fig\.savefig\(|plt\.savefig\(|plt\.show\(|print\()")


class Conversion:
    """Contexte de la conversion, et compte rendu de ce qu'elle a fait ou laissé à faire."""

    def __init__(self, alternatifs: dict[str, str], prefixe_figures: str,
                 langage: str = "java") -> None:
        self.alternatifs = alternatifs          # textes alternatifs fournis par le PO, par figure
        self.prefixe_figures = prefixe_figures  # chemin des figures, relatif au .qmd produit
        self.langage = langage                  # langage des blocs de code, déclaré par le .tex
        self.encadres: dict[str, tuple[str, str, str]] = {}   # encadrés du document (US-40)
        self.prefixe_tikz = ""                  # préfixe des schémas TikZ compilés (US-55)
        self.tikz = 0                           # numéro du schéma en cours
        self.insertions: list[str] = []         # blocs déjà finalisés, à l'abri de la conversion
        self.scripts: dict[str, Path] = {}      # figures calculées : script Python, par nom de figure
        self.matricielles: set[str] = set()     # figures dont la source n'existe qu'en PNG
        self.non_convertis: list[tuple[str, str]] = []
        self.ignorees: Counter[str] = Counter()
        self.figures: list[str] = []
        self.codes: list[str] = []
        self.tableaux = 0
        self.slide = "(préambule)"

    def proteger(self, bloc: str) -> str:
        """Met un bloc déjà finalisé de côté : il ressortira intact à la fin de la conversion."""
        self.insertions.append(bloc)
        return f"\x01{len(self.insertions) - 1}\x01"

    def restaurer(self, texte: str) -> str:
        return re.sub(r"\x01(\d+)\x01", lambda t: self.insertions[int(t[1])], texte)

    def non_converti(self, quoi: str) -> str:
        self.non_convertis.append((self.slide, quoi))
        return f"<!-- NON CONVERTI: {quoi} -->"


# --------------------------------------------------------------------------------------------------
# Lecture du .tex
# --------------------------------------------------------------------------------------------------

def accolade(texte: str, debut: int) -> int:
    """Indice de l'accolade fermante correspondant à celle ouverte en `debut`."""
    profondeur = 0
    for i in range(debut, len(texte)):
        if texte[i] == "{" and texte[i - 1] != "\\":
            profondeur += 1
        elif texte[i] == "}" and texte[i - 1] != "\\":
            profondeur -= 1
            if profondeur == 0:
                return i
    raise ValueError(f"accolade non fermée à partir de {texte[debut:debut + 40]!r}")


def argument(texte: str, position: int) -> tuple[str, int]:
    """Argument entre accolades commençant à `position`, et l'indice qui suit."""
    fin = accolade(texte, position)
    return texte[position + 1:fin], fin + 1


def option(texte: str, position: int) -> tuple[str | None, int]:
    """Argument optionnel entre crochets, s'il y en a un.

    Le crochet fermant est cherché **à la même profondeur** : un titre d'encadré peut contenir des
    crochets, comme « [La syntaxe \\texttt{[debut:fin]}] ». S'arrêter au premier `]` tronquait le
    titre au milieu d'une accolade, et le reste partait dans le corps de la slide.
    """
    if position >= len(texte) or texte[position] != "[":
        return None, position
    profondeur = 0
    for i in range(position, len(texte)):
        if texte[i] in "[{" and texte[i - 1] != "\\":
            profondeur += 1
        elif texte[i] in "]}" and texte[i - 1] != "\\":
            profondeur -= 1
            if profondeur == 0:
                return texte[position + 1:i], i + 1
    raise ValueError(f"crochet non fermé à partir de {texte[position:position + 40]!r}")


def environnement(texte: str, nom: str, depart: int) -> tuple[str, int]:
    """Contenu d'un environnement ouvert en `depart`, en tenant compte des imbrications."""
    ouvre, ferme = f"\\begin{{{nom}}}", f"\\end{{{nom}}}"
    profondeur, i = 1, depart
    while profondeur:
        suivant_ouvre, suivant_ferme = texte.find(ouvre, i), texte.find(ferme, i)
        if suivant_ferme == -1:
            raise ValueError(f"environnement « {nom} » non fermé")
        if suivant_ouvre != -1 and suivant_ouvre < suivant_ferme:
            profondeur, i = profondeur + 1, suivant_ouvre + len(ouvre)
        else:
            profondeur, i = profondeur - 1, suivant_ferme + len(ferme)
    return texte[depart:i - len(ferme)], i


def preambule(source: str) -> dict[str, str]:
    """Titre, sous-titre, auteur et institution, pour l'en-tête de la présentation."""
    entete = {}
    for cle in ("title", "subtitle", "author", "institute"):
        trouve = re.search(rf"\\{cle}\{{", source)
        if trouve:
            valeur, _ = argument(source, trouve.end() - 1)
            entete[cle] = re.sub(r"\s*\\\\\s*", ", ", valeur).strip()
    return entete


# --------------------------------------------------------------------------------------------------
# Conversion du texte
# --------------------------------------------------------------------------------------------------

def macros_du_theme(texte: str, preambule: str = "") -> str:
    """Développe les macros de beamerucad.sty que la conversion ne peut pas deviner.

    `\\figslide{largeur}{fichier}{légende}` place une figure et sa légende : on le récrit sous la
    forme que le reste du script connaît déjà, pour que la légende serve de texte alternatif.
    `\\resultat` annonce la sortie du programme qui suit.

    `\\ucadformula{…}` est l'encadré de formule du cours d'Introduction au ML. Sa définition dit ce
    qu'il est : `\\begin{center}$\\displaystyle #1$\\end{center}`, soit une **formule hors ligne**.
    Sans cette règle, la macro n'était pas reconnue et son contenu s'échappait : chaque `\\frac`,
    `\\sum` ou `\\text` qu'elle contient était alors signalé un à un, 57 fois sur neuf séances.
    """
    motif = re.compile(r"\\figslideb?\{([^}]*)\}\{([^}]*)\}\{", re.S)
    while True:
        trouve = motif.search(texte)
        if not trouve:
            break
        # La légende est le troisième argument : elle contient des accolades (\texttt{…}), donc
        # elle se lit en comptant les accolades, et non avec une expression régulière.
        fin = accolade(texte, trouve.end() - 1)
        largeur, fichier, legende = trouve[1], trouve[2], texte[trouve.end():fin]
        # La légende suit immédiatement l'image : c'est à cette adjacence que le script la reconnaît,
        # et c'est elle qui deviendra le texte alternatif de la figure.
        texte = (texte[:trouve.start()]
                 + f"\\begin{{center}}\\includegraphics[width={largeur}\\linewidth]{{{fichier}}}\n"
                   f"{{\\scriptsize {legende}}}\\end{{center}}"
                 + texte[fin + 1:])
    # Macros du préambule sans argument — `\newcommand{\vw}{\mathbf{w}}`. Elles vivent surtout dans
    # les formules, et **MathJax ne les connaît pas** : il les affiche en rouge, telles quelles. Trois
    # slides du cours d'Introduction au ML montraient « \vw », « \vx », « \vz » en rouge, et seul
    # l'audit d'accessibilité l'a vu — par le contraste du rouge d'erreur de MathJax.
    #
    # Elles sont développées à la source plutôt que déclarées à MathJax : une substitution de texte
    # ne dépend ni de la version de MathJax ni de sa configuration, et les définitions les plus
    # longues passent d'abord, pour que `\vw` ne soit pas coupé par `\v`.
    definitions = {}
    for trouve in re.finditer(r"\\(?:new|renew|provide)command\s*\{\\([A-Za-z]+)\}\s*\{", preambule):
        nom = trouve[1]
        fin = accolade(preambule, trouve.end() - 1)
        corps_macro = preambule[trouve.end():fin]
        # Une définition qui contient elle-même une formule ou un environnement n'est pas une
        # abréviation mathématique : l'injecter dans un `$…$` imbriquerait les dollars, et la
        # structure du document se décalait — un `lstlisting` du cours de Python s'en trouvait
        # coupé. `\resultat`, qui vaut « Résultat $\rightarrow$ », est traité à part plus bas.
        if "$" not in corps_macro and "\\begin" not in corps_macro:
            definitions[nom] = corps_macro
    # Deux écritures des colonnes Beamer coexistent dans le même cours : `\column{0.5\linewidth}`
    # et `\begin{column}{0.5\textwidth}…\end{column}`. On ramène la seconde à la première, pour que
    # `colonnes()` n'ait qu'une forme à connaître.
    texte = re.sub(r"\\begin\{column\}\s*\{([^}]*)\}", r"\\column{\1}", texte)
    texte = texte.replace("\\end{column}", "")

    # `\figduo{l1}{f1}{l2}{f2}{légende}` : deux figures côte à côte sous une même légende. Elles
    # deviennent deux colonnes, et la légende suit — c'est elle qui fera le texte alternatif.
    motif_duo = re.compile(r"\\figduo\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{", re.S)
    while True:
        trouve = motif_duo.search(texte)
        if not trouve:
            break
        fin = accolade(texte, trouve.end() - 1)
        l1, f1, l2, f2 = trouve[1], trouve[2], trouve[3], trouve[4]
        legende = texte[trouve.end():fin]
        texte = (texte[:trouve.start()]
                 + f"\\begin{{center}}\\includegraphics[width={l1}\\linewidth]{{{f1}}}\n"
                   f"\\includegraphics[width={l2}\\linewidth]{{{f2}}}\n"
                   f"{{\\scriptsize {legende}}}\\end{{center}}"
                 + texte[fin + 1:])

    # Réglages de mise en page à deux arguments : ils n'ont pas de contenu, et laissés en place ils
    # se signalent comme non convertis. `\renewcommand{\arraystretch}{1.2}` espace les lignes d'un
    # tableau ; en HTML c'est la feuille de style qui s'en charge.
    for commande in ("renewcommand", "setlength", "addtolength"):
        motif_reglage = re.compile(rf"\\{commande}\s*\{{")
        while True:
            trouve = motif_reglage.search(texte)
            if not trouve:
                break
            fin = accolade(texte, trouve.end() - 1)
            suivant = re.match(r"\s*\{", texte[fin + 1:])
            fin = accolade(texte, fin + 1 + suivant.end() - 1) if suivant else fin
            texte = texte[:trouve.start()] + texte[fin + 1:]

    # `\texorpdfstring{beau}{brut}` : la première forme est celle qu'on lit. Résolue **ici**, avant
    # tout découpage : elle apparaît dans l'argument optionnel d'un `\section[…]{…}`, que le
    # découpage des sections coupe en deux — l'accolade restait alors ouverte et l'import s'arrêtait
    # (séance 5 du cours d'Introduction au ML).
    motif_tex = re.compile(r"\\texorpdfstring\s*\{")
    while True:
        trouve = motif_tex.search(texte)
        if not trouve:
            break
        fin_un = accolade(texte, trouve.end() - 1)
        suivant = re.match(r"\s*\{", texte[fin_un + 1:])
        lisible = texte[trouve.end():fin_un]
        fin = accolade(texte, fin_un + 1 + suivant.end() - 1) if suivant else fin_un
        texte = texte[:trouve.start()] + lisible + texte[fin + 1:]

    texte = texte.replace("\\resultat", "\n\n**Résultat →**\n\n")

    # `\ucadformula{…}` -> formule hors ligne. Le contenu se lit en comptant les accolades : une
    # formule en contient (`\frac{1}{n}`), et une expression régulière s'arrêterait à la première.
    motif = re.compile(r"\\ucadformula\s*\{")
    while True:
        trouve = motif.search(texte)
        if not trouve:
            break
        fin = accolade(texte, trouve.end() - 1)
        formule = texte[trouve.end():fin].strip()
        texte = texte[:trouve.start()] + f"\n\n$$ {formule} $$\n\n" + texte[fin + 1:]

    # La substitution ne touche **que les formules**, et vient **après** `\\ucadformula` : appliquée
    # partout, elle entrait dans les blocs de code — le cours de Python définit des macros dont le
    # nom apparaît dans ses exemples, et un `lstlisting` s'en trouvait coupé en deux. Les
    # environnements `align`, `equation` et `gather` sont des formules sans dollars : les oublier
    # laissait `\\vd` et `\\vz` tels quels dans les quatre équations de la rétropropagation, que
    # MathJax affichait alors en rouge.
    if definitions:
        def developper(trouve: re.Match[str]) -> str:
            formule = trouve[0]
            for nom in sorted(definitions, key=len, reverse=True):
                formule = re.sub(rf"\\{nom}(?![A-Za-z])",
                                 lambda _, c=definitions[nom]: c, formule)
            return formule

        texte = MOTIF_ENVIRONNEMENTS_MATHS.sub(developper, texte)
        texte = MOTIF_MATHS.sub(developper, texte)

    return texte.replace("\\quad", " ")


def sans_commentaires(texte: str) -> str:
    return "\n".join(ligne for ligne in texte.splitlines()
                     if not ligne.lstrip().startswith("%"))


def retirer_tailles(texte: str) -> str:
    """« {\\small … } » disparaît : la taille du texte est affaire de style, pas de contenu."""
    # « \small » peut être suivi d'un espace ou directement d'une autre commande : « {\small\begin{tabular} ».
    motif = re.compile(r"\{\\(small|scriptsize|footnotesize|normalsize|large|Large)\b\s?")
    while True:
        trouve = motif.search(texte)
        if not trouve:
            return texte
        fin = accolade(texte, trouve.start())
        texte = texte[:trouve.start()] + texte[trouve.end():fin] + texte[fin + 1:]


MOTIF_IMAGE = re.compile(r"\\includegraphics(?:\[(?P<options>[^\]]*)\])?\{(?P<nom>[^}]+)\}")
MOTIF_LEGENDE = re.compile(r"\s*\{\\(?:scriptsize|footnotesize|small)\s")


# Commandes non alphabétiques qu'une légende contient : LaTeX les échappe, un texte alternatif les
# veut nues. `\,` et ses variantes sont des espaces fines, sans équivalent dans du texte lu.
PONCTUATION_LATEX = {r"\%": "%", r"\&": "&", r"\_": "_", r"\#": "#", r"\$": "$",
                     r"\,": " ", r"\;": " ", r"\!": "", r"\ ": " "}


def sans_balises(texte: str) -> str:
    """Texte nu d'une légende, pour servir de texte alternatif.

    Un texte alternatif est **lu à voix haute** : aucune formule n'y sera rendue, et les dollars,
    les accolades et les commandes échappées s'y entendraient tels quels. Une légende du cours
    d'Introduction au ML écrivait « pour atteindre $80\\,\\%$ de variance » : le lecteur d'écran
    aurait dit « dollar 80 antislash virgule antislash pourcent dollar ».
    """
    for commande, caractere in PONCTUATION_LATEX.items():
        texte = texte.replace(commande, caractere)
    texte = re.sub(r"\\[A-Za-z]+\s*\{([^{}]*)\}", r"\1", texte)
    texte = re.sub(r"\\[A-Za-z]+\s*", "", texte)
    texte = texte.replace("{", "").replace("}", "").replace("$", "")
    return re.sub(r"\s+", " ", texte).replace('"', "«").strip()


def code_python(nom: str, conversion: Conversion) -> tuple[str, int]:
    """Code du script du PO, sans les lignes qui écrivaient un fichier pour LaTeX."""
    lignes = conversion.scripts[nom].read_text(encoding="utf-8").splitlines()
    gardees = [ligne for ligne in lignes if not EXPORT.match(ligne)]
    return "\n".join(gardees).strip(), len(lignes) - len(gardees)


def bloc_python(nom: str, conversion: Conversion, legende: str | None) -> tuple[str, str]:
    """Figure calculée : le script du PO devient un bloc exécuté, dont Quarto gèle le résultat.

    La slide montre la figure, pas le code : le bloc est exécuté sans écho, et le code est repris juste
    en dessous dans un repli que le lecteur ouvre s'il le souhaite. En revealjs, ni « code-fold » ni un
    callout « collapse » ne replient quoi que ce soit : le repli est donc un <details> HTML, dont Quarto
    colore le contenu comme n'importe quel bloc de code.
    """
    code, retirees = code_python(nom, conversion)
    alt = conversion.alternatifs.get(nom) or (sans_balises(legende) if legende else "")
    origine = ("texte fourni par le PO" if nom in conversion.alternatifs
               else "légende du .tex" if legende else "TODO(PO)")
    conversion.figures.append(
        f"{nom} : bloc Python exécuté depuis {conversion.scripts[nom].name} "
        f"({retirees} ligne(s) d'export retirée(s)), texte alternatif — {origine}")
    chunk = "\n".join([
        "```{python}",
        f'#| fig-alt: "{alt or "TODO(PO): description de la figure"}"',
        "#| echo: false",
        code,
        "```",
    ])
    repli = "\n".join([
        "<details>",
        "<summary>Voir le code de la figure</summary>",
        "",
        "```python",
        code,
        "```",
        "",
        "</details>",
    ])
    return chunk, repli


def figures(texte: str, conversion: Conversion) -> str:
    """Remplace chaque image, et la légende qui la suit, par le shortcode et sa légende.

    Le texte alternatif vient de la légende du `.tex`. Quand il n'y en a pas, il vient du fichier
    passé par `--alt` (phrases fournies par le PO) ; sinon, la figure part avec un `TODO(PO)` visible,
    signalé dans le rapport : le script n'invente pas de description.
    """
    while True:
        trouve = MOTIF_IMAGE.search(texte)
        if not trouve:
            return texte
        # Le dossier ne compte pas (les figures sont celles du cours), et l'extension non plus :
        # le .tex cite le PDF que compile LaTeX, la page incorpore le SVG du même nom.
        nom = Path(trouve["nom"]).stem
        mesure = re.search(r"width=([\d.]+)\\linewidth", trouve["options"] or "")
        largeur = float(mesure[1]) if mesure else None

        legende, fin = None, trouve.end()
        suivante = MOTIF_LEGENDE.match(texte, trouve.end())
        if suivante:
            ouverture = texte.index("{", trouve.end())
            fermeture = accolade(texte, ouverture)
            legende, fin = texte[suivante.end():fermeture], fermeture + 1

        repli = None
        if nom in conversion.scripts:
            insertion, repli = bloc_python(nom, conversion, legende)
        elif nom.startswith("figA"):
            conversion.figures.append(f"{nom} : non importée, produite par le bloc Python d'US-18")
            insertion = ("<!-- FIGURE CALCULÉE (US-18) : " + nom
                         + ", à produire par le bloc Python de _sources/figs/figA.py -->")
        else:
            alt = conversion.alternatifs.get(nom) or (sans_balises(legende) if legende else "")
            origine = ("texte fourni par le PO" if nom in conversion.alternatifs
                       else "légende du .tex" if legende else "TODO(PO)")
            taille = f' largeur="{round(largeur * 100)}%"' if largeur else ""
            if nom in conversion.matricielles:
                # Figure livrée en image matricielle seulement : aucun SVG à incorporer. Elle est
                # posée comme une image ordinaire, avec son texte alternatif. Elle ne suivra pas le
                # mode sombre et se pixellisera au zoom — c'est le prix d'une source sans vectoriel.
                conversion.figures.append(f"{nom} : insérée en PNG (aucune source vectorielle), "
                                          f"texte alternatif — {origine}")
                # Le texte alternatif passe par `fig-alt`, et non par le crochet de l'image : écrit
                # dans le crochet, Pandoc en fait une figure implicite, et le filtre revealjs de
                # Quarto remplace `src` par `data-src` **en perdant l'attribut alt** — l'audit
                # d'accessibilité signalait alors une image sans nom accessible.
                attributs = [f'fig-alt="{(alt or "TODO(PO): description de la figure").replace(chr(34), "&quot;")}"']
                if largeur:
                    attributs.append(f'width="{round(largeur * 100)}%"')
                insertion = (f'![]({conversion.prefixe_figures}/{nom}.png)'
                             f'{{{" ".join(attributs)}}}')
            else:
                conversion.figures.append(f"{nom} : insérée, texte alternatif — {origine}")
                insertion = (f'{{{{< svg {conversion.prefixe_figures}/{nom}.svg '
                             f'alt="{alt or "TODO(PO): description de la figure"}"{taille} >}}}}')

        # Seule l'insertion est mise à l'abri ; la légende, elle, suit le chemin normal du texte.
        bloc = conversion.proteger(insertion)
        if legende:
            bloc += "\n\n::: {.legende}\n" + legende.strip() + "\n:::"
        if repli:
            bloc += "\n\n" + conversion.proteger(repli)
        texte = texte[:trouve.start()] + bloc + texte[fin:]


# Le crochet ouvrant ne compte que s'il n'est pas lui-même précédé d'une barre oblique : « \\[2pt] »
# est un saut de ligne avec espacement, et non le début d'une formule.
MOTIF_MATHS = re.compile(r"\$\$.+?\$\$|\$[^$]+?\$|(?<!\\)\\\[.+?(?<!\\)\\\]", re.S)
# Les environnements qui sont des mathématiques sans porter de dollars.
MOTIF_ENVIRONNEMENTS_MATHS = re.compile(
    r"\\begin\{(align|equation|gather|multline|eqnarray)(\*?)\}.*?\\end\{\1\2\}", re.S)


def maths_en_dollars(formule: str) -> str:
    """Écrit la formule sous la forme que Quarto sait lire.

    Deux façons d'écrire des mathématiques que LaTeX accepte et que Quarto refuse :

    - « \\[ … \\] » : Quarto n'active pas `tex_math_single_backslash` et voit dans `\\[` un crochet
      échappé, non une ouverture de formule. Seuls les `\\begin{pmatrix}` intérieurs passaient en
      mathématiques, et le lecteur lisait « [ X= », la matrice, puis « ^{10000} y= » en toutes
      lettres — c'est ce que montrait la séance 3 du cours de ML ;
    - « $4 = $ » : une espace collée au dollar fermant (ou au dollar ouvrant) empêche Quarto d'y
      voir une formule, et la page affichait les dollars — séance 5 du même cours.
    """
    if formule.startswith("\\["):
        return "$$" + formule[2:-2].strip() + "$$"
    if formule.startswith("$$") or not formule.startswith("$"):
        return formule
    contenu = formule[1:-1].strip()
    return f"${contenu}$" if contenu else formule


# Caractères que LaTeX écrit échappés. Ceux de MARKDOWN_SPECIAUX doivent le rester dans le texte
# courant — sinon Quarto y verrait des maths, un lien ou un attribut —, mais pas dans un code en
# ligne, où les accents graves suffisent et où une barre oblique s'afficherait telle quelle.
ECHAPPES = "{}[]$%&_#~^"
MARKDOWN_SPECIAUX = set("{}[]$_#~^")
MOTIF_ECHAPPE = re.compile(r"\\([" + re.escape(ECHAPPES) + r"])(?:\{\})?")
# Découpe le texte en alternant hors-code et code en ligne, accents graves compris.
MOTIF_CODE_EN_LIGNE = re.compile(r"(`+[^`]*`+)")


def caracteres_echappes(texte: str) -> str:
    """« \\{ » -> « { », en respectant le Markdown et les codes en ligne.

    Dans un code en ligne, le caractère est rendu littéralement : la barre oblique doit disparaître,
    sinon la page affiche « \\{ ». Dans le texte courant, elle doit au contraire rester devant les
    caractères que Markdown interprète — c'est alors une échappe Markdown, et non un reste de LaTeX.

    Le tilde de LaTeX, lui, est une espace insécable : il ne le devient qu'hors des codes en ligne,
    où « ~ » désigne le plus souvent un dossier personnel.
    """
    morceaux = []
    for morceau in MOTIF_CODE_EN_LIGNE.split(texte):
        if morceau.startswith("`"):
            morceaux.append(MOTIF_ECHAPPE.sub(lambda t: t[1], morceau))
        else:
            morceaux.append(MOTIF_ECHAPPE.sub(
                lambda t: ("\\" + t[1]) if t[1] in MARKDOWN_SPECIAUX else t[1],
                morceau).replace("~", "\u00a0"))
    return "".join(morceaux)


def inline(texte: str, conversion: Conversion) -> str:
    """Conversion du texte courant : mise en forme et caractères LaTeX.

    Les formules sont mises de côté le temps de la conversion : leur contenu est du LaTeX, que Quarto
    rend tel quel, et ne doit donc pas être traité comme du texte.
    """
    formules: list[str] = []
    texte = retirer_tailles(sans_commentaires(texte))

    def garder(trouve: re.Match[str]) -> str:
        formules.append(maths_en_dollars(trouve[0]))
        return f"\x00{len(formules) - 1}\x00"

    texte = MOTIF_MATHS.sub(garder, texte)

    # `\textcolor{couleur}{texte}` : la couleur est de la mise en forme, le texte reste. Le
    # traitement vient **après** la mise de côté des mathématiques : dans une formule, `\textcolor`
    # est rendu par MathJax, et le retirer effacerait ce que le PO a mis en couleur — le point
    # binaire rouge du chapitre 1 du cours de C, par exemple.
    for commande, garde in (("textcolor", 2),):
        motif_deux = re.compile(rf"\\{commande}\s*\{{")
        while True:
            trouve = motif_deux.search(texte)
            if not trouve:
                break
            fin_un = accolade(texte, trouve.end() - 1)
            suivant = re.match(r"\s*\{", texte[fin_un + 1:])
            if not suivant:
                texte = texte[:trouve.start()] + texte[trouve.end():fin_un] + texte[fin_un + 1:]
                continue
            debut_deux = fin_un + 1 + suivant.end() - 1
            fin_deux = accolade(texte, debut_deux)
            garde_texte = (texte[debut_deux + 1:fin_deux] if garde == 2
                           else texte[trouve.end():fin_un])
            texte = texte[:trouve.start()] + garde_texte + texte[fin_deux + 1:]

    # Guillemets de LaTeX : « ``mot'' ». En Markdown, un double accent grave **ouvre un code en
    # ligne** et avale tout ce qui suit, barres d'un tableau comprises : la ligne cessait d'être une
    # ligne de tableau, et Pandoc rendait le tout en bloc de lignes, barres verticales apparentes.
    # Constaté sur le chapitre 2 du cours de C ; 189 occurrences dans les quatre chapitres.
    texte = re.sub(r"``\s*(.+?)\s*''", "« \\1 »", texte, flags=re.S)

    # Mise en forme.
    remplacements = [
        (r"\\textbf\{", "**", "**"), (r"\\alert\{", "**", "**"),
        (r"\\emph\{", "*", "*"), (r"\\textit\{", "*", "*"),
        (r"\\texttt\{", "`", "`"), (r"\\textsuperscript\{", "^", "^"),
    ]
    for motif, avant, apres in remplacements:
        while True:
            trouve = re.search(motif, texte)
            if not trouve:
                break
            contenu, suite = argument(texte, trouve.end() - 1)
            texte = texte[:trouve.start()] + avant + contenu + apres + texte[suite:]

    # Commandes de mise en page et caractères.
    def commande(trouve: re.Match[str]) -> str:
        nom = trouve[1]
        if nom in IGNOREES:
            conversion.ignorees[nom] += 1
            return ""
        if nom in CARACTERES:
            return CARACTERES[nom]
        if nom == "newline":
            return "<br>"
        return conversion.non_converti("\\" + nom)

    # « \\ », « \\[2pt] », « \\* » : un saut de ligne, l'espacement en plus étant affaire de style.
    texte = re.sub(r"\\\\\*?\s*(?:\[[^\]]*\])?", "<br>", texte)
    # Espacements verticaux, avec ou sans accolades : « \vspace{3pt} », « \vskip 2ex », « \vspace*{1cm} ».
    texte = re.sub(r"\\(?:vskip|vspace)\*?\s*(?:\{[^}]*\}|-?[\d.]+\s*[a-z]+)", "", texte)
    texte = re.sub(r"\\([A-Za-z]+)\s*(?:\{\})?", commande, texte)
    texte = caracteres_echappes(texte)
    texte = re.sub(r"\x00(\d+)\x00", lambda t: formules[int(t[1])], texte)
    return re.sub(r"\n{3,}", "\n\n", texte).strip()


def titre_de_callout(titre: str | None, conversion: Conversion) -> str:
    """Titre d'un encadré : converti comme le reste, et guillemets échappés.

    Le titre passait brut dans l'attribut `title="…"`. Un `\\texttt{"w"}` y mettait donc du LaTeX et,
    surtout, des guillemets qui fermaient l'attribut : Quarto perdait le div et le signalait par un
    avertissement, que la CI refuse.
    """
    if not titre:
        return ""
    return inline(titre, conversion).replace("\n", " ").replace('"', '\\"').strip()


def cellules_de_tableau(contenu: str) -> list[list[str]]:
    """Découpe un `tabular` en lignes et en cellules, comme LaTeX les lit.

    Découper naïvement sur « & » coupait `\\texttt{\\&x}` en deux : une **esperluette échappée** n'est
    pas un séparateur de colonne, et la moitié de cellule qui en sortait laissait une accolade
    ouverte. L'import du chapitre 2 du cours de C s'arrêtait là, sur « accolade non fermée ».

    Trois règles suffisent : une barre oblique inverse protège le caractère suivant, un séparateur ne
    compte qu'en dehors des accolades, et « \\\\ » termine la ligne — l'espacement optionnel compris.
    """
    lignes: list[list[str]] = []
    ligne: list[str] = []
    tampon: list[str] = []
    profondeur = position = 0
    while position < len(contenu):
        caractere = contenu[position]
        if caractere == "\\" and position + 1 < len(contenu):
            if contenu[position + 1] == "\\" and profondeur == 0:
                ligne.append("".join(tampon))
                lignes.append(ligne)
                ligne, tampon = [], []
                position += 2
                # Une ligne peut finir par « \\[2pt] » : l'espacement n'appartient à aucune cellule.
                espacement = re.match(r"\s*\[[^\]]*\]", contenu[position:])
                position += espacement.end() if espacement else 0
                continue
            tampon.append(contenu[position:position + 2])
            position += 2
            continue
        if caractere == "{":
            profondeur += 1
        elif caractere == "}":
            profondeur -= 1
        elif caractere == "&" and profondeur == 0:
            ligne.append("".join(tampon))
            tampon = []
            position += 1
            continue
        tampon.append(caractere)
        position += 1
    ligne.append("".join(tampon))
    lignes.append(ligne)
    return lignes


def tableau(contenu: str, conversion: Conversion) -> str:
    """tabular -> tableau Markdown ; les filets de booktabs disparaissent."""
    conversion.tableaux += 1
    lignes = []
    for brute in cellules_de_tableau(contenu):
        cellules = [inline(c, conversion).replace("\n", " ").strip() for c in brute]
        if any(cellules):
            lignes.append(cellules)
    if not lignes:
        return ""
    colonnes = max(len(ligne) for ligne in lignes)
    lignes = [ligne + [""] * (colonnes - len(ligne)) for ligne in lignes]
    entete = "| " + " | ".join(lignes[0]) + " |"
    separateur = "|" + "|".join([" --- "] * colonnes) + "|"
    corps = ["| " + " | ".join(ligne) + " |" for ligne in lignes[1:]]
    return "\n".join([entete, separateur] + corps)


def liste(contenu: str, ordonnee: bool, conversion: Conversion) -> str:
    puces = []
    for element in re.split(r"\\item\b", contenu)[1:]:
        corps = convertir(element, conversion).strip()
        if not corps:
            continue
        marque = f"{len(puces) + 1}." if ordonnee else "-"
        decale = corps.replace("\n", "\n" + " " * (len(marque) + 1))
        puces.append(f"{marque} {decale}")
    return "\n".join(puces)


def langage_declare(source: str) -> str:
    """Langage annoncé par le .tex : `\\lstset{language=Python}` ou `\\lstdefinestyle{…,language=…}`.

    Le deviner d'après le contenu suffisait pour un seul cours ; avec un deuxième, la source fait foi.
    """
    preambule = source.split(r"\begin{document}", 1)[0]
    trouve = re.search(r"language\s*=\s*([A-Za-z+#]+)", preambule)
    return trouve[1].lower() if trouve else ""


def schema_tikz(conversion: Conversion) -> str:
    """Un `tikzpicture` devient le SVG que `scripts/figures_tikz.py` en a compilé (US-55).

    La numérotation est la même des deux côtés — l'ordre d'apparition dans le document —, ce qui
    évite une table de correspondance que quelqu'un finirait par désynchroniser.
    """
    conversion.tikz += 1
    nom = f"{conversion.prefixe_tikz}-{conversion.tikz:02d}"
    alt = conversion.alternatifs.get(nom, "")
    origine = "texte fourni par le PO" if alt else "TODO(PO)"
    conversion.figures.append(f"{nom} : schéma TikZ, texte alternatif — {origine}")
    return (f'{{{{< svg {conversion.prefixe_figures}/{nom}.svg '
            f'alt="{alt or "TODO(PO): description du schéma"}" >}}}}')


def code(contenu: str, conversion: Conversion, options: str | None = None) -> str:
    """lstlisting -> bloc de code, dans le langage du cours ; une sortie de programme reste nue.

    Le style est celui que le .tex demande (`[style=out]`, `[style=err]`, `[style=sh]`) : une sortie
    de programme ou une trace d'erreur n'est pas du code, et ne doit pas être colorée comme tel.
    """
    corps = contenu.strip("\n")
    style = re.search(r"style\s*=\s*(\w+)", options or "")
    if style and style[1] in STYLES_CODE:
        langage = STYLES_CODE[style[1]]
        conversion.codes.append(langage or "sortie")
        return f"```{langage}\n{corps}\n```"
    shell = re.search(r"^\s*(\./|\$ |#\s|[a-z-]+\s+--?[a-z])", corps, re.M) and ";" not in corps
    langage = "bash" if shell else conversion.langage
    conversion.codes.append(langage)
    return f"```{langage}\n{corps}\n```"


def colonnes(contenu: str, conversion: Conversion) -> str:
    """`columns` de Beamer -> colonnes Quarto, largeurs comprises (US-60).

    Le cours d'Introduction au ML pose une figure à côté de son commentaire. Jusqu'ici les deux
    colonnes étaient converties l'une après l'autre : le texte passait sous la figure, et la slide
    perdait sa mise en page. Les largeurs sont écrites dans la source (`0.54\\linewidth`), en
    fractions ; Quarto les veut en pourcentages.
    """
    morceaux = re.split(r"\\column\s*\{([^}]*)\}", contenu)
    if len(morceaux) < 3:
        return convertir(contenu, conversion)
    blocs = ["::: {.columns}"]
    for largeur, corps in zip(morceaux[1::2], morceaux[2::2]):
        fraction = re.match(r"\s*([0-9.]+)\s*\\(?:linewidth|textwidth)", largeur)
        pourcent = f'{round(float(fraction[1]) * 100)}%' if fraction else "50%"
        blocs.append(f'::: {{.column width="{pourcent}"}}')
        blocs.append(convertir(corps, conversion))
        blocs.append(":::")
    blocs.append(":::")
    return "\n".join(blocs)


def convertir(texte: str, conversion: Conversion) -> str:
    """Convertit un fragment : environnements connus, puis texte courant."""
    # Les commandes de taille sont retirées ici aussi : « {\small\begin{tabular}… } » entoure parfois
    # un environnement, et ses accolades traverseraient sinon la conversion.
    morceaux, reste = [], retirer_tailles(sans_commentaires(texte))

    # Les mathématiques sont mises de côté **avant** de chercher les environnements : `\begin{cases}`
    # vit à l'intérieur d'un `$…$`, et le prendre pour un environnement du document coupait la
    # formule en deux — c'est ce qui laissait deux `cases` et un `\rightarrow` non convertis au
    # chapitre 1 du cours de C. `inline` les protégera de nouveau, à sa façon.
    formules: list[str] = []

    # La formule est rangée **telle quelle** : cette mise de côté balaie aussi le contenu des
    # `verbatim` et des `lstlisting`, où un `$` est une invite shell et non une formule. La
    # normaliser ici collait l'invite à la commande (« $ pwd » devenait « $pwd ») et soudait deux
    # lignes de terminal du chapitre 0 du cours de Python. C'est `inline`, qui ne voit que du texte
    # courant, qui la normalise.
    def mettre_de_cote(trouve: re.Match[str]) -> str:
        formules.append(trouve[0])
        return f"\x02{len(formules) - 1}\x02"

    def rendre(fragment: str) -> str:
        return re.sub(r"\x02(\d+)\x02", lambda t: formules[int(t[1])], fragment)

    reste = MOTIF_MATHS.sub(mettre_de_cote, reste)
    while True:
        trouve = re.search(r"\\begin\{([A-Za-z*]+)\}", reste)
        if not trouve:
            morceaux.append(inline(rendre(reste), conversion))
            break
        morceaux.append(inline(rendre(reste[:trouve.start()]), conversion))
        nom = trouve[1]
        position = trouve.end()
        titre, position = option(reste, position)
        if nom == "tabular":  # la spécification des colonnes ne sert qu'à LaTeX
            _, position = argument(reste, position)
        elif nom in conversion.encadres and position < len(reste) and reste[position] == "{":
            # Un encadré `tcolorbox` porte son titre entre accolades, là où un encadré Beamer le met
            # entre crochets : `\begin{definitionbox}{Le langage C}`.
            titre, position = argument(reste, position)
        contenu, suite = environnement(reste, nom, position)
        contenu, titre = rendre(contenu), (rendre(titre) if titre else titre)

        if nom in conversion.encadres:
            genre, classe, defaut = conversion.encadres[nom]
            corps = convertir(contenu, conversion)
            entete = (f'::: {{.callout-{genre} .{classe} '
                      f'title="{titre_de_callout(titre, conversion) or defaut}"}}')
            morceaux.append(f"{entete}\n{corps}\n:::")
        elif nom in ENCADRES:
            genre, classe, defaut = ENCADRES[nom]
            corps = convertir(contenu, conversion)
            entete = (f'::: {{.callout-{genre} .{classe} '
                      f'title="{titre_de_callout(titre, conversion) or defaut}"}}')
            morceaux.append(f"{entete}\n{corps}\n:::")
        elif nom in ("itemize", "enumerate"):
            morceaux.append(liste(contenu, nom == "enumerate", conversion))
        elif nom == "lstlisting":
            morceaux.append(code(contenu, conversion, titre))
        elif nom == "verbatim":
            # `verbatim` n'a ni langage ni style : c'est du texte tel quel — une trace d'exécution, un
            # schéma en caractères. Le colorer comme du C inventerait une syntaxe qu'il n'a pas.
            conversion.codes.append("sortie")
            morceaux.append(conversion.proteger("```\n" + contenu.strip("\n") + "\n```"))
        elif nom == "tabular":
            morceaux.append(tableau(contenu, conversion))
        elif nom == "tikzpicture":
            morceaux.append(conversion.proteger(schema_tikz(conversion)))
        elif nom in ("align", "align*", "equation", "equation*", "gather", "gather*"):
            # Mathématiques hors ligne : MathJax les rend telles quelles dans un bloc « $$ ».
            # `align` se compose en `aligned`, qui est sa forme utilisable à l'intérieur de « $$ ».
            interne = {"align": "aligned", "align*": "aligned", "gather": "gathered",
                       "gather*": "gathered"}.get(nom)
            corps = contenu.strip()
            if interne:
                corps = f"\\begin{{{interne}}}\n{corps}\n\\end{{{interne}}}"
            morceaux.append(conversion.proteger(f"$$\n{corps}\n$$"))
        elif nom == "columns":
            morceaux.append(conversion.proteger(colonnes(contenu, conversion)))
        elif nom in ("center", "block", "column"):
            morceaux.append(convertir(contenu, conversion))
        else:
            morceaux.append(conversion.non_converti(f"\\begin{{{nom}}} … \\end{{{nom}}}"))
        reste = reste[suite:]
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(m for m in morceaux if m.strip())).strip()


def page(corps: str, conversion: Conversion) -> list[str]:
    """Un CM rédigé donne une page : ses sections en deviennent les titres (US-40).

    Le document est un `article`, et non un deck : il n'y a pas de frames à découper, mais une
    hiérarchie à préserver. `\\section` devient un titre de niveau 2 — le niveau 1 est le titre de la
    page —, `\\subsection` un niveau 3, et le texte entre deux titres est converti tel quel.
    """
    niveaux = {"section": "##", "subsection": "###", "subsubsection": "####"}
    # Le titre peut être précédé d'un argument facultatif : `\section[court]{affiché}`.
    motif = re.compile(r"\\(section|subsection|subsubsection)\*?(?=[\[{])")
    sorties = []

    def morceau(texte: str, titre: str) -> None:
        conversion.slide = titre or "(avant la première section)"
        # Les figures sont traitées sur le texte d'origine : la légende qui suit l'image y est
        # encore reconnaissable, avant que les commandes de taille ne soient retirées.
        converti = convertir(figures(texte, conversion), conversion)
        if converti.strip():
            sorties.append(conversion.restaurer(converti))

    trouve = motif.search(corps)
    if trouve and corps[:trouve.start()].strip():
        morceau(corps[:trouve.start()], "")

    while trouve:
        _, apres_option = option(corps, trouve.end())
        titre, position = argument(corps, apres_option)
        suivant = motif.search(corps, position)
        sorties.append(f"{niveaux[trouve[1]]} {inline(titre, conversion)}")
        morceau(corps[position:suivant.start() if suivant else len(corps)], titre)
        trouve = suivant
    return sorties


def slides(corps: str, conversion: Conversion) -> list[str]:
    """Une frame donne une slide (titre de niveau 2), une section une slide de section."""
    sorties, position = [], 0
    motif = re.compile(r"\\(section|begin\{frame\})")
    while True:
        trouve = motif.search(corps, position)
        if not trouve:
            break
        if trouve[1] == "section":
            # `\section[titre court]{titre affiché}` : l'argument facultatif ne sert qu'à la table
            # des matières de Beamer. Ne pas le sauter faisait lire « court]{affiché » comme un seul
            # titre — six slides de section de la séance 5 du cours de ML s'affichaient ainsi.
            _, apres_option = option(corps, trouve.end())
            titre, position = argument(corps, apres_option)
            conversion.slide = titre
            sorties.append(f"# {inline(titre, conversion)}")
            continue
        suite = trouve.end()
        _, suite = option(corps, suite)          # [fragile], [plain,noframenumbering]…
        titre, suite = ("", suite) if suite >= len(corps) or corps[suite] != "{" \
            else argument(corps, suite)
        contenu, position = environnement(corps, "frame", suite)
        if "\\titlepage" in contenu:             # la page de titre vient de l'en-tête YAML
            conversion.ignorees["titlepage"] += 1
            continue
        conversion.slide = titre or "(sans titre)"
        # Les figures sont traitées sur le texte d'origine : la légende qui suit l'image est encore
        # reconnaissable à ce moment-là, avant que les commandes de taille ne soient retirées.
        corps_slide = convertir(figures(contenu, conversion), conversion)
        sorties.append(conversion.restaurer(f"## {inline(titre, conversion)}\n\n{corps_slide}"))
    return sorties


# --------------------------------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------------------------------

def nettoyer_svg(source: Path, cible: Path) -> dict[str, int]:
    """Encres et gris en currentColor, fonds clairs transparents, police héritée de la page.

    Le blanc n'est neutralisé que sur les formes : sur un texte, il sert à écrire dans un bloc de
    couleur, et doit le rester.
    """
    ET.register_namespace("", SVG)
    # Les préfixes doivent être réécrits tels quels. matplotlib place ses marqueurs — les points d'un
    # nuage — dans <defs> et les rappelle par <use xlink:href>. Sans cet enregistrement, ElementTree
    # les réécrit « ns4:href » : légal en XML, mais la page les incorpore dans du HTML, où seul
    # « xlink:href » est reconnu. Les marqueurs disparaissaient alors purement et simplement.
    for prefixe, espace in (("xlink", "http://www.w3.org/1999/xlink"),
                            ("dc", "http://purl.org/dc/elements/1.1/"),
                            ("cc", "http://creativecommons.org/ns#"),
                            ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")):
        ET.register_namespace(prefixe, espace)
    arbre = ET.parse(source)
    compte = Counter()
    encres = {c.lower() for c in ENCRES}

    def valeur_nettoyee(propriete: str, valeur: str, balise: str) -> str | None:
        """Ce que devient une couleur, ou None si elle doit rester telle quelle."""
        brute = valeur.strip().lower()
        if propriete in ("fill", "stroke") and brute in encres:
            compte["encre"] += 1
            return "currentColor"
        if propriete == "fill" and balise in FORMES and brute in FONDS_CLAIRS:
            compte["fond"] += 1
            return "none"
        if propriete == "font-family":
            compte["police"] += 1
            return "inherit"
        return None

    for element in arbre.iter():
        balise = element.tag.split("}")[-1]
        for propriete in ("fill", "stroke", "font-family"):
            valeur = element.get(propriete)
            if valeur is not None:
                remplacement = valeur_nettoyee(propriete, valeur, balise)
                if remplacement:
                    element.set(propriete, remplacement)

        # matplotlib n'écrit pas d'attributs mais une feuille de style en ligne :
        # style="fill: #0f3a5e; font-family: DejaVu Sans". Sans cela, ses figures gardaient
        # leurs encres noires en mode sombre — aucune figure du cours de Python n'était adaptée.
        style = element.get("style")
        if not style:
            continue
        declarations = []
        for declaration in style.split(";"):
            propriete, separateur, valeur = declaration.partition(":")
            remplacement = (valeur_nettoyee(propriete.strip().lower(), valeur, balise)
                            if separateur else None)
            declarations.append(f"{propriete.strip()}: {remplacement}" if remplacement
                                else declaration.strip())
        element.set("style", "; ".join(d for d in declarations if d))
    cible.parent.mkdir(parents=True, exist_ok=True)
    arbre.write(cible, encoding="unicode", xml_declaration=False)
    cible.write_text(identifiants_uniques(cible.read_text(encoding="utf-8"), cible.stem).rstrip()
                     + "\n", encoding="utf-8")
    return compte


def identifiants_uniques(svg: str, prefixe: str) -> str:
    """Préfixe les identifiants internes d'une figure par son nom.

    Une figure incorporée dans la page partage l'espace des identifiants avec **toutes les autres**
    de cette page. `pdftocairo` nomme ses glyphes `glyph-0-0`, `glyph-0-1`… et recommence à zéro pour
    chaque figure : sur une page qui en porte vingt, `glyph-0-0` est défini vingt fois, et chaque
    `<use href="#glyph-0-0">` désigne celui de la **première**. Tous les textes des figures suivantes
    s'écrivaient donc avec les lettres de la première — c'est ce que le PO a vu sur les chapitres 1
    et 2 du cours de C.

    Le défaut ne se voit ni dans le SVG isolé, ni dans un contrôle de structure : chaque figure, prise
    seule, est parfaitement valide. Il n'apparaît qu'une fois plusieurs figures posées dans la même
    page.
    """
    # Les deux écritures existent dans les figures de ce site : pdftocairo met des guillemets,
    # dvisvgm des apostrophes. Le navigateur les lit pareil, une expression régulière non.
    identifiants = set(re.findall(r"""\bid=["']([^"']+)["']""", svg))
    if not identifiants:
        return svg
    for identifiant in sorted(identifiants, key=len, reverse=True):
        nouveau = f"{prefixe}-{identifiant}"
        for guillemet in ('"', "'"):
            svg = svg.replace(f"id={guillemet}{identifiant}{guillemet}",
                              f"id={guillemet}{nouveau}{guillemet}")
            svg = svg.replace(f"href={guillemet}#{identifiant}{guillemet}",
                              f"href={guillemet}#{nouveau}{guillemet}")
        svg = svg.replace(f"url(#{identifiant})", f"url(#{nouveau})")
    return svg


# --------------------------------------------------------------------------------------------------
# Écriture
# --------------------------------------------------------------------------------------------------

def ressource(brute: str) -> dict:
    """« lab|cours/x/ressources/lab1.pdf|Lab 1 » -> l'entrée écrite dans l'en-tête de la séance.

    Un corrigé a un quatrième champ, sa **date de publication** : il est obligatoire, et c'est lui qui
    décide du jour où le corrigé rejoint le site. Son fichier vit dans `_corriges/`, que Quarto ne rend
    pas ; il est copié à l'assemblage, sous `corriges/`, le jour venu seulement.
    """
    champs = brute.split("|")
    if len(champs) < 3:
        sys.exit(f"Ressource mal formée : « {brute} » (attendu : type|fichier|titre[|date]).")
    type_, fichier, titre = champs[0], champs[1], champs[2]
    date = champs[3] if len(champs) > 3 else ""
    if type_ not in RESSOURCES and type_ != CORRIGE:
        sys.exit(f"Type de ressource inconnu : « {type_} » "
                 f"(attendu : {', '.join(sorted(RESSOURCES))} ou {CORRIGE}).")
    if type_ == CORRIGE and not ISO.fullmatch(date):
        sys.exit(f"Le corrigé « {titre} » n'a pas de date de publication (type|fichier|titre|AAAA-MM-JJ). "
                 "Sans date, un corrigé ne peut pas être publié : c'est la règle d'US-49.")
    if type_ != CORRIGE and date:
        sys.exit(f"Seul un corrigé porte une date de publication (ici : « {type_} »).")

    # Chemins : `fichier` est relatif au dossier du cours (le filtre y lit le poids), `chemin` est
    # l'adresse publique. Ils se déduisent du chemin donné, et non de `--sortie` : le contrôle de
    # conversion rejoue l'import dans un dossier temporaire, où `--sortie` ne dit plus rien du cours.
    parties = Path(fichier).parts
    if len(parties) < 3 or parties[0] != "cours":
        sys.exit(f"Ressource hors d'un cours : {fichier} (attendu : cours/<slug>/…).")
    slug, relatif = parties[1], str(Path(*parties[2:]))
    publie = f"corriges/{Path(relatif).name}" if type_ == CORRIGE else relatif
    return {"type": type_, "titre": titre or Path(relatif).name, "fichier": relatif,
            "chemin": f"/cours/{slug}/{publie}", "date": date}


def slide_ressources(ressources: list[dict]) -> str:
    """Dernière slide : les ressources de la séance (US-49).

    La slide n'est qu'un emplacement : c'est `assets/lua/ressources.lua` qui la remplit **au rendu**,
    parce que deux de ses données ne sont connues qu'à ce moment-là — le poids de chaque fichier, et le
    fait qu'un corrigé ait atteint ou non sa date de publication. Un corrigé avant sa date n'apparaît
    donc nulle part, pas même en commentaire dans la page.
    """
    return "::: {#ressources-seance}\n:::" if ressources else ""


def section_ressources(ressources: list[dict]) -> str:
    """Même emplacement, en fin de page rédigée : le filtre le remplit au rendu (US-40, US-49)."""
    return "::: {#ressources-seance}\n:::" if ressources else ""


def slide_capsule(video: str, titre: str) -> str:
    """Dernière slide : la capsule vidéo de la séance, chargée seulement au clic (US-19)."""
    return f'## Capsule vidéo\n\n{{{{< capsule {video} titre="{titre}" >}}}}'


def guillemets(valeur: str) -> str:
    return '"' + valeur.replace('"', '\\"') + '"'


def entete_page(entete: dict[str, str], description: str, numero: str,
                ressources: list[dict] | None = None) -> str:
    """En-tête d'un CM rédigé (US-40) : une page, et non une présentation.

    Le **numéro affiché** est une donnée à part : un cours peut commencer à -1 ou à 0 — le chapitre
    d'introduction de Programmation C avancée est le « -1 » —, et le nom du fichier ne sert qu'à
    ordonner. Sans numéro, la page porte son seul titre.
    """
    lignes = ["---", f"title: {guillemets(entete.get('title', 'TODO(PO): titre'))}"]
    if entete.get("subtitle"):
        lignes.append(f"subtitle: {guillemets(entete['subtitle'])}")
    # Une page rédigée n'est pas imprimée en PDF depuis le site : c'est le PDF de LaTeX qui fait
    # foi, attaché en ressource. La table des séances a besoin de le savoir.
    lignes.append('cible: "page"')
    # Marque la page pour la feuille de style et le script de défilement (US-59) : un chapitre rédigé
    # porte des tableaux et des figures plus larges qu'un téléphone, qui doivent défiler dans leur
    # cadre plutôt qu'élargir la page.
    lignes.append("body-classes: cours-page")
    if numero:
        lignes.append(f"numero: {guillemets(numero)}")
    lignes += ressources_yaml(ressources)
    lignes += [
        f"description: {guillemets(description)}",
        f"author: {guillemets(entete.get('author', ''))}",
        # Un chapitre rédigé est long : la table des matières latérale est ce qui le rend navigable.
        "toc: true",
        "toc-location: left",
        "---",
        "",
    ]
    return "\n".join(lignes)


def ressources_yaml(ressources: list[dict] | None) -> list[str]:
    """Bloc `ressources:` de l'en-tête, le même pour une page et pour un deck (US-49).

    `fichier` est relatif au dossier du cours — c'est ce qui permet au filtre d'en lire le poids ;
    `chemin` est l'adresse publique. Un corrigé porte en plus sa date de publication : avant elle,
    ni le filtre ni le rendu ne le laissent apparaître.
    """
    lignes = []
    for ressource in ressources or []:
        lignes.append(f"  - type: {guillemets(ressource['type'])}")
        lignes.append(f"    titre: {guillemets(ressource['titre'])}")
        lignes.append(f"    fichier: {guillemets(ressource['fichier'])}")
        lignes.append(f"    chemin: {guillemets(ressource['chemin'])}")
        if ressource.get("date"):
            lignes.append(f"    date: {guillemets(ressource['date'])}")
    return ["ressources:"] + lignes if lignes else []


def entete_yaml(entete: dict[str, str], description: str, feuille: str, video: str = "",
                ressources: list[dict] | None = None) -> str:
    lignes = [
        "---",
        f"title: {guillemets(entete.get('title', 'TODO(PO): titre'))}",
    ]
    if entete.get("subtitle"):
        lignes.append(f"subtitle: {guillemets(entete['subtitle'])}")
    if video:
        # Métadonnée de la séance : la capsule est aussi une slide, en fin de deck.
        lignes.append(f"video: {guillemets(video)}")
    # Métadonnée de la séance : la slide de fin et la page du cours y lisent les ressources (US-49).
    lignes += ressources_yaml(ressources)
    lignes += [
        f"description: {guillemets(description)}",
        f"author: {guillemets(entete.get('author', ''))}",
        f"institute: {guillemets(entete.get('institute', ''))}",
        "format:",
        "  revealjs:",
        f"    theme: [default, {feuille}]",
        "    slide-number: true",
        # Contenu centré verticalement : sans cela, une slide courte laisse tout le bas de l'écran vide.
        "    center: true",
        # Le deck d'origine ne numérote pas les lignes de code ; les ancres que Quarto ajoute pour
        # cela portent par ailleurs un aria-label interdit sur un lien sans cible.
        "    code-line-numbers: false",
        # Les sections donnent des piles verticales : en navigation linéaire, les flèches parcourent
        # toutes les slides dans l'ordre du cours, comme le PDF Beamer.
        "    navigation-mode: linear",
        "    smaller: true",
        "    scrollable: true",
        "    history: false",
        # Le menu de revealjs est construit à l'exécution : ce script lui donne un nom accessible et
        # rend son panneau atteignable au clavier (US-42).
        "    include-after-body:",
        '      text: \'<script src="/assets/js/slides-accessibilite.js"></script>'
        '<script src="/assets/js/slides-pdf.js"></script>\'',
        "---",
        "",
    ]
    return "\n".join(lignes)


def depuis_la_racine(chemin: Path) -> Path:
    """Chemin relatif au dépôt quand il y est, sinon tel quel (import hors dépôt)."""
    try:
        return chemin.resolve().relative_to(Path(__file__).resolve().parent.parent)
    except ValueError:
        return chemin


def ecrire_rapport(chemin: Path, source: Path, sortie: Path, conversion: Conversion,
                   figures: dict[str, dict[str, int]]) -> None:
    lignes = [
        f"# Rapport de conversion — {source.name}",
        "",
        # Chemin relatif au dépôt : un chemin absolu inscrirait le dossier personnel de qui importe
        # dans un fichier commité, et changerait d'une machine à l'autre.
        f"Produit par `scripts/importer_chapitre.py` (US-15). Sortie : `{depuis_la_racine(sortie)}`.",
        "",
        "## À traiter à la main",
        "",
    ]
    if conversion.non_convertis:
        lignes += [f"- **{slide}** : `{quoi}`" for slide, quoi in conversion.non_convertis]
    else:
        lignes.append("Rien : tout le contenu a été converti.")
    lignes += ["", "## Figures", ""]
    lignes += [f"- {ligne}" for ligne in conversion.figures]
    if figures:
        lignes += ["", "Nettoyage des SVG (encres en `currentColor`, fonds clairs transparents) :", ""]
        lignes += [f"- `{nom}` : {compte['encre']} encre(s), {compte['fond']} fond(s), "
                   f"{compte['police']} police(s)" for nom, compte in figures.items()]
    lignes += [
        "", "## Blocs de code", "",
        *(f"- bloc {i + 1} : `{langage}`" for i, langage in enumerate(conversion.codes)),
        "", "## Tableaux", "", f"{conversion.tableaux} tableau(x) converti(s) en Markdown.",
        "", "## Commandes de mise en page ignorées", "",
        "Elles n'ont pas d'équivalent en HTML : le style s'en charge.", "",
        *(f"- `\\{nom}` : {nombre} fois" for nom, nombre in sorted(conversion.ignorees.items())),
        "",
    ]
    chemin.write_text("\n".join(lignes), encoding="utf-8")


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("source", type=Path, help="fichier .tex du chapitre")
    analyseur.add_argument("--sortie", type=Path, required=True, help="fichier .qmd à écrire")
    analyseur.add_argument("--figures", type=Path, required=True, help="dossier des SVG nettoyés")
    analyseur.add_argument("--rapport", type=Path, help="rapport de conversion (Markdown)")
    analyseur.add_argument("--prefixe-figures",
                           help="chemin des figures écrit dans le .qmd, s'il doit différer du dossier "
                                "réel (utilisé par scripts/verifier_conversion.py, qui écrit ailleurs)")
    analyseur.add_argument("--figure-python", action="append", default=[], metavar="NOM=SCRIPT.py",
                           help="figure produite par un bloc Python exécuté, au lieu d'être importée")
    analyseur.add_argument("--alt", type=Path,
                           help="textes alternatifs des figures sans légende (TOML)")
    analyseur.add_argument("--description", default="",
                           help="description de la page, pour le référencement")
    analyseur.add_argument("--video", default="",
                           help="identifiant YouTube de la capsule de la séance (slide finale, US-19)")
    analyseur.add_argument("--ressource", action="append", default=[],
                           metavar="TYPE|FICHIER|TITRE[|DATE]",
                           help="ressource de la séance : lab, td, notebook ou corrige, son fichier dans "
                                "le dépôt et son titre ; un corrigé exige en plus sa date de publication "
                                "(AAAA-MM-JJ). Répétable (US-49)")
    analyseur.add_argument("--prefixe-tikz",
                           help="préfixe des schémas TikZ compilés (US-55) ; par défaut, le nom du "
                                "fichier de sortie")
    analyseur.add_argument("--titre",
                           help="titre de la page, quand celui du .tex est une couverture LaTeX "
                                "(« Chapitre -1 : Introduction, Programmation C Avancée - L3 GLSI »)")
    analyseur.add_argument("--cible", choices=("slides", "page"), default="slides",
                           help="slides revealjs (un deck Beamer) ou page rédigée (un CM, US-40)")
    analyseur.add_argument("--numero", default="",
                           help="numéro affiché de la séance : « 1 », « 0 », « -1 »… Vide, la page "
                                "porte son seul titre. Le nom du fichier, lui, ne sert qu'à ordonner.")
    analyseur.add_argument("--encadre", action="append", default=[], metavar="NOM=GENRE|TITRE",
                           help="environnement d'encadré du document et le callout qui lui répond, "
                                "par exemple « definitionbox=note|Définition » (répétable, US-40)")
    analyseur.add_argument("--langage-code",
                           help="langage des blocs lstlisting (par défaut : celui que le .tex déclare, "
                                "sinon java). Une commande shell reste du shell.")
    analyseur.add_argument("--feuille", default="../../../assets/css/slides.scss",
                           help="feuille de style des slides, relative au .qmd")
    args = analyseur.parse_args()

    source = args.source.read_text(encoding="utf-8")
    alternatifs = tomllib.loads(args.alt.read_text(encoding="utf-8")) if args.alt else {}
    # Les figures sont citées dans le .qmd par un chemin relatif à lui, comme un lien Markdown.
    prefixe = args.prefixe_figures or os.path.relpath(args.figures, args.sortie.parent)
    # Les figures qui n'existent qu'en PNG sont repérées d'avance : l'insertion diffère, et la
    # conversion a besoin de le savoir au moment où elle écrit la page.
    figs = args.source.parent / "figs"
    matricielles = {f.stem for f in figs.glob("*.png")
                    if not (figs / f"{f.stem}.svg").is_file()} if figs.is_dir() else set()

    conversion = Conversion(alternatifs, prefixe,
                            args.langage_code or langage_declare(source) or "java")
    conversion.prefixe_tikz = args.prefixe_tikz or args.sortie.stem
    conversion.matricielles = matricielles
    # Encadrés propres au document : leur sens est une décision du PO, jamais une déduction. Ils sont
    # déclarés à l'import et enregistrés dans le manifeste, que la CI rejoue.
    for brute in args.encadre:
        nom, _, reste = brute.partition("=")
        genre, _, titre = reste.partition("|")
        if genre not in ("note", "tip", "warning", "important", "caution"):
            sys.exit(f"Encadré « {nom} » : genre de callout inconnu « {genre} » "
                     "(note, tip, warning, important ou caution).")
        conversion.encadres[nom] = (genre, f"encadre-{nom}", titre or nom)
    for couple in args.figure_python:
        nom, _, script = couple.partition("=")
        conversion.scripts[nom] = Path(script)

    debut = source.index("\\begin{document}") + len("\\begin{document}")
    # Le préambule est passé **à part** : on y lit les `\newcommand` du document, et on les
    # développe dans le corps. Faire traverser le préambule par le reste des substitutions cassait
    # le cours de Python, dont les définitions contiennent les motifs que ces substitutions visent.
    corps = macros_du_theme(source[debut:source.index("\\end{document}")],
                            source.split("\\begin{document}", 1)[0])

    entete = preambule(source)
    if args.titre:
        entete["title"] = args.titre
    description = args.description or entete.get("subtitle", "")
    ressources = [ressource(brute) for brute in args.ressource]

    if args.cible == "page":
        # Un CM rédigé : les ressources sont une section de fin, et non une slide.
        morceaux = page(corps, conversion)
        fin = section_ressources(ressources)
        if fin:
            morceaux.append(fin)
        contenu = entete_page(entete, description, args.numero, ressources)
    else:
        morceaux = slides(corps, conversion)
        slide = slide_ressources(ressources)
        if slide:
            morceaux.append(slide)
        if args.video:
            morceaux.append(slide_capsule(args.video, entete.get("title", "Capsule vidéo")))
        contenu = entete_yaml(entete, description, args.feuille, args.video, ressources)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(contenu + "\n\n".join(morceaux) + "\n", encoding="utf-8")

    nettoyees = {}
    dossier_figures = args.source.parent / "figs"
    for ligne in conversion.figures:
        nom = ligne.split(" :")[0]
        origine = dossier_figures / f"{nom}.svg"
        if origine.is_file():
            nettoyees[nom] = nettoyer_svg(origine, args.figures / f"{nom}.svg")
        elif (dossier_figures / f"{nom}.png").is_file():
            # Figure sans source vectorielle : elle est copiée telle quelle, et la page la pose
            # comme une image ordinaire (voir `figures`).
            args.figures.mkdir(parents=True, exist_ok=True)
            (args.figures / f"{nom}.png").write_bytes((dossier_figures / f"{nom}.png").read_bytes())

    if args.rapport:
        ecrire_rapport(args.rapport, args.source, args.sortie, conversion, nettoyees)

    unite = "section(s)" if args.cible == "page" else "slide(s)"
    print(f"{len(morceaux)} {unite} -> {args.sortie}")
    print(f"{len(nettoyees)} figure(s) nettoyée(s) -> {args.figures}")
    if conversion.non_convertis:
        print(f"{len(conversion.non_convertis)} élément(s) à traiter à la main "
              f"(voir {args.rapport or 'le rapport'}) :")
        for slide, quoi in conversion.non_convertis:
            print(f"  - {slide} : {quoi}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
