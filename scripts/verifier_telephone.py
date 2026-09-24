#!/usr/bin/env python3
"""Échoue si un numéro de téléphone apparaît dans le site rendu (US-10, CLAUDE.md §7).

    python3 scripts/verifier_telephone.py            # analyse _site/
    python3 scripts/verifier_telephone.py chemin/    # analyse un autre dossier

Motifs recherchés :
- indicatif du Sénégal : +221 ou 00221 ;
- numéro de 9 chiffres consécutifs (771234567) ;
- numéro sénégalais écrit par groupes (77 123 45 67, 33.821.00.00, 70-123-45-67).

Fichiers analysés : pages et données (.html, .xml, .json, .txt), texte des PDF extrait avec pdftotext
(paquet poppler), et **le texte des figures** (US-66). site_libs/ est exclu : ce sont des bibliothèques
tierces copiées par Quarto, où des nombres sans rapport (valeurs CSS, tracés de police) déclenchent de
faux positifs.

**Le texte d'une figure, et pourquoi il demande deux chemins.** Une figure du site est un SVG, et deux
outils les produisent. `dvisvgm`, qui compile les schémas TikZ, garde le texte comme `<text>` : il se
lit. `pdftocairo`, qui convertit les figures livrées en PDF, découpe chaque lettre en tracé et n'écrit
que des `<use xlink:href="#glyph-0-12">` : **le SVG ne contient plus un seul mot lisible**. La figure de
chaînage de la séance 3 de Structures de Données affiche cinq numéros de téléphone, et ni ce contrôle,
ni un lecteur d'écran, ni une recherche dans la page ne les voyaient.

Pour ces figures-là, le contrôle remonte au **PDF d'origine**, commité à côté du SVG dans
`_sources/figs/`, et en extrait le texte. C'est le même angle mort que celui des textes alternatifs,
traité de la même façon : regarder ce que la figure montre, et non ce que le fichier déclare.

La tolérance des blocs de code **ne s'applique pas aux figures** : un numéro dessiné dans une figure est
affiché au lecteur, il n'est pas un exemple d'API.

**Exception, décidée par le PO au Sprint 3 : les blocs de code des cours.** Un exemple d'API peut contenir
un numéro fictif (« "771112233" » dans une requête de commande). Un numéro qui n'apparaît **que** dans des
blocs de code est donc toléré — partout ailleurs, y compris dans la même page hors du code, dans le PDF de
la séance ou dans l'index de recherche, il fait échouer le contrôle.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

MOTIFS = {
    "indicatif +221": re.compile(r"(?<![\w+])\+\s*221"),
    # Ni chiffre ni point avant : « y="1205.002214" », dans un SVG, contient « 00221 ».
    "indicatif 00221": re.compile(r"(?<![\d.])00\s*221"),
    # Ni lettre ni chiffre autour : exclut les empreintes hexadécimales des noms de fichiers
    # (bootstrap-cba6febe789600312bd9….min.css), qui changent à chaque modification du CSS.
    "9 chiffres consécutifs": re.compile(r"(?<![\w.])\d{9}(?!\w)"),
    "numéro par groupes": re.compile(r"(?<![\d/.\-])(?:7[05678]|3[03])[ .\-]\d{3}[ .\-]\d{2}[ .\-]\d{2}(?!\d)"),
}
# Un littéral binaire n'est pas un numéro : « 10111010\u2082 » ressort de pdftotext en « 101110102 »,
# neuf chiffres d'affilée. Aucun numéro sénégalais ne commence par 0 ou 1, et aucun ne s'écrit avec
# les seuls chiffres 0 et 1 : le chapitre 1 du cours de C en produisait neuf faux positifs.
BINAIRE = re.compile(r"^[01]{8}2?$")
EXTENSIONS_TEXTE = {".html", ".xml", ".json", ".txt"}
MOTIF_TEXTE_SVG = re.compile(r"<text\b[^>]*>(.*?)</text>", re.S)
EXCLUS = {"site_libs"}
# Blocs de code d'une page : <pre> englobe le code coloré de Quarto, <code> les extraits en ligne.
MOTIF_CODE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>", re.S)
MOTIF_BALISES = re.compile(r"<[^>]+>")


def numeros_du_code(racine: Path) -> set[str]:
    """Numéros qui n'existent que dans les blocs de code des pages (exception du PO, Sprint 3)."""
    tolerés = set()
    for fichier in sorted(racine.rglob("*.html")):
        if EXCLUS.intersection(fichier.relative_to(racine).parts):
            continue
        html = fichier.read_text(encoding="utf-8", errors="replace")
        for bloc in MOTIF_CODE.findall(html):
            texte = MOTIF_BALISES.sub("", bloc)
            for motif in MOTIFS.values():
                tolerés.update(m.group(0) for m in motif.finditer(texte))
    return tolerés


