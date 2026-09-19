# Figures Seance 8 — les trois schemas de la partie "pourquoi et comment lire un graphique".
#
# Ecrit faute de retrouver le script d'origine : les trois figures etaient citees par SLIDES_S8.tex
# sans exister nulle part. Leur contenu ne sort pas de nulle part — il suit les legendes du .tex et
# les slides qui les commentent (paniers A et B, anatomie d'un graphique, trois questions).
#
# Meme style que les autres scripts du cours : memes couleurs, DejaVu Sans, sorties PDF et SVG.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"   # le texte reste du texte (US-51)
from matplotlib.patches import FancyArrowPatch
import numpy as np, os

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
BLUE, DARK, GREEN, ORANGE, MUT = ("#2563AB", "#0F3A5E", "#2E8B57", "#D9822B", "#5A6B75")
os.makedirs("figs", exist_ok=True)


def save(fig, nom):
    fig.savefig(f"figs/{nom}.pdf", bbox_inches="tight")
    fig.savefig(f"figs/{nom}.svg", bbox_inches="tight")
    plt.close(fig)
    print(nom, "ok")


# ---- f8_meme_moyenne : deux paniers, meme moyenne, compositions opposees ----
# Panier A : dix fruits autour de 200 g. Panier B : des legers et des lourds, aucun a 200 g.
panier_a = [196, 198, 199, 200, 200, 201, 202, 203, 199, 202]
panier_b = [118, 121, 124, 119, 122, 278, 281, 284, 279, 274]
tranches = np.arange(100, 321, 20)

fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.8), sharey=True)
for ax, valeurs, titre, couleur in ((axes[0], panier_a, "Panier A", BLUE),
                                    (axes[1], panier_b, "Panier B", ORANGE)):
    ax.hist(valeurs, bins=tranches, color=couleur, edgecolor="white", linewidth=1.2)
    ax.axvline(200, color=DARK, linestyle="--", linewidth=1.8)
    ax.text(206, 8.6, "moyenne : 200 g", ha="left", va="top", fontsize=10,
            color=DARK, fontweight="bold")
    ax.set_title(titre, fontsize=13, color=DARK, fontweight="bold")
    ax.set_xlabel("masse (g)")
    ax.set_ylim(0, 9)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("nombre de fruits")
axes[0].text(104, 6.2, "tous les fruits\nsont autour\nde la moyenne", fontsize=10, color=MUT,
             style="italic", va="top")
axes[1].text(160, 6.2, "aucun fruit\nne pèse 200 g", fontsize=10, color=MUT,
             style="italic", va="top", ha="center")
fig.tight_layout()
save(fig, "f8_meme_moyenne")


# ---- f8_anatomie : les elements d'un graphique, montres sur un graphique ----
fig, ax = plt.subplots(figsize=(10.5, 4.8))
fruits = ["mangue", "banane", "orange"]
masses = [305, 128, 197]
barres = ax.bar(fruits, masses, color=[GREEN, ORANGE, BLUE], width=0.55)
ax.set_title("Masse moyenne par fruit", fontsize=13, color=DARK, fontweight="bold", pad=40)
ax.set_xlabel("fruit", labelpad=10)
ax.set_ylabel("masse moyenne (g)", labelpad=10)
ax.set_ylim(0, 360)
ax.spines[["top", "right"]].set_visible(False)

# Les quatre reperes vivent dans la marge, en coordonnees d'axes : « annotation_clip=False » est ce
# qui les empeche d'etre rognes par le cadre.
reperes = [
    ("le titre : ce que l'on regarde", (0.34, 1.11), (0.06, 1.30)),
    ("l'axe des y :\nla mesure, avec son unité", (-0.10, 0.60), (-0.36, 1.02)),
    ("l'axe des x :\nles groupes comparés", (0.46, -0.13), (0.12, -0.34)),
    ("les formes :\nelles portent l'information", (0.86, 0.34), (1.25, 0.76)),
]
for texte, cible, position in reperes:
    ax.annotate(texte, xy=cible, xytext=position, xycoords="axes fraction",
                textcoords="axes fraction", fontsize=10, color=MUT, ha="center", va="center",
                annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color=MUT, lw=1.3,
                                connectionstyle="arc3,rad=0.2"))
for barre, masse in zip(barres, masses):
    ax.text(barre.get_x() + barre.get_width() / 2, masse + 8, f"{masse} g",
            ha="center", fontsize=10, color=DARK, fontweight="bold")
fig.tight_layout()
save(fig, "f8_anatomie")


# ---- f8_choisir : trois questions, trois graphiques ----
fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
questions = [
    "« Comment se répartissent\nles masses ? »",
    "« Quel fruit est le plus\nlourd en moyenne ? »",
    "« Les fruits longs sont-ils\nles plus lourds ? »",
]
reponses = ["histogramme", "diagramme en barres", "nuage de points"]

graine = np.random.default_rng(8)
axes[0].hist(graine.normal(200, 55, 240), bins=12, color=BLUE, edgecolor="white", linewidth=1.0)
axes[1].bar(["mangue", "banane", "orange"], [305, 128, 197], color=[GREEN, ORANGE, BLUE], width=0.55)
longueur = graine.normal(9, 1.6, 60)
axes[2].scatter(longueur, longueur * 22 + graine.normal(0, 22, 60), s=22, color=GREEN, alpha=0.75)

for ax, question, reponse in zip(axes, questions, reponses):
    ax.set_title(question, fontsize=11, color=MUT, pad=14)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel(reponse, fontsize=12, color=DARK, fontweight="bold", labelpad=8)
fig.tight_layout()
save(fig, "f8_choisir")

print("FINI")
