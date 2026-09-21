#!/usr/bin/env python3
"""Brouillons de textes alternatifs, à soumettre au PO (US-58).

    python3 scripts/brouillons_alt.py <fichier.tex> --prefixe NN-slug [--script fig=chemin.py]

Une figure sans légende dans le `.tex` n'a pas de texte alternatif, et le script n'en invente pas
(CLAUDE.md §7). Jusqu'ici il s'arrêtait en demandant une phrase au PO, figure par figure : 33 schémas
pour les seuls chapitres restants du cours de C, soit 33 allers-retours.

Ce module rédige un **brouillon** à partir de **ce que la source contient**, et rien d'autre :

- pour un `tikzpicture`, **les relations entre ses nœuds** — qui mène à qui, dans quel ordre, ce que
  contient un tableau — telles que ses `\\node` et ses `\\draw` les écrivent ;
- pour une figure matplotlib, le titre, les axes, les séries, et **le sens de la courbe** quand il se
  lit dans les données tracées sans exécuter le script.

Le brouillon n'est **jamais écrit dans le site** : il est présenté au PO, qui accepte, corrige ou
réécrit. Tant qu'il n'a pas validé, la page garde son `TODO(PO)`.

Ce que le brouillon ne fait pas, et c'est délibéré : il ne dit pas ce que la figure *signifie*.
« Windows, macOS et Linux mènent à Docker, qui mène à gcc, gdb, valgrind et make » se vérifie ligne à
ligne dans le `.tex` ; « le schéma montre comment unifier les environnements » ne se vérifie pas. Le
verbe reste « mène à » même quand la flèche veut visiblement dire autre chose : la source dit une
direction, pas une intention. Quand elle porte une étiquette, celle-ci est citée telle quelle.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

LONGUEUR_MAXIMALE = 300   # au-delà, un texte alternatif n'est plus lu : on coupe la liste des libellés
LIBELLES_CITES = 8        # nombre de libellés cités avant « … »
# Un brouillon tronqué se lit mal à voix haute : « et 3 autre(s) » n'apprend rien, et un texte qui
# s'arrête sur « … » laisse le lecteur au milieu d'une phrase. Sur demande du PO, le brouillon cite
# alors **tout** ce que la source contient, quitte à faire deux phrases.
COMPLET = False

# Commandes de mise en forme sans contenu propre : elles disparaissent d'un libellé.
MISE_EN_FORME = re.compile(
    r"\\(?:tiny|scriptsize|footnotesize|small|normalsize|large|Large|LARGE|huge|Huge"
    r"|bfseries|itshape|ttfamily|rmfamily|sffamily|centering|strut|,|;|!|quad|qquad)\b\s*")
# Commandes à un argument dont seul l'argument compte : \textbf{x} -> x.
UN_ARGUMENT = re.compile(r"\\(?:text[a-z]{2}|emph|mathrm|mathbf|texttt|underline|textcolor)\s*\{")
# Symboles mathématiques : les perdre changerait le sens de « 13 \div 2 = 6 » en « 13 2 = 6 ».
SYMBOLES = {r"\div": "÷", r"\times": "×", r"\cdot": "·", r"\pm": "±", r"\mp": "∓",
            r"\rightarrow": "→", r"\Rightarrow": "⇒", r"\leftarrow": "←", r"\to": "→",
            r"\leq": "≤", r"\geq": "≥", r"\neq": "≠", r"\approx": "≈", r"\equiv": "≡",
            r"\ldots": "…", r"\dots": "…", r"\cdots": "…", r"\infty": "∞",
            r"\alpha": "α", r"\beta": "β", r"\lambda": "λ", r"\mu": "μ", r"\sigma": "σ",
            r"\checkmark": "✓", r"\bullet": "•", r"\%": "%", r"\&": "&", r"\_": "_",
            r"\#": "#", r"\$": "$"}


def texte_nu(brut: str) -> str:
    """Libellé LaTeX ramené à ce qu'un lecteur y lirait."""
    texte = brut.replace(r"\\", " ").replace("~", " ")
    for commande, symbole in SYMBOLES.items():
        # La garde ne vaut que pour les commandes alphabétiques (`\to` ne doit pas manger `\top`).
        # Une ponctuation échappée, elle, colle à la lettre suivante : « K\&R ».
        garde = r"(?![A-Za-z])" if commande[-1].isalpha() else ""
        texte = re.sub(re.escape(commande) + garde, symbole, texte)
    texte = MISE_EN_FORME.sub("", texte)
    # \textbf{x} -> x, en boucle : les commandes s'imbriquent (\textbf{\texttt{x}}).
    for _ in range(4):
        remplace = UN_ARGUMENT.sub("{", texte)
        if remplace == texte:
            break
        texte = remplace
    texte = re.sub(r"\\[A-Za-z@]+\s*", "", texte)
    texte = texte.replace("$", "").replace("{", "").replace("}", "")
    # Tirets de LaTeX : \u00ab --- \u00bb est un tiret cadratin, \u00ab -- \u00bb un demi-cadratin. Les laisser tels quels
    # ferait lire \u00ab Docker --- Environnement unifi\u00e9 \u00bb \u00e0 un lecteur d'\u00e9cran.
    texte = texte.replace("---", "\u2014").replace("--", "\u2013").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", texte).strip(" .,;:")


def accolade_du_libelle(dessin: str, depart: int) -> int:
    """Position de l'accolade qui porte le libellé, après les options et les coordonnées.

    Un nœud s'écrit `\\node[options] (nom) at ({calcul},y) {libellé}` : les options tiennent des
    accolades (`nodes={…}`), et une coordonnée calculée aussi (`({(3-\\i)*1.2},0.8)`). Prendre la
    première accolade venue donnait « rectangle,draw,minimum width=0.8cm » pour libellé.
    """
    position = depart
    while position < len(dessin):
        caractere = dessin[position]
        if caractere == "{":
            return position
        if caractere in "([":
            position = fin_de_groupe(dessin, position)
            continue
        if caractere == ";":        # nœud sans libellé : la commande se termine avant l'accolade
            return -1
        position += 1
    return -1


def fin_de_groupe(texte: str, ouvrant: int) -> int:
    """Position juste après le groupe apparié ouvert en `ouvrant` — parenthèses ou crochets."""
    paires = {"(": ")", "[": "]", "{": "}"}
    fermant = paires[texte[ouvrant]]
    profondeur, position = 0, ouvrant
    while position < len(texte):
        if texte[position] == texte[ouvrant]:
            profondeur += 1
        elif texte[position] == fermant:
            profondeur -= 1
            if profondeur == 0:
                return position + 1
        position += 1
    return len(texte)


