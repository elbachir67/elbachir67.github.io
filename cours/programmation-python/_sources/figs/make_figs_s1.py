# Figure Séance 1 — indexation d'une chaîne (Programmation Python, UCAD)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"   # le texte reste du texte (US-51)
from matplotlib.patches import FancyBboxPatch
import os

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
BLUE, DARK, GREEN, ORANGE, MUT = "#2563AB", "#0F3A5E", "#2E8B57", "#D9822B", "#5A6B75"
os.makedirs("figs", exist_ok=True)

word = "Saint-Louis"
n = len(word)
fig, ax = plt.subplots(figsize=(11.6, 3.7))
ax.set_xlim(-0.6, n + 0.6); ax.set_ylim(0, 3.7); ax.axis("off")

cw = 1.0
for i, ch in enumerate(word):
    x = i
    ax.add_patch(FancyBboxPatch((x + 0.06, 1.5), cw - 0.12, 0.9,
                                boxstyle="round,pad=0.01", fc="#EAF2FB", ec=BLUE, lw=1.6))
    ax.text(x + cw / 2, 1.95, ch, ha="center", va="center", fontsize=17,
            family="monospace", color=DARK, fontweight="bold")
    # index positif
    ax.text(x + cw / 2, 2.72, str(i), ha="center", va="center", fontsize=12,
            color=BLUE, fontweight="bold")
    # index negatif
    ax.text(x + cw / 2, 1.18, str(i - n), ha="center", va="center", fontsize=11,
            color=ORANGE)

ax.text(-0.5, 2.72, "indice", ha="right", va="center", fontsize=10.5, color=BLUE)
ax.text(-0.5, 1.18, "négatif", ha="right", va="center", fontsize=10.5, color=ORANGE)

# crochet de decoupage [0:5] -> "Saint"
ax.annotate("", xy=(5.0, 0.78), xytext=(0.0, 0.78),
            arrowprops=dict(arrowstyle="<->", color=GREEN, lw=2))
ax.text(2.5, 0.45, 'ville[0:5]  vaut  "Saint"   (fin exclue)', ha="center",
        fontsize=11.5, color=GREEN, fontweight="bold")

ax.text(n / 2, 3.42, 'ville = "Saint-Louis"     ville[0] = "S"     ville[-1] = "s"',
        ha="center", fontsize=12.5, color=MUT)

fig.savefig("figs/f1_indexing.pdf", bbox_inches="tight")
fig.savefig("figs/f1_indexing.svg", bbox_inches="tight")
fig.savefig("figs/f1_indexing.png", bbox_inches="tight", dpi=160)
print("f1_indexing ok")
