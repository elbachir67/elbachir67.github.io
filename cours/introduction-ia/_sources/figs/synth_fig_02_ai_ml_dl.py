#!/usr/bin/env python3
"""
Synthèse Figure 02: Hiérarchie IA / ML / Deep Learning
Cercles concentriques avec exemples positionnés
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.figsize': (10, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_figure():
    fig, ax = plt.subplots()
    
    # Cercles concentriques
    circles = [
        (0, 0, 4.0, '#2E86AB', 0.15, 'Intelligence Artificielle', 14),
        (0, 0, 2.8, '#A23B72', 0.20, 'Machine Learning', 12),
        (0, 0, 1.5, '#28A745', 0.25, 'Deep\nLearning', 11)
    ]
    
    for x, y, r, color, alpha, label, fontsize in circles:
        circle = plt.Circle((x, y), r, color=color, alpha=alpha, zorder=1)
        ax.add_patch(circle)
        circle_edge = plt.Circle((x, y), r, fill=False, color=color, 
                                  linewidth=2.5, zorder=2)
        ax.add_patch(circle_edge)
    
    # Labels des cercles
    ax.text(0, 3.5, 'Intelligence Artificielle', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#2E86AB')
    ax.text(0, 2.3, 'Machine Learning', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#A23B72')
    ax.text(0, 0, 'Deep\nLearning', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#28A745')
    
    # Exemples dans chaque zone
    # Zone IA (non-ML)
    ia_examples = [
        (-3.2, 2.5, 'GPS\n(planificateur)'),
        (-3.2, 0.5, 'Wolfram Alpha\n(calcul formel)'),
        (-3.2, -1.5, 'MYCIN\n(système expert)'),
        (3.2, 2.5, 'A*\n(recherche)'),
        (3.2, 0.5, 'Prolog\n(logique)'),
        (3.2, -1.5, 'Prouveur de\nthéorèmes'),
    ]
    
    for x, y, text in ia_examples:
        ax.text(x, y, text, ha='center', va='center', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#e3f2fd', 
                         edgecolor='#2E86AB', alpha=0.9))
    
    # Zone ML (non-DL)
    ml_examples = [
        (-1.8, -2.0, 'Random\nForest'),
        (1.8, -2.0, 'SVM'),
        (-2.0, 1.5, 'k-NN'),
        (2.0, 1.5, 'Naïve\nBayes'),
    ]
    
    for x, y, text in ml_examples:
        ax.text(x, y, text, ha='center', va='center', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fce4ec', 
                         edgecolor='#A23B72', alpha=0.9))
    
    # Zone DL
    dl_examples = [
        (0, -0.8, 'GPT-4'),
        (-0.7, 0.5, 'CNN'),
        (0.7, 0.5, 'BERT'),
    ]
    
    for x, y, text in dl_examples:
        ax.text(x, y, text, ha='center', va='center', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f5e9', 
                         edgecolor='#28A745', alpha=0.9))
    
    # Annotations avec flèches
    annotations = [
        ((-3.2, -3.0), 'IA sans ML:\nRègles explicites,\nrecherche, logique'),
        ((3.2, -3.0), 'ML sans DL:\nAlgorithmes classiques,\npeu de couches'),
        ((0, -3.5), 'Deep Learning:\nRéseaux profonds,\nreprésentation apprise'),
    ]
    
    for pos, text in annotations:
        ax.text(pos[0], pos[1], text, ha='center', va='top', fontsize=8,
                style='italic', color='#495057')
    
    # Configuration
    ax.set_xlim(-5, 5)
    ax.set_ylim(-4.5, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('La Hiérarchie : IA ⊃ ML ⊃ Deep Learning\n'
                 '« Le ML est une APPROCHE pour faire de l\'IA.\n'
                 'Le DL est une TECHNIQUE de ML. »',
                 fontsize=11, fontweight='bold', pad=10,
                 linespacing=1.3)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('synth_fig_02_ai_ml_dl.pdf')
    fig.savefig('synth_fig_02_ai_ml_dl.png')
    plt.close()
    print("Figure générée: synth_fig_02_ai_ml_dl.pdf")