def sans_foreach(dessin: str) -> str:
    """Schéma privé de ses boucles : leurs nœuds sont comptés, pas cités.

    Le libellé d'un nœud de boucle est une **variable** (`{$2^{\\i}$}`) : nettoyé, il ne reste que
    « 2^ », qui n'apprend rien à personne. `repetitions_tikz` en donne le nombre, qui lui est écrit.
    """
    while True:
        trouve = re.search(r"\\foreach\b", dessin)
        if not trouve:
            return dessin
        liste = dessin.find("{", trouve.end())
        if liste == -1:
            return dessin[:trouve.start()]
        apres = fin_de_groupe(dessin, liste)
        corps = re.match(r"\s*\{", dessin[apres:])
        fin = fin_de_groupe(dessin, apres + corps.end() - 1) if corps \
            else (dessin.find(";", apres) + 1 or len(dessin))
        dessin = dessin[:trouve.start()] + dessin[fin:]


def repetitions_tikz(dessin: str) -> int:
    """Nombre de cases posées par les boucles `\\foreach` : les bits d'un octet, par exemple.

    Ces cases n'ont pas de libellé lisible dans la source — leur contenu est une variable de boucle —,
    mais leur nombre, lui, y est écrit noir sur blanc.
    """
    total = 0
    for trouve in re.finditer(r"\\foreach\b[^{]*\{", dessin):
        liste = contenu_accolade(dessin, trouve.end() - 1)
        total += len([item for item in liste.split(",") if item.strip()])
    return total


def contenu_accolade(texte: str, ouvrante: int) -> str:
    """Contenu de l'accolade ouverte en `ouvrante`, accolades imbriquées comprises."""
    profondeur, position = 0, ouvrante
    while position < len(texte):
        if texte[position] == "{":
            profondeur += 1
        elif texte[position] == "}":
            profondeur -= 1
            if profondeur == 0:
                return texte[ouvrante + 1:position]
        position += 1
    return texte[ouvrante + 1:]


def liste_citee(libelles: list[str]) -> str:
    cites = libelles if COMPLET else libelles[:LIBELLES_CITES]
    liste = ", ".join(f"« {libelle} »" for libelle in cites)
    if len(libelles) > len(cites):
        liste += f", et {len(libelles) - len(cites)} autre(s)"
    return liste


def serie(cases: list[str]) -> str:
    """Une suite ordonnée : on cite le début, puis où elle s'arrête.

    Les seize colonnes d'une table hexadécimale ne valent pas « 0, 1, 2 et 13 autres » : elles vont
    de « 0 » à « F », et c'est cela qu'un lecteur a besoin d'entendre.
    """
    if COMPLET or len(cases) <= LIBELLES_CITES:
        return enumerer(cases)
    return ", ".join(cases[:LIBELLES_CITES - 2]) + f", jusqu'à {cases[-1]}"


def enumerer(elements: list[str]) -> str:
    """« A, B et C » : une énumération française, et non une liste à puces dans une phrase."""
    cites = elements if COMPLET else elements[:LIBELLES_CITES]
    reste = len(elements) - len(cites)
    if reste > 0:
        return ", ".join(cites) + f" et {reste} autre(s)"
    if len(cites) == 1:
        return cites[0]
    return ", ".join(cites[:-1]) + " et " + cites[-1]


def tronquer(texte: str) -> str:
    """Un texte alternatif trop long n'est plus lu : on coupe à la virgule qui précède la limite.

    En mode complet, rien n'est coupé : le texte est seulement **découpé en phrases**, aux
    points-virgules, pour rester dicible d'un trait par un lecteur d'écran.
    """
    if COMPLET:
        return phraser(texte)
    if len(texte) <= LONGUEUR_MAXIMALE:
        return texte
    coupe = texte.rfind(", ", 0, LONGUEUR_MAXIMALE)
    return (texte[:coupe] if coupe > 0 else texte[:LONGUEUR_MAXIMALE]) + "…"


# Articulations d'un brouillon : c'est là qu'une phrase peut se terminer sans rien couper en deux.
ARTICULATIONS = {" ; ": ". ", ", libellés : ": ". Libellés : ", ", séries : ": ". Séries : "}


def phraser(texte: str) -> str:
    """Coupe un long brouillon en phrases, à ses articulations.

    Une phrase de six cents caractères est indicible d'un trait. On coupe là où le brouillon
    s'articule — un point-virgule, l'entrée en matière des libellés ou des séries — et jamais au
    milieu d'une énumération. Quand il n'y a aucune articulation, la coupure se fait entre deux
    libellés et la seconde phrase reprend par « Elle porte aussi ».
    """
    if len(texte) <= LONGUEUR_MAXIMALE:
        return texte
    nu = texte.rstrip(".")
    morceaux = re.split("(" + "|".join(re.escape(a) for a in ARTICULATIONS) + ")", nu)
    if len(morceaux) > 1:
        phrases, phrase = [], morceaux[0]
        for separateur, suite in zip(morceaux[1::2], morceaux[2::2]):
            if len(phrase) + len(separateur) + len(suite) > LONGUEUR_MAXIMALE:
                phrases.append(phrase)
                phrase = ARTICULATIONS[separateur].lstrip(". ") + suite
            else:
                phrase += separateur + suite
        phrases.append(phrase)
    else:
        elements = nu.split(", «")
        milieu = len(elements) // 2
        phrases = [", «".join(elements[:milieu]),
                   "Elle porte aussi «" + ", «".join(elements[milieu:])]
    return " ".join(p.strip()[0].upper() + p.strip()[1:] + "." for p in phrases if p.strip())


# --- Schémas TikZ : les relations que la source décrit ---------------------------------------------
#
# Un schéma n'est pas un sac de libellés : ses nœuds sont **reliés**, et ces liens sont écrits dans la
# source, arc par arc. Compter « 8 libellés et 7 flèches » n'apprend rien à qui ne voit pas l'image ;
# « Windows, macOS et Linux mènent à Docker, qui mène à gcc, gdb, valgrind et make » se vérifie ligne
# à ligne dans le `.tex`, et dit ce que le schéma montre.
#
# Le verbe reste **« mène à »**, même quand la flèche signifie visiblement autre chose : la source dit
# une direction, pas une intention. Quand elle porte une étiquette (`node[midway] {inspire}`), celle-ci
# est citée telle quelle — c'est le PO qui l'a écrite.

