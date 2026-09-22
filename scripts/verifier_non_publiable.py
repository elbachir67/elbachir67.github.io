#!/usr/bin/env python3
"""Échoue si le site publie ce qui ne doit jamais l'être (US-59).

    python3 scripts/verifier_non_publiable.py            # analyse _site/ **et** le dépôt
    python3 scripts/verifier_non_publiable.py chemin/    # analyse un autre dossier

Trois choses ne doivent jamais paraître sur le site, et rien ne les empêchait d'y arriver :

**Les documents réservés à l'enseignant.** Un guide pédagogique, une grille de correction, un barème
voisinent le CM et les TP dans `_import/` : une seule ligne de commande de différence, et le document
part en ligne pour tout le monde, définitivement.

**Les corrigés, pistes et indications de correction.** Décision du PO : aucun ne paraît sur le site
et aucun ne vit dans le dépôt, sans date ni exception — c'est ce qui remplace la publication datée
d'US-49. Trois « pistes de résolution » et le corrigé d'un devoir surveillé étaient partis en ligne
sous le type `tp`, que leur seul nom de fichier trahissait. Ce contrôle regarde donc **les fichiers
suivis par Git** autant que le site rendu.

**Les termes que le PO ne veut pas voir publiés.** Le sigle d'une filière, par exemple : il date, il
ne dit rien à un lecteur extérieur, et il se recopie de source en source sans que personne le relise.

Le contrôle regarde le **site rendu**, et non les sources : c'est ce qui est publié qui compte, quel
que soit le chemin par lequel il y est arrivé. Il porte sur le nom du fichier et sur le texte des
pages, parce que c'est ainsi que le PO les désigne.

Ce qui devient publiable se retire d'ici ; c'est une décision du PO, et elle se lit dans
l'historique de ce fichier.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# Motifs de noms réservés, en minuscules et sans l'extension. Le nom complet n'est pas exigé : un
# « guide_enseignant_v2.pdf » est le même document.
RESERVES = {
    "guide_enseignant": "guide pédagogique réservé à l'enseignant (cours de C, décision du PO)",
    "bareme": "barème de notation",
    # Un corrigé se reconnaît à son nom, quel que soit le type sous lequel il est déclaré : les
    # trois « pistes de résolution » du cours de C étaient publiées comme des TP.
    "corrige": "corrigé : aucun corrigé ne se publie ni ne vit dans le dépôt (décision du PO)",
    "correction": "document de correction (décision du PO)",
    "pistes": "pistes de résolution : c'est une correction (décision du PO)",
    # Abréviation employée par les fiches d'exercices du cours de ML : dix-huit fichiers
    # `CORR_EXOS_S*.pdf` vivaient dans `_import/` et passaient la liste du PO, qui ne connaissait
    # que « corrige » et « correction ». Le motif est exact, pour ne pas prendre « corrélation ».
    "corr_exos": "corrigé d'exercices (décision du PO)",
    # Les encadrés de correction des sources, nommés par le PO : un fichier qui les porte dans
    # son nom est un corrigé, quel que soit le reste.
    "corrbox": "encadré de correction (décision du PO)",
    "solbox": "encadré de solution (décision du PO)",
    "correctionbox": "encadré de correction (décision du PO)",
    "solution": "solution d'exercice : c'est une correction (décision du PO)",
}
# Termes que le PO ne veut pas voir sur le site, quelle que soit la page. La correction se fait
# **à la source** — le .tex du cours et sa copie dans `_import/` —, puis l'import est rejoué : sans
# cela, le terme revient au prochain import.
TERMES_INTERDITS = {
    "GLSI": "sigle de filière, retiré à la demande du PO : « L3 GLSI » devient « L3 »",
}

# Où un document publié peut apparaître : le fichier lui-même, ou un lien qui y mène.
EXTENSIONS_TEXTE = {".html", ".xml", ".json", ".txt"}
EXCLUS = {"site_libs"}


def normalise(nom: str) -> str:
    """« TD-Ch01_Corrigé.pdf » -> « td_ch01_corrige ».

    La casse, les tirets et les accents ne comptent pas : c'est le mot qui compte, et le PO écrit
    aussi bien « Corrigé » que « CORRIGE » ou « corriges ».
    """
    sans_accents = "".join(c for c in unicodedata.normalize("NFD", Path(nom).stem.lower())
                           if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", sans_accents)


def reserve(nom: str) -> str | None:
    """Raison pour laquelle ce nom de fichier est réservé, ou None.

    Le motif doit **commencer un mot** : « fig_05_resolution_preuve » est une figure, et non une
    solution — sans cette condition, « résolution » faisait sortir du dépôt une figure du cours
    d'Introduction à l'IA. La fin du mot, elle, reste libre : « corriges » et « solutions » sont
    les mêmes documents que « corrige » et « solution ».
    """
    normalise_ = normalise(nom)
    for motif, raison in RESERVES.items():
        if re.search(rf"(?:^|_){re.escape(motif)}", normalise_):
            return raison
    return None


def fichiers_publies(racine: Path) -> list[tuple[Path, str]]:
    """Documents réservés présents dans le site, sous leur nom de fichier."""
    trouves = []
    for fichier in sorted(racine.rglob("*")):
        if not fichier.is_file() or EXCLUS.intersection(fichier.relative_to(racine).parts):
            continue
        raison = reserve(fichier.name)
        if raison:
            trouves.append((fichier, raison))
    return trouves


def fichiers_du_depot() -> list[tuple[Path, str]]:
    """Documents réservés **suivis par Git**, publiés ou non.

    Le site rendu ne suffit pas : un corrigé commité mais non lié reste dans l'historique public
    du dépôt, où n'importe qui le lit. Le contrôle porte donc sur `git ls-files`, qui est la
    définition exacte de « dans le dépôt ». Hors d'un dépôt Git, il ne dit rien plutôt que de
    prétendre avoir vérifié.
    """
    racine = Path(__file__).resolve().parent.parent
    try:
        liste = subprocess.run(["git", "-C", str(racine), "ls-files", "-z"],
                               capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        print("Dépôt Git introuvable : seul le site rendu est vérifié.")
        return []
    trouves = []
    for nom in sorted(filter(None, liste.split("\0"))):
        raison = reserve(Path(nom).name)
        if raison:
            trouves.append((racine / nom, raison))
    return trouves


def liens_vers_reserves(racine: Path) -> list[tuple[Path, str, str]]:
    """Liens d'une page vers un document réservé — même si le fichier, lui, n'a pas été copié."""
    trouves = []
    for fichier in sorted(racine.rglob("*")):
        if (not fichier.is_file() or fichier.suffix not in EXTENSIONS_TEXTE
                or EXCLUS.intersection(fichier.relative_to(racine).parts)):
            continue
        texte = fichier.read_text(encoding="utf-8", errors="replace")
        for cible in re.findall(r'(?:href|src)="([^"]+)"', texte):
            # Seuls les liens vers un **fichier** comptent : la règle porte sur les noms de
            # fichiers. Une ancre interne n'en est pas un, et le cours de C intitule légitimement
            # une section « Solutions pour retourner un tableau ».
            if cible.startswith("#") or not Path(cible.split("?")[0].split("#")[0]).suffix:
                continue
            raison = reserve(Path(cible.split("?")[0].split("#")[0]).name)
            if raison:
                trouves.append((fichier, cible, raison))
    return trouves


def termes_publies(racine: Path) -> list[tuple[Path, int, str, str]]:
    """Termes interdits présents dans le texte d'une page, hors balises."""
    trouves = []
    for fichier in sorted(racine.rglob("*")):
        if (not fichier.is_file() or fichier.suffix not in EXTENSIONS_TEXTE
                or EXCLUS.intersection(fichier.relative_to(racine).parts)):
            continue
        texte = fichier.read_text(encoding="utf-8", errors="replace")
        for terme, raison in TERMES_INTERDITS.items():
            for trouve in re.finditer(rf"\b{re.escape(terme)}\b", texte):
                ligne = texte.count("\n", 0, trouve.start()) + 1
                extrait = " ".join(texte[max(0, trouve.start() - 50):trouve.end() + 30].split())
                trouves.append((fichier, ligne, extrait, raison))
    return trouves


