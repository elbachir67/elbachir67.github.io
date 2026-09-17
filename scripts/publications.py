#!/usr/bin/env python3
"""Génère la page des publications (US-09).

Deux étapes, rejouables :

1. bib  : publications/sources.toml -> Crossref -> publications/publications.bib
2. page : publications/publications.bib -> publications/index.qmd

    python3 scripts/publications.py          # les deux étapes (accès réseau)
    python3 scripts/publications.py page     # la page seule, depuis le .bib (hors ligne)

Aucune donnée n'est inventée : ce que Crossref ne fournit pas est écrit « TODO(PO): … ».
Exception : une publication acceptée sans DOI (statut « a-paraitre ») est décrite à la main dans
sources.toml ; elle s'affiche « (à paraître) » et le script la complète via Crossref dès que le DOI existe.
Bibliothèque standard uniquement (Python 3.11 ou plus récent, pour tomllib).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import tomllib
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from itertools import groupby
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCES = RACINE / "publications" / "sources.toml"
BIB = RACINE / "publications" / "publications.bib"
PAGE = RACINE / "publications" / "index.qmd"

CROSSREF = "https://api.crossref.org/works"
# Identification demandée par Crossref pour les appels d'API ; aucune adresse personnelle.
AGENT = "site-perso-publications/1.0 (+https://github.com/elbachir67/elbachir67.github.io)"
PAUSE = 1.0  # secondes entre deux appels, par courtoisie envers l'API

# Ordre des champs dans le .bib.
CHAMPS = ["author", "title", "booktitle", "series", "volume", "pages",
          "publisher", "year", "doi", "eventtitle", "eventdate", "venue", "pubstate"]
A_PARAITRE = "a-paraitre"    # statut dans sources.toml
FORTHCOMING = "forthcoming"  # valeur biblatex correspondante (pubstate) dans le .bib

# Clé BibTeX = ancre de la page : minuscules, chiffres et tirets, sans année (voir sources.toml).
FORMAT_CLE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Typographie : un nom d'auteur ou une plage de pages ne se coupe pas en fin de ligne.
INSECABLE = "\u00a0"
SANS_COUPURE = "\u2060"  # word joiner, de part et d'autre du tiret des pages


# --- Outils texte ------------------------------------------------------------------------------

def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def normaliser(texte: str) -> str:
    """Forme de comparaison : minuscules, sans accents ni ponctuation."""
    return re.sub(r"[^a-z0-9]+", " ", sans_accents(texte).lower()).strip()


def normaliser_pages(pages: str | None) -> str:
    return re.sub(r"\s*[-–—]+\s*", "-", pages or "").strip()


def initiales(prenoms: str) -> str:
    """« El Hadji Bassirou » -> « E. H. B. » ; « Jean-Pierre » -> « J.-P. »."""
    mots = []
    for mot in prenoms.replace(".", ". ").split():
        parties = [p for p in mot.split("-") if p]
        mots.append("-".join(p[0] + "." for p in parties))
    return " ".join(mots)


# --- Crossref ----------------------------------------------------------------------------------

def appeler(url: str) -> dict:
    """GET JSON avec reprises sur les erreurs temporaires (429, 5xx, réseau)."""
    for essai in range(4):
        requete = urllib.request.Request(url, headers={"User-Agent": AGENT})
        try:
            with urllib.request.urlopen(requete, timeout=30) as reponse:
                donnees = json.load(reponse)
            time.sleep(PAUSE)
            return donnees
        except urllib.error.HTTPError as erreur:
            if erreur.code == 404:
                raise
            if erreur.code != 429 and erreur.code < 500:
                raise
            derniere = erreur
        except urllib.error.URLError as erreur:
            derniere = erreur
        time.sleep(5 * (essai + 1))
    raise RuntimeError(f"Crossref ne répond pas : {url} ({derniere})")


def chercher(source: dict) -> tuple[dict | None, str]:
    """Retrouve la notice Crossref d'une publication. Renvoie (notice, explication)."""
    parametres = urllib.parse.urlencode({"query.bibliographic": source["titre"], "rows": 10})
    notices = appeler(f"{CROSSREF}?{parametres}")["message"]["items"]
    titre = normaliser(source["titre"])
    # Même titre, ou titre publié qui prolonge celui de la source (sous-titre ajouté à la publication).
    candidates = [
        n for n in notices
        if (t := normaliser((n.get("title") or [""])[0])) == titre or t.startswith(titre + " ")
    ]
    if len(candidates) > 1 and source.get("pages"):
        memes_pages = [n for n in candidates
                       if normaliser_pages(n.get("page")) == normaliser_pages(source["pages"])]
        if memes_pages:
            candidates = memes_pages
    dois = ", ".join(n["DOI"] for n in candidates)
    if len(candidates) == 1:
        return candidates[0], f"trouvée ({dois})"
    if not candidates:
        return None, "introuvable dans Crossref"
    return None, f"plusieurs notices possibles ({dois})"


