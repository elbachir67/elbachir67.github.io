# Figures Séance 0 — Programmation Python (UCAD)
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


def box(ax, x, y, w, h, text, fc, ec, fs=12, tc=None, bold=True, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec=ec, lw=1.8))
    tc = tc or ec
    if sub:
        ax.text(x + w / 2, y + h * 0.64, text, ha="center", va="center",
                fontsize=fs, color=tc, fontweight="bold" if bold else "normal")
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                fontsize=fs - 3, color=MUT)
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=tc, fontweight="bold" if bold else "normal")


def arrow(ax, p, q, color=MUT, lw=2.2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16,
                                 color=color, lw=lw))


def save(fig, name):
    fig.savefig(f"figs/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"figs/{name}.svg", bbox_inches="tight")
    fig.savefig(f"figs/{name}.png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    print(name, "ok")


# ============================================================== f0_atelier
fig, ax = plt.subplots(figsize=(11.0, 5.6))
ax.set_xlim(0, 11.0); ax.set_ylim(0, 5.8); ax.axis("off")
layers = [
    (0.5, 0.35, 6.4, 0.82, "L'ordinateur", "Windows, macOS ou Linux", MUT, "#F2F4F5"),
    (0.8, 1.42, 5.8, 0.82, "Anaconda", "la distribution : Python + l'outil conda", BLUE, "#EAF2FB"),
    (1.1, 2.49, 5.2, 0.82, "Environnement \u00ab prog-python \u00bb", "une bulle isol\u00e9e cr\u00e9\u00e9e par conda", DARK, "#E2EBF4"),
    (1.4, 3.56, 4.6, 0.82, "Biblioth\u00e8ques", "numpy \u00b7 pandas \u00b7 matplotlib", GREEN, "#EDF7F0"),
    (1.7, 4.63, 4.0, 0.82, "Jupyter", "le cahier o\u00f9 l'on travaille", ORANGE, "#FBF1E6"),
]
for x, y, w, h, t, sub, ec, fc in layers:
    box(ax, x, y, w, h, t, fc, ec, fs=13, sub=sub)
for i in range(4):
    ax.annotate("", xy=(3.6, layers[i + 1][1] - 0.02),
                xytext=(3.6, layers[i][1] + layers[i][3] + 0.02),
                arrowprops=dict(arrowstyle="-|>", color=MUT, lw=1.7))
# Git / GitHub : le carnet de bord, sur le côté
box(ax, 7.7, 2.3, 3.0, 1.25, "Git + GitHub", "#FBEDEC", RED, fs=13, sub="le carnet de bord\nversionn\u00e9")
ax.annotate("", xy=(7.65, 2.95), xytext=(6.35, 2.95),
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8))
ax.text(7.0, 3.18, "versionne", ha="center", fontsize=10, color=RED, style="italic")
ax.text(2.85, 5.55, "Chaque \u00e9tage s'appuie sur celui du dessous", ha="center",
        fontsize=11.5, color=MUT, style="italic")
save(fig, "f0_atelier")

# ============================================================== f0_notebook
fig, ax = plt.subplots(figsize=(9.6, 5.2))
ax.set_xlim(0, 9.6); ax.set_ylim(0, 5.4); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.4, 0.3), 8.8, 4.8, boxstyle="round,pad=0.02",
                            fc="white", ec=MUT, lw=1.6))
ax.add_patch(FancyBboxPatch((0.4, 4.5), 8.8, 0.6, boxstyle="round,pad=0.02",
                            fc="#F2F4F5", ec=MUT, lw=1.6))
ax.text(0.8, 4.8, "prise_en_main.ipynb", fontsize=12, va="center",
        fontweight="bold", color=DARK)
# markdown cell
box(ax, 0.8, 3.35, 8.0, 0.85, "", "#FFFFFF", BLUE)
ax.text(1.05, 3.98, "Cellule Markdown \u2014 du texte mis en forme", fontsize=10.5,
        color=BLUE, fontweight="bold")
ax.text(1.05, 3.60, "# Mon premier notebook", fontsize=11, family="monospace", color=DARK)
# code cell
box(ax, 0.8, 1.95, 8.0, 1.1, "", "#F7FAFD", GREEN)
ax.text(1.05, 2.82, "Cellule de code \u2014 du Python ex\u00e9cutable (Maj+Entr\u00e9e)",
        fontsize=10.5, color=GREEN, fontweight="bold")
