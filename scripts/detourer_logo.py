#!/usr/bin/env python3
"""Détoure le sceau de l'UCAD : le fond blanc devient transparent (charte, US-48).

    python3 scripts/detourer_logo.py _import/ucad_logo.png assets/img/ucad-sceau.png

Le sceau est rond et posé sur un fond blanc, mais il contient **aussi** du blanc — les lances, les
dents de la roue, le motif du bas. Rendre transparent « tout ce qui est blanc » le troueraient. Le
script part donc des bords de l'image et ne rend transparent que le blanc **qui leur est relié** :
l'intérieur du sceau est hors d'atteinte, par construction.

Le bord est ensuite adouci : sans cela, le cercle sort en escalier sur une page claire comme sombre.

Ce script ne sert qu'une fois par emblème ; il est commité pour que le détourage soit rejouable si le
PO fournit un autre fichier. Il demande Pillow et NumPy, déjà présents pour les figures.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

SEUIL_BLANC = 232          # un pixel plus clair que cela, sur les trois canaux, est du fond
ADOUCISSEMENT = 0.6        # rayon du flou appliqué au seul canal alpha, en pixels
COULEURS = 64              # l'emblème n'en a que trois, plus les nuances du bord


def fond_relie_aux_bords(pixels: np.ndarray) -> np.ndarray:
    """Masque du fond : les pixels clairs que l'on atteint depuis un bord, de proche en proche."""
    hauteur, largeur = pixels.shape[:2]
    clair = (pixels[:, :, :3] >= SEUIL_BLANC).all(axis=2)
    fond = np.zeros((hauteur, largeur), dtype=bool)

    file = deque()
    for x in range(largeur):
        file.extend([(0, x), (hauteur - 1, x)])
    for y in range(hauteur):
        file.extend([(y, 0), (y, largeur - 1)])

    while file:
        y, x = file.popleft()
        if fond[y, x] or not clair[y, x]:
            continue
        fond[y, x] = True
        if y > 0:
            file.append((y - 1, x))
        if y < hauteur - 1:
            file.append((y + 1, x))
        if x > 0:
            file.append((y, x - 1))
        if x < largeur - 1:
            file.append((y, x + 1))
    return fond


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.splitlines()[2].strip())
        return 1
    source, cible = Path(sys.argv[1]), Path(sys.argv[2])
    image = Image.open(source).convert("RGBA")
    pixels = np.array(image)

    fond = fond_relie_aux_bords(pixels)
    pixels[fond, 3] = 0
    detouree = Image.fromarray(pixels)

    # Le flou ne touche que l'alpha : les couleurs de l'emblème ne bougent pas.
    rouge, vert, bleu, alpha = detouree.split()
    alpha = alpha.filter(ImageFilter.GaussianBlur(ADOUCISSEMENT))
    detouree = Image.merge("RGBA", (rouge, vert, bleu, alpha))

    # L'emblème n'a qu'une poignée de couleurs : une palette suffit, et divise le poids par six.
    detouree = detouree.quantize(colors=COULEURS, method=Image.Quantize.FASTOCTREE)

    cible.parent.mkdir(parents=True, exist_ok=True)
    detouree.save(cible, optimize=True)
    transparents = int(fond.sum())
    print(f"{cible} : {detouree.width}×{detouree.height}, "
          f"{transparents} pixel(s) de fond rendus transparents "
          f"({round(cible.stat().st_size / 1024)} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
