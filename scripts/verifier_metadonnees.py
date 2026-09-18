#!/usr/bin/env python3
"""Échoue si le référencement du site rendu est incomplet (US-13).

    python3 scripts/verifier_metadonnees.py            # analyse _site/
    python3 scripts/verifier_metadonnees.py chemin/    # analyse un autre dossier

Vérifie, pour chaque page HTML (hors site_libs/) :
- un titre et une description non vides, et uniques **dans leur langue** : deux versions d'une même page
  (française et anglaise) portent légitimement le même titre, et les balises hreflang les relient ;
- les métadonnées de partage og:title, og:description, og:image et twitter:card ;
- une image d'aperçu en URL absolue https, présente dans le site rendu.
Vérifie aussi que sitemap.xml liste chaque page et que robots.txt indique ce sitemap.
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

BALISES_REQUISES = ["og:title", "og:description", "og:image", "twitter:card"]
# Page laissée vide par Quarto à la place d'un brouillon (« draft-mode: gone ») : elle n'a ni en-tête ni
# contenu, et n'est pas publiée. Rien à y vérifier.
MOTIF_BROUILLON = re.compile(r"<head\b", re.I)


def brouillon(html: str) -> bool:
    return MOTIF_BROUILLON.search(html) is None


class LecteurEntete(HTMLParser):
    """Relève le titre et les balises <meta> d'une page."""

    def __init__(self) -> None:
        super().__init__()
        self.titre, self.metas, self.langue, self._dans_titre = "", {}, "", False

    def handle_starttag(self, balise, attributs):
        attributs = dict(attributs)
        if balise == "html":
            self.langue = (attributs.get("lang") or "")[:2]
        if balise == "title":
            self._dans_titre = True
        elif balise == "meta":
            cle = attributs.get("name") or attributs.get("property")
            if cle and cle not in self.metas:
                self.metas[cle] = (attributs.get("content") or "").strip()

    def handle_endtag(self, balise):
        if balise == "title":
            self._dans_titre = False

    def handle_data(self, donnees):
        if self._dans_titre:
            self.titre += donnees


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer quarto render d'abord).")
    erreurs: list[tuple[str, str]] = []

    def erreur(fichier, message):
        erreurs.append((str(fichier), message))

    pages = sorted(p for p in racine.rglob("*.html") if "site_libs" not in p.relative_to(racine).parts)
    brouillons = [p for p in pages if brouillon(p.read_text(encoding="utf-8"))]
    pages = [p for p in pages if p not in brouillons]
    titres, descriptions = defaultdict(list), defaultdict(list)
    for page in pages:
        lecteur = LecteurEntete()
        lecteur.feed(page.read_text(encoding="utf-8"))
        titre, description = " ".join(lecteur.titre.split()), lecteur.metas.get("description", "")
        if not titre:
            erreur(page, "titre absent")
        if not description:
            erreur(page, "description absente")
        titres[(lecteur.langue, titre)].append(page)
        descriptions[(lecteur.langue, description)].append(page)
        for balise in BALISES_REQUISES:
            if not lecteur.metas.get(balise):
                erreur(page, f"métadonnée {balise} absente")
        image = lecteur.metas.get("og:image", "")
        if image:
            url = urlparse(image)
            if url.scheme != "https":
                erreur(page, f"og:image n'est pas une URL https absolue : {image}")
            elif not (racine / url.path.lstrip("/")).is_file():
                erreur(page, f"og:image introuvable dans le site rendu : {image}")

    for (langue, valeur), liste, nature in [(v, l, "titre") for v, l in titres.items()] + \
                                           [(v, l, "description") for v, l in descriptions.items()]:
        if valeur and len(liste) > 1:
            for page in liste:
                erreur(page, f"{nature} identique sur {len(liste)} pages en « {langue} » : « {valeur} »")

    sitemap = racine / "sitemap.xml"
    if not sitemap.is_file():
        erreur(sitemap, "sitemap.xml absent")
    else:
        espace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        adresses = [loc.text or "" for loc in ET.parse(sitemap).getroot().findall("s:url/s:loc", espace)]
        chemins = {urlparse(a).path.lstrip("/") for a in adresses}
        for page in pages:
            if page.relative_to(racine).as_posix() not in chemins:
                erreur(page, "page absente de sitemap.xml")

    robots = racine / "robots.txt"
    if not robots.is_file():
        erreur(robots, "robots.txt absent")
    elif not re.search(r"(?im)^Sitemap:\s*https://\S+/sitemap\.xml\s*$", robots.read_text(encoding="utf-8")):
        erreur(robots, "robots.txt n'indique pas l'adresse de sitemap.xml")

    for fichier, message in erreurs:
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error file={fichier},title=Référencement::{message}")
        print(f"{fichier}: {message}")
    if erreurs:
        print(f"ÉCHEC : {len(erreurs)} problème(s) de référencement dans {racine}/.")
        return 1
    langues = ", ".join(sorted({l for l, _ in titres} - {""})) or "aucune"
    ignores = f" ({len(brouillons)} brouillon(s) non publié(s) ignoré(s))" if brouillons else ""
    print(f"OK : {len(pages)} page(s) avec titre et description uniques par langue ({langues}), "
          f"métadonnées de partage, sitemap.xml et robots.txt.{ignores}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
