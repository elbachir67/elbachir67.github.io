#!/usr/bin/env python3
"""Convertit un chapitre de cours Beamer en slides Quarto revealjs (US-15).

    python3 scripts/importer_chapitre.py cours/<slug>/_sources/cm1_archi_seance1.tex \
        --sortie cours/<slug>/chapitres/01-<slug>.qmd \
        --figures cours/<slug>/figures \
        --rapport cours/<slug>/_sources/rapport-import.md

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
            "toprule", "midrule", "bottomrule", "addlinespace", "small", "scriptsize", "footnotesize",
            "normalsize", "large", "Large", "raggedright", "noindent", "titlepage"}

# Couleurs d'encre du jeu de figures : elles suivront la couleur du texte de la page.
ENCRES = {"#000", "#000000", "black", "#1a3a5c", "#1A3A5C", "#1c2a33", "#1C2A33",
          "#333", "#333333", "#444", "#444444", "#5a5a5a", "#5A5A5A", "#5a6b75", "#5A6B75"}
# Fonds clairs : transparents, pour rester lisibles en mode sombre comme en projection.
FONDS_CLAIRS = {"#fff", "#ffffff", "white", "#f8f9fb", "#fafafa", "#f7f7f7"}
FORMES = {"rect", "circle", "ellipse", "polygon", "polyline", "path", "line"}


class Conversion:
    """Contexte de la conversion, et compte rendu de ce qu'elle a fait ou laissé à faire."""

    def __init__(self, alternatifs: dict[str, str], prefixe_figures: str) -> None:
        self.alternatifs = alternatifs          # textes alternatifs fournis par le PO, par figure
        self.prefixe_figures = prefixe_figures  # chemin des figures, relatif au .qmd produit
        self.insertions: list[str] = []         # blocs déjà finalisés, à l'abri de la conversion
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
    """Argument optionnel entre crochets, s'il y en a un."""
    if position < len(texte) and texte[position] == "[":
        fin = texte.index("]", position)
        return texte[position + 1:fin], fin + 1
    return None, position


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


def sans_balises(texte: str) -> str:
    """Texte nu d'une légende, pour servir de texte alternatif."""
    texte = re.sub(r"\\[A-Za-z]+\s*\{([^{}]*)\}", r"\1", texte)
    texte = re.sub(r"\\[A-Za-z]+\s*", "", texte).replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", texte).replace('"', "«").strip()


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
        nom = trouve["nom"]
        mesure = re.search(r"width=([\d.]+)\\linewidth", trouve["options"] or "")
        largeur = float(mesure[1]) if mesure else None

        legende, fin = None, trouve.end()
        suivante = MOTIF_LEGENDE.match(texte, trouve.end())
        if suivante:
            ouverture = texte.index("{", trouve.end())
            fermeture = accolade(texte, ouverture)
            legende, fin = texte[suivante.end():fermeture], fermeture + 1

        if nom.startswith("figA"):
            conversion.figures.append(f"{nom} : non importée, produite par le bloc Python d'US-18")
            insertion = ("<!-- FIGURE CALCULÉE (US-18) : " + nom
                         + ", à produire par le bloc Python de _sources/figs/figA.py -->")
        else:
            alt = conversion.alternatifs.get(nom) or (sans_balises(legende) if legende else "")
            origine = ("texte fourni par le PO" if nom in conversion.alternatifs
                       else "légende du .tex" if legende else "TODO(PO)")
            conversion.figures.append(f"{nom} : insérée, texte alternatif — {origine}")
            taille = f' largeur="{round(largeur * 100)}%"' if largeur else ""
            insertion = (f'{{{{< svg {conversion.prefixe_figures}/{nom}.svg '
                         f'alt="{alt or "TODO(PO): description de la figure"}"{taille} >}}}}')

        # Seule l'insertion est mise à l'abri ; la légende, elle, suit le chemin normal du texte.
        bloc = conversion.proteger(insertion)
        if legende:
            bloc += "\n\n::: {.legende}\n" + legende.strip() + "\n:::"
        texte = texte[:trouve.start()] + bloc + texte[fin:]


MOTIF_MATHS = re.compile(r"\$\$.+?\$\$|\$[^$]+?\$|\\\[.+?\\\]", re.S)


