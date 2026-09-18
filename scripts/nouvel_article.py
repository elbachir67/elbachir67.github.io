#!/usr/bin/env python3
"""Crée un article de blog vide, correctement structuré (US-22).

    python3 scripts/nouvel_article.py "Titre de l'article" [--langue fr|en] [--categories a,b]

Le fichier est créé dans `blog/posts/<date>-<slug>/index.qmd` (ou `en/blog/posts/…`), avec son en-tête et
une trame de sections. Il est marqué `draft: true` : tant que le PO ne retire pas cette ligne, l'article
n'est pas publié — ni page, ni entrée dans la liste, le flux ou le plan du site.

Le script **n'écrit que ce fichier** : il ne commite pas, ne pousse pas, et ne touche à rien d'autre.
Écrire l'article revient au PO.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LONGUEUR_SLUG = 60
MOTS = {
    "fr": {
        "dossier": "blog/posts",
        "description": "TODO(PO): une phrase, qui sert d'extrait dans la liste du blog.",
        "trame": ["## Le point de départ", "## Ce que j'ai fait", "## Ce que j'en retiens"],
        "amorce": "<!-- Écrire l'article ici. La trame ci-dessous est une suggestion : la changer ou la\n"
                  "     supprimer librement. Retirer « draft: true » de l'en-tête publie l'article. -->",
    },
    "en": {
        "dossier": "en/blog/posts",
        "description": "TODO(PO): one sentence, used as the excerpt in the blog list.",
        "trame": ["## The starting point", "## What I did", "## What I take away"],
        "amorce": "<!-- Write the post here. The outline below is a suggestion: change it or remove it.\n"
                  "     Removing « draft: true » from the header publishes the post. -->",
    },
}


def sans_accent(texte: str) -> str:
    return "".join(l for l in unicodedata.normalize("NFD", texte) if unicodedata.category(l) != "Mn")


def slug(titre: str) -> str:
    """« L'hexagone, enfin ! » -> « l-hexagone-enfin » : ni accent, ni caractère spécial."""
    mots = re.findall(r"[a-z0-9]+", sans_accent(titre).lower())
    identifiant = "-".join(mots)
    while len(identifiant) > LONGUEUR_SLUG and "-" in identifiant:
        identifiant = identifiant.rsplit("-", 1)[0]
    return identifiant or "article"


def categories_du_blog(dossier: Path) -> list[str]:
    """Catégories déjà employées : les proposer évite d'en inventer une de plus à chaque article."""
    trouvees: set[str] = set()
    for article in dossier.glob("*/index.qmd"):
        entete = article.read_text(encoding="utf-8").split("---\n")
        if len(entete) < 2:
            continue
        ligne = re.search(r"^categories:\s*\[(.*?)\]", entete[1], re.M)
        if ligne:
            trouvees.update(c.strip() for c in ligne[1].split(",") if c.strip())
    return sorted(trouvees)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("titre", help="titre de l'article, entre guillemets")
    analyseur.add_argument("--langue", choices=("fr", "en"), default="fr")
    analyseur.add_argument("--categories", default="",
                           help="catégories séparées par des virgules (celles du blog sont proposées)")
    analyseur.add_argument("--date", default=dt.date.today().isoformat(),
                           help="date de l'article, AAAA-MM-JJ (aujourd'hui par défaut)")
    args = analyseur.parse_args()

    mots = MOTS[args.langue]
    dossier_blog = RACINE / mots["dossier"]
    dossier = dossier_blog / f"{args.date}-{slug(args.titre)}"
    if dossier.exists():
        print(f"Ce dossier existe déjà : {dossier.relative_to(RACINE)}. Rien n'a été écrit.")
        return 1

    connues = categories_du_blog(dossier_blog)
    demandees = [c.strip() for c in args.categories.split(",") if c.strip()]
    inconnues = [c for c in demandees if c not in connues]
    categories = ", ".join(demandees)
    rappel = (f"# Catégories déjà employées sur le blog : {', '.join(connues)}.\n" if connues else "")

    dossier.mkdir(parents=True)
    page = dossier / "index.qmd"
    page.write_text(
        "---\n"
        f'title: "{args.titre}"\n'
        f'description: "{mots["description"]}"\n'
        f"date: {args.date}\n"
        f"{rappel}"
        f"categories: [{categories}]\n"
        "# Retirer cette ligne publie l'article : c'est au PO de le faire, après relecture.\n"
        "draft: true\n"
        "---\n\n"
        f"{mots['amorce']}\n\n"
        + "\n\n".join(mots["trame"]) + "\n",
        encoding="utf-8")

    print(f"Article créé : {page.relative_to(RACINE)}")
    if not demandees:
        print("Aucune catégorie donnée : en choisir au moins une avant de publier"
              + (f" (déjà employées : {', '.join(connues)})." if connues else "."))
    elif inconnues:
        print(f"Nouvelle(s) catégorie(s) : {', '.join(inconnues)}. "
              "Une catégorie de plus est une entrée de plus dans la colonne du blog.")
    print("Rien n'a été commité ni poussé : l'article attend d'être écrit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
