#!/usr/bin/env python3
"""
Figures — Seance 2 : Analyse algorithmique
Cours : Structures de Donnees et Algorithmes Avances — M1 — ESP/UCAD
Dr. El Hadji Bassirou TOURE

Les valeurs affichees sont CALCULEES : le comptage d'operations est obtenu en
instrumentant reellement les boucles (compteur incremente a chaque operation
elementaire, selon la convention granulaire du cours), et le cout des
insertions en tete est obtenu en simulant le deplacement des elements.

Sortie : fig_01.pdf/.png ... fig_05.pdf/.png dans le dossier du script.
"""

import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))

BLEU = '#1A4D8F'
BLEU_CLAIR = '#D6E4F5'
VERT = '#2E7D32'
ORANGE = '#E07B00'
ROUGE = '#B3261E'
GRIS = '#9E9E9E'

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10


def save(fig, nom):
    fig.savefig(os.path.join(OUT, nom + '.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(OUT, nom + '.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  ->', nom + '.pdf')


# =====================================================================
# FIGURE 1 — Comptage granulaire : f(n) mesure vs formule
# =====================================================================
def compte_somme(n):
    """
    int s = 0;                      -> 1 affectation
    for (int i = 0; i < n; i++)     -> 1 affectation + (n+1) comparaisons + n*(1 add + 1 aff)
        s = s + i;                  -> n * (1 addition + 1 affectation)
    Compteur incremente a chaque operation elementaire.
    """
    ops = 0
    s = 0; ops += 1          # s = 0
    i = 0; ops += 1          # i = 0
    while True:
        ops += 1             # comparaison i < n
        if not i < n:
            break
        s = s + i; ops += 2  # addition + affectation
        i = i + 1; ops += 2  # addition + affectation
    return ops


def figure_01():
    ns = list(range(0, 11))
    mesures = [compte_somme(n) for n in ns]
    formule = [5 * n + 3 for n in ns]
    assert mesures == formule, (mesures, formule)
    print("  f(n) mesure :", mesures)
    print("  f(n) = 5n + 3 : verifie pour n = 0..10")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(ns, mesures, 'o-', color=BLEU, linewidth=2, markersize=6,
            label="opérations comptées (instrumentation)")
    ax.plot(ns, formule, '--', color=ORANGE, linewidth=2,
            label=r"$f(n) = 5n + 3$")
    for n in [2, 5, 8]:
        ax.annotate(str(formule[n]), xy=(n, formule[n]), xytext=(n - 0.4, formule[n] + 5),
                    fontsize=9, color=ORANGE)
    ax.set_xlabel("n")
    ax.set_ylabel("nombre d'opérations élémentaires")
    ax.set_title("Comptage granulaire de la somme des n premiers entiers",
                 fontsize=11, color=BLEU)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    save(fig, 'fig_01')


# =====================================================================
# FIGURE 2 — Definition de Big-O : f(n) <= c g(n) a partir de n0
# =====================================================================
def figure_02():
    n = np.linspace(1, 30, 400)
    f = 3 * n ** 2 + 20 * n + 50
    c = 5
    g = n ** 2

    # plus petit n0 entier tel que f(n) <= c g(n) pour tout n >= n0
    n0 = None
    for k in range(1, 200):
        if all(3 * m ** 2 + 20 * m + 50 <= c * m ** 2 for m in range(k, 400)):
            n0 = k
            break
    print("  c =", c, "-> n0 =", n0,
          "| f(n0) =", 3 * n0 ** 2 + 20 * n0 + 50, "<= c*g(n0) =", c * n0 ** 2)

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(n, f, color=BLEU, linewidth=2, label=r"$f(n) = 3n^2 + 20n + 50$")
    ax.plot(n, c * g, color=ORANGE, linewidth=2, label=r"$c \cdot g(n) = 5n^2$")
    ax.axvline(n0, color=ROUGE, linestyle=':', linewidth=1.6)
    ax.text(n0 + 0.4, max(f) * 0.15, r"$n_0 = %d$" % n0, color=ROUGE, fontsize=11)
    masque = n >= n0
    ax.fill_between(n[masque], f[masque], (c * g)[masque],
                    color=ORANGE, alpha=0.15)
    ax.set_xlabel("n")
    ax.set_ylabel("coût")
    ax.set_title(r"$f(n) \in \mathcal{O}(n^2)$ : au-delà de $n_0$, $c\,g(n)$ domine $f$",
                 fontsize=11, color=BLEU)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc='upper left')
    plt.tight_layout()
    save(fig, 'fig_02')


# =====================================================================
# FIGURE 3 — Classes de complexite
# =====================================================================
def figure_03():
    n = np.arange(1, 101)
    courbes = [
        (np.ones_like(n, dtype=float), r"$\mathcal{O}(1)$", VERT),
        (np.log2(n), r"$\mathcal{O}(\log n)$", '#00838F'),
        (n.astype(float), r"$\mathcal{O}(n)$", BLEU),
        (n * np.log2(n), r"$\mathcal{O}(n \log n)$", ORANGE),
        (n.astype(float) ** 2, r"$\mathcal{O}(n^2)$", ROUGE),
    ]
    print("  a n = 100 :", {lab: float(y[-1]) for y, lab, _ in courbes})

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, logscale in zip(axes, [False, True]):
        for y, lab, col in courbes:
            ax.plot(n, y, label=lab, color=col, linewidth=2)
        ax.set_xlabel("n")
        ax.set_ylabel("coût")
        ax.grid(alpha=0.3)
        if logscale:
            ax.set_yscale('log')
            ax.set_title("échelle logarithmique", fontsize=10, color=GRIS)
        else:
            ax.set_ylim(0, 1200)
            ax.set_title("échelle linéaire", fontsize=10, color=GRIS)
    axes[0].legend(fontsize=9, loc='upper left')
    fig.suptitle("Les classes de complexité usuelles", fontsize=11, color=BLEU)
    plt.tight_layout()
    save(fig, 'fig_03')


# =====================================================================
# FIGURE 4 — Master Theorem : cout par niveau de l'arbre de recursion
# =====================================================================
def cout_par_niveau(a, b, expo_f, n, coef=1.0):
    """T(n) = a T(n/b) + coef * n^expo_f : cout total du niveau i."""
    niveaux = int(math.log(n, b))
    return [a ** i * coef * (n / b ** i) ** expo_f for i in range(niveaux + 1)]


def figure_04():
    n = 1024
    cas = [
        (2, 2, 0.0, "Cas 1 : $T(n)=2T(n/2)+\\mathcal{O}(1)$\nles feuilles dominent $\\rightarrow \\Theta(n)$", VERT),
        (2, 2, 1.0, "Cas 2 : $T(n)=2T(n/2)+\\Theta(n)$\ntous les niveaux égaux $\\rightarrow \\Theta(n\\log n)$", BLEU),
        (2, 2, 2.0, "Cas 3 : $T(n)=2T(n/2)+\\Theta(n^2)$\nla racine domine $\\rightarrow \\Theta(n^2)$", ORANGE),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.0))
    for ax, (a, b, e, titre, col) in zip(axes, cas):
        couts = cout_par_niveau(a, b, e, n)
        total = sum(couts)
        print("  ", titre.split(chr(10))[0], "| total =", round(total, 1),
              "| niveaux =", len(couts))
        ax.bar(range(len(couts)), couts, color=col, alpha=0.8)
        ax.set_xlabel("niveau de récursion")
        ax.set_ylabel("coût du niveau")
        ax.set_title(titre, fontsize=9)
        ax.grid(alpha=0.25, axis='y')
    fig.suptitle("n = 1024 : où se dépense le travail dans un diviser-pour-régner",
                 fontsize=11, color=BLEU)
    plt.tight_layout()
    save(fig, 'fig_04')