def inline(texte: str, conversion: Conversion) -> str:
    """Conversion du texte courant : mise en forme et caractères LaTeX.

    Les formules sont mises de côté le temps de la conversion : leur contenu est du LaTeX, que Quarto
    rend tel quel, et ne doit donc pas être traité comme du texte.
    """
    formules: list[str] = []
    texte = retirer_tailles(sans_commentaires(texte))

    def garder(trouve: re.Match[str]) -> str:
        formules.append(trouve[0])
        return f"\x00{len(formules) - 1}\x00"

    texte = MOTIF_MATHS.sub(garder, texte)

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
        if nom == "oe":
            return "œ"
        if nom == "newline":
            return "<br>"
        return conversion.non_converti("\\" + nom)

    texte = re.sub(r"\\(vskip|vspace)\*?\s*-?[\d.]+\s*(pt|ex|em|cm|mm)", "", texte)
    texte = re.sub(r"\\([A-Za-z]+)\s*(?:\{\})?", commande, texte)
    texte = (texte.replace("\\%", "%").replace("\\&", "&").replace("\\_", "_")
             .replace("\\#", "#").replace("~", "\u00a0"))
    texte = re.sub(r"\x00(\d+)\x00", lambda t: formules[int(t[1])], texte)
    return re.sub(r"\n{3,}", "\n\n", texte).strip()


def tableau(contenu: str, conversion: Conversion) -> str:
    """tabular -> tableau Markdown ; les filets de booktabs disparaissent."""
    conversion.tableaux += 1
    lignes = []
    for brute in contenu.split("\\\\"):
        cellules = [inline(c, conversion).replace("\n", " ").strip()
                    for c in brute.split("&")]
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


def code(contenu: str, conversion: Conversion) -> str:
    """lstlisting -> bloc de code ; le langage se déduit du contenu, Java ou shell."""
    corps = contenu.strip("\n")
    shell = re.search(r"^\s*(\./|\$ |#\s|[a-z-]+\s+--?[a-z])", corps, re.M) and ";" not in corps
    langage = "bash" if shell else "java"
    conversion.codes.append(langage)
    return f"```{langage}\n{corps}\n```"


def convertir(texte: str, conversion: Conversion) -> str:
    """Convertit un fragment : environnements connus, puis texte courant."""
    # Les commandes de taille sont retirées ici aussi : « {\small\begin{tabular}… } » entoure parfois
    # un environnement, et ses accolades traverseraient sinon la conversion.
    morceaux, reste = [], retirer_tailles(sans_commentaires(texte))
    while True:
        trouve = re.search(r"\\begin\{([A-Za-z*]+)\}", reste)
        if not trouve:
            morceaux.append(inline(reste, conversion))
            break
        morceaux.append(inline(reste[:trouve.start()], conversion))
        nom = trouve[1]
        position = trouve.end()
        titre, position = option(reste, position)
        if nom == "tabular":  # la spécification des colonnes ne sert qu'à LaTeX
            _, position = argument(reste, position)
        contenu, suite = environnement(reste, nom, position)

        if nom in ENCADRES:
            genre, classe, defaut = ENCADRES[nom]
            corps = convertir(contenu, conversion)
            entete = f'::: {{.callout-{genre} .{classe} title="{titre or defaut}"}}'
            morceaux.append(f"{entete}\n{corps}\n:::")
        elif nom in ("itemize", "enumerate"):
            morceaux.append(liste(contenu, nom == "enumerate", conversion))
        elif nom == "lstlisting":
            morceaux.append(code(contenu, conversion))
        elif nom == "tabular":
            morceaux.append(tableau(contenu, conversion))
        elif nom in ("center", "block", "columns", "column"):
            morceaux.append(convertir(contenu, conversion))
        else:
            morceaux.append(conversion.non_converti(f"\\begin{{{nom}}} … \\end{{{nom}}}"))
        reste = reste[suite:]
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(m for m in morceaux if m.strip())).strip()


