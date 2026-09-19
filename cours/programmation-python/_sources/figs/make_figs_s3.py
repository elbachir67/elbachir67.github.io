# Figure Séance 3 — controle du flux (Programmation Python, UCAD)
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

fig, ax = plt.subplots(figsize=(12.0, 6.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 6.3); ax.axis("off")

def box(x, y, w, h, text, ec, fc, fs=11, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                fc=fc, ec=ec, lw=1.7))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fs, color=tc or DARK)

def arr(p, q, color=MUT, lw=1.9, style="-|>", cs=None):
    kw = dict(arrowstyle=style, mutation_scale=15, color=color, lw=lw)
    if cs: kw["connectionstyle"] = cs
    ax.add_patch(FancyArrowPatch(p, q, **kw))

def panel(x0, y0, x1, y1, c):
    ax.add_patch(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle="round,pad=0.02",
                                fc="white", ec=c, lw=1.3))

# ============================ PANNEAU A : DECIDER ============================
panel(0.3, 0.4, 5.85, 6.1, BLUE)
ax.text(0.55, 5.8, "Decider  —  if / elif / else", ha="left", fontsize=13.5,
        color=BLUE, fontweight="bold")

# condition 1
box(0.65, 4.55, 2.5, 0.72, "condition 1 ?", ORANGE, "#FBF1E6", fs=11)
box(3.9, 4.55, 1.6, 0.72, "bloc 1", BLUE, "#EAF2FB", fs=11)
arr((3.15, 4.91), (3.9, 4.91), ORANGE)
ax.text(3.5, 5.08, "oui", ha="center", fontsize=9, color=ORANGE)

# condition 2
box(0.65, 3.15, 2.5, 0.72, "condition 2 ?", ORANGE, "#FBF1E6", fs=11)
box(3.9, 3.15, 1.6, 0.72, "bloc 2", BLUE, "#EAF2FB", fs=11)
arr((1.9, 4.55), (1.9, 3.87), MUT)
ax.text(2.1, 4.21, "non", ha="left", fontsize=9, color=MUT)
arr((3.15, 3.51), (3.9, 3.51), ORANGE)
ax.text(3.5, 3.68, "oui", ha="center", fontsize=9, color=ORANGE)

# else
box(0.65, 1.75, 2.5, 0.72, "else", MUT, "#F2F4F5", fs=11)
box(3.9, 1.75, 1.6, 0.72, "bloc 3", BLUE, "#EAF2FB", fs=11)
arr((1.9, 3.15), (1.9, 2.47), MUT)
ax.text(2.1, 2.81, "non", ha="left", fontsize=9, color=MUT)
arr((3.15, 2.11), (3.9, 2.11), MUT)

ax.text(0.65, 1.05, "le 1er test vrai gagne ;\nsinon, le bloc else",
        fontsize=9.5, color=MUT, style="italic", va="center")

# ============================ PANNEAU B : REPETER ===========================
panel(6.15, 0.4, 11.7, 6.1, GREEN)
ax.text(6.4, 5.8, "Repeter  —  for / while", ha="left", fontsize=13.5,
        color=GREEN, fontweight="bold")

box(7.7, 4.85, 2.4, 0.66, "debut", MUT, "#F2F4F5", fs=11)
box(7.55, 3.35, 2.7, 0.8, "test :\nencore un element ?", ORANGE, "#FBF1E6", fs=10)
box(7.75, 1.7, 2.3, 0.72, "corps de\nla boucle", GREEN, "#EDF7F0", fs=10.5)
box(7.85, 0.62, 2.1, 0.6, "sortie", DARK, "#E2EBF4", fs=11)

arr((8.9, 4.85), (8.9, 4.15), MUT)                 # debut -> test
arr((8.9, 3.35), (8.9, 2.42), GREEN)               # test -> corps
ax.text(9.05, 2.9, "vrai", ha="left", fontsize=9, color=GREEN)
# retour corps -> test (boucle)
arr((10.05, 2.06), (10.25, 3.6), MUT, cs="arc3,rad=-0.6")
ax.text(10.75, 2.85, "tour\nsuivant", ha="center", fontsize=8.5, color=MUT)
# test -> sortie (faux)
arr((7.55, 3.6), (7.05, 3.6), ORANGE)
arr((7.05, 3.6), (7.05, 0.92), ORANGE)
arr((7.05, 0.92), (7.85, 0.92), ORANGE)
ax.text(6.75, 2.2, "faux", ha="center", fontsize=9, color=ORANGE, rotation=90)

fig.savefig("figs/f3_flux.pdf", bbox_inches="tight")
fig.savefig("figs/f3_flux.svg", bbox_inches="tight")
fig.savefig("figs/f3_flux.png", bbox_inches="tight", dpi=160)
print("f3_flux ok")
