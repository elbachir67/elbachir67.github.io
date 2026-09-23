#!/usr/bin/env python3
"""Échoue si le site promet quelque chose qu'il ne sert pas (US-65).

    python3 scripts/verifier_publication.py            # analyse _site/
    python3 scripts/verifier_publication.py chemin/    # analyse un autre dossier rendu

Le cours de Structures de Données est parti en ligne **sans page d'accueil** : son dossier n'avait
pas d'`index.qmd`, le seul fichier que les quatre autres cours possédaient. La carte du catalogue
menait à un 404, et le TP de mise en place, commité mais référencé par aucune page, n'a jamais été
copié dans `_site/`. Aucun contrôle ne l'a vu : ils regardent tous les **chapitres**, et celui des
liens, confié à lychee, ne teste que les liens **externes**.

Trois promesses, donc, et trois vérifications :

1. **Un dossier de `cours/` promet une page de cours.** Il doit porter un `index.qmd`, et cette
   page doit exister dans le site rendu.
2. **Un lien interne promet une page.** Tous les `href` et `src` du site qui ne sortent pas du
   domaine sont suivis : le fichier visé doit exister, un dossier valant son `index.html`.
3. **Une ressource déclarée au manifeste promet un fichier.** Chaque `fichier` de `cours.yml` et de
   `_sources/import.toml` doit être servi dans `_site/`.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

RACINE = Path(__file__).resolve().parent.parent
EXCLUS = {"site_libs"}
# Les liens qui sortent du site : lychee s'en charge, et un `mailto:` n'est pas un fichier.
SCHEMAS_EXTERNES = {"http", "https", "mailto", "tel", "data", "javascript", "ftp", "about"}
MOTIF_LIEN = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"')
# `fichier: "ressources/tp-1.pdf"` dans cours.yml. Le YAML est lu à l'expression régulière, comme
# le fait déjà verifier_conversion.py : le dépôt n'a pas de dépendance YAML.
MOTIF_FICHIER_YAML = re.compile(r'fichier:\s*"([^"]+)"')


def pages_html(site: Path) -> list[Path]:
    return sorted(page for page in site.rglob("*.html")
                  if not EXCLUS.intersection(page.relative_to(site).parts))


def cours_sans_page(site: Path) -> list[tuple[str, str]]:
    """Un dossier de cours doit porter un `index.qmd`, et sa page doit être rendue."""
    dossier_cours = RACINE / "cours"
    if not dossier_cours.is_dir():
        return []
    ecarts = []
    for cours in sorted(dossier_cours.iterdir()):
        if not cours.is_dir() or cours.name.startswith("_"):
            continue
        if not (cours / "index.qmd").is_file():
            ecarts.append((f"cours/{cours.name}/",
                           "aucun index.qmd : le cours n'a pas de page d'accueil, et la carte du "
                           "catalogue mène à un 404"))
        elif not (site / "cours" / cours.name / "index.html").is_file():
            ecarts.append((f"cours/{cours.name}/index.qmd",
                           "page non rendue : vérifier que le dossier n'est pas exclu du rendu"))
    return ecarts


def cible_du_lien(page: Path, site: Path, lien: str) -> Path | None:
    """Fichier visé par un lien interne, ou None si le lien ne vise pas le site."""
    decoupe = urlsplit(lien)
    if decoupe.scheme.lower() in SCHEMAS_EXTERNES or lien.startswith("//"):
        return None
    chemin = unquote(decoupe.path)
    if not chemin:            # « #ancre » ou « ?requête » : la page elle-même
        return None
    base = site if chemin.startswith("/") else page.parent
    cible = (base / chemin.lstrip("/")).resolve()
    # Un lien qui sort du site rendu n'est pas à nous : ne rien en dire plutôt que de se tromper.
    if not cible.is_relative_to(site.resolve()):
        return None
    return cible / "index.html" if chemin.endswith("/") or cible.is_dir() else cible


def liens_casses(site: Path) -> list[tuple[str, str]]:
    """Tout lien interne doit mener à un fichier servi."""
    ecarts = []
    for page in pages_html(site):
        vus = set()
        for lien in MOTIF_LIEN.findall(page.read_text(encoding="utf-8", errors="ignore")):
            if lien in vus:
                continue
            vus.add(lien)
            cible = cible_du_lien(page, site, lien)
            if cible is not None and not cible.is_file():
                ecarts.append((str(page.relative_to(site)), f"lien mort vers « {lien} »"))
    return ecarts


def ressources_declarees(cours: Path) -> set[str]:
    """Fichiers promis par le manifeste et par la fiche du cours, relatifs au dossier du cours."""
    promis: set[str] = set()
    manifeste = cours / "_sources" / "import.toml"
    if manifeste.is_file():
        charge = tomllib.loads(manifeste.read_text(encoding="utf-8"))
        promis |= {ressource["fichier"]
                   for chapitre in charge.get("chapitres", [])
                   for ressource in chapitre.get("ressources", [])
                   if "fichier" in ressource}
    fiche = cours / "cours.yml"
    if fiche.is_file():
        promis |= set(MOTIF_FICHIER_YAML.findall(fiche.read_text(encoding="utf-8")))
    return promis


def ressources_non_servies(site: Path) -> list[tuple[str, str]]:
    """Une ressource déclarée doit être servie : Quarto ne copie que ce qu'une page référence."""
    dossier_cours = RACINE / "cours"
    if not dossier_cours.is_dir():
        return []
    ecarts = []
    for cours in sorted(dossier_cours.iterdir()):
        if not cours.is_dir() or cours.name.startswith("_"):
            continue
        for fichier in sorted(ressources_declarees(cours)):
            if not (site / "cours" / cours.name / fichier).is_file():
                ecarts.append((f"cours/{cours.name}/{fichier}",
                               "déclarée au manifeste et absente du site : aucune page ne la "
                               "référence, Quarto ne l'a donc pas copiée"))
    return ecarts


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not site.is_dir():
        print(f"Dossier introuvable : {site} (lancer python3 scripts/rendre.py d'abord).")
        return 1

    ecarts = cours_sans_page(site) + ressources_non_servies(site) + liens_casses(site)
    for quoi, raison in ecarts:
        print(f"{quoi} : {raison}")

    if ecarts:
        print(f"\nÉCHEC : {len(ecarts)} promesse(s) que le site ne tient pas.")
        return 1
    pages = pages_html(site)
    cours = [c for c in sorted((RACINE / "cours").glob("*")) if c.is_dir()]
    promises = sum(len(ressources_declarees(c)) for c in cours)
    print(f"OK : {len(cours)} cours avec leur page, {promises} ressource(s) déclarée(s) servie(s), "
          f"et aucun lien interne mort dans {len(pages)} page(s) de {site}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
