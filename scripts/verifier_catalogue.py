#!/usr/bin/env python3
"""Échoue si le catalogue des cours décrit deux fois la même chose (US-66).

    python3 scripts/verifier_catalogue.py            # analyse le dépôt

Le catalogue a deux sources, et elles ne doivent pas se recouper (US-11, US-14) :

* `enseignement/cours.yml` — les cours qui n'ont pas encore de page ;
* `cours/<slug>/cours.yml` — les cours publiés, qui décrivent eux-mêmes leurs métadonnées.

`enseignement/cours.lua` refusait déjà qu'un cours publié figure dans `cours.yml`, mais il comparait
les titres **caractère pour caractère**. Trois doublons ont traversé ce contrôle, et un étudiant a
donc longtemps vu deux cartes pour un seul cours :

* « Structures de Données **&** Algorithmes Avancés » contre « Structures de Données **et**
  Algorithmes Avancés » — une esperluette d'écart ;
* « Introduction à l'IA **: logique mathématique et calcul formel** » contre « Introduction à
  l'IA » — un sous-titre d'écart ;
* « IPDL 1 » et « IPDL 2 » — deux entrées pour un cours proposé à deux niveaux, que rien ne
  rapprochait.

Ce contrôle compare donc des titres **normalisés** — sans accents, sans casse, l'esperluette lue
« et », la ponctuation effacée — et tient un titre pour un doublon d'un autre quand il l'égale une
fois son sous-titre retiré. Le troisième cas ne se reconnaît pas à un titre : il se voit à la
lecture, et c'est au PO de le trancher (US-66, dernier critère).

Bibliothèque standard uniquement, comme les autres contrôles du dépôt : le YAML est lu à
l'expression régulière, faute de dépendance YAML.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CATALOGUE = RACINE / "enseignement" / "cours.yml"
COURS = RACINE / "cours"

MOTIF_TITRE_LISTE = re.compile(r'^\s*-\s+titre:\s*"([^"]+)"', re.M)
MOTIF_TITRE_SEUL = re.compile(r'^titre:\s*"([^"]+)"', re.M)


def normaliser(titre: str) -> str:
    """Ramène un titre à ce qui le distingue : les lettres et les chiffres, dans l'ordre.

    L'esperluette devient « et » avant l'effacement de la ponctuation, sans quoi « A & B » et
    « A et B » ne se rejoindraient pas.
    """
    sans_accent = "".join(c for c in unicodedata.normalize("NFD", titre.lower())
                          if unicodedata.category(c) != "Mn")
    sans_accent = sans_accent.replace("&", " et ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", sans_accent).split())


def sans_sous_titre(titre_normalise: str, titre_brut: str) -> str:
    """Le titre privé de ce qui suit son premier deux-points, s'il en a un."""
    if ":" not in titre_brut:
        return titre_normalise
    return normaliser(titre_brut.split(":", 1)[0])


def entrees() -> list[tuple[str, str]]:
    """Les (titre, origine) du catalogue, dans l'ordre où un lecteur les rencontre."""
    trouvees: list[tuple[str, str]] = []
    if CATALOGUE.exists():
        for titre in MOTIF_TITRE_LISTE.findall(CATALOGUE.read_text(encoding="utf-8")):
            trouvees.append((titre, "enseignement/cours.yml"))
    for fichier in sorted(COURS.glob("*/cours.yml")):
        titres = MOTIF_TITRE_SEUL.findall(fichier.read_text(encoding="utf-8"))
        if not titres:
            trouvees.append(("", str(fichier.relative_to(RACINE))))
            continue
        trouvees.append((titres[0], str(fichier.relative_to(RACINE))))
    return trouvees


def verifier() -> list[str]:
    fautes: list[str] = []
    toutes = entrees()

    for titre, origine in toutes:
        if not titre.strip():
            fautes.append(f"{origine} : aucun titre.")

    # Deux entrées pour un même titre. Le message nomme les deux origines : le lecteur doit savoir
    # laquelle retirer, et c'est toujours celle de enseignement/cours.yml quand l'autre est publiée.
    par_titre: dict[str, list[tuple[str, str]]] = {}
    for titre, origine in toutes:
        if titre.strip():
            par_titre.setdefault(normaliser(titre), []).append((titre, origine))
    for cle, groupe in sorted(par_titre.items()):
        if len(groupe) > 1:
            details = " ; ".join(f"« {t} » ({o})" for t, o in groupe)
            fautes.append(f"Deux entrées du catalogue pour un même cours : {details}.")

    # Un titre qui en égale un autre une fois son sous-titre retiré : le cas « Introduction à
    # l'IA : … » contre « Introduction à l'IA ».
    connus = {normaliser(t): (t, o) for t, o in toutes if t.strip()}
    for titre, origine in toutes:
        if not titre.strip() or ":" not in titre:
            continue
        tronque = sans_sous_titre(normaliser(titre), titre)
        if tronque and tronque != normaliser(titre) and tronque in connus:
            autre_titre, autre_origine = connus[tronque]
            fautes.append(
                f"« {titre} » ({origine}) et « {autre_titre} » ({autre_origine}) nomment le même "
                f"cours : le sous-titre est le seul écart.")

    return fautes


def main() -> int:
    if not CATALOGUE.exists():
        print(f"ERREUR : {CATALOGUE.relative_to(RACINE)} est introuvable.", file=sys.stderr)
        return 1
    fautes = verifier()
    if fautes:
        for faute in fautes:
            print(f"ERREUR : {faute}", file=sys.stderr)
        print(f"\n{len(fautes)} doublon(s) dans le catalogue des cours.", file=sys.stderr)
        return 1
    print(f"OK : {len(entrees())} cours au catalogue, aucun doublon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
