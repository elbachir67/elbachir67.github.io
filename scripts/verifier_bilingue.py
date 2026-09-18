#!/usr/bin/env python3
"""Échoue si le site bilingue est incomplet ou incohérent (US-36).

    python3 scripts/verifier_bilingue.py            # analyse _site/
    python3 scripts/verifier_bilingue.py chemin/    # analyse un autre dossier

Vérifie, pour le périmètre bilingue (tout sauf les dossiers hors périmètre) :
- chaque page française a son équivalent anglais sous `en/`, et réciproquement, en tenant compte des
  dossiers dont le nom change de langue (`recherche` / `research`, `enseignement` / `teaching`) ;
- les pages monolingues (cours, articles de blog) n'ont ni équivalent exigé ni `hreflang` ;
- chaque page porte les trois balises `hreflang` : `fr`, `en` et `x-default` ;
- les deux versions d'une page annoncent les mêmes adresses (`hreflang` réciproques) ;
- `x-default` pointe vers la version française.

Les pages hors périmètre (les cours, monolingues par décision du PO) ne sont pas appariées et ne
doivent pas porter de `hreflang`.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Chemins monolingues, exclus de l'appariement : les cours restent en français (décision PO du Sprint 3),
# et un article de blog n'est pas forcément traduit (US-25). Le blog lui-même, lui, existe dans les deux
# langues : seul ce qu'il y a sous posts/ sort du périmètre.
HORS_PERIMETRE = ("cours/", "blog/posts/")
# Dossiers dont le nom change d'une langue à l'autre (décision PO : /en/research/, /en/teaching/).
# La même table figure dans assets/lua/hreflang.lua : si les deux divergent, l'appariement ou la
# réciprocité des hreflang échoue ici.
VERS_EN = {"recherche": "research", "enseignement": "teaching"}
VERS_FR = {en: fr for fr, en in VERS_EN.items()}
MOTIF_HREFLANG = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')


def pages(racine: Path) -> list[Path]:
    return sorted(p for p in racine.rglob("*.html")
                  if "site_libs" not in p.relative_to(racine).parts)


def traduire(chemin: str, correspondances: dict[str, str]) -> str:
    """Traduit le premier segment d'un chemin, les autres étant identiques dans les deux langues."""
    premier, separateur, reste = chemin.partition("/")
    return correspondances.get(premier, premier) + separateur + reste


def hreflangs(page: Path) -> dict[str, str]:
    return dict(MOTIF_HREFLANG.findall(page.read_text(encoding="utf-8")))


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer scripts/rendre.py d'abord).")
    erreurs: list[tuple[str, str]] = []

    def erreur(page, message):
        erreurs.append((str(page), message))

    francaises, anglaises = {}, {}
    for page in pages(racine):
        relatif = page.relative_to(racine)
        parts = relatif.parts
        if parts[0] == "en":
            chemin = traduire("/".join(parts[1:]), VERS_FR)
            if not chemin.startswith(HORS_PERIMETRE):
                anglaises[chemin] = page
        elif not "/".join(parts).startswith(HORS_PERIMETRE):
            francaises["/".join(parts)] = page

    for chemin in sorted(set(francaises) | set(anglaises)):
        fr, en = francaises.get(chemin), anglaises.get(chemin)
        if fr is None:
            erreur(en, f"page anglaise sans équivalent français attendu à {chemin}")
            continue
        if en is None:
            erreur(fr, f"page française sans équivalent anglais attendu à en/{traduire(chemin, VERS_EN)}")
            continue
        liens = {"fr": hreflangs(fr), "en": hreflangs(en)}
        for langue, page in (("fr", fr), ("en", en)):
            manquantes = [b for b in ("fr", "en", "x-default") if b not in liens[langue]]
            if manquantes:
                erreur(page, f"balise(s) hreflang absente(s) : {', '.join(manquantes)}")
        if not any(erreurs) or (liens["fr"] and liens["en"]):
            for balise in ("fr", "en"):
                gauche, droite = liens["fr"].get(balise), liens["en"].get(balise)
                if gauche and droite and gauche != droite:
                    erreur(fr, f"hreflang {balise} asymétrique : {gauche} côté français, "
                               f"{droite} côté anglais")
            for langue, page in (("fr", fr), ("en", en)):
                defaut, vers_fr = liens[langue].get("x-default"), liens[langue].get("fr")
                if defaut and vers_fr and defaut != vers_fr:
                    erreur(page, f"x-default ({defaut}) devrait pointer vers la version française ({vers_fr})")

    for page in pages(racine):
        relatif = "/".join(page.relative_to(racine).parts)
        relatif = relatif[3:] if relatif.startswith("en/") else relatif
        if relatif.startswith(HORS_PERIMETRE) and hreflangs(page):
            erreur(page, "page hors périmètre bilingue : elle ne doit pas porter de hreflang")

    for fichier, message in erreurs:
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error file={fichier},title=Site bilingue::{message}")
        print(f"{fichier}: {message}")
    if erreurs:
        print(f"ÉCHEC : {len(erreurs)} problème(s) de cohérence bilingue dans {racine}/.")
        return 1
    print(f"OK : {len(francaises)} page(s) française(s) et {len(anglaises)} anglaise(s) appariées, "
          f"hreflang réciproques.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