# `below=0.05cm of cm`, `right=of bcpl`, `above left=0.2cm of x` : un nœud posé par rapport à un autre.
RELATIF = re.compile(r"\b(?:above|below|left|right)(?:\s+(?:above|below|left|right))?\s*"
                     r"=\s*(?:[^,\]]*?\s+)?of\s+([A-Za-z0-9_.-]+)")
# `arrow/.style={->,>=stealth,thick}` : le style porte la pointe, et `\draw[arrow]` ne la montre pas.
STYLE = re.compile(r"([A-Za-z0-9_-]+)\s*/\.style\s*=\s*\{")
ECART_MEME_RANGEE = 0.15  # unités TikZ : deux nœuds d'une même rangée ont la même ordonnée
                          # à peu de chose près ; au-delà, ce sont deux rangées
TOLERANCE_BORD = 0.8      # unités TikZ : distance admise entre un bout de flèche et un nœud
# Amorces écrites par ce module, par opposition aux libellés repris de la figure.
AMORCES = ("une flèche", "des flèches", "s'y ajoutent", "les flèches portent")


class Noeud:
    """Un nœud du schéma : son libellé, sa position, et les textes qui l'annotent."""

    __slots__ = ("nom", "libelle", "x", "y", "annotations", "tiret")

    def __init__(self, nom: str, libelle: str, x: float | None, y: float | None) -> None:
        self.nom, self.libelle, self.x, self.y = nom, libelle, x, y
        self.annotations: list[str] = []
        self.tiret = False      # annoter au tiret plutôt qu'entre parenthèses (voir brouillon_tikz)

    @property
    def texte(self) -> str:
        """Libellé et annotations en un seul morceau : « BCPL (1966) », « BCPL — 1966 (Richards) »."""
        if not self.annotations:
            return self.libelle
        jointes = ", ".join(self.annotations)
        return f"{self.libelle} — {jointes}" if self.tiret else f"{self.libelle} ({jointes})"


class Arete:
    """Un lien entre deux nœuds, et ce que la flèche porte écrit."""

    __slots__ = ("depart", "arrivee", "etiquette", "flechee")

    def __init__(self, depart: str, arrivee: str, etiquette: str, flechee: bool) -> None:
        self.depart, self.arrivee = depart, arrivee
        self.etiquette, self.flechee = etiquette, flechee


def styles_fleches(dessin: str) -> set[str]:
    """Noms de styles définis avec une pointe de flèche, pour que `\\draw[arrow]` compte comme telle."""
    trouves = set()
    for trouve in STYLE.finditer(dessin):
        corps = contenu_accolade(dessin, trouve.end() - 1)
        if "->" in corps or "<-" in corps:
            trouves.add(trouve[1])
    return trouves


def coordonnees(texte: str) -> tuple[float | None, float | None]:
    """« 2.5,-1 » -> (2.5, -1.0). Une coordonnée calculée n'en est pas une : on renonce."""
    morceaux = texte.split(",")
    if len(morceaux) != 2:
        return None, None
    try:
        return float(morceaux[0].strip()), float(morceaux[1].strip())
    except ValueError:
        return None, None


def groupe_suivant(dessin: str, position: int, ouvrant: str) -> tuple[str, int]:
    """Contenu du groupe `ouvrant` s'il commence ici (espaces passés), et la position d'après."""
    while position < len(dessin) and dessin[position] in " \n\t":
        position += 1
    if position < len(dessin) and dessin[position] == ouvrant:
        fin = fin_de_groupe(dessin, position)
        return dessin[position + 1:fin - 1], fin
    return "", position


def noeuds_tikz(dessin: str) -> tuple[dict[str, Noeud], list[str]]:
    """Tous les nœuds du schéma, nommés ou non, dans leur ordre d'apparition.

    Un nœud sans nom posé « of » un autre n'est pas un nœud : c'est son annotation — une date sous une
    pastille, une unité sous une case. Il est rattaché à celui qu'il annote.

    Les autres nœuds sans nom sont gardés quand même, avec leur position : une flèche tracée en
    coordonnées y aboutit souvent, et c'est elle qui dit la relation.
    """
    noeuds: dict[str, Noeud] = {}
    ordre: list[str] = []
    attentes: list[tuple[str, str]] = []     # (ancre, texte) rattachés après lecture de tous les nœuds
    for numero, trouve in enumerate(re.finditer(r"\\node\b", dessin)):
        options, position = groupe_suivant(dessin, trouve.end(), "[")
        nom, position = groupe_suivant(dessin, position, "(")
        x = y = None
        apres_at = re.match(r"\s*at\s*", dessin[position:])
        if apres_at:
            brut, position = groupe_suivant(dessin, position + apres_at.end(), "(")
            x, y = coordonnees(brut)
        accolade = accolade_du_libelle(dessin, position)
        if accolade == -1:
            continue
        libelle = texte_nu(contenu_accolade(dessin, accolade))
        if not libelle:
            continue
        ancre = RELATIF.search(options)
        nom = nom.strip()
        if not nom and ancre:
            attentes.append((ancre[1].split(".")[0], libelle))
            continue
        cle = nom or f"\x00{numero}"        # un nœud anonyme garde une clé, jamais montrée
        noeuds[cle] = Noeud(cle, libelle, x, y)
        ordre.append(cle)
    for ancre, libelle in attentes:
        if ancre in noeuds:
            noeuds[ancre].annotations.append(libelle)
        else:
            cle = f"\x00a{len(noeuds)}"
            noeuds[cle] = Noeud(cle, libelle, None, None)
            ordre.append(cle)
    return noeuds, ordre


def noeud_proche(x: float | None, y: float | None, noeuds: dict[str, Noeud]) -> str:
    """Nœud dont la boîte touche ce point, s'il n'y en a qu'un : une flèche part de son bord.

    Une flèche s'attache au **bord** d'une boîte, pas à son centre : `\\draw[->] (0,0.3) -- (0,-0.1)`
    part de la case posée en `(0,0.8)`, une demi-hauteur plus haut. Au-delà d'une case d'écart, on
    renonce plutôt que de deviner.
    """
    if x is None or y is None:
        return ""
    candidats = []
    for cle, noeud in noeuds.items():
        if noeud.x is None or noeud.y is None:
            continue
        distance = abs(noeud.x - x) + abs(noeud.y - y)
        if distance <= TOLERANCE_BORD:
            candidats.append((distance, cle))
    candidats.sort()
    if len(candidats) == 1 or (len(candidats) > 1 and candidats[0][0] < candidats[1][0]):
        return candidats[0][1]
    return ""


