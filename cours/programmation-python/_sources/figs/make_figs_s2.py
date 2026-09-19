# Figure Séance 2 — panorama des structures (Programmation Python, UCAD)
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

fig, ax = plt.subplots(figsize=(12.0, 6.4))
ax.set_xlim(0, 12); ax.set_ylim(0, 6.6); ax.axis("off")

def cell(x, y, w, h, text, ec, fc, fs=12, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fs, color=tc or DARK, family="monospace")

def title(x, y, t, c):
    ax.text(x, y, t, ha="left", va="center", fontsize=13.5, color=c, fontweight="bold")

# panneaux
def panel(x0, y0, x1, y1, c):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02",
                                fc="white", ec=c, lw=1.4, alpha=1.0))

# ---------- LISTE (haut gauche) ----------
panel(0.3, 3.45, 5.8, 6.15, BLUE)
title(0.55, 5.85, "Liste — ordonnee, modifiable", BLUE)
ax.text(5.55, 5.85, "[ ]", ha="right", fontsize=13, color=BLUE, fontweight="bold", family="monospace")
vals = ["Dakar", "Louga", "Mbour"]
for i, v in enumerate(vals):
    x = 0.7 + i*1.65
    cell(x, 4.25, 1.5, 0.7, v, BLUE, "#EAF2FB", fs=11)
    ax.text(x + 0.75, 5.12, str(i), ha="center", fontsize=11, color=BLUE, fontweight="bold")
ax.text(0.7, 3.75, "acces par indice : villes[0]", fontsize=9.5, color=MUT, style="italic")

# ---------- TUPLE (haut droite) ----------
panel(6.2, 3.45, 11.7, 6.15, ORANGE)
title(6.45, 5.85, "Tuple — fige", ORANGE)
ax.text(11.45, 5.85, "( )", ha="right", fontsize=13, color=ORANGE, fontweight="bold", family="monospace")
for i, v in enumerate(["14.69", "-17.44"]):
    x = 6.7 + i*2.2
    cell(x, 4.25, 2.0, 0.7, v, ORANGE, "#FBF1E6", fs=11)
ax.text(6.7, 3.78, "modification interdite (verrouille)", fontsize=9.5, color=MUT, style="italic")

# ---------- DICTIONNAIRE (bas gauche) ----------
panel(0.3, 0.4, 5.8, 3.1, GREEN)
title(0.55, 2.82, "Dictionnaire — cle vers valeur", GREEN)
ax.text(5.55, 2.82, "{ }", ha="right", fontsize=13, color=GREEN, fontweight="bold", family="monospace")
pairs = [("nom", "Fatou"), ("age", "30")]
for i, (k, v) in enumerate(pairs):
    y = 1.95 - i*0.78
    cell(0.7, y, 1.5, 0.62, k, GREEN, "#EDF7F0", fs=11)
    ax.add_patch(FancyArrowPatch((2.25, y+0.31), (2.95, y+0.31),
                                 arrowstyle="-|>", mutation_scale=12, color=MUT, lw=1.6))
    cell(3.0, y, 1.9, 0.62, v, GREEN, "#EDF7F0", fs=11)
ax.text(0.7, 0.62, "acces par cle : patient['nom']", fontsize=9.5, color=MUT, style="italic")

# ---------- ENSEMBLE (bas droite) ----------
panel(6.2, 0.4, 11.7, 3.1, RED)
title(6.45, 2.82, "Ensemble — sans doublons", RED)
ax.text(11.45, 2.82, "{ }", ha="right", fontsize=13, color=RED, fontweight="bold", family="monospace")
ax.add_patch(FancyBboxPatch((6.7, 0.95), 4.7, 1.45, boxstyle="round,pad=0.03",
                            fc="#FBEDEC", ec=RED, lw=1.4, linestyle="--"))
for i, v in enumerate(["Dakar", "Louga", "Mbour"]):
    x = 6.95 + i*1.55
    cell(x, 1.35, 1.4, 0.62, v, RED, "white", fs=10.5)
ax.text(6.7, 0.62, "pas d'indice ; doublons retires", fontsize=9.5, color=MUT, style="italic")

fig.savefig("figs/f2_structures.pdf", bbox_inches="tight")
fig.savefig("figs/f2_structures.svg", bbox_inches="tight")
fig.savefig("figs/f2_structures.png", bbox_inches="tight", dpi=160)
print("f2_structures ok")