def slides(corps: str, conversion: Conversion) -> list[str]:
    """Une frame donne une slide (titre de niveau 2), une section une slide de section."""
    sorties, position = [], 0
    motif = re.compile(r"\\(section|begin\{frame\})")
    while True:
        trouve = motif.search(corps, position)
        if not trouve:
            break
        if trouve[1] == "section":
            titre, position = argument(corps, trouve.end())
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
    arbre = ET.parse(source)
    compte = Counter()
    for element in arbre.iter():
        balise = element.tag.split("}")[-1]
        for attribut in ("fill", "stroke"):
            valeur = element.get(attribut)
            if valeur is None:
                continue
            if valeur.lower() in {c.lower() for c in ENCRES}:
                element.set(attribut, "currentColor")
                compte["encre"] += 1
            elif attribut == "fill" and balise in FORMES and valeur.lower() in FONDS_CLAIRS:
                element.set(attribut, "none")
                compte["fond"] += 1
        if element.get("font-family"):
            element.set("font-family", "inherit")
            compte["police"] += 1
    cible.parent.mkdir(parents=True, exist_ok=True)
    arbre.write(cible, encoding="unicode", xml_declaration=False)
    cible.write_text(cible.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")
    return compte


# --------------------------------------------------------------------------------------------------
# Écriture
# --------------------------------------------------------------------------------------------------

def entete_yaml(entete: dict[str, str], description: str, feuille: str) -> str:
    def guillemets(valeur: str) -> str:
        return '"' + valeur.replace('"', '\\"') + '"'

    lignes = [
        "---",
        f"title: {guillemets(entete.get('title', 'TODO(PO): titre'))}",
    ]
    if entete.get("subtitle"):
        lignes.append(f"subtitle: {guillemets(entete['subtitle'])}")
    lignes += [
        f"description: {guillemets(description)}",
        f"author: {guillemets(entete.get('author', ''))}",
        f"institute: {guillemets(entete.get('institute', ''))}",
        "format:",
        "  revealjs:",
        f"    theme: [default, {feuille}]",
        "    slide-number: true",
        # Le deck d'origine ne numérote pas les lignes de code ; les ancres que Quarto ajoute pour
        # cela portent par ailleurs un aria-label interdit sur un lien sans cible.
        "    code-line-numbers: false",
        # Les sections donnent des piles verticales : en navigation linéaire, les flèches parcourent
        # toutes les slides dans l'ordre du cours, comme le PDF Beamer.
        "    navigation-mode: linear",
        "    smaller: true",
        "    scrollable: true",
        "    history: false",
        "---",
        "",
    ]
    return "\n".join(lignes)


def ecrire_rapport(chemin: Path, source: Path, sortie: Path, conversion: Conversion,
                   figures: dict[str, dict[str, int]]) -> None:
    lignes = [
        f"# Rapport de conversion — {source.name}",
        "",
        f"Produit par `scripts/importer_chapitre.py` (US-15). Sortie : `{sortie}`.",
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
    analyseur.add_argument("--alt", type=Path,
                           help="textes alternatifs des figures sans légende (TOML)")
    analyseur.add_argument("--description", default="",
                           help="description de la page, pour le référencement")
    analyseur.add_argument("--feuille", default="../../../assets/css/slides.scss",
                           help="feuille de style des slides, relative au .qmd")
    args = analyseur.parse_args()

    source = args.source.read_text(encoding="utf-8")
    alternatifs = tomllib.loads(args.alt.read_text(encoding="utf-8")) if args.alt else {}
    # Les figures sont citées dans le .qmd par un chemin relatif à lui, comme un lien Markdown.
    prefixe = os.path.relpath(args.figures, args.sortie.parent)
    conversion = Conversion(alternatifs, prefixe)

    debut = source.index("\\begin{document}") + len("\\begin{document}")
    corps = source[debut:source.index("\\end{document}")]
    pages = slides(corps, conversion)

    entete = preambule(source)
    description = args.description or entete.get("subtitle", "")
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(entete_yaml(entete, description, args.feuille)
                           + "\n\n".join(pages) + "\n", encoding="utf-8")

    nettoyees = {}
    dossier_figures = args.source.parent / "figs"
    for ligne in conversion.figures:
        nom = ligne.split(" :")[0]
        origine = dossier_figures / f"{nom}.svg"
        if origine.is_file():
            nettoyees[nom] = nettoyer_svg(origine, args.figures / f"{nom}.svg")

    if args.rapport:
        ecrire_rapport(args.rapport, args.source, args.sortie, conversion, nettoyees)

    print(f"{len(pages)} slide(s) -> {args.sortie}")
    print(f"{len(nettoyees)} figure(s) nettoyée(s) -> {args.figures}")
    if conversion.non_convertis:
        print(f"{len(conversion.non_convertis)} élément(s) à traiter à la main "
              f"(voir {args.rapport or 'le rapport'}) :")
        for slide, quoi in conversion.non_convertis:
            print(f"  - {slide} : {quoi}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
