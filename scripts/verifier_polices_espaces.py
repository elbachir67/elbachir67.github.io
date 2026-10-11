#!/usr/bin/env python3
"""Échoue si deux schémas d'une page se volent leurs polices, ou si une espace fine est devenue une
virgule (#199).

    python3 scripts/verifier_polices_espaces.py            # analyse _site/
    python3 scripts/verifier_polices_espaces.py chemin/    # analyse un autre dossier

Deux défauts partis en ligne sans qu'aucun contrôle ne les voie, parce que chacun ne se montre
qu'**une fois la page assemblée** :

1. **Polices et glyphes des figures incorporées.** dvisvgm nommait ses polices `nf0`, `nf1`… dans
   chaque schéma, réduites aux lettres dont ce schéma avait besoin. Deux schémas d'une même page
   déclaraient chacun leur `nf0` : le navigateur n'en gardait qu'un, et les lettres manquantes
   sortaient dans une police de secours — « struc t Point p » au chapitre 4 du cours de C. Le
   contrôle des identifiants ne pouvait pas le voir : une police se déclare par son **nom**, dans
   une feuille de style, et non par un `id`. Ici, toute police déclarée (`@font-face`, `<font>`) et
   tout glyphe défini (`<symbol>`, `<glyph>`, identifiant `glyph-…`) doit appartenir à **un seul**
   SVG de la page.

2. **Espace fine `\\,` lue comme une virgule.** Hors formule, le convertisseur laissait `\\,` dans
   le Markdown, qui la lit comme une virgule échappée : « 80,% », « 10,000 » — un nombre anglais.
   Le contrôle part de la **source** : pour chaque `\\,` d'un `.tex` importé entre un nombre et
   « % », trois chiffres ou des guillemets, il cherche dans la page rendue la forme fautive
   (« 80,% », « 10,000 », « «, »). Partir de la source évite les faux positifs : « 1,000 » écrit tel
   quel dans un code Python n'est pas un défaut.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import html
import os
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
EXCLUS = {"site_libs"}

SVG = re.compile(r"<svg\b.*?</svg>", re.S | re.I)
# Le contenu d'un bloc de code n'est pas un élément du document : un cours de HTML y écrit des
# balises en toutes lettres (même raison que dans verifier_identifiants.py).
CODE = re.compile(r"(<(pre|code)\b[^>]*>)(.*?)(</\2>)", re.S | re.I)
POLICE = re.compile(r"@font-face\s*\{[^}]*?font-family\s*:\s*['\"]?([^;'\"}]+)", re.I)
POLICE_ELEMENT = re.compile(r"<font(?:-face)?\b[^>]*?(?:font-family|id)=['\"]([^'\"]+)", re.I)
GLYPHE = re.compile(
    r"""<(symbol|glyph)\b[^>]*?\bid=['"]([^'"]+)|(?<![-\w])id=['"]([^'"]*glyph[^'"]*)['"]""", re.I)

# Formules et commentaires d'une source LaTeX, repérés comme l'import les repère : la `\,` d'une
# formule est rendue par MathJax, et n'est pas en cause. Un motif à part se décalait au premier
# dollar échappé (`\$`) et laissait passer « 10\,000 requêtes » de Structures de Données.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importer_chapitre import MOTIF_MATHS, sans_commentaires  # noqa: E402  (même dossier)
# `\,` entre un nombre et « % » ou trois chiffres, et `\,` collée à des guillemets.
# Le pourcentage s'écrit `\%` en LaTeX : la forme fautive, elle, est « 80,% ».
ESPACE_FINE = re.compile(r"(\d+)\\,(\\?%|\d{3})|«\s*\\,|\\,\s*»")
BALISES = re.compile(r"<[^>]+>")


def annoncer(fichier: Path, titre: str, message: str) -> None:
    chemin = fichier.relative_to(RACINE) if fichier.is_relative_to(RACINE) else fichier
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={chemin},title={titre}::{message}")
    print(f"{chemin}: {message}")


def polices_partagees(page: Path) -> list[str]:
    """Polices et glyphes que plusieurs SVG de la page déclarent, chacun avec ses SVG."""
    contenu = CODE.sub(lambda t: t[1] + " " + t[4], page.read_text(encoding="utf-8", errors="replace"))
    proprietaires: dict[str, set[int]] = defaultdict(set)
    for numero, svg in enumerate(SVG.findall(contenu), start=1):
        for nom in POLICE.findall(svg) + POLICE_ELEMENT.findall(svg):
            proprietaires[f"police « {nom.strip()} »"].add(numero)
        for balise, identifiant, autre in GLYPHE.findall(svg):
            proprietaires[f"glyphe « {identifiant or autre} »"].add(numero)
    return sorted(f"{nom} (SVG n° {', '.join(map(str, sorted(svgs)))})"
                  for nom, svgs in proprietaires.items() if len(svgs) > 1)


def formes_fautives(source: str) -> list[str]:
    """Ce que la page afficherait si les `\\,` de la source étaient devenues des virgules."""
    texte = MOTIF_MATHS.sub(" ", sans_commentaires(source))
    fautives = []
    for trouve in ESPACE_FINE.finditer(texte):
        if trouve[1]:
            fautives.append(f"{trouve[1]},{trouve[2].lstrip(chr(92))}")
        else:
            fautives.append("«," if "«" in trouve[0] else ",»")
    return sorted(set(fautives))


def virgules(site: Path) -> tuple[int, list[tuple[Path, str]]]:
    """Pages de cours où une `\\,` de la source s'affiche en virgule."""
    pages, fautes = 0, []
    for manifeste in sorted((RACINE / "cours").glob("*/_sources/import.toml")):
        cours = manifeste.parent.parent
        for chapitre in tomllib.loads(manifeste.read_text(encoding="utf-8"))["chapitres"]:
            source = cours / chapitre["tex"]
            rendu = site / cours.relative_to(RACINE) / Path(chapitre["sortie"]).with_suffix(".html")
            if not source.is_file() or not rendu.is_file():
                continue
            pages += 1
            attendues = formes_fautives(source.read_text(encoding="utf-8", errors="replace"))
            if not attendues:
                continue
            texte = html.unescape(BALISES.sub("", rendu.read_text(encoding="utf-8", errors="replace")))
            for forme in attendues:
                if forme in texte:
                    fautes.append((rendu, forme))
    return pages, fautes


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    if not site.is_dir():
        sys.exit(f"Dossier introuvable : {site} (lancer quarto render d'abord).")

    pages = [p for p in sorted(site.rglob("*.html")) if not EXCLUS.intersection(p.relative_to(site).parts)]
    echecs = 0
    for page in pages:
        partagees = polices_partagees(page)
        if partagees:
            echecs += 1
            detail = " ; ".join(partagees[:4]) + (f" ; et {len(partagees) - 4} autre(s)"
                                                   if len(partagees) > 4 else "")
            annoncer(page, "Police partagée entre figures",
                     f"{len(partagees)} police(s) ou glyphe(s) déclarés par plusieurs SVG : {detail}. "
                     "Le navigateur n'en garde qu'un, et les lettres des autres figures sortent dans "
                     "une police de secours.")

    chapitres, fautes = virgules(site)
    par_page: dict[Path, list[str]] = defaultdict(list)
    for page, forme in fautes:
        par_page[page].append(forme)
    for page, formes in par_page.items():
        echecs += 1
        annoncer(page, "Espace fine rendue en virgule",
                 f"la source écrit « \\, » là où la page affiche {', '.join(f'« {f} »' for f in formes)}.")

    if echecs:
        print(f"ÉCHEC : {echecs} page(s) en défaut dans {site.name}/.")
        return 1
    print(f"OK : aucune police ni aucun glyphe partagés entre les SVG de {len(pages)} page(s), et "
          f"aucune espace fine rendue en virgule dans {chapitres} chapitre(s) de cours.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
