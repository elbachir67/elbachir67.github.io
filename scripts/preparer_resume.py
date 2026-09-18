#!/usr/bin/env python3
"""Prépare le brouillon d'un article de blog à partir d'un document (US-21).

    python3 scripts/preparer_resume.py <fichier.tex|.pdf> [--langue fr|en]

C'est la partie mécanique de la commande `/resume` : elle vérifie que le document **peut** être résumé
publiquement, extrait son texte, et crée un brouillon marqué `draft: true` avec la citation de sa source.
La rédaction, elle, appartient à la commande — et au PO, qui relit avant publication.

**Règle des travaux non acceptés (CLAUDE.md §7).** Un article soumis ou en évaluation n'apparaît pas sur le
site, même résumé. Le document est donc rapproché des publications listées dans `publications/sources.toml` :

- publication trouvée, publiée ou « à paraître » → le résumé est permis, et la citation est préremplie ;
- publication trouvée avec un autre statut → **refus** (code 2) ;
- document du dossier `cours/` → permis : ce sont les supports du PO, déjà publiés sur le site ;
- document inconnu → **à confirmer par le PO** (code 3) : le script ne devine pas si un texte est publiable.

Codes de sortie : 0 brouillon prêt · 2 refus · 3 confirmation du PO nécessaire · 1 erreur d'utilisation.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REFUS, A_CONFIRMER = 2, 3
PUBLIABLES = {"publie", "a-paraitre"}
MOTS = {
    "fr": {"dossier": "blog/posts", "source": "Source", "brouillon": "Brouillon",
           "categorie": "recherche", "titre": "TODO: titre de l'article",
           "description": "TODO: une phrase qui donne envie de lire, sans promettre plus que le document."},
    "en": {"dossier": "en/blog/posts", "source": "Source", "brouillon": "Draft",
           "categorie": "research", "titre": "TODO: article title",
           "description": "TODO: one sentence, promising no more than the document does."},
}


def sans_accent(texte: str) -> str:
    return "".join(l for l in unicodedata.normalize("NFD", texte) if unicodedata.category(l) != "Mn")


def normaliser(titre: str) -> str:
    """Titre comparable : sans accent, sans ponctuation, en minuscules."""
    return " ".join(re.findall(r"[a-z0-9]+", sans_accent(titre).lower()))


def identifiant(texte: str) -> str:
    mots = re.findall(r"[a-z0-9]+", sans_accent(texte).lower())
    return "-".join(mots[:6]) or "resume"


def texte_du_document(document: Path) -> str:
    if document.suffix == ".pdf":
        if shutil.which("pdftotext") is None:
            sys.exit("pdftotext introuvable : installer poppler pour résumer un PDF.")
        return subprocess.run(["pdftotext", str(document), "-"],
                              capture_output=True, text=True, check=True).stdout
    return document.read_text(encoding="utf-8", errors="replace")


def titre_du_document(document: Path, texte: str) -> str:
    """Titre annoncé par le document : \\title{…} pour un .tex, première ligne notable pour un PDF."""
    trouve = re.search(r"\\title\{(.+?)\}", texte, re.S)
    if trouve:
        return " ".join(trouve[1].split())
    for ligne in texte.splitlines():
        if len(ligne.strip()) > 15:
            return ligne.strip()
    return document.stem


def publication_correspondante(titre: str, sources: Path) -> dict | None:
    """Publication de sources.toml dont le titre recouvre celui du document."""
    if not sources.is_file():
        return None
    donnees = tomllib.loads(sources.read_text(encoding="utf-8"))
    cible = normaliser(titre)
    for publication in donnees.get("publication", []):
        connu = normaliser(publication.get("titre", ""))
        if connu and (connu in cible or cible in connu):
            return publication
    return None


def citation(publication: dict | None, document: Path, langue: str) -> str:
    """Le brouillon cite toujours d'où il vient : c'est la première chose que le PO vérifie."""
    if publication:
        morceaux = [publication.get("titre", "")]
        for champ in ("evenement", "lieu", "event_year"):
            if publication.get(champ):
                morceaux.append(str(publication[champ]))
        reference = ", ".join(morceaux)
        ancre = f"/publications/#{publication['cle']}"
        if langue == "en":
            return f"This post summarises **{reference}** ([full reference]({ancre}))."
        return f"Cet article résume **{reference}** ([référence complète]({ancre}))."
    chemin = document.relative_to(RACINE) if document.is_relative_to(RACINE) else document.name
    if langue == "en":
        return f"This post summarises the document `{chemin}` of this repository."
    return f"Cet article résume le document `{chemin}` de ce dépôt."


def ecrire_brouillon(document: Path, publication: dict | None, langue: str, titre: str) -> Path:
    mots = MOTS[langue]
    jour = dt.date.today().isoformat()
    dossier = RACINE / mots["dossier"] / f"{jour}-{identifiant(titre)}"
    dossier.mkdir(parents=True, exist_ok=True)
    page = dossier / "index.qmd"
    page.write_text(
        "---\n"
        f'title: "{mots["titre"]}"\n'
        f'description: "{mots["description"]}"\n'
        f"date: {jour}\n"
        f"categories: [{mots['categorie']}]\n"
        "# Retiré par le PO, et par personne d'autre, une fois l'article relu (US-21).\n"
        "draft: true\n"
        "---\n\n"
        f"{citation(publication, document, langue)}\n\n"
        "<!-- Écrire l'article ici, à partir du document seul : aucun chiffre, aucun résultat ni aucune\n"
        "     conclusion qui ne s'y trouve. Ce qui manque reste un TODO(PO), jamais une supposition. -->\n",
        encoding="utf-8")
    return page


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("document", type=Path, help="fichier .tex ou .pdf à résumer")
    analyseur.add_argument("--langue", choices=("fr", "en"), default="fr")
    analyseur.add_argument("--sources", type=Path, default=RACINE / "publications" / "sources.toml",
                           help="liste des publications (par défaut publications/sources.toml)")
    args = analyseur.parse_args()

    if not args.document.is_file():
        print(f"Fichier introuvable : {args.document}")
        return 1

    document = args.document.resolve()
    texte = texte_du_document(document)
    titre = titre_du_document(document, texte)
    publication = publication_correspondante(titre, args.sources)
    print(f"Document : {document.name}\nTitre lu : {titre}")

    if publication:
        statut = publication.get("statut", "publie")
        if statut not in PUBLIABLES:
            print(f"\nREFUS : « {publication['titre']} » a le statut « {statut} » dans "
                  f"{args.sources.relative_to(RACINE) if args.sources.is_relative_to(RACINE) else args.sources}.")
            print("Un travail soumis ou en évaluation n'apparaît pas sur le site, même résumé "
                  "(CLAUDE.md §7, règle « Travaux non acceptés »). Rien n'a été écrit.")
            return REFUS
        print(f"Publication reconnue : {publication['cle']} (statut « {statut} ») — résumé permis.")
    elif document.is_relative_to(RACINE / "cours"):
        print("Support de cours du dépôt : déjà publié sur le site, résumé permis.")
    else:
        print("\nÀ CONFIRMER : ce document ne figure pas dans publications/sources.toml.")
        print("Demander au PO s'il s'agit d'un travail publié ou accepté avant d'en écrire quoi que ce "
              "soit : le script ne devine pas. Rien n'a été écrit.")
        return A_CONFIRMER

    page = ecrire_brouillon(document, publication, args.langue, titre)
    print(f"\nBrouillon : {page.relative_to(RACINE)} (draft: true)")
    print(f"Texte du document : {len(texte.splitlines())} lignes, à lire avant d'écrire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
