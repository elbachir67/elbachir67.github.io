#!/usr/bin/env python3
"""Vérifie qu'aucune figure n'a été vidée en chemin (US-54).

Une figure publiée vide est un défaut **silencieux** : la page se rend, les liens sont bons, aucun
contrôle ne bronche, et l'étudiant voit un cadre blanc. C'est arrivé en US-51 — les 45 points de
`f8_scatter` étaient invisibles depuis leur import, parce qu'un préfixe `xlink` perdu à l'écriture
cassait les `<use>` qui les dessinaient.

Le contrôle regarde trois choses, pour chaque figure d'un cours :

1. **L'écart avec la source.** Le nettoyage ne fait que réécrire des couleurs et une police : il ne
   doit retirer aucun élément dessiné. Un écart au-delà de `ECART_TOLERE` fait échouer, avec les
   deux comptes.
2. **Ce qui reste visible.** Une figure sans aucun élément dessiné échoue, et un `<use>` dont la
   référence ne résout pas ne compte pas.
3. **Ce que le HTML saura lire.** Une figure est *incorporée* dans la page : ce n'est alors plus du
   XML, et un préfixe autre que `xlink:` n'y désigne rien. C'est la forme exacte du défaut d'US-51,
   qu'aucune lecture XML ne peut voir — elle est donc cherchée dans le texte.

Les figures incorporées dans le site rendu sont vérifiées de la même façon : c'est là que le lecteur
les voit, et c'est là que le défaut se manifestait.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "_site"
XLINK = "{http://www.w3.org/1999/xlink}href"

# Un élément dessiné laisse une trace à l'écran. Les définitions n'en laissent pas : elles attendent
# d'être rappelées par un <use>.
DESSINES = {"rect", "circle", "ellipse", "polygon", "polyline", "path", "line", "text", "image"}
DEFINITIONS = {"defs", "clipPath", "symbol", "marker", "pattern", "mask"}
# Le nettoyage ne retire rien : la moindre perte est suspecte. Le seuil laisse passer l'arrondi d'une
# figure à un seul élément, pas la disparition d'un nuage de points.
ECART_TOLERE = 0.02


def sans_espace(balise: str) -> str:
    return balise.split("}")[-1]


def identifiants(racine: ET.Element) -> set[str]:
    return {element.get("id") for element in racine.iter() if element.get("id")}


def elements_dessines(racine: ET.Element) -> int:
    """Compte ce qui laisse une trace : les formes, et les <use> dont la référence existe."""
    connus = identifiants(racine)
    total = 0

    def parcourir(element: ET.Element) -> None:
        nonlocal total
        for enfant in element:
            balise = sans_espace(enfant.tag)
            if balise in DEFINITIONS:
                continue                       # une définition ne dessine pas par elle-même
            if balise in DESSINES:
                total += 1
            elif balise == "use":
                # Un <use> qui ne résout pas ne dessine rien : c'est le défaut d'US-51.
                reference = enfant.get(XLINK) or enfant.get("href") or ""
                if reference.startswith("#") and reference[1:] in connus:
                    total += 1
            parcourir(enfant)

    parcourir(racine)
    return total


def uses_casses(racine: ET.Element) -> list[str]:
    """Références de <use> qui ne pointent sur rien — le symptôme, avant même le comptage."""
    connus = identifiants(racine)
    casses = []
    for element in racine.iter():
        if sans_espace(element.tag) != "use":
            continue
        reference = element.get(XLINK) or element.get("href") or ""
        if not (reference.startswith("#") and reference[1:] in connus):
            casses.append(reference or "(sans référence)")
    return casses


# Une fois la figure incorporée dans la page, ce n'est plus du XML mais du HTML : les préfixes n'y
# sont pas résolus, et seuls « xlink:href » — connu de l'analyseur HTML — et « href » y renvoient à
# quelque chose. Un « ns4:href », pourtant légal en XML, n'y désigne rien : c'était le défaut d'US-51.
USE_BRUT = re.compile(r"<use\b[^>]*>")
REFERENCE_LISIBLE = re.compile(r"(?:^|\s)(?:xlink:)?href\s*=")


def references_illisibles_en_html(texte: str) -> int:
    """Nombre de <use> dont la référence sera perdue à l'incorporation dans la page."""
    return sum(1 for balise in USE_BRUT.findall(texte) if not REFERENCE_LISIBLE.search(balise))


def figures_des_cours() -> list[tuple[Path, Path | None]]:
    """Chaque figure publiée, avec sa source d'origine quand elle en a une."""
    couples = []
    for publiee in sorted(RACINE.glob("cours/*/figures/*.svg")):
        source = publiee.parent.parent / "_sources" / "figs" / publiee.name
        couples.append((publiee, source if source.is_file() else None))
    return couples


