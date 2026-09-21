#!/usr/bin/env python3
"""Brouillons de textes alternatifs, à soumettre au PO (US-58).

    python3 scripts/brouillons_alt.py <fichier.tex> --prefixe NN-slug [--script fig=chemin.py]

Une figure sans légende dans le `.tex` n'a pas de texte alternatif, et le script n'en invente pas
(CLAUDE.md §7). Jusqu'ici il s'arrêtait en demandant une phrase au PO, figure par figure : 33 schémas
pour les seuls chapitres restants du cours de C, soit 33 allers-retours.

Ce module rédige un **brouillon** à partir de **ce que la source contient**, et rien d'autre :

- pour un `tikzpicture`, les libellés de ses nœuds, ses flèches et ses tableaux de nœuds ;
- pour une figure matplotlib, le titre, les axes, les séries et les textes posés par le script.

Le brouillon n'est **jamais écrit dans le site** : il est présenté au PO, qui accepte, corrige ou
réécrit. Tant qu'il n'a pas validé, la page garde son `TODO(PO)`.

Ce que le brouillon ne fait pas, et c'est délibéré : il ne dit pas ce que la figure *signifie*. Il
énumère ce qui y est écrit. « Trois boîtes, « pile », « tas », « code », et deux flèches » se vérifie
en regardant l'image ; « le schéma montre comment la mémoire est organisée » ne se vérifie pas.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LONGUEUR_MAXIMALE = 300   # au-delà, un texte alternatif n'est plus lu : on coupe la liste des libellés
LIBELLES_CITES = 8        # nombre de libellés cités avant « … »

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


def libelles_tikz(dessin: str) -> list[str]:
    """Textes écrits dans un `tikzpicture` : nœuds et étiquettes de flèches.

    Les matrices de nœuds sont traitées à part (`tableau_tikz`) : elles tiennent tout un tableau dans
    une seule accolade, et l'aplatir donnerait un libellé de cinquante mots.
    """
    sans_matrice = sans_foreach(re.sub(r"\\matrix\b", "\x00", dessin))
    trouves: list[str] = []
    for motif in (r"\\node\b", r"(?<![\\\w])node(?=[\[ (])"):
        for depart in (t.end() for t in re.finditer(motif, sans_matrice)):
            accolade = accolade_du_libelle(sans_matrice, depart)
            if accolade != -1:
                trouves.append(contenu_accolade(sans_matrice, accolade))
    libelles = []
    for brut in trouves:
        propre = texte_nu(brut)
        if propre and propre not in libelles:
            libelles.append(propre)
    return libelles


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


def tableau_tikz(dessin: str) -> str:
    """Dimensions et première ligne d'une `matrix of nodes` : ce qu'un lecteur y voit d'abord."""
    trouve = re.search(r"\\matrix\b", dessin)
    if not trouve:
        return ""
    accolade = accolade_du_libelle(dessin, trouve.end())
    if accolade == -1:
        return ""
    lignes = [ligne for ligne in contenu_accolade(dessin, accolade).split(r"\\") if ligne.strip()]
    if not lignes:
        return ""
    premiere = [texte_nu(case) for case in lignes[0].split("&")]
    colonnes = max(len(ligne.split("&")) for ligne in lignes)
    entete = ", ".join(f"« {case} »" for case in premiere if case)
    return (f"Tableau de {len(lignes)} ligne(s) et {colonnes} colonne(s)"
            + (f", première ligne : {entete}" if entete else ""))


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


def fleches_tikz(dessin: str) -> int:
    """Nombre de traits fléchés du schéma (`\\draw[->]`, `\\path[<->]`, `edge`)."""
    return len(re.findall(r"(?:draw|path|edge)\s*\[[^\]]*(?<![<>-])-(?:>|latex|stealth)", dessin)) \
        + len(re.findall(r"(?:draw|path|edge)\s*\[[^\]]*<->", dessin))


def liste_citee(libelles: list[str]) -> str:
    cites = libelles[:LIBELLES_CITES]
    liste = ", ".join(f"« {libelle} »" for libelle in cites)
    if len(libelles) > len(cites):
        liste += f", et {len(libelles) - len(cites)} autre(s)"
    return liste


def tronquer(texte: str) -> str:
    """Un texte alternatif trop long n'est plus lu : on coupe à la virgule qui précède la limite."""
    if len(texte) <= LONGUEUR_MAXIMALE:
        return texte
    coupe = texte.rfind(", ", 0, LONGUEUR_MAXIMALE)
    return (texte[:coupe] if coupe > 0 else texte[:LONGUEUR_MAXIMALE]) + "…"


def brouillon_tikz(dessin: str) -> str:
    """Brouillon d'un `tikzpicture` : ce qui y est écrit, et comment c'est relié. Rien de plus."""
    morceaux = []
    tableau = tableau_tikz(dessin)
    if tableau:
        morceaux.append(tableau)
    libelles = libelles_tikz(dessin)
    if libelles:
        debut = "libellés" if tableau else "Schéma portant "f"{len(libelles)} libellé(s)"
        morceaux.append(f"{debut} : {liste_citee(libelles)}")
    cases = repetitions_tikz(dessin)
    if cases:
        morceaux.append(f"et une suite de {cases} cases")
    if not morceaux:
        return ""
    fleches = fleches_tikz(dessin)
    if fleches == 1:
        morceaux.append("reliés par une flèche")
    elif fleches > 1:
        morceaux.append(f"reliés par {fleches} flèches")
    return tronquer(", ".join(morceaux) + ".")


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


def corps_de_figure(script: str, nom: str) -> str:
    """Portion du script qui produit `nom.pdf` : de sa fonction à son `savefig`.

    Un générateur de chapitre tient toutes ses figures dans un fichier (1411 lignes pour le chapitre 2
    du cours de C) : lire le fichier entier donnerait les libellés de vingt figures pour une seule.
    """
    depart = 0
    for trouve in re.finditer(r"^def\s+(\w+)\s*\(", script, re.M):
        fin = script.find("\ndef ", trouve.end())
        bloc = script[trouve.start():fin if fin != -1 else len(script)]
        if re.search(rf"savefig\(\s*[\"'][^\"']*{re.escape(nom)}\.", bloc):
            return bloc
        depart = trouve.end()
    return script if depart == 0 else ""


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
    poses = [texte for texte in uniques(texte_pose(corps)) if texte not in series]
    if poses and not morceaux:
        morceaux.append(f"Figure portant {len(poses)} libellé(s) : {liste_citee(poses)}")
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
    args = analyseur.parse_args()

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
