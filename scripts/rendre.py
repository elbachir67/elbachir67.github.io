#!/usr/bin/env python3
"""Rend le site bilingue : un profil Quarto par langue, puis assemblage (US-36, ADR-0003).

    python3 scripts/rendre.py            # rendu des deux langues
    python3 scripts/rendre.py --propre   # en repartant d'un cache Quarto vide

1. `quarto render --profile fr` produit le site français dans `_site/`.
2. `quarto render --profile en` produit le site anglais dans `_site-en/`.
3. `_site-en/en/` est copié dans `_site/en/`.
4. Les deux plans de site sont fusionnés dans `_site/sitemap.xml`, et les deux index de recherche dans
   `_site/search.json` : les pages des deux langues lisent l'index de la racine, avec des liens corrects.

Deux dossiers de sortie sont nécessaires : deux rendus dans le même dossier s'écrasent, car chaque rendu
nettoie sa sortie (constaté pendant le spike US-37).

Piège : rendre un fichier isolé avec un profil (`quarto render page.qmd --profile en`) laisse dans le cache
`.quarto` des métadonnées de ce profil, et une page peut ressortir dans la mauvaise langue. En cas de doute,
relancer avec `--propre`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE_FR = RACINE / "_site"
SORTIE_EN = RACINE / "_site-en"
ESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


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


def fusionner_recherche() -> None:
    """Ajoute les pages anglaises à l'index de recherche de la racine.

    Les pages des deux langues résolvent « search.json » depuis la racine du site : un seul index sert
    donc les deux, et les liens (« en/… ») restent justes des deux côtés.
    """
    fr, en = SORTIE_FR / "search.json", SORTIE_EN / "search.json"
    if not (fr.is_file() and en.is_file()):
        print("Pas d'index de recherche à fusionner.")
        return
    entrees = json.loads(fr.read_text(encoding="utf-8"))
    connues = {e.get("href") for e in entrees}
    ajoutees = [e for e in json.loads(en.read_text(encoding="utf-8"))
                if e.get("href", "").startswith("en/") and e.get("href") not in connues]
    fr.write_text(json.dumps(entrees + ajoutees, ensure_ascii=False), encoding="utf-8")
    print(f"-> {fr.relative_to(RACINE)} ({len(entrees)} entrées françaises + {len(ajoutees)} anglaises)")


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


def main() -> int:
    if "--propre" in sys.argv[1:]:
        shutil.rmtree(RACINE / ".quarto", ignore_errors=True)
        print("Cache .quarto vidé.")
    rendre("fr")
    rendre("en")
    assembler()
    fusionner_sitemaps()
    fusionner_recherche()
    return 0


if __name__ == "__main__":
    sys.exit(main())