# =====================================================================
# FIGURE 5 — Cout cumule de n insertions en tete
# =====================================================================
def cout_insertions_tete(n, contigu):
    """
    contigu = True  : add(0, x) decale les k elements deja presents.
    contigu = False : add(0, x) cree un noeud et rebranche une reference.
    Retourne le cout cumule (nombre de deplacements / rebranchements).
    """
    total = 0
    cumul = []
    for k in range(n):
        total += k if contigu else 1
        cumul.append(total)
    return cumul


def figure_05():
    n = 2000
    tableau = cout_insertions_tete(n, True)
    chaine = cout_insertions_tete(n, False)
    print("  n =", n, "| contigu :", tableau[-1], "deplacements",
          "| chaine :", chaine[-1], "rebranchements",
          "| rapport =", round(tableau[-1] / chaine[-1], 1))

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(range(n), tableau, color=ROUGE, linewidth=2,
            label="ArrayList.add(0, x) : cumul $\\approx n^2/2$")
    ax.plot(range(n), chaine, color=VERT, linewidth=2,
            label="LinkedList.addFirst(x) : cumul $= n$")
    ax.set_xlabel("nombre d'insertions effectuées")
    ax.set_ylabel("opérations cumulées")
    ax.set_title("Même contrat, même résultat, coûts incomparables",
                 fontsize=11, color=BLEU)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    save(fig, 'fig_05')


if __name__ == '__main__':
    print("Figures S02 :")
    figure_01()
    figure_02()
    figure_03()
    figure_04()
    figure_05()
    print("Termine.")
