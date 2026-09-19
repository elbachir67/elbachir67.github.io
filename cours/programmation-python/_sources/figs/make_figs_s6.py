# Figure Seance 6 (morphometrie pinsons) — vectorisation + axis
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"   # le texte reste du texte (US-51)
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
BLUE, DARK, GREEN, ORANGE, RED, MUT = ("#2563AB", "#0F3A5E", "#2E8B57",
                                       "#D9822B", "#C0392B", "#5A6B75")
os.makedirs("figs", exist_ok=True)

fig, ax = plt.subplots(figsize=(12.0, 5.6))
ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis("off")

def cell(x, y, w, h, text, ec, fc, fs=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008", fc=fc, ec=ec, lw=1.5))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=DARK, family="monospace")

def arrow(p, q, color=MUT, lw=2.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=15, color=color, lw=lw))

def panel(x0, y0, x1, y1, c):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02",
                                fc="white", ec=c, lw=1.3))

# ==================== PANNEAU A : VECTORISATION (masses) ====================
panel(0.3, 0.4, 5.9, 5.25, BLUE)
ax.text(0.55, 4.95, "La vectorisation", ha="left", fontsize=13.5, color=BLUE, fontweight="bold")
ax.text(0.55, 4.55, "masse (g)", ha="left", fontsize=9.5, color=MUT, style="italic")

haut = [15, 16, 21, 22, 28, 27]
bas  = [17, 18, 23, 24, 30, 29]
for i, v in enumerate(haut):
    x = 0.55 + i*0.9
    cell(x, 3.35, 0.78, 0.68, str(v), BLUE, "#EAF2FB")
    cell(x, 1.45, 0.78, 0.68, str(bas[i]), GREEN, "#EDF7F0")
    arrow((x + 0.39, 3.3), (x + 0.39, 2.18), MUT, lw=1.5)

ax.text(5.6, 2.72, "+ 2", ha="right", fontsize=14, color=ORANGE, fontweight="bold")
ax.text(0.55, 0.75, "une seule operation agit sur chaque masse, sans boucle",
        ha="left", fontsize=9, color=MUT, style="italic")

# ==================== PANNEAU B : AXIS (matrice 6x4) ====================
panel(6.1, 0.4, 11.7, 5.25, ORANGE)
ax.text(6.35, 4.95, "L'argument  axis", ha="left", fontsize=13.5, color=ORANGE, fontweight="bold")

entetes = ["bec_l", "bec_h", "aile", "masse"]
grille = [[9.1, 8.0, 67, 15],
          [9.4, 8.3, 68, 16],
          [12.8, 10.5, 74, 21],
          [13.2, 10.9, 75, 22],
          [16.1, 14.2, 80, 28],
          [15.7, 13.8, 79, 27]]

x0, y0, cw, ch = 8.05, 1.15, 0.83, 0.5
# entetes de colonnes
for c in range(4):
    ax.text(x0 + c*cw + cw/2, y0 + 6*ch + 0.18, entetes[c], ha="center", fontsize=8, color=MUT)
# grille (ligne 0 en haut)
for r in range(6):
    for c in range(4):
        v = grille[r][c]
        txt = f"{v:.1f}" if isinstance(v, float) else str(v)
        cell(x0 + c*cw, y0 + (5-r)*ch, cw-0.06, ch-0.06, txt, DARK, "#EFF3F7", fs=8)

# axis=1 (par specimen) : fleche vers la droite, en haut
arrow((x0 - 0.05, y0 + 6*ch + 0.55), (x0 + 4*cw - 0.1, y0 + 6*ch + 0.55), GREEN, lw=2.0)
ax.text(x0 + 2*cw, y0 + 6*ch + 0.78, "axis=1  (par specimen)", ha="center", fontsize=9, color=GREEN)

# axis=0 (par mesure) : fleche vers le bas, a gauche
arrow((x0 - 0.35, y0 + 6*ch - 0.05), (x0 - 0.35, y0 + 0.05), BLUE, lw=2.0)
ax.text(x0 - 0.62, y0 + 3*ch, "axis=0  (par mesure)", ha="center", fontsize=9,
        color=BLUE, rotation=90, va="center")

ax.text(6.35, 0.72, "axis=0 : par mesure (colonne)   ;   axis=1 : par specimen (ligne)",
        ha="left", fontsize=8.5, color=MUT, style="italic")

fig.savefig("figs/f6_numpy.pdf", bbox_inches="tight")
fig.savefig("figs/f6_numpy.svg", bbox_inches="tight")
fig.savefig("figs/f6_numpy.png", bbox_inches="tight", dpi=160)
print("f6_numpy (pinsons) ok")
