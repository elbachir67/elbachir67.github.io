#!/usr/bin/env python3
"""Rend le site bilingue : un profil Quarto par langue, puis assemblage (US-36, ADR-0003).

    python3 scripts/rendre.py            # rendu des deux langues
    python3 scripts/rendre.py --propre   # en repartant d'un cache Quarto vide

1. `quarto render --profile fr` produit le site français dans `_site/`.
2. `quarto render --profile en` produit le site anglais dans `_site-en/`.
3. `_site-en/en/` est copié dans `_site/en/`.
4. Les deux plans de site sont fusionnés dans `_site/sitemap.xml`.
5. Chaque langue garde son index de recherche : le français à la racine, l'anglais dans `_site/en/`, les pages
   anglaises étant rattachées à cette racine. Une recherche ne renvoie donc que des pages de la langue lue.

Deux dossiers de sortie sont nécessaires : deux rendus dans le même dossier s'écrasent, car chaque rendu
nettoie sa sortie (constaté pendant le spike US-37).

Piège : rendre un fichier isolé avec un profil (`quarto render page.qmd --profile en`) laisse dans le cache
`.quarto` des métadonnées de ce profil, et une page peut ressortir dans la mauvaise langue. En cas de doute,
relancer avec `--propre`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE_FR = RACINE / "_site"
SORTIE_EN = RACINE / "_site-en"
ESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
MOTIF_DECALAGE = re.compile(r'(<meta name="quarto:offset" content=")((?:\.\./)*)(")')


def decaler(trouve: re.Match[str]) -> str:
    """Remonte d'un cran la racine d'une page anglaise : le site anglais a sa racine en /en/."""
    return trouve[1] + (trouve[2][3:] or "./") + trouve[3]


def rendre(profil: str) -> None:
    print(f"== quarto render --profile {profil}")
    subprocess.run(["quarto", "render", "--profile", profil], cwd=RACINE, check=True)


def assembler() -> None:
    """Place le site anglais sous _site/en/."""
    source = SORTIE_EN / "en"
    if not source.is_dir():
        sys.exit(f"Rendu anglais introuvable : {source}")
    cible = SORTIE_FR / "en"
    shutil.rmtree(cible, ignore_errors=True)
    shutil.copytree(source, cible)
    print(f"-> {cible.relative_to(RACINE)} ({sum(1 for _ in cible.rglob('*.html'))} pages)")


def index_de_recherche_par_langue() -> None:
    """Donne son propre index de recherche à chaque langue.

    Quarto fait chercher `search.json` à la racine du site, via la méta « quarto:offset » de chaque page.
    Les pages anglaises sont donc rattachées à `/en/` : elles lisent `/en/search.json`, écrit ici depuis le
    rendu anglais, et les liens des résultats, relatifs à cette racine, restent justes. Sans cela, les deux
    langues partageraient un seul index et une recherche en anglais proposerait des pages françaises.
    """
    source, cible = SORTIE_EN / "search.json", SORTIE_FR / "en" / "search.json"
    if not source.is_file():
        print("Pas d'index de recherche anglais.")
        return
    # Le profil anglais rend aussi la page d'accueil du projet, en français : on ne garde que les pages de en/.
    entrees = [e | {"href": e["href"][3:]} for e in json.loads(source.read_text(encoding="utf-8"))
               if e.get("href", "").startswith("en/")]
    cible.write_text(json.dumps(entrees, ensure_ascii=False), encoding="utf-8")

    pages = [p for p in (SORTIE_FR / "en").rglob("*.html") if "site_libs" not in p.parts]
    for page in pages:
        texte = page.read_text(encoding="utf-8")
        page.write_text(MOTIF_DECALAGE.sub(decaler, texte, count=1), encoding="utf-8")
    print(f"-> {cible.relative_to(RACINE)} ({len(entrees)} entrées anglaises, {len(pages)} pages rattachées)")


def fusionner_sitemaps() -> None:
    """Ajoute les URL anglaises au sitemap français, sans doublon."""
    fr, en = SORTIE_FR / "sitemap.xml", SORTIE_EN / "sitemap.xml"
    if not (fr.is_file() and en.is_file()):
        print("Pas de sitemap à fusionner.")
        return
    ET.register_namespace("", ESPACE)
    arbre = ET.parse(fr)
    racine = arbre.getroot()
    connues = {u.findtext(f"{{{ESPACE}}}loc") for u in racine.findall(f"{{{ESPACE}}}url")}
    ajoutees = 0
    for url in ET.parse(en).getroot().findall(f"{{{ESPACE}}}url"):
        adresse = url.findtext(f"{{{ESPACE}}}loc") or ""
        # Le profil anglais rend aussi la page d'accueil du projet : on ne garde que les URL de /en/.
        if "/en/" in adresse and adresse not in connues:
            racine.append(url)
            ajoutees += 1
    arbre.write(fr, encoding="UTF-8", xml_declaration=True)
    print(f"-> {fr.relative_to(RACINE)} ({len(connues)} URL françaises + {ajoutees} anglaises)")


def zoom_des_slides() -> None:
    """Rétablit le zoom sur les présentations.

    Quarto écrit « user-scalable=no » dans la balise viewport des slides : sur un téléphone, le lecteur ne
    peut plus agrandir le texte, ce que WCAG 1.4.4 demande. Revealjs met déjà le contenu à l'échelle du
    cadre ; autoriser le zoom ne casse rien et rend les slides lisibles de près.
    """
    pages = [p for p in SORTIE_FR.rglob("*.html") if "site_libs" not in p.parts]
    corrigees = 0
    for page in pages:
        texte = page.read_text(encoding="utf-8")
        if "user-scalable=no" not in texte or "reveal" not in texte:
            continue
        page.write_text(texte.replace("maximum-scale=1.0, user-scalable=no",
                                      "maximum-scale=5.0, user-scalable=yes"), encoding="utf-8")
        corrigees += 1
    if corrigees:
        print(f"-> zoom rétabli sur {corrigees} présentation(s)")


def main() -> int:
    if "--propre" in sys.argv[1:]:
        shutil.rmtree(RACINE / ".quarto", ignore_errors=True)
        print("Cache .quarto vidé.")
    rendre("fr")
    rendre("en")
    assembler()
    fusionner_sitemaps()
    index_de_recherche_par_langue()
    zoom_des_slides()
    return 0


if __name__ == "__main__":
    sys.exit(main())