def aretes_tikz(dessin: str, noeuds: dict[str, Noeud]) -> tuple[list[Arete], list[tuple[str, str]]]:
    """Les liens tracés, et les flèches qui ne mènent qu'à un texte.

    Un chemin dont les deux bouts sont des nœuds — nommés, ou retrouvés par leur position — est une
    relation. Un chemin qui se termine par `node {…}` sans aboutir à un nœud porte quand même une
    information : la flèche mène à ce texte-là. Le reste des `\\draw` dessine des cadres, et est ignoré.
    """
    flechees = styles_fleches(dessin)
    aretes: list[Arete] = []
    libres: list[tuple[str, str]] = []
    for trouve in re.finditer(r"\\(?:draw|path)\b", dessin):
        options, position = groupe_suivant(dessin, trouve.end(), "[")
        fin = dessin.find(";", position)
        corps = dessin[position:fin if fin != -1 else len(dessin)]
        flechee = ("->" in options or "<-" in options
                   or any(style.strip() in flechees for style in options.split(",")))
        etiquette = ""
        for label in re.finditer(r"\bnode\b", corps):
            accolade = accolade_du_libelle(corps, label.end())
            if accolade != -1:
                etiquette = etiquette or texte_nu(contenu_accolade(corps, accolade))
        etapes = []
        position_corps = 0
        while True:
            debut = corps.find("(", position_corps)
            if debut == -1:
                break
            apres = fin_de_groupe(corps, debut)
            avant = corps[position_corps:debut]
            # Une parenthèse qui suit « node[…] » appartient à l'étiquette, pas au chemin. Et
            # « ++(-0.5,0) » est un **déplacement**, pas une position : la lire comme une coordonnée
            # absolue rattachait la flèche au nœud posé à l'origine.
            if not re.search(r"\bnode\b[^()]*$", avant) and not avant.rstrip().endswith("+"):
                etapes.append(corps[debut + 1:apres - 1].strip())
            position_corps = apres
        connus = []
        for etape in etapes:
            nom = etape.split(".")[0].strip()
            if nom in noeuds:
                connus.append(nom)
                continue
            proche = noeud_proche(*coordonnees(etape), noeuds)
            if proche and proche not in connus[-1:]:
                connus.append(proche)
        if len(connus) < 2:
            if flechee and etiquette:
                libres.append((connus[0] if connus else "", etiquette))
            continue
        renverse = "<-" in options and "<->" not in options
        for depart, arrivee in zip(connus, connus[1:]):
            if depart == arrivee:   # un chemin qui repasse par son nœud n'est pas une relation
                continue
            if renverse:
                depart, arrivee = arrivee, depart
            aretes.append(Arete(depart, arrivee, etiquette, flechee))
    return aretes, libres


def phrases_des_liens(noeuds: dict[str, Noeud], ordre: list[str],
                      aretes: list[Arete]) -> tuple[list[str], set[str]]:
    """Les relations, groupées comme on les dirait à voix haute, et les nœuds qu'elles citent."""
    sortants: dict[str, list[Arete]] = {nom: [] for nom in noeuds}
    entrants: dict[str, list[Arete]] = {nom: [] for nom in noeuds}
    for arete in aretes:
        sortants[arete.depart].append(arete)
        entrants[arete.arrivee].append(arete)

    faites: set[int] = set()
    phrases: list[str] = []
    cites: set[str] = set()

    def libelle(nom: str) -> str:
        cites.add(nom)
        return noeuds[nom].texte

    def verbe(liens: list[Arete], pluriel: bool) -> str:
        if not any(lien.flechee for lien in liens):
            return "sont reliés à" if pluriel else "est relié à"
        return "mènent à" if pluriel else "mène à"

    # 1. Les carrefours : plusieurs nœuds mènent au même, qui mène parfois à plusieurs autres.
    for nom in ordre:
        arrivant = [a for a in entrants[nom] if id(a) not in faites]
        if len(arrivant) < 2:
            continue
        faites.update(id(a) for a in arrivant)
        phrase = f"{enumerer([libelle(a.depart) for a in arrivant])} {verbe(arrivant, True)} {libelle(nom)}"
        partant = [a for a in sortants[nom] if id(a) not in faites]
        if partant:
            faites.update(id(a) for a in partant)
            phrase += f", qui {verbe(partant, False)} {enumerer([libelle(a.arrivee) for a in partant])}"
        phrases.append(phrase)

    # 2. Les éventails : un nœud mène à plusieurs.
    for nom in ordre:
        partant = [a for a in sortants[nom] if id(a) not in faites]
        if len(partant) < 2:
            continue
        faites.update(id(a) for a in partant)
        phrases.append(f"{libelle(nom)} {verbe(partant, False)} "
                       f"{enumerer([libelle(a.arrivee) for a in partant])}")

    # 3. Les chaînes : une suite où chaque nœud mène au suivant.
    for nom in ordre:
        if any(id(a) not in faites for a in entrants[nom]):
            continue
        etapes, courant = [], nom
        while True:
            suite = [a for a in sortants[courant] if id(a) not in faites]
            if len(suite) != 1:
                break
            faites.add(id(suite[0]))
            etapes.append(suite[0])
            courant = suite[0].arrivee
        if not etapes:
            continue
        suivants = [libelle(a.arrivee) for a in etapes]
        phrase = f"{libelle(nom)} {verbe(etapes, False)} {suivants[0]}"
        if len(suivants) > 1:
            phrase += f", puis {enumerer(suivants[1:])}"
        phrases.append(phrase)

    # 4. Ce qui reste, lien par lien.
    for arete in aretes:
        if id(arete) in faites:
            continue
        faites.add(id(arete))
        phrases.append(f"{libelle(arete.depart)} {verbe([arete], False)} {libelle(arete.arrivee)}")

    etiquettes = uniques(arete.etiquette for arete in aretes)
    if etiquettes:
        phrases.append("les flèches portent "
                       + enumerer([f"« {etiquette} »" for etiquette in etiquettes]))
    return phrases, cites