def figures_orphelines() -> list[tuple[str, str]]:
    """Figures converties et commitées qu'aucun chapitre n'affiche.

    Une figure protégée à l'intérieur d'un bloc lui-même protégé perdait son marqueur à la
    restauration : la figure restait sur le disque, passait tous les contrôles de fichier, et
    n'apparaissait sur aucune slide. Treize figures du cours de ML étaient dans ce cas, et rien
    ne le disait. Le contrôle est bête : le nom de chaque figure doit se lire quelque part dans
    les chapitres du cours.
    """
    manquantes = []
    for dossier in sorted(RACINE.glob("cours/*/figures")):
        chapitres = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                              for p in sorted(dossier.parent.glob("chapitres/*.qmd")))
        for figure in sorted(dossier.iterdir()):
            if figure.suffix.lower() not in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
                continue
            if figure.stem not in chapitres:
                manquantes.append((str(figure.relative_to(RACINE)),
                                   "figure convertie mais citée par aucun chapitre : "
                                   "elle ne s'affichera nulle part"))
    return manquantes


def controler_fichier(publiee: Path, source: Path | None) -> list[str]:
    ecarts = []
    try:
        arbre = ET.parse(publiee).getroot()
    except ET.ParseError as erreur:
        return [f"illisible : {erreur}"]

    dessines = elements_dessines(arbre)
    illisibles = references_illisibles_en_html(publiee.read_text(encoding="utf-8", errors="ignore"))
    if illisibles:
        ecarts.append(f"{illisibles} référence(s) <use> écrites avec un préfixe que le HTML ne "
                      "résout pas : la figure se videra une fois incorporée dans la page "
                      "(attendu : « xlink:href » ou « href »)")
    casses = uses_casses(arbre)
    if casses:
        ecarts.append(f"{len(casses)} référence(s) <use> qui ne pointent sur rien "
                      f"(par exemple « {casses[0]} ») : ces éléments ne s'affichent pas")
    if dessines == 0:
        ecarts.append("figure vide : aucun élément dessiné ne subsiste")

    if source is not None:
        attendus = elements_dessines(ET.parse(source).getroot())
        perdus = attendus - dessines
        if attendus and perdus > max(1, round(attendus * ECART_TOLERE)):
            ecarts.append(f"{perdus} élément(s) dessiné(s) perdus au nettoyage "
                          f"({attendus} dans la source, {dessines} après) : le nettoyage ne doit "
                          "réécrire que des couleurs et une police")
    return ecarts


def svg_du_site() -> list[tuple[Path, int, str]]:
    """Figures incorporées dans les pages rendues : (page, numéro, source XML du svg)."""
    trouvees = []
    if not SITE.is_dir():
        return trouvees
    for page in sorted(SITE.rglob("*.html")):
        if "site_libs" in str(page):
            continue
        html = page.read_text(encoding="utf-8", errors="ignore")
        for numero, morceau in enumerate(re.findall(r"<svg\b.*?</svg>", html, re.S), start=1):
            trouvees.append((page, numero, morceau))
    return trouvees


def main() -> int:
    ecarts: list[tuple[str, str]] = []

    couples = figures_des_cours()
    for publiee, source in couples:
        for message in controler_fichier(publiee, source):
            ecarts.append((str(publiee.relative_to(RACINE)), message))

    ecarts += figures_orphelines()

    incorporees = svg_du_site()
    for page, numero, morceau in incorporees:
        try:
            arbre = ET.fromstring(morceau)
        except ET.ParseError:
            continue                           # un svg d'icône, tronqué par la recherche : ignoré
        if elements_dessines(arbre) == 0:
            ecarts.append((f"{page.relative_to(RACINE)} (figure {numero})",
                           "figure incorporée vide : rien ne s'affichera"))
        elif references_illisibles_en_html(morceau):
            ecarts.append((f"{page.relative_to(RACINE)} (figure {numero})",
                           "références <use> illisibles en HTML : la figure s'affichera amputée"))

    for fichier, message in ecarts:
        print(f"{fichier}: {message}")
    if ecarts:
        print(f"\nÉCHEC : {len(ecarts)} figure(s) vidée(s), amputée(s) ou jamais affichée(s).")
        return 1
    print(f"OK : {len(couples)} figure(s) de cours et {len(incorporees)} figure(s) incorporée(s) "
          "dessinent quelque chose, sont toutes citées, et sans perte au nettoyage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
