#!/usr/bin/env python3
"""Échoue si le site publie ce qui ne doit jamais l'être (US-59).

    python3 scripts/verifier_non_publiable.py            # analyse _site/
    python3 scripts/verifier_non_publiable.py chemin/    # analyse un autre dossier

Deux choses ne doivent jamais paraître sur le site, et rien ne les empêchait d'y arriver :

**Les documents réservés à l'enseignant.** Un guide pédagogique, une grille de correction, un barème
voisinent le CM et les TP dans `_import/` : une seule ligne de commande de différence, et le document
part en ligne pour tout le monde, définitivement.

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
import sys
from pathlib import Path

# Motifs de noms réservés, en minuscules et sans l'extension. Le nom complet n'est pas exigé : un
# « guide_enseignant_v2.pdf » est le même document.
RESERVES = {
    "guide_enseignant": "guide pédagogique réservé à l'enseignant (cours de C, décision du PO)",
    "grille_correction": "grille de correction",
    "bareme": "barème de notation",
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
    """« Guide-Enseignant v2.pdf » -> « guide_enseignant_v2 » : la casse et les tirets ne comptent pas."""
    return re.sub(r"[^a-z0-9]+", "_", Path(nom).stem.lower())


def fichiers_publies(racine: Path) -> list[tuple[Path, str]]:
    """Documents réservés présents dans le site, sous leur nom de fichier."""
    trouves = []
    for fichier in sorted(racine.rglob("*")):
        if not fichier.is_file() or EXCLUS.intersection(fichier.relative_to(racine).parts):
            continue
        nom = normalise(fichier.name)
        for motif, raison in RESERVES.items():
            if motif in nom:
                trouves.append((fichier, raison))
                break
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
            nom = normalise(Path(cible).name)
            for motif, raison in RESERVES.items():
                if motif in nom:
                    trouves.append((fichier, cible, raison))
                    break
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
        print(f"ÉCHEC : {fautes} élément(s) non publiable(s) dans {racine}/. "
              "Corriger à la source (le .tex du cours et sa copie dans _import/), "
              "puis rejouer l'import.")
        return 1
    print(f"OK : rien de non publiable dans {racine}/ "
          f"({len(RESERVES)} nom(s) de document et {len(TERMES_INTERDITS)} terme(s) surveillés).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
