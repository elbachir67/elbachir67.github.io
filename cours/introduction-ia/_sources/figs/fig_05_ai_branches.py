#!/usr/bin/env python3
"""
Figure 05: Les branches de l'Intelligence Artificielle
Chapitre: S01 - Qu'est-ce que l'IA ?

Carte conceptuelle des sous-domaines de l'IA.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, ConnectionPatch
import numpy as np

# Configuration globale
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'figure.figsize': (14, 10),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Couleurs par domaine
COLORS = {
    'central': '#1565C0',
    'central_light': '#BBDEFB',
    'search': '#2E7D32',
    'search_light': '#C8E6C9',
    'knowledge': '#6A1B9A',
    'knowledge_light': '#E1BEE7',
    'ml': '#C62828',
    'ml_light': '#FFCDD2',
    'prob': '#EF6C00',
    'prob_light': '#FFE0B2',
    'nlp': '#00838F',
    'nlp_light': '#B2EBF2',
    'vision': '#AD1457',
    'vision_light': '#F8BBD9',
    'robotics': '#4E342E',
    'robotics_light': '#D7CCC8',
    'arrow': '#546E7A',
}

def create_figure():
    fig, ax = plt.subplots()
    
    # Position centrale pour "IA"
    center_x, center_y = 7, 5
    
    # Cercle central IA
    central = Circle((center_x, center_y), 1.2, 
                    facecolor=COLORS['central_light'],
                    edgecolor=COLORS['central'],
                    linewidth=3)
    ax.add_patch(central)
    ax.text(center_x, center_y, 'Intelligence\nArtificielle', 
            fontsize=12, fontweight='bold', ha='center', va='center',
            color=COLORS['central'])
    
    # Définir les branches
    branches = [
        {'name': 'Search &\nPlanning', 'x': 2, 'y': 8, 
         'color': COLORS['search'], 'light': COLORS['search_light'],
         'examples': 'A*, BFS, DFS\nPlanification\nJeux (Minimax)',
         'course': 'Séance 3'},
        {'name': 'Représentation\n& Raisonnement', 'x': 6, 'y': 9,
         'color': COLORS['knowledge'], 'light': COLORS['knowledge_light'],
         'examples': 'Logique\nOntologies\nSystèmes experts',
         'course': 'Séance 2'},
        {'name': 'Machine\nLearning', 'x': 10.5, 'y': 8,
         'color': COLORS['ml'], 'light': COLORS['ml_light'],
         'examples': 'Supervisé\nNon-supervisé\nRenforcement',
         'course': 'S2'},
        {'name': 'Raisonnement\nProbabiliste', 'x': 12, 'y': 5,
         'color': COLORS['prob'], 'light': COLORS['prob_light'],
         'examples': 'Bayes\nRéseaux bayésiens\nHMM',
         'course': 'Séance 5'},
        {'name': 'Traitement du\nLangage (NLP)', 'x': 10.5, 'y': 2,
         'color': COLORS['nlp'], 'light': COLORS['nlp_light'],
         'examples': 'Traduction\nChatbots\nLLMs',
         'course': '—'},
        {'name': 'Vision par\nOrdinateur', 'x': 6, 'y': 1,
         'color': COLORS['vision'], 'light': COLORS['vision_light'],
         'examples': 'Reconnaissance\nSegmentation\nDétection',
         'course': '—'},
        {'name': 'Robotique', 'x': 2, 'y': 2,
         'color': COLORS['robotics'], 'light': COLORS['robotics_light'],
         'examples': 'Perception\nContrôle\nNavigation',
         'course': '—'},
    ]
    
    # Dessiner les branches
    for branch in branches:
        # Boîte principale
        box = FancyBboxPatch((branch['x'] - 1.3, branch['y'] - 0.9), 2.6, 1.8,
                            boxstyle="round,pad=0.05,rounding_size=0.2",
                            facecolor=branch['light'],
                            edgecolor=branch['color'],
                            linewidth=2.5)
        ax.add_patch(box)
        
        # Nom de la branche
        ax.text(branch['x'], branch['y'] + 0.5, branch['name'], 
                fontsize=10, fontweight='bold', ha='center', va='center',
                color=branch['color'], linespacing=0.9)
        
        # Exemples
        ax.text(branch['x'], branch['y'] - 0.4, branch['examples'], 
                fontsize=8, ha='center', va='center',
                color='#424242', linespacing=0.95)
        
        # Badge "ce cours" si applicable
        if branch['course'] != '—':
            badge_color = '#4CAF50' if branch['course'].startswith('S') else branch['color']
            ax.text(branch['x'] + 1.0, branch['y'] + 0.7, branch['course'],
                   fontsize=7, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.15', facecolor=badge_color, 
                            edgecolor='none', alpha=0.8),
                   color='white', fontweight='bold')
        
        # Ligne vers le centre
        ax.plot([branch['x'], center_x], [branch['y'], center_y], 
               color=COLORS['arrow'], linewidth=1.5, alpha=0.5, zorder=0)
    
    # Connexions entre domaines (dépendances)
    connections = [
        (('Search &\nPlanning', 2, 8), ('Représentation\n& Raisonnement', 6, 9)),
        (('Raisonnement\nProbabiliste', 12, 5), ('Machine\nLearning', 10.5, 8)),
        (('Vision par\nOrdinateur', 6, 1), ('Robotique', 2, 2)),
        (('Machine\nLearning', 10.5, 8), ('Traitement du\nLangage (NLP)', 10.5, 2)),
        (('Machine\nLearning', 10.5, 8), ('Vision par\nOrdinateur', 6, 1)),
    ]
    
    for (name1, x1, y1), (name2, x2, y2) in connections:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='<->',
                                  connectionstyle='arc3,rad=0.2',
                                  color=COLORS['arrow'],
                                  lw=1,
                                  alpha=0.3))
    
    # Légende
    legend_y = 0.3
    ax.text(0.5, legend_y, 'Couvert dans ce cours', fontsize=9, va='center')
    ax.add_patch(FancyBboxPatch((3.5, legend_y - 0.2), 0.4, 0.4,
                                boxstyle="round,pad=0.05",
                                facecolor='#4CAF50', edgecolor='none'))
    
    ax.text(5, legend_y, 'Connexions entre domaines', fontsize=9, va='center')
    ax.plot([8, 9], [legend_y, legend_y], color=COLORS['arrow'], 
           linewidth=1.5, alpha=0.5)
    
    # Configuration des axes
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-0.5, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Les Branches de l\'Intelligence Artificielle', 
                fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('fig_05_ai_branches.pdf')
    fig.savefig('fig_05_ai_branches.png')
    plt.close()
    print("Figure 05 générée: fig_05_ai_branches.pdf")