def rangee(noeuds: list[Noeud]) -> str:
    """L'ordre dans lequel se lisent des nœuds : leurs coordonnées le disent. Vide si elles manquent.

    Beaucoup de schémas n'ont aucune flèche — une suite de cases mémoire, un titre au-dessus d'une
    rangée de boîtes. Leur source dit quand même quelque chose : **la disposition**. On regroupe les
    nœuds en rangées, de haut en bas, et chaque rangée se lit de gauche à droite.
    """
    places = [noeud for noeud in noeuds if noeud.x is not None and noeud.y is not None]
    if len(places) != len(noeuds) or len(places) < 2:
        return ""
    lignes: list[list[Noeud]] = []
    for noeud in sorted(places, key=lambda n: -n.y):
        if lignes and abs(lignes[-1][0].y - noeud.y) < ECART_MEME_RANGEE:
            lignes[-1].append(noeud)
        else:
            lignes.append([noeud])
    rendues = [enumerer([noeud.texte for noeud in sorted(ligne, key=lambda n: n.x)])
               for ligne in lignes]
    if len(rendues) == 1:
        return "de gauche à droite : " + rendues[0]
    if all(len(ligne) == 1 for ligne in lignes):
        # Une colonne : « A ; puis B ; puis C » se lit moins bien que « A, B et C ».
        return "de haut en bas : " + enumerer([ligne[0].texte for ligne in lignes])
    return "de haut en bas : " + " ; puis ".join(rendues)


def tableau_tikz(dessin: str) -> str:
    """Ce qu'une `matrix of nodes` organise : ses colonnes, ses lignes, et ce qu'elles portent."""
    trouve = re.search(r"\\matrix\b", dessin)
    if not trouve:
        return ""
    accolade = accolade_du_libelle(dessin, trouve.end())
    if accolade == -1:
        return ""
    lignes = [ligne for ligne in contenu_accolade(dessin, accolade).split(r"\\") if ligne.strip()]
    if not lignes:
        return ""
    entete = [texte_nu(case) for case in lignes[0].split("&")]
    premiere_colonne = [texte_nu(ligne.split("&")[0]) for ligne in lignes]
    morceaux = [f"Tableau de {len(lignes)} lignes et "
                f"{max(len(ligne.split('&')) for ligne in lignes)} colonnes"]
    if any(entete):
        morceaux.append("en-tête " + serie([case for case in entete if case]))
    if len(premiere_colonne) > 1 and any(premiere_colonne[1:]):
        morceaux.append("première colonne " + serie([case for case in premiere_colonne if case]))
    return ", ".join(morceaux)


def brouillon_tikz(dessin: str) -> str:
    """Brouillon d'un `tikzpicture` : les relations que sa source décrit, et rien d'interprété."""
    propre = sans_foreach(re.sub(r"\\matrix\b", "\x00", dessin))
    noeuds, ordre = noeuds_tikz(propre)
    aretes, fleches_seules = aretes_tikz(propre, noeuds)
    morceaux: list[str] = []

    # Les parenthèses s'imbriqueraient si une seule annotation en portait déjà : dans ce cas, tout
    # le schéma passe au tiret, pour que la phrase se lise d'une seule façon.
    if any("(" in annotation for noeud in noeuds.values() for annotation in noeud.annotations):
        for noeud in noeuds.values():
            noeud.tiret = True

    tableau = tableau_tikz(dessin)
    if tableau:
        morceaux.append(tableau)

    cites: set[str] = set()
    if aretes:
        phrases, cites = phrases_des_liens(noeuds, ordre, aretes)
        morceaux += phrases
    # Les flèches qui n'aboutissent qu'à un texte : le résultat d'un calcul, le plus souvent.
    par_depart: dict[str, list[str]] = {}
    for depart, etiquette in fleches_seules:
        par_depart.setdefault(depart, []).append(etiquette)
    for depart, etiquettes in par_depart.items():
        arrivees = enumerer(uniques(etiquettes))
        if depart:
            cites.add(depart)
            morceaux.append(f"{noeuds[depart].texte} mène à {arrivees}")
        else:
            morceaux.append(("une flèche mène à " if len(etiquettes) == 1
                             else "des flèches mènent à ") + arrivees)

    restants = [noeuds[nom] for nom in ordre if nom not in cites]
    if restants:
        dispose = rangee(restants) or enumerer([noeud.texte for noeud in restants])
        if morceaux:
            morceaux.append("s'y ajoutent, " + dispose if ":" in dispose
                            else "s'y ajoutent " + dispose)
        else:
            amorce = dispose if ":" in dispose else "le schéma porte " + dispose
            morceaux.append(amorce[0].upper() + amorce[1:])

    cases = repetitions_tikz(dessin)
    if cases:
        morceaux.append(f"une suite de {cases} cases s'y répète")
    if not morceaux:
        return ""
    # Pas de majuscule forcée sur un libellé de la figure : « char et short mènent à int » deviendrait
    # « Char et short… » dans un cours de C. Seules les amorces que ce module écrit lui-même la
    # prennent, et seulement quand elles ouvrent la phrase.
    if morceaux[0].startswith(AMORCES):
        morceaux[0] = morceaux[0][0].upper() + morceaux[0][1:]
    return tronquer(" ; ".join(morceaux) + ".")


# --- Figures matplotlib ------------------------------------------------------------------------

def chaine(nom: str) -> re.Pattern:
    """Appel `nom(…)` dont le premier argument est une chaîne : `set_title("…")`, `label="…"`."""
    return re.compile(rf"{nom}\s*\(?\s*=?\s*(?P<prefixe>[fFrRbB]{{0,2}})"
                      r"(?P<guillemet>[\"'])(?P<texte>(?:\\.|(?!(?P=guillemet)).)*)(?P=guillemet)")


TITRE = chaine(r"(?:set_title|suptitle|set_suptitle)")
AXE_X = chaine("set_xlabel")
AXE_Y = chaine("set_ylabel")
SERIE = chaine(r"label\s*=")
# `ax.text(x, y, "texte", ha='center')` : le texte est un argument **positionnel**, et « center »
# n'en est pas un. Le repérer par sa place, et non par la première chaîne venue.
POSE = re.compile(r"\.(?:text|annotate)\s*\(")
LITTERALE = re.compile(r"^(?P<prefixe>[fFrRbB]{0,2})(?P<guillemet>[\"'])"
                       r"(?P<texte>(?:\\.|(?!(?P=guillemet)).)*)(?P=guillemet)\s*$")


