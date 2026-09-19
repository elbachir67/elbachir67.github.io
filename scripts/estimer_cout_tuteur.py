#!/usr/bin/env python3
"""Estime le coût par question du tuteur, sur la taille réelle des séances (US-26).

    python3 scripts/estimer_cout_tuteur.py            # toutes les séances du dépôt
    python3 scripts/estimer_cout_tuteur.py --plafond 10

Le calcul sert l'ADR-0004 : il rend ses chiffres reproductibles, et servira à nouveau quand le contexte
sera réellement produit (US-28) puis quand les garde-fous seront dimensionnés (US-30).

Hypothèses, toutes discutables et toutes écrites ici plutôt que cachées dans un tableur :

- le contexte d'une séance est le texte de ses slides, sans les shortcodes de figure ni les marqueurs de
  bloc — ce que verra le tuteur ;
- un jeton vaut environ 3,7 caractères en français (4 en anglais, d'après la documentation d'Anthropic) ;
- les modèles postérieurs à Claude 4.6 emploient un tokeniseur qui produit environ 30 % de jetons en plus
  pour le même texte : Sonnet 5 est dans ce cas, Haiku 4.5 non ;
- une session d'étudiant compte cinq questions : la première écrit le cache, les suivantes le lisent ;
- prompt système 500 jetons, question 60, historique 500, réponse 300.

Tarifs au 18/09/2026 (https://platform.claude.com/docs/en/about-claude/pricing), en dollars par million
de jetons. Les mettre à jour ici, et nulle part ailleurs.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CARACTERES_PAR_JETON = 3.7
SYSTEME, QUESTION, HISTORIQUE, SORTIE = 500, 60, 500, 300
QUESTIONS_PAR_SESSION = 5

MODELES = {
    "Haiku 4.5": {"entree": 1.0, "ecriture": 1.25, "lecture": 0.10, "sortie": 5.0, "tokeniseur": 1.0},
    "Sonnet 5": {"entree": 2.0, "ecriture": 2.50, "lecture": 0.20, "sortie": 10.0, "tokeniseur": 1.3},
}


def texte_de_la_seance(seance: Path) -> str:
    """Ce que le tuteur lira : le texte des slides, sans les shortcodes ni les marqueurs de bloc."""
    corps = seance.read_text(encoding="utf-8").split("---\n", 2)[2]
    corps = re.sub(r"\{\{<[^>]*>\}\}", "", corps)
    corps = re.sub(r"^(:::|#\| ).*$", "", corps, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", corps).strip()


def cout(jetons: float, prix: float) -> float:
    return jetons * prix / 1_000_000


def couts_par_question(contexte_jetons: float, modele: dict) -> tuple[float, float, float]:
    """(première question, questions suivantes, moyenne sur une session) en dollars."""
    facteur = modele["tokeniseur"]
    contexte = (contexte_jetons + SYSTEME) * facteur
    premiere = (cout(contexte, modele["ecriture"]) + cout(QUESTION * facteur, modele["entree"])
                + cout(SORTIE * facteur, modele["sortie"]))
    suivante = (cout(contexte, modele["lecture"])
                + cout((QUESTION + HISTORIQUE) * facteur, modele["entree"])
                + cout(SORTIE * facteur, modele["sortie"]))
    session = premiere + (QUESTIONS_PAR_SESSION - 1) * suivante
    return premiere, suivante, session / QUESTIONS_PAR_SESSION


def sans_cache(contexte_jetons: float, modele: dict) -> float:
    facteur = modele["tokeniseur"]
    return (cout((contexte_jetons + SYSTEME + QUESTION + HISTORIQUE) * facteur, modele["entree"])
            + cout(SORTIE * facteur, modele["sortie"]))


def par_recherche_vectorielle(modele: dict, extraits_jetons: float = 1200) -> float:
    """Coût d'une question si l'on n'envoie que des extraits retrouvés, sans cache."""
    facteur = modele["tokeniseur"]
    return (cout((extraits_jetons + SYSTEME + QUESTION + HISTORIQUE) * facteur, modele["entree"])
            + cout(SORTIE * facteur, modele["sortie"]))


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--plafond", type=float, default=10.0,
                           help="plafond mensuel en dollars, pour le nombre de questions (10 par défaut)")
    args = analyseur.parse_args()

    seances = sorted(RACINE.glob("cours/*/chapitres/*.qmd"))
    if not seances:
        print("Aucune séance trouvée sous cours/*/chapitres/.")
        return 1

    print("Taille des séances")
    tailles = {}
    for seance in seances:
        texte = texte_de_la_seance(seance)
        jetons = len(texte) / CARACTERES_PAR_JETON
        tailles[seance.stem] = jetons
        print(f"  {seance.stem:<28} {len(texte):>6} caractères  ≈ {jetons:>6.0f} jetons")

    plus_longue = max(tailles, key=tailles.get)
    print(f"\nCoût par question, sur la séance la plus longue ({plus_longue})")
    moyennes = {}
    for nom, modele in MODELES.items():
        premiere, suivante, moyenne = couts_par_question(tailles[plus_longue], modele)
        moyennes[nom] = moyenne
        print(f"  {nom:<11} 1re question {premiere * 100:>6.3f} ¢ · suivantes {suivante * 100:>6.3f} ¢ "
              f"· moyenne {moyenne * 100:>6.3f} ¢")
        print(f"  {'':<11} sans mise en cache : {sans_cache(tailles[plus_longue], modele) * 100:>6.3f} ¢ "
              f"· par recherche vectorielle : {par_recherche_vectorielle(modele) * 100:>6.3f} ¢")

    print(f"\nCe qu'achète un plafond de {args.plafond:.0f} $ par mois")
    for nom, moyenne in moyennes.items():
        print(f"  {nom:<11} {int(args.plafond / moyenne):>6} questions, "
              f"soit {int(args.plafond / moyenne / 30):>4} par jour en moyenne")

    print("\nCe qu'une promotion consomme en un mois")
    for etudiants in (20, 40, 80):
        questions = etudiants * 10
        print(f"  {etudiants:>3} étudiants × 10 questions = {questions:>4} questions → "
              + " · ".join(f"{nom} {questions * moyenne:.2f} $" for nom, moyenne in moyennes.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