def titre_des_actes(notice: dict) -> tuple[str | None, str | None]:
    """Renvoie (titre du volume, collection). Pour un chapitre, lit la notice du livre."""
    conteneurs = notice.get("container-title") or []
    collection = conteneurs[0] if len(conteneurs) > 1 else None
    volume = conteneurs[-1] if conteneurs else None
    doi = notice["DOI"]
    if notice.get("type") == "book-chapter" and "_" in doi:
        try:
            livre = appeler(f"{CROSSREF}/{urllib.parse.quote(doi.rsplit('_', 1)[0])}")["message"]
        except urllib.error.HTTPError:
            livre = {}
        if livre.get("type") in {"book", "edited-book", "proceedings"} and livre.get("title"):
            volume = livre["title"][0]
            if livre.get("subtitle"):
                volume += ": " + livre["subtitle"][0]
    return volume, collection


# --- Étape 1 : sources.toml -> publications.bib -------------------------------------------------

def est_le_po(prenoms: str, nom: str, po: dict) -> bool:
    return (normaliser(nom) == normaliser(po["nom"])
            and normaliser(prenoms)[:1] == normaliser(po["prenoms"])[:1])


def verifier_sources(sources: list[dict]) -> None:
    """Clés explicites, au bon format et uniques ; auteurs fournis pour une publication à paraître.
    Vérifié avant tout appel réseau."""
    vues: set[str] = set()
    for source in sources:
        cle = source.get("cle", "")
        if not FORMAT_CLE.fullmatch(cle):
            sys.exit(f"Clé absente ou invalide ({cle!r}) pour « {source['titre']} » : "
                     "minuscules, chiffres et tirets uniquement.")
        if re.search(r"(?:19|20)\d{2}", cle):
            sys.exit(f"Clé avec une année ({cle!r}) : les clés doivent rester stables, sans année.")
        if cle in vues:
            sys.exit(f"Clé en double : {cle}")
        vues.add(cle)
        if source.get("statut") == A_PARAITRE and not source.get("auteurs"):
            sys.exit(f"Publication à paraître sans auteurs ({cle}) : renseigner « auteurs » dans sources.toml.")


def auteur_bib(prenoms: str, nom: str, po: dict) -> str:
    """« Nom, Prénoms » ; le nom du PO est rétabli quand une notice l'abrège ou omet l'accent."""
    if est_le_po(prenoms, nom, po):
        prenoms, nom = po["prenoms"], po["nom"]
    return f"{nom}, {prenoms}" if prenoms else nom