def litteral(brut: str, prefixe: str = "") -> str:
    """Chaîne Python telle qu'elle s'affichera, `$maths$` comprises.

    Une f-string porte des trous que seule l'exécution remplit (`f"{total:.2f} s"`). Les recopier
    donnerait un texte alternatif qui parle de « {total:.2f} » : ils deviennent « … ».
    """
    texte = brut.replace("\\'", "'").replace('\\"', '"').replace("\\n", " ")
    if "f" in prefixe.lower():
        texte = re.sub(r"\{[^{}]*\}", "…", texte.replace("{{", "\x02").replace("}}", "\x03"))
        texte = texte.replace("\x02", "{").replace("\x03", "}")
    return texte_nu(texte.replace("$", ""))


def texte_pose(corps: str) -> list[str]:
    """Textes posés par `.text(...)` / `.annotate(...)` : le premier argument qui est une chaîne."""
    trouves = []
    for appel in POSE.finditer(corps):
        ouvrante = appel.end() - 1
        arguments = decouper(corps[ouvrante + 1:fin_de_groupe(corps, ouvrante) - 1])
        for argument in arguments:
            forme = LITTERALE.match(argument.strip())
            if forme:
                trouves.append(litteral(forme["texte"], forme["prefixe"]))
                break
    return trouves


def decouper(arguments: str) -> list[str]:
    """Découpe une liste d'arguments aux virgules de premier niveau."""
    morceaux, profondeur, debut, guillemet = [], 0, 0, ""
    for position, caractere in enumerate(arguments):
        if guillemet:
            guillemet = "" if caractere == guillemet and arguments[position - 1] != "\\" else guillemet
        elif caractere in "\"'":
            guillemet = caractere
        elif caractere in "([{":
            profondeur += 1
        elif caractere in ")]}":
            profondeur -= 1
        elif caractere == "," and profondeur == 0:
            morceaux.append(arguments[debut:position])
            debut = position + 1
    morceaux.append(arguments[debut:])
    return morceaux


# --- Le sens d'une courbe, quand il se lit dans les données tracées ------------------------------
#
# Une figure calculée ne dit pas ce qu'elle montre : c'est le script qui le dit. Quand la série tracée
# est **lisible dans la source** — une liste de nombres, ou une expression dont on peut établir le
# sens sans l'exécuter —, le brouillon ajoute « croissante » ou « décroissante », et les bornes si
# elles sont connues. Quand elle ne l'est pas, il se tait : mieux vaut un brouillon plus court qu'une
# phrase que personne n'a vérifiée. **Rien n'est exécuté** : le script du PO n'est que lu.

TRACES = re.compile(r"\.(?:plot|step|scatter|bar|barh|semilogy|semilogx|loglog|fill_between)\s*\(")
AFFECTATION = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s*$", re.M)
LINSPACE = re.compile(r"(?:np|numpy)\.(?:linspace|arange)\s*\(\s*([^,)]+)\s*,\s*([^,)]+)")
CROISSANTES = ("np.exp", "numpy.exp", "np.log", "numpy.log", "np.log2", "np.log10",
               "np.sqrt", "numpy.sqrt", "np.cumsum", "numpy.cumsum", "np.sinh", "np.arctan")
NOMBRE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")
# Un trait de dessin est un `plot` de deux points : `ax.plot([x, x], [haut, bas])`. Ce n'est pas une
# courbe, et annoncer qu'il « croît de 5,75 à 5,85 » n'apprendrait rien à personne. En deçà de ce
# nombre de points écrits en clair, on se tait.
POINTS_MINIMUM = 5


def nombres_litteraux(expression: str) -> list[float] | None:
    """Les nombres d'une liste écrite en clair — `[1, 2, 4, 8]`. Sinon, rien."""
    depouille = expression.strip()
    if not (depouille.startswith("[") and depouille.endswith("]")):
        return None
    valeurs = []
    for morceau in decouper(depouille[1:-1]):
        morceau = morceau.strip()
        if not NOMBRE.match(morceau):
            return None
        valeurs.append(float(morceau))
    return valeurs or None


def sens_des_nombres(valeurs: list[float]) -> str:
    """« croissante », « décroissante », ou rien quand la suite fait les deux."""
    if len(valeurs) < 2:
        return ""
    ecarts = [apres - avant for avant, apres in zip(valeurs, valeurs[1:])]
    if all(ecart >= 0 for ecart in ecarts) and any(ecarts):
        return "croissante"
    if all(ecart <= 0 for ecart in ecarts) and any(ecarts):
        return "décroissante"
    return ""


def affectations(corps: str) -> dict[str, str]:
    """Les variables posées dans le corps de la figure, pour remonter d'un nom à son expression."""
    return {trouve[1]: trouve[2] for trouve in AFFECTATION.finditer(corps)}


def sens_de_la_serie(expression: str, table: dict[str, str], profondeur: int = 0) -> str:
    """Sens de la série tracée, établi sans exécuter le script. Vide si la source ne le dit pas."""
    expression = expression.strip()
    if profondeur > 3 or not expression:
        return ""
    valeurs = nombres_litteraux(expression)
    if valeurs and len(valeurs) >= POINTS_MINIMUM:
        sens = sens_des_nombres(valeurs)
        return f"{sens} de {nombre(valeurs[0])} à {nombre(valeurs[-1])}" if sens else ""
    if expression in table:
        return sens_de_la_serie(table[expression], table, profondeur + 1)
    if any(expression.startswith(fonction + "(") for fonction in CROISSANTES):
        return "croissante"
    bornes = LINSPACE.match(expression)
    if bornes:
        try:
            debut, fin = float(bornes[1]), float(bornes[2])
        except ValueError:
            return "croissante"
        return f"croissante de {nombre(debut)} à {nombre(fin)}" if fin > debut else "décroissante"
    # `hours * ticks_per_hour` : une série croissante multipliée par des facteurs constants le reste,
    # à condition qu'aucun ne soit négatif — et on ne le suppose pas, on le vérifie.
    facteurs = [morceau.strip() for morceau in expression.split("*")]
    if len(facteurs) > 1:
        variables, positifs = [], True
        for facteur in facteurs:
            valeur = valeur_numerique(facteur, table)
            if valeur is None:
                variables.append(facteur)
            elif valeur <= 0:
                positifs = False
        if len(variables) == 1 and positifs:
            return sens_de_la_serie(variables[0], table, profondeur + 1).split(" de ")[0]
    return ""


