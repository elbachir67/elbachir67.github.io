# Figure Séance 4 — anatomie d'un appel de fonction (Programmation Python, UCAD)
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

fig, ax = plt.subplots(figsize=(12.0, 5.0))
ax.set_xlim(0, 12); ax.set_ylim(0, 5.0); ax.axis("off")

def box(x, y, w, h, ec, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                fc=fc, ec=ec, lw=1.8))

def arr(p, q, color=MUT, lw=2.2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=17,
                                 color=color, lw=lw))

# ---------------- Arguments (gauche) ----------------
box(0.4, 2.1, 2.4, 1.5, BLUE, "#EAF2FB")
ax.text(1.6, 3.25, "Arguments", ha="center", fontsize=12.5, color=BLUE, fontweight="bold")
ax.text(1.6, 2.62, "moyenne(12, 16)", ha="center", fontsize=13, family="monospace", color=DARK)

# ---------------- Fonction (centre) ----------------
box(3.7, 1.35, 4.7, 2.95, GREEN, "#F2FBF5")
ax.text(6.05, 3.92, "La fonction", ha="center", fontsize=12.5, color=GREEN, fontweight="bold")
ax.text(3.95, 3.28, "def moyenne(a, b):", ha="left", fontsize=13.5, family="monospace",
        color=DARK)
ax.text(4.45, 2.62, "return (a + b) / 2", ha="left", fontsize=13.5, family="monospace",
        color=DARK)
# slots parametres
ax.text(3.95, 1.85, "a = 12", ha="left", fontsize=11.5, family="monospace", color=BLUE)
ax.text(6.0, 1.85, "b = 16", ha="left", fontsize=11.5, family="monospace", color=BLUE)

# ---------------- Valeur renvoyee (droite) ----------------
box(9.35, 2.1, 2.3, 1.5, ORANGE, "#FBF1E6")
ax.text(10.5, 3.25, "Valeur renvoyee", ha="center", fontsize=12, color=ORANGE, fontweight="bold")
ax.text(10.5, 2.6, "14.0", ha="center", fontsize=16, family="monospace",
        color=DARK, fontweight="bold")

# ---------------- fleches ----------------
arr((2.85, 2.85), (3.65, 2.85), BLUE)
ax.text(3.25, 3.08, "remplissent\na et b", ha="center", fontsize=9, color=BLUE)
arr((8.45, 2.85), (9.3, 2.85), ORANGE)
ax.text(8.9, 3.12, "return", ha="center", fontsize=10, color=ORANGE, fontweight="bold")

ax.text(6.0, 0.55, "Les arguments (12, 16) remplissent les parametres (a, b) ; "
                   "return renvoie 14.0, reutilisable dans un calcul.",
        ha="center", fontsize=11.5, color=MUT, style="italic")

fig.savefig("figs/f4_fonction.pdf", bbox_inches="tight")
fig.savefig("figs/f4_fonction.svg", bbox_inches="tight")
fig.savefig("figs/f4_fonction.png", bbox_inches="tight", dpi=160)
print("f4_fonction ok")