def entree(source: dict, po: dict) -> tuple[dict[str, str], str]:
    notice, explication = chercher(source)
    statut = source.get("statut", "publie")
    champs: dict[str, str] = {}
    if notice is None and statut == A_PARAITRE:
        # Acceptée, sans notice Crossref : description manuelle de sources.toml, sans DOI.
        auteurs = []
        for auteur in source["auteurs"]:  # « Nom, Prénoms »
            nom, _, prenoms = (p.strip() for p in auteur.partition(","))
            auteurs.append(auteur_bib(prenoms, nom, po))
        champs["author"] = " and ".join(auteurs)
        champs["title"] = source["titre"]
        champs["publisher"] = source.get("editeur") or "TODO(PO): éditeur des actes"
        champs["year"] = str(source["event_year"])
        champs["pubstate"] = FORTHCOMING
        explication = f"à paraître : description manuelle ({explication})"
    elif notice is None:
        todo = f"TODO(PO): notice {explication}"
        champs["author"] = todo
        champs["title"] = source["titre"]
        champs["year"] = str(source["event_year"])
        champs["doi"] = todo
    else:
        champs["author"] = (" and ".join(auteur_bib(a.get("given", ""), a.get("family", ""), po)
                                         for a in notice.get("author", []))
                            or "TODO(PO): auteurs absents de la notice Crossref")
        champs["title"] = notice["title"][0]
        volume, collection = titre_des_actes(notice)
        if volume:
            champs["booktitle"] = volume
        if collection:
            champs["series"] = collection
        if notice.get("volume"):
            champs["volume"] = notice["volume"]
        if notice.get("page"):
            champs["pages"] = normaliser_pages(notice["page"]).replace("-", "--")
        if notice.get("publisher"):
            champs["publisher"] = notice["publisher"]
        champs["year"] = str(notice["issued"]["date-parts"][0][0])
        champs["doi"] = notice["DOI"]
        if statut == A_PARAITRE:
            explication += " : DOI disponible, retirer statut = \"a-paraitre\" de sources.toml"
    champs["eventtitle"] = source["evenement"]
    champs["eventdate"] = str(source["event_year"])
    if source.get("lieu"):
        champs["venue"] = source["lieu"]
    if statut not in {"publie", A_PARAITRE}:
        champs["pubstate"] = statut  # écartée de la page
    return champs, explication


def echapper_bib(valeur: str) -> str:
    return re.sub(r"(?<!\\)([&%$#])", r"\\\1", valeur)


def ecrire_bib(entrees: list[tuple[str, dict[str, str]]]) -> str:
    lignes = [
        "% Fichier généré par scripts/publications.py depuis publications/sources.toml et Crossref.",
        "% Ne pas modifier à la main : corriger sources.toml, puis relancer le script (README.md).",
        "",
    ]
    largeur = max(len(c) for c in CHAMPS)
    for cle, champs in entrees:
        lignes.append(f"@inproceedings{{{cle},")
        for champ in CHAMPS:
            if champ in champs:
                valeur = champs[champ] if champ == "doi" else echapper_bib(champs[champ])
                if champ == "title":
                    valeur = "{" + valeur + "}"  # conserve la casse du titre publié
                lignes.append(f"  {champ.ljust(largeur)} = {{{valeur}}},")
        lignes += ["}", ""]
    return "\n".join(lignes)


def etape_bib() -> None:
    config = tomllib.loads(SOURCES.read_text(encoding="utf-8"))
    po, entrees = config["auteur"], []
    verifier_sources(config["publication"])
    for source in config["publication"]:
        champs, explication = entree(source, po)
        print(f"  {source['cle']:32} {explication}")
        entrees.append((source["cle"], champs))
    BIB.write_text(ecrire_bib(entrees), encoding="utf-8")
    print(f"-> {BIB.relative_to(RACINE)} ({len(entrees)} références)")


# --- Étape 2 : publications.bib -> index.qmd ----------------------------------------------------

def lire_bib(texte: str) -> list[tuple[str, dict[str, str]]]:
    """Lecteur BibTeX minimal, pour le format écrit par ecrire_bib (accolades imbriquées)."""
    entrees = []
    for debut in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", texte):
        i, champs = debut.end(), {}
        while True:
            m = re.compile(r"\s*(\w+)\s*=\s*\{").match(texte, i)
            if not m:
                break
            profondeur, j = 1, m.end()
            while profondeur:
                profondeur += {"{": 1, "}": -1}.get(texte[j], 0)
                j += 1
            valeur = texte[m.end():j - 1]
            if valeur.startswith("{") and valeur.endswith("}"):
                valeur = valeur[1:-1]
            champs[m.group(1).lower()] = re.sub(r"\\([&%$#])", r"\1", " ".join(valeur.split()))
            i = re.compile(r"\s*,?").match(texte, j).end()
        entrees.append((debut.group(1), champs))
    return entrees


def echapper_md(texte: str) -> str:
    return re.sub(r"([\\`*_\[\]<>@#|$])", r"\\\1", texte)