def valeur_numerique(expression: str, table: dict[str, str], profondeur: int = 0) -> float | None:
    """Valeur d'une expression **entièrement littérale**, noms résolus dans le corps de la figure.

    `ticks_per_hour = 3600 * 10` est un nombre, même écrit comme un calcul. On l'établit avec `ast`,
    sans jamais exécuter le script : un nœud qui n'est ni un nombre, ni un nom connu, ni une des
    quatre opérations fait renoncer.
    """
    if profondeur > 4:
        return None
    try:
        arbre = ast.parse(expression.strip(), mode="eval").body
    except SyntaxError:
        return None

    def evaluer(noeud, niveau: int) -> float | None:
        if niveau > 8:
            return None
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, (int, float)):
            return float(noeud.value)
        if isinstance(noeud, ast.Name):
            return (valeur_numerique(table[noeud.id], table, profondeur + 1)
                    if noeud.id in table else None)
        if isinstance(noeud, ast.UnaryOp) and isinstance(noeud.op, (ast.UAdd, ast.USub)):
            interne = evaluer(noeud.operand, niveau + 1)
            return None if interne is None else (interne if isinstance(noeud.op, ast.UAdd) else -interne)
        if isinstance(noeud, ast.BinOp):
            gauche, droite = evaluer(noeud.left, niveau + 1), evaluer(noeud.right, niveau + 1)
            if gauche is None or droite is None:
                return None
            if isinstance(noeud.op, ast.Add):
                return gauche + droite
            if isinstance(noeud.op, ast.Sub):
                return gauche - droite
            if isinstance(noeud.op, ast.Mult):
                return gauche * droite
            if isinstance(noeud.op, ast.Div) and droite != 0:
                return gauche / droite
        return None

    return evaluer(arbre, 0)


def nombre(valeur: float) -> str:
    """Nombre écrit comme on le lit en français : « 0,5 », « 100 »."""
    entier = int(valeur)
    return str(entier) if valeur == entier else f"{valeur:g}".replace(".", ",")


def courbes(corps: str) -> list[str]:
    """Le sens de chaque série tracée, quand la source le dit."""
    table = affectations(corps)
    trouves = []
    for appel in TRACES.finditer(corps):
        ouvrante = appel.end() - 1
        arguments = decouper(corps[ouvrante + 1:fin_de_groupe(corps, ouvrante) - 1])
        positionnels = [a for a in arguments if "=" not in a.split("(")[0]]
        if not positionnels:
            continue
        # `plot(x, y)` trace y contre x ; `plot(y)` trace y seul.
        serie = positionnels[1] if len(positionnels) > 1 else positionnels[0]
        sens = sens_de_la_serie(serie, table)
        etiquette = SERIE.search(", ".join(arguments))
        if not sens:
            continue
        nom = litteral(etiquette["texte"], etiquette["prefixe"]) if etiquette else ""
        trouves.append(f"la courbe « {nom} » est {sens}" if nom else f"la courbe tracée est {sens}")
    return uniques(trouves)


def corps_de_figure(script: str, nom: str) -> str:
    """Portion du script qui produit `nom` : le code qui précède l'appel qui la nomme.

    Trois écritures cohabitent dans les cours du PO, et il faut les trois :

    - une **fonction par figure**, qui se termine par `savefig("…fig01_memoire.pdf")` — chapitre 2 du
      cours de C, 1411 lignes pour vingt figures ;
    - un **fichier par figure** — chapitre 1 du même cours ;
    - un script **linéaire**, où chaque figure se termine par `save(fig, "f4_zeros")` et où le code
      d'une figure est simplement ce qui sépare son appel du précédent — cours d'Introduction au ML.

    Lire le fichier entier donnerait les libellés de toutes les figures pour une seule.
    """
    fonctions = list(re.finditer(r"^def\s+\w+\s*\(", script, re.M))
    for trouve in fonctions:
        fin = script.find("\ndef ", trouve.end())
        bloc = script[trouve.start():fin if fin != -1 else len(script)]
        if re.search(rf"savefig\(\s*[\"'][^\"']*{re.escape(nom)}\.", bloc):
            return bloc

    # Script linéaire : les appels qui nomment une figure, dans l'ordre. Celui qui porte `nom`
    # termine son code ; le précédent termine celui d'avant.
    appels = list(re.finditer(r"\b\w+\s*\([^()]*[\"']([\w.-]+?)(?:\.\w+)?[\"'][^()]*\)", script))
    bornes = [(a.start(), a.end(), a[1]) for a in appels
              if re.search(r"\bsave\w*\s*\(", script[a.start():a.end()])]
    for position, (debut, fin, trouve_nom) in enumerate(bornes):
        if trouve_nom != nom:
            continue
        precedent = bornes[position - 1][1] if position > 0 else 0
        return script[precedent:fin]

    return script if not fonctions else ""


def brouillon_matplotlib(script: str, nom: str) -> str:
    """Brouillon d'une figure calculée : titre, axes, séries et textes posés par le script."""
    corps = corps_de_figure(script, nom)
    if not corps:
        return ""
    morceaux = []
    titre = TITRE.search(corps)
    if titre:
        morceaux.append(f"Figure intitulée « {litteral(titre['texte'], titre['prefixe'])} »")
    for motif, place in ((AXE_X, "en abscisse"), (AXE_Y, "en ordonnée")):
        trouve = motif.search(corps)
        if trouve:
            morceaux.append(f"« {litteral(trouve['texte'], trouve['prefixe'])} » {place}")
    series = uniques(litteral(t["texte"], t["prefixe"]) for t in SERIE.finditer(corps))
    if series:
        morceaux.append("séries : " + liste_citee(series))
    # Le sens de la courbe passe **avant** la liste des libellés : c'est ce qu'un lecteur retient d'un
    # graphique, et la liste des libellés est ce que la troncature coupe en premier.
    morceaux += courbes(corps)
    poses = [texte for texte in uniques(texte_pose(corps)) if texte not in series]
    if poses and not morceaux:
        morceaux.append("Figure portant " + liste_citee(poses))
    elif poses:
        morceaux.append("libellés : " + liste_citee(poses))
    return tronquer(", ".join(morceaux) + ".") if morceaux else ""


def uniques(valeurs) -> list[str]:
    """Textes distincts, dans l'ordre, sans ceux qui n'ont rien à dire.

    Une f-string entièrement calculée (`f"{valeur:.2f}"`) se réduit à « … » : la citer ferait croire
    au PO qu'un libellé de la figure est vide.
    """
    vus: list[str] = []
    for valeur in valeurs:
        if valeur and valeur.strip("… .,:;-") and valeur not in vus:
            vus.append(valeur)
    return vus


# --- Le titre sous lequel la figure apparaît ------------------------------------------------------

TITRAGE = re.compile(r"\\(?:frametitle|section|subsection|subsubsection|chapter)\*?\s*\{")