def signaler(chemin: Path, message: str) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={chemin},title=Document réservé::{message}")
    print(f"{chemin}: {message}")


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer quarto render d'abord).")

    fautes = 0
    for fichier, raison in fichiers_du_depot():
        signaler(fichier, f"document réservé versionné : {raison}")
        fautes += 1
    for fichier, raison in fichiers_publies(racine):
        signaler(fichier, f"document réservé publié : {raison}")
        fautes += 1
    for fichier, cible, raison in liens_vers_reserves(racine):
        signaler(fichier, f"lien vers un document réservé — « {cible} » : {raison}")
        fautes += 1
    for fichier, ligne, extrait, raison in termes_publies(racine):
        signaler(fichier, f"ligne {ligne} : terme interdit dans « {extrait} » — {raison}")
        fautes += 1

    if fautes:
        print(f"ÉCHEC : {fautes} élément(s) non publiable(s) dans le dépôt ou dans {racine}/. "
              "Un corrigé, une piste ou une correction se retire du dépôt ; un terme interdit se "
              "corrige à la source (le .tex du cours et sa copie dans _import/), puis l'import "
              "est rejoué.")
        return 1
    print(f"OK : rien de non publiable dans le dépôt ni dans {racine}/ "
          f"({len(RESERVES)} nom(s) de document et {len(TERMES_INTERDITS)} terme(s) surveillés).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
