#!/usr/bin/env python3
"""
Figures — Seance 1 : ADTs et Interfaces Java
Cours : Structures de Donnees et Algorithmes Avances — M1 — ESP/UCAD
Dr. El Hadji Bassirou TOURE

Toutes les traces (pile, file circulaire, postfixe) sont CALCULEES par
simulation reelle des structures, puis dessinees. Aucune valeur n'est ecrite
a la main dans le dessin.

Sortie : fig_01.pdf/.png ... fig_05.pdf/.png dans le dossier du script.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))

BLEU = '#1A4D8F'
BLEU_CLAIR = '#D6E4F5'
VERT = '#2E7D32'
VERT_CLAIR = '#D9EFD9'
ORANGE = '#E07B00'
ORANGE_CLAIR = '#FDE8CC'
GRIS = '#9E9E9E'
GRIS_CLAIR = '#EDEDED'

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10


def save(fig, nom):
    fig.savefig(os.path.join(OUT, nom + '.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(OUT, nom + '.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  ->', nom + '.pdf')


def boite(ax, x, y, w, h, texte, fc, ec, fs=10, bold=False, mono=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor=fc, edgecolor=ec, linewidth=1.4))
    ax.text(x + w / 2, y + h / 2, texte, ha='center', va='center', fontsize=fs,
            fontweight='bold' if bold else 'normal',
            family='monospace' if mono else 'DejaVu Sans')


def fleche(ax, p1, p2, couleur=GRIS, style='-|>', lw=1.4):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                                 color=couleur, linewidth=lw,
                                 shrinkA=2, shrinkB=2))


# =====================================================================
# FIGURE 1 — ADT (contrat) vs implementations
# =====================================================================
def figure_01():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis('off')

    boite(ax, 2.6, 3.9, 4.8, 1.0,
          "interface Deque<T>\naddFirst · addLast · removeFirst · removeLast · size",
          BLEU_CLAIR, BLEU, fs=10, bold=True)
    ax.text(5.0, 5.05, "LE CONTRAT — ce que la structure promet",
            ha='center', va='center', fontsize=10, color=BLEU, fontweight='bold')

    impls = [
        (0.35, "ArrayDeque<T>\ntableau circulaire\nredimensionnable"),
        (3.55, "LinkedDeque<T>\nnoeuds doublement\nchaines"),
        (6.75, "TestDeque<T>\nimplementation\nnaive de reference"),
    ]
    for x, txt in impls:
        boite(ax, x, 1.4, 2.9, 1.25, txt, VERT_CLAIR, VERT, fs=9)
        fleche(ax, (x + 1.45, 2.65), (5.0, 3.9), couleur=VERT)

    ax.text(5.0, 0.95, "LES IMPLEMENTATIONS — comment la promesse est tenue",
            ha='center', va='center', fontsize=10, color=VERT, fontweight='bold')
    ax.text(5.0, 0.35,
            "Le code client ne depend que du contrat : changer d'implementation "
            "ne change pas une ligne du client.",
            ha='center', va='center', fontsize=9, style='italic', color='#444444')
    save(fig, 'fig_01')


# =====================================================================
# FIGURE 2 — Tableau contigu vs noeuds chaines
# =====================================================================
def figure_02():
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.0))

    # --- tableau contigu
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.2)
    ax.axis('off')
    ax.text(0.1, 1.95, "ArrayList : cases contigues en memoire",
            fontsize=11, fontweight='bold', color=BLEU)
    valeurs = ['Fatou', 'Moussa', 'Awa', 'Cheikh', 'Aminata', '', '']
    for i, v in enumerate(valeurs):
        x = 0.4 + i * 1.3
        fc = BLEU_CLAIR if v else 'white'
        ax.add_patch(Rectangle((x, 0.85), 1.2, 0.7, facecolor=fc,
                               edgecolor=BLEU, linewidth=1.3))
        ax.text(x + 0.6, 1.2, v, ha='center', va='center', fontsize=9)
        ax.text(x + 0.6, 0.62, str(i), ha='center', va='center',
                fontsize=8, color=GRIS)
    ax.text(0.4, 0.2,
            "get(i) : adresse = base + i x taille  ->  1 acces, cout constant\n"
            "add(0, x) : il faut decaler les 5 elements vers la droite  ->  cout proportionnel a n",
            fontsize=9, va='center', color='#333333')

    # --- noeuds chaines
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.2)
    ax.axis('off')
    ax.text(0.1, 1.95, "LinkedList : noeuds disperses, relies par des references",
            fontsize=11, fontweight='bold', color=VERT)
    noms = ['Fatou', 'Moussa', 'Awa', 'Cheikh']
    for i, v in enumerate(noms):
        x = 0.6 + i * 2.3
        ax.add_patch(Rectangle((x, 0.9), 1.3, 0.6, facecolor=VERT_CLAIR,
                               edgecolor=VERT, linewidth=1.3))
        ax.text(x + 0.65, 1.2, v, ha='center', va='center', fontsize=9)
        ax.add_patch(Rectangle((x + 1.3, 0.9), 0.35, 0.6, facecolor='white',
                               edgecolor=VERT, linewidth=1.3))
        if i < len(noms) - 1:
            fleche(ax, (x + 1.65, 1.2), (x + 2.3, 1.2), couleur=VERT)
        else:
            ax.text(x + 1.47, 1.2, "/", ha='center', va='center',
                    fontsize=11, color=VERT)
    ax.text(0.6, 0.25,
            "get(i) : il faut suivre i references depuis la tete  ->  cout proportionnel a i\n"
            "addFirst(x) : creer un noeud et rebrancher une reference  ->  cout constant",
            fontsize=9, va='center', color='#333333')

    plt.tight_layout()
    save(fig, 'fig_02')


# =====================================================================
# FIGURE 3 — Trace d'une pile (verification de parentheses)
# =====================================================================
def figure_03():
    expression = "( a + [ b ] )"
    tokens = expression.split()
    ouvrantes = {'(': ')', '[': ']', '{': '}'}

    pile = []
    etapes = []          # (token, etat de la pile apres traitement)
    for t in tokens:
        if t in ouvrantes:
            pile.append(t)
        elif t in ouvrantes.values():
            pile.pop()
        etapes.append((t, list(pile)))

    print("  trace pile :", [(t, ''.join(p)) for t, p in etapes])

    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, len(etapes) * 1.35 + 0.6)
    ax.set_ylim(0, 3.4)
    ax.axis('off')
    ax.text(0.3, 3.15, "Expression : " + expression,
            fontsize=11, fontweight='bold', color=BLEU)

    for k, (t, etat) in enumerate(etapes):
        x = 0.4 + k * 1.35
        ax.text(x + 0.45, 2.75, t, ha='center', va='center', fontsize=11,
                fontweight='bold', family='monospace')
        for niveau, symbole in enumerate(etat):
            y = 0.55 + niveau * 0.5
            ax.add_patch(Rectangle((x, y), 0.9, 0.45, facecolor=ORANGE_CLAIR,
                                   edgecolor=ORANGE, linewidth=1.2))
            ax.text(x + 0.45, y + 0.22, symbole, ha='center', va='center',
                    fontsize=10, family='monospace')
        ax.plot([x, x], [0.5, 2.4], color=GRIS, linewidth=1.0)
        ax.plot([x + 0.9, x + 0.9], [0.5, 2.4], color=GRIS, linewidth=1.0)
        ax.plot([x, x + 0.9], [0.5, 0.5], color=GRIS, linewidth=1.4)
        ax.text(x + 0.45, 0.2, str(k + 1), ha='center', va='center',
                fontsize=8, color=GRIS)

    ax.text(0.3, 3.15 - 3.0,
            "Pile vide a la fin  ->  expression equilibree",
            fontsize=9, style='italic', color=VERT)
    save(fig, 'fig_03')


# =====================================================================
# FIGURE 4 — File sur tableau circulaire
# =====================================================================
def figure_04():
    m = 6
    tab = [None] * m
    tete, taille = 0, 0

    def enqueue(x):
        nonlocal taille
        tab[(tete + taille) % m] = x
        taille += 1

    def dequeue():
        nonlocal tete, taille
        v = tab[tete]
        tab[tete] = None
        tete = (tete + 1) % m
        taille -= 1
        return v

    instantanes = []
    for nom in ['Fatou', 'Moussa', 'Awa', 'Cheikh']:
        enqueue(nom)
    instantanes.append(("4 clients en attente", list(tab), tete, taille))
    dequeue(); dequeue()
    instantanes.append(("2 clients servis", list(tab), tete, taille))
    enqueue('Aminata'); enqueue('Ibrahima'); enqueue('Ndeye')
    instantanes.append(("3 arrivees : la fin repasse en case 0",
                        list(tab), tete, taille))

    for titre, t, h, n in instantanes:
        print("  file :", titre, "| tete =", h, "| taille =", n,
              "|", [v if v else '.' for v in t])

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    for ax, (titre, t, h, n) in zip(axes, instantanes):
        ax.set_xlim(0, m * 1.0 + 0.4)
        ax.set_ylim(0, 2.6)
        ax.axis('off')
        ax.set_title(titre, fontsize=10, color=BLEU, pad=6)
        for i in range(m):
            x = 0.2 + i * 1.0
            occupe = t[i] is not None
            ax.add_patch(Rectangle((x, 1.0), 0.9, 0.7,
                                   facecolor=BLEU_CLAIR if occupe else 'white',
                                   edgecolor=BLEU, linewidth=1.2))
            if occupe:
                ax.text(x + 0.45, 1.35, t[i][:4], ha='center', va='center',
                        fontsize=8)
            ax.text(x + 0.45, 0.78, str(i), ha='center', va='center',
                    fontsize=8, color=GRIS)
        xt = 0.2 + h * 1.0 + 0.45
        ax.annotate("tete", xy=(xt, 1.72), xytext=(xt, 2.25),
                    ha='center', fontsize=9, color=ORANGE,
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.4))
        xf = 0.2 + ((h + n) % m) * 1.0 + 0.45
        ax.annotate("prochaine", xy=(xf, 0.98), xytext=(xf, 0.35),
                    ha='center', fontsize=9, color=VERT,
                    arrowprops=dict(arrowstyle='-|>', color=VERT, lw=1.4))
    plt.tight_layout()
    save(fig, 'fig_04')


# =====================================================================
# FIGURE 5 — Evaluation postfixe pas a pas
# =====================================================================
def figure_05():
    expression = "3 4 + 2 * 7 -"
    pile = []
    etapes = []
    for t in expression.split():
        if t.lstrip('-').isdigit():
            pile.append(int(t))
        else:
            b = pile.pop()
            a = pile.pop()
            pile.append({'+': a + b, '-': a - b, '*': a * b,
                         '/': a // b}[t])
        etapes.append((t, list(pile)))

    print("  postfixe", expression, "=", etapes[-1][1][0])
    for t, p in etapes:
        print("    jeton", t, "-> pile", p)

    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.set_xlim(0, len(etapes) * 1.35 + 0.6)
    ax.set_ylim(0, 3.6)
    ax.axis('off')
    ax.text(0.3, 3.35, "Expression postfixe : " + expression,
            fontsize=11, fontweight='bold', color=BLEU)

    for k, (t, etat) in enumerate(etapes):
        x = 0.4 + k * 1.35
        est_op = not t.lstrip('-').isdigit()
        ax.text(x + 0.45, 2.95, t, ha='center', va='center', fontsize=11,
                fontweight='bold', family='monospace',
                color=ORANGE if est_op else BLEU)
        for niveau, val in enumerate(etat):
            y = 0.6 + niveau * 0.55
            ax.add_patch(Rectangle((x, y), 0.9, 0.5, facecolor=VERT_CLAIR,
                                   edgecolor=VERT, linewidth=1.2))
            ax.text(x + 0.45, y + 0.25, str(val), ha='center', va='center',
                    fontsize=10, family='monospace')
        ax.plot([x, x], [0.55, 2.6], color=GRIS, linewidth=1.0)
        ax.plot([x + 0.9, x + 0.9], [0.55, 2.6], color=GRIS, linewidth=1.0)
        ax.plot([x, x + 0.9], [0.55, 0.55], color=GRIS, linewidth=1.4)
    ax.text(0.3, 0.15,
            "Un seul parcours des jetons : chaque jeton est empile ou "
            "declenche un depilement de deux operandes.",
            fontsize=9, style='italic', color='#333333')
    save(fig, 'fig_05')


if __name__ == '__main__':
    print("Figures S01 :")
    figure_01()
    figure_02()
    figure_03()
    figure_04()
    figure_05()
    print("Termine.")
