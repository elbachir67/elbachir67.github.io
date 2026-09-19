# Figure Seance 7 (pandas) — un DataFrame schematise
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

def box(x, y, w, h, text, ec, fc, fs=10, bold=False, tc=None, mono=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004", fc=fc, ec=ec, lw=1.4))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=tc or DARK, fontweight="bold" if bold else "normal",
            family="monospace" if mono else "sans-serif")

def arrow(p, q, color=MUT, lw=1.8):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw))

# ----- geometrie du tableau -----
cols = ["", "espece", "bec_long", "bec_haut", "aile", "masse"]
wdt  = [0.62, 1.85, 1.15, 1.15, 0.95, 0.95]
xpos = [2.15]
for w in wdt:
    xpos.append(xpos[-1] + w)
rows = [
    ("0", "fuliginosa", "9.1",  "8.0",  "67",  "15"),
    ("1", "fortis",     "13.2", "10.9", "NaN", "22"),
    ("2", "magnirostris","16.1","14.2", "80",  "28"),
    ("3", "fuliginosa", "9.4",  "8.3",  "68",  "16"),
]
ytop, rh = 4.25, 0.62
MASSE = 5          # index de la colonne mise en avant
ROWHL = 2          # ligne mise en avant (masse 28 > 25)

# entetes
for c, name in enumerate(cols):
    fc = "#FBF1E6" if c == MASSE else ("#EAF2FB" if c > 0 else "white")
    ec = ORANGE if c == MASSE else (BLUE if c > 0 else "white")
    box(xpos[c], ytop, wdt[c], rh, name, ec, fc, fs=9.5, bold=True)

# lignes de donnees
for r, row in enumerate(rows):
    y = ytop - (r+1)*rh
    for c, val in enumerate(row):
        if c == 0:                                   # colonne d'index
            box(xpos[c], y, wdt[c], rh, val, MUT, "#F2F4F5", fs=9, bold=True)
        elif c == MASSE:                             # colonne masse (selection)
            box(xpos[c], y, wdt[c], rh, val, ORANGE, "#FBF1E6", fs=9)
        elif r == ROWHL:                             # ligne filtree
            box(xpos[c], y, wdt[c], rh, val, GREEN, "#EDF7F0", fs=9)
        elif val == "NaN":                           # case manquante
            box(xpos[c], y, wdt[c], rh, val, RED, "#FBEDEC", fs=9, tc=RED)
        else:
            box(xpos[c], y, wdt[c], rh, val, "#B9C4CE", "white", fs=9)

xR = xpos[-1]        # bord droit du tableau
yb = ytop - 4*rh     # bas du tableau

# ----- annotations -----
# colonnes nommees (haut)
ax.text((xpos[1]+xR)/2, ytop + rh + 0.28, "colonnes nommees", ha="center",
        fontsize=10.5, color=BLUE, fontweight="bold")
# index (gauche)
ax.text(xpos[0]-0.05, (ytop+yb)/2, "index", ha="right", va="center",
        fontsize=10.5, color=MUT, fontweight="bold", rotation=90)
# selection d'une colonne
arrow((xpos[MASSE]+wdt[MASSE]/2, yb - 0.05), (xpos[MASSE]+wdt[MASSE]/2, yb - 0.6), ORANGE)
ax.text(xR + 0.15, yb - 0.55, "une colonne = Series\ndf[\"masse\"]", ha="left", va="center",
        fontsize=9.5, color=ORANGE, family="monospace")
# filtre = des lignes
arrow((xR + 0.15, ytop - (ROWHL+0.5)*rh), (xR + 0.02, ytop - (ROWHL+0.5)*rh), GREEN)
ax.text(xR + 0.2, ytop - (ROWHL+0.5)*rh, "un filtre garde des lignes\ndf[df[\"masse\"] > 25]",
        ha="left", va="center", fontsize=9.5, color=GREEN, family="monospace")
# NaN : petite legende en haut a gauche (pas de fleche qui traverse)
box(0.45, 4.78, 0.6, 0.42, "NaN", RED, "#FBEDEC", fs=9, tc=RED)
ax.text(1.15, 4.99, "= valeur manquante", ha="left", va="center",
        fontsize=9.5, color=RED, style="italic")

ax.text(2.15, 0.35, "Un DataFrame : des colonnes nommees et un index. On selectionne des colonnes, on filtre des lignes.",
        ha="left", fontsize=9.5, color=MUT, style="italic")

fig.savefig("figs/f7_pandas.pdf", bbox_inches="tight")
fig.savefig("figs/f7_pandas.svg", bbox_inches="tight")
fig.savefig("figs/f7_pandas.png", bbox_inches="tight", dpi=160)
print("f7_pandas ok")
