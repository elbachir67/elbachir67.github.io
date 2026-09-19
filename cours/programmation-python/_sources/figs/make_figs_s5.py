# Figure Seance 5 — heritage + polymorphisme (Programmation Python, UCAD)
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

fig, ax = plt.subplots(figsize=(12.0, 6.0))
ax.set_xlim(0, 12); ax.set_ylim(0, 6.2); ax.axis("off")

def box(x, y, w, h, ec, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015", fc=fc, ec=ec, lw=1.8))

def arrow(p, q, color=MUT, lw=2.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=color, lw=lw))

def panel(x0, y0, x1, y1, c):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02",
                                fc="white", ec=c, lw=1.3))

# ==================== PANNEAU A : HERITAGE ====================
panel(0.3, 0.4, 5.85, 6.05, BLUE)
ax.text(0.55, 5.75, "L'heritage", ha="left", fontsize=13.5, color=BLUE, fontweight="bold")

# Parent
box(1.15, 3.75, 3.8, 1.35, BLUE, "#EAF2FB")
ax.text(3.05, 4.82, "CompteBancaire", ha="center", fontsize=12.5, color=DARK, fontweight="bold", family="monospace")
ax.text(1.35, 4.34, "attributs : titulaire, solde", ha="left", fontsize=9, color=MUT)
ax.text(1.35, 4.02, "methodes : depot, retrait,", ha="left", fontsize=9, color=MUT)
ax.text(1.35, 3.78, "                 __str__, description", ha="left", fontsize=9, color=MUT)

# Enfant
box(1.15, 0.95, 3.8, 1.55, GREEN, "#EDF7F0")
ax.text(3.05, 2.22, "CompteEpargne", ha="center", fontsize=12.5, color=DARK, fontweight="bold", family="monospace")
ax.text(1.35, 1.78, "herite de tout ci-dessus", ha="left", fontsize=9, color=MUT, style="italic")
ax.text(1.35, 1.48, "ajoute : taux, ajouter_interets", ha="left", fontsize=9, color=GREEN)
ax.text(1.35, 1.18, "surcharge : description", ha="left", fontsize=9, color=ORANGE)

# fleche enfant -> parent
arrow((3.05, 2.5), (3.05, 3.72), MUT)
ax.text(3.25, 3.12, "est un", ha="left", fontsize=9.5, color=MUT, style="italic")

# ==================== PANNEAU B : POLYMORPHISME ====================
panel(6.15, 0.4, 11.7, 6.05, ORANGE)
ax.text(6.4, 5.75, "Le polymorphisme", ha="left", fontsize=13.5, color=ORANGE, fontweight="bold")
ax.text(6.4, 5.35, "un meme appel  .description()", ha="left", fontsize=10.5, color=MUT, family="monospace")

# objet 1
box(6.55, 3.7, 2.5, 0.95, BLUE, "#EAF2FB")
ax.text(7.8, 4.32, "CompteBancaire", ha="center", fontsize=9.5, color=DARK, fontweight="bold", family="monospace")
ax.text(7.8, 3.95, "titulaire Astou", ha="center", fontsize=9, color=MUT)
arrow((9.1, 4.17), (9.95, 4.17), BLUE)
box(10.0, 3.78, 1.5, 0.78, DARK, "#E2EBF4")
ax.text(10.75, 4.17, "compte\ncourant", ha="center", fontsize=9.5, color=DARK)

# objet 2
box(6.55, 1.5, 2.5, 0.95, GREEN, "#EDF7F0")
ax.text(7.8, 2.12, "CompteEpargne", ha="center", fontsize=9.5, color=DARK, fontweight="bold", family="monospace")
ax.text(7.8, 1.75, "titulaire Bineta", ha="center", fontsize=9, color=MUT)
arrow((9.1, 1.97), (9.95, 1.97), GREEN)
box(10.0, 1.55, 1.5, 0.85, DARK, "#E2EBF4")
ax.text(10.75, 1.97, "compte\nepargne\na 0.05", ha="center", fontsize=9, color=DARK)

ax.text(6.4, 0.7, "Python choisit la version selon le type reel de l'objet.",
        ha="left", fontsize=9.5, color=MUT, style="italic")

fig.savefig("figs/f5_objet.pdf", bbox_inches="tight")
fig.savefig("figs/f5_objet.svg", bbox_inches="tight")
fig.savefig("figs/f5_objet.png", bbox_inches="tight", dpi=160)
print("f5_objet ok")
