#!/usr/bin/env python3
"""Vérifie qu'aucune ressource PDF n'est plus ancienne que sa source (US-76).

    python3 scripts/verifier_ressources.py

Chaque cours décrit ses ressources dans `_sources/ressources.toml` (voir
`scripts/compiler_ressources.py`). Le contrôle ne compile rien — la CI n'a pas LaTeX — et vérifie,
pour chaque PDF servi :

- qu'il est décrit par le manifeste de son cours, avec une source présente dans le dépôt ;
- que l'**empreinte** enregistrée est celle de la source telle qu'elle est aujourd'hui. Une source
  modifiée depuis la compilation du PDF change d'empreinte : le PDF servi est alors plus ancien que
  sa source, et le contrôle échoue jusqu'à ce qu'il soit recompilé ;
- qu'une ressource sans empreinte dit pourquoi (`en_attente`) : un PDF que sa source ne produit pas
  encore — elle ne compile pas, ou son texte diverge et attend l'arbitrage du PO. Il est listé, et
  ne fait pas échouer le contrôle : c'est une dette connue, nommée, et non un oubli.

La date de modification d'un fichier ne dit rien dans un dépôt Git, qui ne la conserve pas :
« plus ancienne » se lit donc dans l'empreinte, et non dans une date.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import hashlib
import os
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def signaler(chemin: Path, message: str) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={chemin.relative_to(RACINE)},title=Ressources::{message}")
    print(f"{chemin.relative_to(RACINE)}: {message}")


def main() -> int:
    erreurs, a_jour, en_attente = 0, 0, []
    decrits: set[Path] = set()
    for manifeste in sorted(RACINE.glob("cours/*/_sources/ressources.toml")):
        cours = manifeste.parent.parent
        for entree in tomllib.loads(manifeste.read_text(encoding="utf-8")).get("ressources", []):
            pdf, source = cours / entree["pdf"], cours / entree["source"]
            decrits.add(pdf)
            if not pdf.is_file():
                signaler(manifeste, f"{entree['pdf']} : ressource décrite mais absente du dépôt")
                erreurs += 1
            if not source.is_file():
                signaler(manifeste, f"{entree['source']} : source absente du dépôt")
                erreurs += 1
                continue
            if entree.get("empreinte"):
                if hashlib.sha256(source.read_bytes()).hexdigest() != entree["empreinte"]:
                    signaler(pdf, f"plus ancienne que sa source {entree['source']}, modifiée depuis "
                                  "la compilation : recompiler (scripts/compiler_ressources.py)")
                    erreurs += 1
                else:
                    a_jour += 1
            elif entree.get("en_attente"):
                en_attente.append(f"{pdf.relative_to(RACINE)} : {entree['en_attente']}")
            else:
                signaler(pdf, "ni empreinte ni raison d'attente dans le manifeste")
                erreurs += 1

    for pdf in sorted(RACINE.glob("cours/*/ressources/*.pdf")):
        if pdf not in decrits:
            signaler(pdf, "PDF servi sans source décrite dans _sources/ressources.toml")
            erreurs += 1

    for ligne in en_attente:
        print(f"en attente : {ligne}")
    if erreurs:
        print(f"ÉCHEC : {erreurs} problème(s) dans les ressources PDF.")
        return 1
    print(f"OK : {a_jour} ressource(s) PDF produites par leur source telle qu'elle est, "
          f"{len(en_attente)} en attente, nommée(s) ci-dessus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
