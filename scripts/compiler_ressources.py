#!/usr/bin/env python3
"""Recompile les ressources PDF depuis leurs sources et compare leur texte au PDF servi (US-76).

    python3 scripts/compiler_ressources.py                     # tous les cours : compile et compare
    python3 scripts/compiler_ressources.py programmation-frontend-1
    python3 scripts/compiler_ressources.py --remplacer         # remplace ce dont seule la forme change
    python3 scripts/compiler_ressources.py --remplacer \
        --accepter programmation-frontend-1/lab-2-html-structurant.pdf

Les PDF de ressource étaient commités, jamais recompilés : ce que le dépôt servait était un artefact,
et non le résultat de sa source. US-75 l'a montré en recompilant huit PDF pour en retirer un sigle —
la recompilation a révélé quatre défauts que rien d'autre ne pouvait voir.

Chaque cours décrit ses ressources dans `_sources/ressources.toml` : le PDF servi, sa source, le
moteur, et l'empreinte de la source dont le PDF est le produit. La source vit dans `_sources/`, à côté
des sources des chapitres, et y est compilée : ses figures et ses styles y sont déjà. Le champ
`depuis` nomme le dossier de `_import/` où chercher ce que `_sources/` n'a pas.

- **Moteur** : LuaLaTeX si la source charge `fontspec`, pdflatex sinon. Deux passes au moins, et
  d'autres tant que LaTeX le demande (« Rerun ») : la table des matières n'apparaît qu'à la deuxième
  passe, décale les pages, et ses numéros ne sont justes qu'à la troisième. Cinq passes au plus.
- **Une erreur dans le journal fait échouer la compilation**, même si un PDF sort : LaTeX en mode non
  interactif saute l'erreur et produit quand même un document, amputé.
- **Comparaison** : les lettres et les chiffres du texte extrait des deux PDF (`pdftotext`), dans
  l'ordre. Espaces, ponctuation et typographie (apostrophes, tirets) ne comptent pas : ils varient
  avec les polices de la machine qui compile, sans que le texte change. Les ligatures « ff », « fi »,
  « fl », « ffi », « ffl », et les lettres « œ » et « æ », sont retirées des deux côtés : certains
  PDF ne les exposent pas à l'extraction.
- Le **corps** des pages et leurs **marges** sont comparés à part. Le corps — la page sans ses
  bandes du haut et du bas — l'est dans l'ordre. Les marges — en-têtes et pieds de page — le sont
  par leurs caractères : quand un saut de page se déplace, un en-tête change de place dans le texte
  sans que rien ne change, mais un en-tête dont le texte change est signalé.
- Sur une page, un écart dont les caractères retirés et ajoutés sont les mêmes est un
  réordonnancement de l'extraction — une formule, un tableau, du gras —, et non un texte changé. Un
  bloc retiré d'une page et ajouté à l'identique sur une autre a suivi un saut de page.
- Un écart fait **seulement de chiffres** est une numérotation générée (table des matières, renvoi
  de page) : il est compté à part, et non comme un texte changé.
- Un PDF dont seule la mise en forme change est remplacé avec `--remplacer`. Un PDF dont **le texte**
  change ne l'est jamais sans l'accord du PO, que `--accepter` enregistre nommément.

L'extraction a ses limites : une police dont les glyphes sortent dans le désordre peut produire des
écarts que l'œil ne voit pas. Ils sont rapportés comme les autres, et c'est le PO qui tranche.

La compilation demande LaTeX : elle tourne en local, **jamais en CI**. La CI vérifie seulement,
avec `verifier_ressources.py`, qu'aucune ressource n'est plus ancienne que sa source.

Bibliothèque standard uniquement ; `pdftotext` (poppler) et la distribution LaTeX sont requis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RELANCER = re.compile(r"Rerun to get|Label\(s\) may have changed|rerunfilecheck.*Rerun|"
                      r"Rerun LaTeX", re.I)
FONTSPEC = re.compile(r"^[^%\n]*\\usepackage\s*(?:\[[^\]]*\])?\s*\{[^}]*\bfontspec\b", re.M)


def empreinte(fichier: Path) -> str:
    return hashlib.sha256(fichier.read_bytes()).hexdigest()


def moteur(source: Path) -> str:
    """LuaLaTeX si la source charge fontspec, pdflatex sinon (décision du PO)."""
    return "lualatex" if FONTSPEC.search(source.read_text(encoding="utf-8", errors="replace")) \
        else "pdflatex"


def manifestes(noms: list[str]) -> list[Path]:
    tous = sorted(RACINE.glob("cours/*/_sources/ressources.toml"))
    return [m for m in tous if not noms or m.parent.parent.name in noms]


def compiler(cours: Path, entree: dict, dossier: Path) -> tuple[Path | None, list[str]]:
    """Compile la source dans `dossier`, deux passes. Rend le PDF, ou None et les erreurs."""
    source = cours / entree["source"]
    environnement = dict(os.environ)
    if entree.get("depuis"):
        # « // » : kpathsea cherche aussi dans les sous-dossiers ; le « : » final garde les chemins
        # de la distribution.
        environnement["TEXINPUTS"] = f".:{RACINE / entree['depuis']}//:"
    erreurs: list[str] = []
    for passe in range(1, 6):
        execution = subprocess.run(
            [entree["moteur"], "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={dossier}", source.name],
            cwd=source.parent, env=environnement, capture_output=True, text=True,
            errors="replace", timeout=1200)
        journal = dossier / f"{source.stem}.log"
        lignes = journal.read_text(errors="replace").splitlines() if journal.is_file() else []
        erreurs = [ligne for ligne in lignes if ligne.startswith("!")]
        if execution.returncode != 0 or erreurs:
            return None, erreurs or [f"{entree['moteur']} a échoué (code {execution.returncode})"]
        if passe >= 2 and not RELANCER.search("\n".join(lignes)):
            break
    pdf = dossier / f"{source.stem}.pdf"
    return (pdf, []) if pdf.is_file() else (None, ["aucun PDF produit"])


def cle(ligne: str) -> str:
    return "".join(c for c in re.sub(r"ff[il]|f[fil]|[œŒæÆ]", "", ligne) if c.isalnum())


# Bandes du haut et du bas d'une page, en points : en-tête et pied de page y vivent. 2,3 cm et 2 cm
# laissent le corps du texte entier dans toutes les mises en page des cours.
HAUT, BAS = 65, 57


def extraire(pdf: Path, *zone: str) -> list[str]:
    texte = subprocess.run(["pdftotext", *zone, str(pdf), "-"], capture_output=True, text=True,
                           errors="replace").stdout
    return [unicodedata.normalize("NFKC", page) for page in texte.split("\f")]


def format_page(pdf: Path) -> tuple[int, int]:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    largeur, hauteur = re.search(r"Page size:\s*([\d.]+) x ([\d.]+)", info).groups()
    return round(float(largeur)), round(float(hauteur))


def caracteres(pdf: Path) -> tuple[list[str], list[int]]:
    """Lettres et chiffres du corps des pages, avec la page de chacun (voir l'en-tête)."""
    largeur, hauteur = format_page(pdf)
    corps = extraire(pdf, "-x", "0", "-y", str(HAUT), "-W", str(largeur),
                     "-H", str(hauteur - HAUT - BAS))
    lus, numeros = [], []
    for numero, page in enumerate(corps, 1):
        for ligne in page.splitlines():
            if cle(ligne).isdigit():
                continue
            for caractere in cle(ligne):
                lus.append(caractere)
                numeros.append(numero)
    return lus, numeros


def marges(pdf: Path) -> set[str]:
    """Lignes distinctes des en-têtes et pieds de page, sans les chiffres (numéros de page)."""
    largeur, hauteur = format_page(pdf)
    lignes = set()
    for y, h in ((0, HAUT), (hauteur - BAS, BAS)):
        for page in extraire(pdf, "-x", "0", "-y", str(y), "-W", str(largeur), "-H", str(h)):
            lignes |= {re.sub(r"\d", "", cle(l)) for l in page.splitlines()} - {""}
    return lignes


def ecarts(ancien: Path, nouveau: Path) -> tuple[list[tuple[str, str, str]], int]:
    """Écarts de texte : (page, ancien texte, nouveau texte), réordonnancements écartés."""
    (avant, pages_avant), (apres, pages_apres) = caracteres(ancien), caracteres(nouveau)
    with tempfile.TemporaryDirectory() as dossier:
        # diff compare des lignes : un caractère par ligne, et diff fait le reste, vite.
        gauche, droite = Path(dossier, "avant"), Path(dossier, "apres")
        gauche.write_text("\n".join(avant) + "\n", encoding="utf-8")
        droite.write_text("\n".join(apres) + "\n", encoding="utf-8")
        sortie = subprocess.run(["diff", str(gauche), str(droite)], capture_output=True,
                                text=True).stdout
    morceaux = []
    for trouve in re.finditer(r"^(\d+)(?:,(\d+))?([acd])(\d+)(?:,(\d+))?$", sortie, re.M):
        a1, a2 = int(trouve[1]), int(trouve[2] or trouve[1])
        b1, b2 = int(trouve[4]), int(trouve[5] or trouve[4])
        retire = "".join(avant[a1 - 1:a2]) if trouve[3] != "a" else ""
        ajoute = "".join(apres[b1 - 1:b2]) if trouve[3] != "d" else ""
        page = pages_apres[b1 - 1] if trouve[3] != "d" and b1 <= len(pages_apres) \
            else pages_avant[min(a1, len(pages_avant)) - 1]
        contexte = "".join(avant[max(0, a1 - 30):a1 - 1 if trouve[3] != "a" else a1])
        morceaux.append((page, contexte, retire, ajoute))
    # Une page dont les caractères retirés et ajoutés se compensent n'a fait que réordonner.
    bilan: dict[int, Counter] = {}
    for page, _, retire, ajoute in morceaux:
        if (retire + ajoute).isdigit():
            continue  # une numérotation générée, comptée à part, ne pèse pas dans le bilan
        bilan.setdefault(page, Counter()).update(retire)
        bilan[page].subtract(ajoute)
    reordonnees = {page for page, compte in bilan.items() if not +compte and not -compte}
    # Un bloc déplacé d'une page à l'autre — un en-tête, une ligne de table des matières — est
    # retiré ici et ajouté là, à l'identique.
    retires = Counter(r for _, _, r, a in morceaux if r and not a and len(r) > 3)
    ajoutes = Counter(a for _, _, r, a in morceaux if a and not r and len(a) > 3)
    deplaces = retires & ajoutes
    gardes, numerotation = [], []
    for page, contexte, retire, ajoute in morceaux:
        bloc = retire if not ajoute else ajoute if not retire else ""
        if page in reordonnees or deplaces.get(bloc, 0) > 0:
            continue
        if (retire + ajoute).isdigit():
            numerotation.append(page)
            continue
        gardes.append((str(page), f"…{contexte[-30:]} [{retire}]", f"…{contexte[-30:]} [{ajoute}]"))
    # Les marges se comparent par leurs caractères : une ligne de texte qui affleure la bande du bas
    # s'y coupe autrement d'un PDF à l'autre (« Justi / er » contre « Justifier »), sans changer.
    avant_marges, apres_marges = marges(ancien), marges(nouveau)
    if Counter("".join(avant_marges)) != Counter("".join(apres_marges)):
        perdues, nouvelles = avant_marges - apres_marges, apres_marges - avant_marges
        gardes.append(("marge", f"[{' / '.join(sorted(perdues))}]", f"[{' / '.join(sorted(nouvelles))}]"))
    return gardes, len(numerotation)


def traiter(cours: Path, entree: dict, remplacer: bool, acceptes: set[str],
            garder: Path | None = None) -> dict:
    servi = cours / entree["pdf"]
    resultat = {"cours": cours.name, "pdf": entree["pdf"], "moteur": entree["moteur"]}
    with tempfile.TemporaryDirectory() as dossier:
        pdf, erreurs = compiler(cours, entree, Path(dossier))
        if pdf is None:
            return {**resultat, "etat": "ne compile pas", "erreurs": erreurs[:3]}
        if garder:
            shutil.copy(pdf, garder / f"{cours.name}__{Path(entree['pdf']).name}")
        differences, numerotation = ecarts(servi, pdf)
        resultat["ecarts"], resultat["numerotation"] = differences, numerotation
        if not differences:
            resultat["etat"] = "forme seule" if servi.read_bytes() != pdf.read_bytes() else "identique"
        else:
            resultat["etat"] = "texte divergent"
        accepte = f"{cours.name}/{Path(entree['pdf']).name}" in acceptes
        if remplacer and (not differences or accepte):
            shutil.copy(pdf, servi)
            resultat["remplace"] = True
            resultat["empreinte"] = empreinte(cours / entree["source"])
    return resultat


ENTETE = """# Ressources PDF de ce cours et leurs sources (US-76).
#
# scripts/compiler_ressources.py les recompile en local et compare leur texte au PDF servi ;
# scripts/verifier_ressources.py vérifie en CI qu'aucune ressource n'est plus ancienne que sa source.
#
# - pdf, source : chemins relatifs au dossier du cours ;
# - moteur : lualatex si la source charge fontspec, pdflatex sinon ;
# - depuis : dossier de _import/ où chercher ce que _sources/ n'a pas (en local seulement) ;
# - empreinte : SHA-256 de la source dont le PDF servi est le produit ;
# - en_attente : pourquoi le PDF servi n'est pas encore le produit de sa source.
"""
CLES = ("pdf", "source", "moteur", "depuis", "empreinte", "en_attente")


def ecrire_manifeste(manifeste: Path, entrees: list[dict]) -> None:
    lignes = [ENTETE.rstrip("\n")]
    for entree in entrees:
        lignes += ["", "[[ressources]]"]
        # Une chaîne JSON est une chaîne TOML valide : guillemets et barres obliques échappés.
        lignes += [f"{cle} = {json.dumps(entree[cle], ensure_ascii=False)}" for cle in CLES if entree.get(cle)]
    manifeste.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def mettre_a_jour(manifeste: Path, resultats: list[dict]) -> None:
    """Écrit l'empreinte des sources dont le PDF servi est désormais le produit."""
    remplaces = {r["pdf"]: r["empreinte"] for r in resultats if r.get("remplace")}
    if not remplaces:
        return
    entrees = tomllib.loads(manifeste.read_text(encoding="utf-8"))["ressources"]
    for entree in entrees:
        if entree["pdf"] in remplaces:
            entree["empreinte"] = remplaces[entree["pdf"]]
            entree.pop("en_attente", None)
    ecrire_manifeste(manifeste, entrees)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("cours", nargs="*", help="slugs des cours (par défaut : tous)")
    analyseur.add_argument("--remplacer", action="store_true",
                           help="remplacer les PDF dont seule la forme change")
    analyseur.add_argument("--garder", type=Path,
                           help="dossier où garder une copie des PDF compilés, pour les regarder")
    analyseur.add_argument("--accepter", action="append", default=[],
                           help="cours/fichier.pdf dont l'écart de texte est accepté par le PO (répétable)")
    args = analyseur.parse_args()
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext introuvable : installer poppler.")

    taches = []
    for manifeste in manifestes(args.cours):
        cours = manifeste.parent.parent
        for entree in tomllib.loads(manifeste.read_text(encoding="utf-8")).get("ressources", []):
            attendu = moteur(cours / entree["source"])
            if entree["moteur"] != attendu:
                sys.exit(f"{cours.name}/{entree['pdf']} : moteur {entree['moteur']}, "
                         f"la source exige {attendu}")
            taches.append((manifeste, cours, entree))
    with ThreadPoolExecutor(4) as executeur:
        resultats = list(executeur.map(
            lambda t: traiter(t[1], t[2], args.remplacer, set(args.accepter), args.garder), taches))

    for manifeste in {t[0] for t in taches}:
        mettre_a_jour(manifeste, [r for r in resultats if r["cours"] == manifeste.parent.parent.name])

    for resultat in resultats:
        marque = " (remplacé)" if resultat.get("remplace") else ""
        if resultat.get("numerotation"):
            marque += f" — {resultat['numerotation']} écart(s) de numérotation générée"
        print(f"{resultat['etat']:<16} {resultat['cours']}/{resultat['pdf']} [{resultat['moteur']}]{marque}")
        for erreur in resultat.get("erreurs", []):
            print(f"    {erreur}")
        for page, ancien, nouveau in resultat.get("ecarts", [])[:20]:
            print(f"    p. {page} : « {ancien[:160]} » -> « {nouveau[:160]} »")
        if len(resultat.get("ecarts", [])) > 20:
            print(f"    … {len(resultat['ecarts']) - 20} autre(s) écart(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