ax.text(1.05, 2.40, 'In [1]:  print("Salut Dakar !")', fontsize=11.5,
        family="monospace", color=DARK)
# output
box(ax, 0.8, 0.85, 8.0, 0.75, "", "#FFFFFF", ORANGE)
ax.text(1.05, 1.38, "Sortie \u2014 le r\u00e9sultat s'affiche sous la cellule",
        fontsize=10.5, color=ORANGE, fontweight="bold")
ax.text(1.05, 1.05, "Salut Dakar !", fontsize=11.5, family="monospace", color=DARK)
ax.text(4.8, 0.52, "Le num\u00e9ro In [1] indique l'ordre d'ex\u00e9cution \u2014 pas la position dans la page.",
        ha="center", fontsize=10.5, color=MUT, style="italic")
save(fig, "f0_notebook")

# ============================================================== f0_traceback
fig, ax = plt.subplots(figsize=(11.2, 4.6))
ax.set_xlim(0, 11.2); ax.set_ylim(0, 4.6); ax.axis("off")
# faux terminal
ax.add_patch(FancyBboxPatch((0.3, 1.3), 6.7, 3.0, boxstyle="round,pad=0.02",
                            fc="#1F2A33", ec=DARK, lw=1.5))
mono = dict(family="monospace", fontsize=11, color="#E8EDF0")
lines = [
    'Traceback (most recent call last):',
    '  File "analyse.py", line 2, in <module>',
    '    print("Age : " + age)',
    '          ~~~~~~~~~^~~~~',
    'TypeError: can only concatenate str',
    '           (not "int") to str',
]
ys = [3.95, 3.55, 3.15, 2.78, 2.30, 1.95]
for ln, yy in zip(lines, ys):
    ax.text(0.5, yy, ln, va="center", **mono)
# annotations
ax.annotate("\u2462 le fichier et la ligne", xy=(2.4, 3.55), xytext=(7.4, 3.95),
            fontsize=11, color=BLUE, fontweight="bold", va="center",
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.7))
ax.annotate("\u2461 la fl\u00e8che pointe l'endroit", xy=(3.0, 2.78), xytext=(7.4, 2.95),
            fontsize=11, color=ORANGE, fontweight="bold", va="center",
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.7))
ax.annotate("\u2460 \u00c0 LIRE EN PREMIER\n   le type + le message", xy=(3.2, 2.12),
            xytext=(7.4, 1.55), fontsize=11.5, color=RED, fontweight="bold", va="center",
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.0))
ax.text(3.65, 0.75, "Un traceback se lit de BAS en HAUT : la derni\u00e8re ligne dit le pourquoi.",
        ha="center", fontsize=11.5, color=MUT, style="italic")
save(fig, "f0_traceback")

# ============================================================== f0_gitflow
fig, ax = plt.subplots(figsize=(12.2, 3.5))
ax.set_xlim(0, 12.2); ax.set_ylim(0, 3.5); ax.axis("off")
stages = [
    (0.2, "Dossier de travail", "vos fichiers", BLUE, "#EAF2FB"),
    (3.2, "Zone d'index", "(staging)", ORANGE, "#FBF1E6"),
    (6.2, "D\u00e9p\u00f4t local", "l'historique", GREEN, "#EDF7F0"),
    (9.2, "GitHub", "copie en ligne", DARK, "#E2EBF4"),
]
w, h, y = 2.7, 1.2, 1.5
for x, t, sub, ec, fc in stages:
    box(ax, x, y, w, h, t, fc, ec, fs=13, sub=sub)
acts = [("git add", 0.2), ("git commit", 0.2), ("git push", 0.2)]
xs = [2.9, 5.9, 8.9]
labels = ["git add", "git commit", "git push"]
for xx, lab in zip(xs, labels):
    arrow(ax, (xx, y + h / 2), (xx + 0.3, y + h / 2), color=MUT, lw=2.0)
    ax.text(xx + 0.15, y + h + 0.18, lab, ha="center", fontsize=10.5,
            family="monospace", color=DARK, fontweight="bold")
ax.text(6.1, 0.45, "Chaque commit est une sauvegarde dat\u00e9e et nomm\u00e9e ; "
                   "push l'envoie sur GitHub.",
        ha="center", fontsize=11.5, color=MUT, style="italic")
save(fig, "f0_gitflow")

print("FINI")
