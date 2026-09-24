#!/usr/bin/env python3
"""
Synthèse Figure 05: Branches de l'Intelligence Artificielle
Vue d'ensemble avec indication des séances du cours
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.figsize': (14, 10),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_figure():
    fig, ax = plt.subplots()
    
    # Centre : IA
    center = (7, 5)
    center_circle = Circle(center, 1.2, facecolor='#2E86AB', alpha=0.3,
                           edgecolor='#2E86AB', linewidth=3)
    ax.add_patch(center_circle)
    ax.text(center[0], center[1], 'Intelligence\nArtificielle', ha='center',
            va='center', fontsize=12, fontweight='bold', color='#2E86AB')
    
    # Branches
    branches = [
        {
            'name': 'Recherche &\nPlanification',
            'pos': (2, 8),
            'color': '#28A745',
            'topics': ['BFS, DFS, UCS', 'A* et heuristiques', 'Recherche locale'],
            'seance': 'S3',
            'refs': 'AIMA Ch.3-4'
        },
        {
            'name': 'Représentation\n& Raisonnement',
            'pos': (7, 9),
            'color': '#F18F01',
            'topics': ['Logique propositionnelle', 'Logique 1er ordre', 'Inférence'],
            'seance': 'S2',
            'refs': 'AIMA Ch.7-9'
        },
        {
            'name': 'Raisonnement\nIncertain',
            'pos': (12, 8),
            'color': '#A23B72',
            'topics': ['Probabilités', 'Réseaux bayésiens', 'Filtrage'],
            'seance': 'S5',
            'refs': 'AIMA Ch.12-16'
        },
        {
            'name': 'Machine\nLearning',
            'pos': (13, 5),
            'color': '#dc3545',
            'topics': ['Supervisé', 'Non supervisé', 'Deep Learning'],
            'seance': 'ML S2',
            'refs': 'Murphy, Prince'
        },
        {
            'name': 'Prise de\nDécision',
            'pos': (12, 2),
            'color': '#17a2b8',
            'topics': ['MDPs', 'Value Iteration', 'Q-Learning'],
            'seance': 'S6',
            'refs': 'AIMA Ch.17, Sutton'
        },
        {
            'name': 'Traitement\ndu Langage',
            'pos': (7, 1),
            'color': '#6f42c1',
            'topics': ['NLP', 'Transformers', 'LLMs'],
            'seance': '—',
            'refs': 'Spécialisé'
        },
        {
            'name': 'Vision par\nOrdinateur',
            'pos': (2, 2),
            'color': '#fd7e14',
            'topics': ['CNN', 'Détection', 'Segmentation'],
            'seance': '—',
            'refs': 'Spécialisé'
        },
        {
            'name': 'Robotique',
            'pos': (1, 5),
            'color': '#20c997',
            'topics': ['Perception', 'Contrôle', 'SLAM'],
            'seance': '—',
            'refs': 'AIMA Ch.26'
        },
    ]
    
    # Dessiner les branches
    for branch in branches:
        x, y = branch['pos']
        color = branch['color']
        
        # Ligne vers le centre
        ax.plot([center[0], x], [center[1], y], '-', color='#ccc', 
                linewidth=1.5, zorder=1)
        
        # Boîte de la branche
        box_width = 2.2
        box_height = 2.0
        box = FancyBboxPatch((x - box_width/2, y - box_height/2), 
                              box_width, box_height,
                              boxstyle="round,pad=0.03,rounding_size=0.2",
                              facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2, zorder=2)
        ax.add_patch(box)
        
        # Nom
        ax.text(x, y + 0.6, branch['name'], ha='center', va='center',
                fontsize=9, fontweight='bold', color=color)
        
        # Topics
        topics_text = '\n'.join([f'• {t}' for t in branch['topics']])
        ax.text(x, y - 0.2, topics_text, ha='center', va='center',
                fontsize=7, color='#333')
        
        # Badge de séance
        seance = branch['seance']
        if seance != '—':
            badge_color = '#28A745' if 'S' in seance else '#6c757d'
            ax.text(x + box_width/2 - 0.1, y + box_height/2 - 0.1, seance,
                    ha='center', va='center', fontsize=8, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor=badge_color,
                             edgecolor='none'))
        
        # Référence
        ax.text(x, y - 0.85, branch['refs'], ha='center', va='center',
                fontsize=6, style='italic', color='#888')
    
    # Légende
    legend_y = -0.5
    ax.text(7, legend_y, 'Légende:', ha='center', fontsize=10, fontweight='bold')
    
    legend_items = [
        (3, 'S2-S6 = Couvert dans ce cours', '#28A745'),
        (7, 'ML S2 = Cours de ML au semestre 2', '#dc3545'),
        (11, '— = Non couvert (cours spécialisés)', '#6c757d'),
    ]
    
    for x, text, color in legend_items:
        ax.plot(x - 1.5, legend_y - 0.5, 's', markersize=10, color=color)
        ax.text(x - 1.2, legend_y - 0.5, text, ha='left', va='center', fontsize=8)
    
    # Configuration
    ax.set_xlim(-1, 15)
    ax.set_ylim(-1.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Les Branches de l\'Intelligence Artificielle\n'
                 'et leur couverture dans le cursus M1 IABD',
                 fontsize=13, fontweight='bold', pad=15)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('synth_fig_05_branches.pdf')
    fig.savefig('synth_fig_05_branches.png')
    plt.close()
    print("Figure générée: synth_fig_05_branches.pdf")
