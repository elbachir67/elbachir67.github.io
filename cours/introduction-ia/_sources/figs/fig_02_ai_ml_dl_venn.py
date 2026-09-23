#!/usr/bin/env python3
"""
Figure 02: Diagramme de Venn IA / ML / DL
Chapitre: S01 - Qu'est-ce que l'IA ?

Montre la relation d'inclusion : DL ⊂ ML ⊂ IA
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

# Configuration globale
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'figure.figsize': (11, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Couleurs
COLORS = {
    'ia': '#E3F2FD',         # Bleu très clair
    'ia_border': '#1565C0',   # Bleu foncé
    'ml': '#FFF3E0',          # Orange très clair
    'ml_border': '#E65100',   # Orange foncé
    'dl': '#E8F5E9',          # Vert très clair
    'dl_border': '#2E7D32',   # Vert foncé
    'text': '#212121',
    'example': '#616161',
}

def create_figure():
    fig, ax = plt.subplots()
    
    # Cercles concentriques (du plus grand au plus petit)
    # IA - le plus grand cercle
    ia_circle = Circle((0, 0), 4, facecolor=COLORS['ia'], 
                       edgecolor=COLORS['ia_border'], linewidth=3, alpha=0.7)
    ax.add_patch(ia_circle)
    
    # ML - cercle moyen
    ml_circle = Circle((0.5, -0.3), 2.5, facecolor=COLORS['ml'], 
                       edgecolor=COLORS['ml_border'], linewidth=3, alpha=0.7)
    ax.add_patch(ml_circle)
    
    # DL - le plus petit cercle
    dl_circle = Circle((0.8, -0.5), 1.3, facecolor=COLORS['dl'], 
                       edgecolor=COLORS['dl_border'], linewidth=3, alpha=0.7)
    ax.add_patch(dl_circle)
    
    # Labels des ensembles
    ax.text(-3.0, 3.2, 'Intelligence\nArtificielle', fontsize=14, fontweight='bold',
            color=COLORS['ia_border'], ha='center')
    ax.text(-1.2, 1.5, 'Machine\nLearning', fontsize=12, fontweight='bold',
            color=COLORS['ml_border'], ha='center')
    ax.text(0.8, -0.5, 'Deep\nLearning', fontsize=11, fontweight='bold',
            color=COLORS['dl_border'], ha='center')
    
    # Exemples dans chaque zone
    # Zone IA pure (non-ML)
    ia_examples = [
        (-2.8, 0.5, "GPS (A*)"),
        (-2.8, -0.3, "Wolfram Alpha"),
        (-2.8, -1.1, "Systèmes experts"),
        (-2.8, -1.9, "Solveurs SAT"),
        (-3.0, 1.5, "Planification"),
    ]
    for x, y, text in ia_examples:
        ax.text(x, y, f"• {text}", fontsize=9, color=COLORS['example'], ha='left')
    
    # Zone ML pure (non-DL)
    ml_examples = [
        (1.8, 1.5, "Random Forest"),
        (2.5, 0.8, "SVM"),
        (2.8, 0.1, "k-NN"),
        (2.5, -0.6, "Naive Bayes"),
        (1.8, -1.3, "Régression logistique"),
    ]
    for x, y, text in ml_examples:
        ax.text(x, y, f"• {text}", fontsize=9, color=COLORS['example'], ha='left')
    
    # Zone DL
    dl_examples = [
        (0.8, -1.5, "• CNN, Transformers"),
        (0.8, -2.0, "• GPT, Claude"),
    ]
    for x, y, text in dl_examples:
        ax.text(x, y, text, fontsize=9, color=COLORS['example'], ha='center')
    
    # Encadrés explicatifs
    # Box pour IA
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=COLORS['ia_border'], alpha=0.9)
    ax.text(-3.5, -3.5, "IA = toutes les méthodes\npour créer des systèmes\n« intelligents »", 
            fontsize=9, ha='left', va='top', bbox=bbox_props, color=COLORS['ia_border'])
    
    # Box pour ML
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=COLORS['ml_border'], alpha=0.9)
    ax.text(0.5, -3.5, "ML = une APPROCHE\npour faire de l'IA\n(apprendre des données)", 
            fontsize=9, ha='center', va='top', bbox=bbox_props, color=COLORS['ml_border'])
    
    # Box pour DL
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=COLORS['dl_border'], alpha=0.9)
    ax.text(3.5, -3.5, "DL = une TECHNIQUE\nde ML\n(réseaux profonds)", 
            fontsize=9, ha='left', va='top', bbox=bbox_props, color=COLORS['dl_border'])
    
    # Flèches montrant l'inclusion
    ax.annotate('', xy=(1.5, 2.8), xytext=(2.8, 2.0),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    ax.text(2.9, 2.0, 'ML ⊂ IA', fontsize=10, color='gray')
    
    ax.annotate('', xy=(2.0, 0.3), xytext=(3.2, 1.0),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    ax.text(3.3, 1.0, 'DL ⊂ ML', fontsize=10, color='gray')
    
    # Configuration des axes
    ax.set_xlim(-5, 5)
    ax.set_ylim(-4.5, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Intelligence Artificielle, Machine Learning et Deep Learning\n'
                 'Trois ensembles emboîtés, pas des synonymes', fontsize=12, pad=10)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('fig_02_ai_ml_dl_venn.pdf')
    fig.savefig('fig_02_ai_ml_dl_venn.png')
    plt.close()
    print("Figure 02 générée: fig_02_ai_ml_dl_venn.pdf")