def hors_code(html: str) -> str:
    """Page sans ses blocs de code : le reste doit rester vierge de tout numéro."""
    return MOTIF_CODE.sub(" ", html)


def texte_du_pdf(fichier: Path) -> str:
    if shutil.which("pdftotext") is None:
        sys.exit(f"pdftotext introuvable : impossible de vérifier {fichier} (installer poppler).")
    resultat = subprocess.run(["pdftotext", str(fichier), "-"], capture_output=True, text=True, check=True)
    return resultat.stdout


def texte_du_svg(fichier: Path) -> str:
    """Ce qu'une figure affiche : son `<text>`, ou le texte de son PDF d'origine."""
    contenu = fichier.read_text(encoding="utf-8", errors="replace")
    mots = " ".join(MOTIF_BALISES.sub("", bloc) for bloc in MOTIF_TEXTE_SVG.findall(contenu))
    if mots.strip():
        return mots
    # SVG sans un mot lisible : il vient de `pdftocairo`, qui a découpé les lettres en tracés. Le
    # texte se lit dans le PDF commité à côté, dans `_sources/figs/`.
    if fichier.parent.name == "figures":
        pdf = fichier.parent.parent / "_sources" / "figs" / f"{fichier.stem}.pdf"
        if pdf.is_file():
            return texte_du_pdf(pdf)
    return ""


def figures_du_depot() -> list[Path]:
    """Figures publiées par un cours, lues depuis le dépôt : `_site/` n'en garde que le SVG."""
    dossier = RACINE / "cours"
    return sorted(dossier.glob("*/figures/*.svg")) if dossier.is_dir() else []


def fichiers_a_analyser(racine: Path):
    for fichier in sorted(racine.rglob("*")):
        if not fichier.is_file() or EXCLUS.intersection(fichier.relative_to(racine).parts):
            continue
        if fichier.suffix == ".pdf":
            yield fichier, texte_du_pdf(fichier)
        elif fichier.suffix == ".svg":
            yield fichier, texte_du_svg(fichier)
        elif fichier.suffix in EXTENSIONS_TEXTE:
            yield fichier, fichier.read_text(encoding="utf-8", errors="replace")
    # Les figures incorporées par `{{< svg >}}` n'existent pas comme fichier dans `_site/` : leur
    # contenu est écrit dans la page, glyphes compris. On les lit donc dans le dépôt.
    for figure in figures_du_depot():
        yield figure, texte_du_svg(figure)


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer quarto render d'abord).")
    tolerés = numeros_du_code(racine)
    trouves, analyses = 0, 0
    for fichier, texte in fichiers_a_analyser(racine):
        analyses += 1
        if fichier.suffix == ".html":
            # Dans une page, la tolérance se lit sur place : on retire les blocs de code et le reste est
            # vérifié sans exception. Un numéro écrit en clair dans le texte échoue, même s'il figure
            # aussi dans un exemple de code ailleurs.
            texte, tolerance = hors_code(texte), set()
        else:
            # PDF et index de recherche : le texte a perdu la structure du code. Les numéros vus dans les
            # blocs de code des pages y sont donc tolérés, et eux seuls.
            tolerance = tolerés
        if fichier.suffix == ".svg":
            # Un numéro dessiné dans une figure est affiché au lecteur : aucune tolérance.
            tolerance = set()
        for nom, motif in MOTIFS.items():
            for m in motif.finditer(texte):
                if m.group(0) in tolerance or BINAIRE.match(m.group(0)):
                    continue
                trouves += 1
                ligne = texte.count("\n", 0, m.start()) + 1
                extrait = " ".join(texte[max(0, m.start() - 40):m.end() + 20].split())
                message = f"{nom} : « {m.group(0)} » dans « {extrait} »"
                if os.environ.get("GITHUB_ACTIONS"):
                    print(f"::error file={fichier},line={ligne},title=Numéro de téléphone::{message}")
                print(f"{fichier}:{ligne}: {message}")
    if trouves:
        print(f"ÉCHEC : {trouves} numéro(s) de téléphone possible(s) dans {racine}/.")
        return 1
    exception = f", {len(tolerés)} toléré(s) dans des blocs de code" if tolerés else ""
    print(f"OK : aucun numéro de téléphone dans {analyses} fichier(s) de {racine}/ "
          f"(hors site_libs/{exception}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