def titre_courant(source: str, position: int) -> str:
    """Titre de la slide ou de la section qui contient `position` : le repère que le PO reconnaît."""
    dernier = ""
    for trouve in TITRAGE.finditer(source):
        if trouve.start() > position:
            break
        dernier = texte_nu(contenu_accolade(source, trouve.end() - 1))
    return dernier


# --- Assemblage -----------------------------------------------------------------------------------

MOTIF_IMAGE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{(?P<nom>[^}]+)\}")
# Une légende du .tex suit l'image : la figure a déjà son texte alternatif, il n'y a rien à rédiger.
MOTIF_LEGENDE = re.compile(r"\s*\{\\(?:scriptsize|footnotesize|small)\s")


class Brouillon:
    """Une figure sans légende, le repère où la trouver, et la phrase proposée au PO."""

    def __init__(self, nom: str, titre: str, texte: str, source: str) -> None:
        self.nom, self.titre, self.texte, self.source = nom, titre, texte, source


def script_de_la_figure(nom: str, dossiers: list[Path]) -> Path | None:
    """Script Python qui dessine `nom`, cherché à côté des sources.

    Deux usages coexistent dans les cours du PO : un script par figure (`fig_01_….py`, chapitre 1 du
    cours de C) et un générateur unique pour tout le chapitre (`generate_figures.py`, chapitre 2). On
    reconnaît le second à son `savefig` : c'est lui qui nomme le fichier produit.
    """
    for dossier in dossiers:
        if not dossier.is_dir():
            continue
        direct = dossier / f"{nom}.py"
        if direct.is_file():
            return direct
        for candidat in sorted(dossier.glob("*.py")):
            texte = candidat.read_text(encoding="utf-8", errors="ignore")
            if re.search(rf"savefig\(\s*[\"'][^\"']*{re.escape(nom)}\.", texte):
                return candidat
            # Un générateur linéaire enregistre par un auxiliaire — `save(fig, "f4_zeros")` — et son
            # `savefig` ne voit qu'une variable. C'est le nom cité en clair qui le désigne.
            if re.search(rf"[\"']{re.escape(nom)}[\"']", texte):
                return candidat
    return None


def brouillons(source: str, prefixe: str, scripts: dict[str, Path] | None = None,
               dossiers: list[Path] | None = None) -> list[Brouillon]:
    """Tous les brouillons d'un `.tex`, dans l'ordre où les figures apparaissent."""
    scripts = dict(scripts or {})
    dossiers = dossiers or []
    trouves: list[Brouillon] = []
    corps = source.split(r"\begin{document}", 1)[-1]
    decalage = len(source) - len(corps)

    numero = 0
    for trouve in re.finditer(r"\\begin\{tikzpicture\}", corps):
        fin = corps.index(r"\end{tikzpicture}", trouve.start())
        numero += 1
        nom = f"{prefixe}-{numero:02d}"
        trouves.append(Brouillon(nom, titre_courant(source, decalage + trouve.start()),
                                 brouillon_tikz(corps[trouve.start():fin]), "schéma TikZ"))

    for trouve in MOTIF_IMAGE.finditer(corps):
        if MOTIF_LEGENDE.match(corps, trouve.end()):
            continue    # la légende du .tex fait le texte alternatif : rien à proposer
        nom = Path(trouve["nom"]).stem
        script = scripts.get(nom) or script_de_la_figure(nom, dossiers)
        texte = brouillon_matplotlib(script.read_text(encoding="utf-8"), nom) if script else ""
        trouves.append(Brouillon(nom, titre_courant(source, decalage + trouve.start()), texte,
                                 "script matplotlib" if script else "image sans source lisible"))
    return trouves


def presentation(trouves: list[Brouillon], commande: str = "") -> str:
    """Les brouillons présentés au PO **en une seule fois**, figure par figure (US-58)."""
    if not trouves:
        return ""
    lignes = [f"Brouillons de textes alternatifs — {len(trouves)} figure(s) sans légende dans le .tex",
              "",
              "Rien n'est écrit dans le site tant que le PO n'a pas validé. Pour chaque figure :",
              "accepter le brouillon, le corriger, ou le réécrire.", ""]
    sans_brouillon = []
    for numero, brouillon in enumerate(trouves, start=1):
        lignes.append(f"{numero:2d}. {brouillon.nom}   [{brouillon.source}]")
        lignes.append(f"    Dans : {brouillon.titre or '(sans titre)'}")
        if brouillon.texte:
            lignes.append(f"    Brouillon : {brouillon.texte}")
        else:
            lignes.append("    Brouillon : AUCUN — la source ne contient aucun texte lisible.")
            sans_brouillon.append(brouillon.nom)
        lignes.append("")
    if sans_brouillon:
        lignes += [f"Sans brouillon possible ({len(sans_brouillon)}) : " + ", ".join(sans_brouillon),
                   "Ces figures-là n'offrent rien à lire dans leur source : leur phrase revient au PO.",
                   ""]
    if commande:
        lignes += ["Une fois les phrases validées, relancer avec :", f"    {commande}", ""]
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("source", type=Path, help="le .tex de la séance ou du chapitre")
    analyseur.add_argument("--prefixe", default="figure",
                           help="préfixe des schémas TikZ compilés (NN-slug)")
    analyseur.add_argument("--script", action="append", default=[], metavar="NOM=CHEMIN.py",
                           help="script matplotlib d'une figure calculée (répétable ; par défaut, "
                                "cherché à côté du .tex)")
    analyseur.add_argument("--figures-source", type=Path,
                           help="dossier des figures (par défaut : celui du .tex, et figs/)")
    analyseur.add_argument("--complet", action="store_true",
                           help="cite tout ce que la source contient, sans « et N autre(s) » ni "
                                "troncature, quitte à faire deux phrases")
    args = analyseur.parse_args()

    global COMPLET
    COMPLET = args.complet

    scripts = {}
    for morceau in args.script:
        nom, chemin = morceau.split("=", 1)
        scripts[nom] = Path(chemin)

    dossiers = [d for d in (args.figures_source, args.source.parent,
                            args.source.parent / "figs") if d]
    trouves = brouillons(args.source.read_text(encoding="utf-8"), args.prefixe, scripts, dossiers)
    if not trouves:
        print("Aucune figure sans légende : rien à soumettre au PO.")
        return 0
    print(presentation(trouves))
    return 0


if __name__ == "__main__":
    sys.exit(main())