def auteurs_md(champ: str, po: dict) -> str:
    if champ.startswith("TODO(PO)"):
        return echapper_md(champ)
    noms = []
    for auteur in champ.split(" and "):
        nom, _, prenoms = (p.strip() for p in auteur.partition(","))
        affiche = INSECABLE.join(echapper_md(f"{initiales(prenoms)} {nom}".strip()).split(" "))
        noms.append(f"**{affiche}**" if est_le_po(prenoms, nom, po) else affiche)
    return ", ".join(noms)


def reference_md(cle: str, c: dict[str, str], po: dict) -> str:
    actes = f"*{echapper_md(c['booktitle'])}*" if c.get("booktitle") else ""
    # Entre parenthèses : la conférence si son sigle n'est pas déjà dans le titre des actes, et la ville.
    evenement = c.get("eventtitle", "")
    sigles = normaliser(evenement.split()[0]).split() if evenement else []
    precisions = []
    if evenement and not any(s in normaliser(c.get("booktitle", "")).split() for s in sigles):
        precisions.append(echapper_md(evenement))
    if c.get("venue"):
        precisions.append(echapper_md(c["venue"]))
    if precisions:
        actes = f"{actes} ({', '.join(precisions)})" if actes else ", ".join(precisions)
    details = [actes] if actes else []
    if c.get("series"):
        details.append(echapper_md(c["series"]))
    if c.get("volume"):
        details.append(f"vol.{INSECABLE}{echapper_md(c['volume'])}")
    if c.get("pages"):
        details.append(f"pp.{INSECABLE}{c['pages'].replace('--', SANS_COUPURE + '–' + SANS_COUPURE)}")
    edition = ", ".join(details) + "." if details else ""
    a_paraitre = c.get("pubstate") == FORTHCOMING
    if a_paraitre:  # année de publication inconnue, pas de DOI
        edition += f" {echapper_md(c['publisher'])} (à paraître)." if c.get("publisher") else " (à paraître)"
    else:
        edition += f" {echapper_md(c['publisher'])}, {c['year']}." if c.get("publisher") else f" {c['year']}."
    lignes = [f"[{echapper_md(c['title'])}]{{.publication-titre}}", auteurs_md(c["author"], po),
              edition.strip()]
    if not a_paraitre:
        doi = c.get("doi", "")
        lignes.append(echapper_md(doi) if doi.startswith("TODO(PO)")
                      else f"DOI [{echapper_md(doi)}](https://doi.org/{doi})")
    return "\n".join([f"::: {{#{cle} .publication}}", "\\\n".join(lignes), ":::"])


def etape_page() -> None:
    po = tomllib.loads(SOURCES.read_text(encoding="utf-8"))["auteur"]
    entrees = lire_bib(BIB.read_text(encoding="utf-8"))
    publiees = [(cle, c) for cle, c in entrees if c.get("pubstate") in {None, FORTHCOMING}]
    # Classement par année de conférence (décision du PO) ; year reste l'année de publication.
    annee_conference = lambda e: e[1].get("eventdate") or e[1]["year"]
    publiees.sort(key=annee_conference, reverse=True)  # tri stable : ordre du .bib dans une année
    lignes = [
        "---",
        'title: "Publications"',
        "# Page générée par scripts/publications.py depuis publications/publications.bib.",
        "# Ne pas modifier à la main : voir la section « Publications » du README.md.",
        "---",
        "",
        "Classées par année de conférence, de la plus récente à la plus ancienne. "
        "Chaque référence publiée renvoie à la version de l'éditeur par son DOI.",
    ]
    for annee, groupe in groupby(publiees, key=annee_conference):
        lignes += ["", f"## {annee} {{#annee-{annee}}}"]
        for cle, champs in groupe:
            lignes += ["", reference_md(cle, champs, po)]
    PAGE.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    ecartees = len(entrees) - len(publiees)
    print(f"-> {PAGE.relative_to(RACINE)} ({len(publiees)} publiées, {ecartees} écartée(s) par statut)")


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analyseur.add_argument("etape", nargs="?", choices=["tout", "bib", "page"], default="tout",
                           help="tout (défaut), bib (Crossref -> .bib) ou page (.bib -> index.qmd)")
    etape = analyseur.parse_args().etape
    if etape in {"tout", "bib"}:
        print("Crossref :")
        etape_bib()
    if etape in {"tout", "page"}:
        etape_page()
    return 0


if __name__ == "__main__":
    sys.exit(main())
