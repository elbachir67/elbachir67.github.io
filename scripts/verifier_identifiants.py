#!/usr/bin/env python3
"""Échoue si un identifiant apparaît deux fois dans une page rendue (US-59).

    python3 scripts/verifier_identifiants.py            # analyse _site/
    python3 scripts/verifier_identifiants.py chemin/    # analyse un autre dossier

Un `id` doit être unique dans un document : c'est la règle de HTML, et le navigateur s'y fie. Quand
deux éléments le portent, toute référence — `<use href="#…">`, `url(#…)`, une ancre, un `aria-*` —
désigne **le premier**, et les autres sont muets.

C'est ce qui a brouillé les figures des chapitres 1 et 2 du cours de C : `pdftocairo` découpe chaque
lettre en tracé, la définit sous `glyph-0-0`, `glyph-0-1`… et **recommence à zéro pour chaque
figure**. Vingt figures dans une page définissaient vingt fois le même identifiant, et les lettres de
la première s'écrivaient dans toutes les autres. Chaque figure, prise seule, était pourtant valide :
seul l'assemblage était fautif, et aucun contrôle ne regardait l'assemblage.

Ce contrôle-là le regarde, et il ne coûte rien : il lit le HTML produit, compte, et n'a besoin ni de
navigateur ni d'image. Il ne remplace pas la comparaison visuelle — un défaut de rendu sans doublon
lui échapperait — mais il attrape cette famille-ci sans le moindre faux positif.

**Tolérances.** Quarto pose lui-même quelques identifiants en double dans chaque page (ses blocs de
style). Ils sont listés ici, et eux seuls : tout autre doublon fait échouer.

Bibliothèque standard uniquement.
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path

# Identifiants que Quarto répète dans toutes ses pages : ses propres blocs <style>. Ils ne servent à
# aucune référence, et ne viennent pas de nous.
TOLERES = {"quarto-text-highlighting-styles", "quarto-bootstrap", "quarto-html-after-body"}
EXCLUS = {"site_libs"}
# `\bid=` attraperait aussi `data-anchor-id=`, que Quarto pose sur chaque titre : la frontière de mot
# passe après le tiret. Ce qui précède un vrai attribut `id` est un blanc, jamais une lettre ni un
# tiret.
MOTIF = re.compile(r"""(?<![-\w])id=["']([^"']+)["']""")
# Les identifiants d'un bloc <script> ne sont pas des éléments du document : un gabarit y écrit
# souvent du HTML d'exemple.
SCRIPTS = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)


def doublons(page: Path) -> list[tuple[str, int]]:
    """Identifiants portés par plusieurs éléments de la page, du plus répété au moins."""
    html = SCRIPTS.sub(" ", page.read_text(encoding="utf-8", errors="replace"))
    comptes = Counter(MOTIF.findall(html))
    return sorted(((nom, n) for nom, n in comptes.items() if n > 1 and nom not in TOLERES),
                  key=lambda paire: -paire[1])


def main() -> int:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine} (lancer quarto render d'abord).")

    pages = [p for p in sorted(racine.rglob("*.html"))
             if not EXCLUS.intersection(p.relative_to(racine).parts)]
    fautives = 0
    for page in pages:
        repetes = doublons(page)
        if not repetes:
            continue
        fautives += 1
        detail = ", ".join(f"« {nom} » ×{n}" for nom, n in repetes[:5])
        if len(repetes) > 5:
            detail += f", et {len(repetes) - 5} autre(s)"
        message = (f"{len(repetes)} identifiant(s) en double : {detail}. "
                   "Une référence à l'un d'eux désigne le premier élément, et les autres sont muets.")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error file={page},title=Identifiant en double::{message}")
        print(f"{page}: {message}")

    if fautives:
        print(f"ÉCHEC : {fautives} page(s) sur {len(pages)} portent un identifiant en double "
              f"dans {racine}/.")
        return 1
    print(f"OK : aucun identifiant en double dans {len(pages)} page(s) de {racine}/ "
          f"(hors site_libs/, {len(TOLERES)} identifiant(s) de Quarto tolérés).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
