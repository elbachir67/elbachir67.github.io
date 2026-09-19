#!/usr/bin/env python3
"""Rend le site bilingue : un profil Quarto par langue, puis assemblage (US-36, ADR-0003).

    python3 scripts/rendre.py            # rendu des deux langues
    python3 scripts/rendre.py --propre   # en repartant d'un cache Quarto vide

1. `quarto render --profile fr` produit le site français dans `_site/`.
2. `quarto render --profile en` produit le site anglais dans `_site-en/`.
3. `_site-en/en/` est copié dans `_site/en/`.
4. Les deux plans de site sont fusionnés dans `_site/sitemap.xml`, et chaque séance de cours est imprimée
   en PDF à côté de sa page (US-17).
5. Le flux RSS du blog est annoncé dans l'en-tête de chaque page, dans la langue de la page.
6. Chaque langue garde son index de recherche : le français à la racine, l'anglais dans `_site/en/`, les pages
   anglaises étant rattachées à cette racine. Une recherche ne renvoie donc que des pages de la langue lue.

Deux dossiers de sortie sont nécessaires : deux rendus dans le même dossier s'écrasent, car chaque rendu
nettoie sa sortie (constaté pendant le spike US-37).

Piège : rendre un fichier isolé avec un profil (`quarto render page.qmd --profile en`) laisse dans le cache
`.quarto` des métadonnées de ce profil, et une page peut ressortir dans la mauvaise langue. En cas de doute,
relancer avec `--propre`.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tomllib
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


def annoncer_le_flux() -> None:
    """Annonce le flux RSS du blog dans l'en-tête de chaque page (US-25).

    Quarto ne pose cette balise que sur la page qui porte le listing : un lecteur qui arrive sur l'accueil
    ou sur un cours ne voit pas qu'un flux existe. Chaque page reçoit donc celui de sa langue, et seulement
    si elle n'en a pas déjà un — la page du blog garde le sien, écrit par Quarto.
    """
    flux = {
        "en": '<link rel="alternate" type="application/rss+xml" '
              'title="Blog — El Hadji Bassirou Touré" href="/en/blog/index.xml">',
        "fr": '<link rel="alternate" type="application/rss+xml" '
              'title="Blog — El Hadji Bassirou Touré" href="/blog/index.xml">',
    }
    annoncees = 0
    for page in (p for p in SORTIE_FR.rglob("*.html") if "site_libs" not in p.parts):
        texte = page.read_text(encoding="utf-8")
        if "application/rss+xml" in texte or "</head>" not in texte:
            continue
        langue = "en" if page.relative_to(SORTIE_FR).parts[0] == "en" else "fr"
        page.write_text(texte.replace("</head>", flux[langue] + "\n</head>", 1), encoding="utf-8")
        annoncees += 1
    print(f"-> flux RSS annoncé sur {annoncees} page(s)")


def pdf_des_seances() -> None:
    """Imprime chaque présentation en PDF, à côté de sa page (US-17).

    L'impression est faite par le navigateur, via scripts/generer_pdf.js. Elle demande les paquets Node du
    dépôt (`npm ci`) : quand ils manquent, le rendu continue sans les PDF et le dit, plutôt que d'échouer.
    """
    if not (RACINE / "node_modules" / "playwright-core").is_dir():
        print("PDF des séances ignorés : lancer « npm ci » pour les produire.")
        return
    subprocess.run(["node", str(RACINE / "scripts" / "generer_pdf.js"), str(SORTIE_FR)],
                   cwd=RACINE, check=True)


def corriges_du_jour() -> None:
    """Publie les corrigés dont la date est atteinte, et eux seuls (US-49).

    Un corrigé vit dans `cours/<slug>/_corriges/`, que Quarto ne rend pas : le dossier est invisible du
    site tant que personne ne l'y copie. C'est ici que la date décide — avant elle, le fichier reste
    hors du site, et la page ne porte aucun lien vers lui (le filtre Lua applique la même règle).

    Conséquence à connaître : un corrigé rejoint le site au **premier rendu qui suit sa date**, donc au
    prochain déploiement, et non à minuit.
    """
    aujourdhui = dt.date.today().isoformat()
    publies, attendus = 0, 0
    for manifeste in sorted((RACINE / "cours").glob("*/_sources/import.toml")):
        cours = manifeste.parent.parent
        for chapitre in tomllib.loads(manifeste.read_text(encoding="utf-8")).get("chapitres", []):
            for ressource in chapitre.get("ressources", []):
                if ressource.get("type") != "corrige":
                    continue
                date = ressource.get("date", "")
                if not date or date > aujourdhui:
                    attendus += 1
                    continue
                fichier = cours / ressource["fichier"]
                cible = SORTIE_FR / "cours" / cours.name / "corriges" / fichier.name
                cible.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(fichier, cible)
                publies += 1
    if publies or attendus:
        print(f"-> {publies} corrigé(s) publié(s), {attendus} en attente de leur date")


def main() -> int:
    # Les sorties de Quarto et de Node arrivent au fil de l'eau : sans cela, les messages de ce script
    # seraient affichés après elles, dans le désordre.
    sys.stdout.reconfigure(line_buffering=True)
    if "--propre" in sys.argv[1:]:
        shutil.rmtree(RACINE / ".quarto", ignore_errors=True)
        print("Cache .quarto vidé.")
    rendre("fr")
    rendre("en")
    assembler()
    fusionner_sitemaps()
    index_de_recherche_par_langue()
    zoom_des_slides()
    annoncer_le_flux()
    corriges_du_jour()
    pdf_des_seances()
    return 0


if __name__ == "__main__":
    sys.exit(main())
