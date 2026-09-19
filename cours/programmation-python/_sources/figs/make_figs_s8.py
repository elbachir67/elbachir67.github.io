# Figures Seance 8 v2 — fil rouge "fruits du marche"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"   # le texte reste du texte (US-51)
from matplotlib.patches import FancyBboxPatch
import numpy as np, os

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
BLUE, DARK, GREEN, ORANGE, MUT = ("#2563AB", "#0F3A5E", "#2E8B57", "#D9822B", "#5A6B75")
os.makedirs("figs", exist_ok=True)

fruit = ["mangue"]*10 + ["banane"]*10 + ["orange"]*10
masse = [301,313,277,283,272,329,321,326,310,312, 137,117,120,122,119,114,126,106,114,115,
         201,223,206,210,196,205,197,177,230,198]
longueur = [10.3,12.1,10.3,10.6,10.8,10.5,11.5,10.9,11.0,10.9, 18.4,19.1,19.1,19.0,18.9,19.3,20.0,19.6,17.1,19.7,
            8.1,8.8,8.1,8.1,8.3,7.3,8.9,8.2,7.6,8.6]
sucre = [14.7,13.7,13.9,14.2,13.2,13.8,14.3,14.6,14.1,13.7, 11.1,11.1,12.1,11.3,12.8,12.3,11.6,11.2,12.2,12.6,
         9.2,8.5,9.1,9.0,9.2,9.2,9.4,8.4,9.0,8.5]

COUL = {"mangue": ORANGE, "banane": "#C9A227", "orange": BLUE}
FRUITS = ["mangue", "banane", "orange"]
def idx(f): return [i for i, x in enumerate(fruit) if x == f]

def plot_hist(ax):
    ax.hist(masse, bins=range(100, 360, 20), color=BLUE, edgecolor="white")
    ax.set_xlabel("masse (g)"); ax.set_ylabel("nombre de fruits")
    ax.set_title("Distribution des masses")

def plot_bar(ax):
    moy = [np.mean([masse[i] for i in idx(f)]) for f in FRUITS]
    ax.bar(FRUITS, moy, color=[COUL[f] for f in FRUITS], edgecolor="white")
    ax.set_ylabel("masse moyenne (g)"); ax.set_title("Masse moyenne par fruit")

def plot_scatter(ax, legend=True):
    for f in FRUITS:
        ii = idx(f)
        ax.scatter([longueur[i] for i in ii], [masse[i] for i in ii],
                   c=COUL[f], label=f, s=46, edgecolor="white", linewidth=0.6)
    ax.set_xlabel("longueur (cm)"); ax.set_ylabel("masse (g)")
    ax.set_title("Masse selon la longueur")
    if legend: ax.legend(fontsize=9, loc="upper right")

for nom, fn in [("f8_hist", plot_hist), ("f8_bar", plot_bar), ("f8_scatter", plot_scatter)]:
    fig, ax = plt.subplots(figsize=(6.4, 4.0)); fn(ax); fig.tight_layout()
    fig.savefig(f"figs/{nom}.pdf", bbox_inches="tight")
    fig.savefig(f"figs/{nom}.svg", bbox_inches="tight")
    fig.savefig(f"figs/{nom}.png", bbox_inches="tight", dpi=150); plt.close(fig)
    print(nom, "ok")

fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.0))
plot_hist(axes[0]); plot_bar(axes[1]); plot_scatter(axes[2]); fig.tight_layout()
fig.savefig("figs/f8_galerie.pdf", bbox_inches="tight")
fig.savefig("figs/f8_galerie.svg", bbox_inches="tight")
fig.savefig("figs/f8_galerie.png", bbox_inches="tight", dpi=150); plt.close(fig)
print("f8_galerie ok")

# ---- schema table -> X / y ----
fig, ax = plt.subplots(figsize=(11.0, 4.0))
ax.set_xlim(0, 11); ax.set_ylim(0, 4.0); ax.axis("off")
def cell(x, y, w, h, t, ec, fc, fs=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004", fc=fc, ec=ec, lw=1.3))
    ax.text(x+w/2, y+h/2, t, ha="center", va="center", fontsize=fs, color=DARK,
            fontweight="bold" if bold else "normal", family="monospace")

head = ["masse", "longueur", "sucre"]
rows = [("301", "10.3", "14.7", "mangue"), ("137", "18.4", "11.1", "banane"),
        ("201", "8.1", "9.2", "orange")]
x0, y0, cw, ch = 1.6, 1.1, 1.35, 0.6
for c, n in enumerate(head):
    cell(x0+c*cw, y0+3*ch, cw, ch, n, BLUE, "#EAF2FB", fs=9, bold=True)
cell(x0+3*cw+0.3, y0+3*ch, 1.6, ch, "fruit", ORANGE, "#FBF1E6", fs=9, bold=True)
for r, row in enumerate(rows):
    y = y0+(2-r)*ch
    for c in range(3):
        cell(x0+c*cw, y, cw, ch, row[c], "#B9C4CE", "white")
    cell(x0+3*cw+0.3, y, 1.6, ch, row[3], "#E0A96D", "#FBF1E6", fs=9)
ax.text(x0+1.5*cw, y0+4*ch+0.12, "X  (les mesures)", ha="center", fontsize=11.5,
        color=BLUE, fontweight="bold")
ax.text(x0+3*cw+1.1, y0+4*ch+0.12, "y  (a predire)", ha="center", fontsize=11.5,
        color=ORANGE, fontweight="bold")
ax.text(x0, 0.45, "Le modele apprend le lien  X  ->  y  :  reconnaitre le fruit a partir de ses mesures.",
        ha="left", fontsize=10, color=MUT, style="italic")
fig.savefig("figs/f8_xy.pdf", bbox_inches="tight")
fig.savefig("figs/f8_xy.svg", bbox_inches="tight")
fig.savefig("figs/f8_xy.png", bbox_inches="tight", dpi=150); plt.close(fig)
print("f8_xy ok")
