#!/usr/bin/env python3
"""
Figure 04: Les différents types d'agents
Chapitre: S01 - Qu'est-ce que l'IA ?

Progression du plus simple (réflexe) au plus sophistiqué (apprenant).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Configuration globale
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'figure.figsize': (14, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Couleurs
COLORS = {
    'reflexe': '#FFCDD2',
    'reflexe_border': '#C62828',
    'modele': '#FFE0B2',
    'modele_border': '#EF6C00',
    'but': '#FFF9C4',
    'but_border': '#F9A825',
    'utilite': '#C8E6C9',
    'utilite_border': '#2E7D32',
    'apprenant': '#BBDEFB',
    'apprenant_border': '#1565C0',
    'arrow': '#546E7A',
    'text': '#212121',
}

def create_figure():
    fig, ax = plt.subplots()
    
    # Positions des 5 types d'agents
    agents = [
        {'name': 'Agent Réflexe\nSimple', 'x': 1, 'color': COLORS['reflexe'], 
         'border': COLORS['reflexe_border'],
         'desc': 'Règles condition→action\nSur perception actuelle',
         'example': 'Thermostat'},
        {'name': 'Agent Basé\nsur Modèle', 'x': 3.5, 'color': COLORS['modele'],
         'border': COLORS['modele_border'],
         'desc': 'Maintient un état interne\nModèle de l\'environnement',
         'example': 'Aspirateur avec mémoire'},
        {'name': 'Agent Basé\nsur Buts', 'x': 6, 'color': COLORS['but'],
         'border': COLORS['but_border'],
         'desc': 'Objectifs explicites\nRecherche et planification',
         'example': 'GPS Navigator'},
        {'name': 'Agent Basé\nsur Utilité', 'x': 8.5, 'color': COLORS['utilite'],
         'border': COLORS['utilite_border'],
         'desc': 'Fonction d\'utilité\nOptimisation',
         'example': 'Trading algorithmique'},
        {'name': 'Agent\nApprenant', 'x': 11, 'color': COLORS['apprenant'],
         'border': COLORS['apprenant_border'],
         'desc': 'Amélioration continue\nApprentissage par expérience',
         'example': 'AlphaGo'},
    ]
    
    y_main = 4.5
    box_width = 2
    box_height = 1.8
    
    # Dessiner les boîtes des agents
    for agent in agents:
        # Boîte principale
        box = FancyBboxPatch((agent['x'] - box_width/2, y_main - box_height/2), 
                             box_width, box_height,
                             boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=agent['color'],
                             edgecolor=agent['border'],
                             linewidth=2.5)
        ax.add_patch(box)
        
        # Nom de l'agent
        ax.text(agent['x'], y_main + 0.3, agent['name'], 
                fontsize=10, fontweight='bold', ha='center', va='center',
                color=agent['border'])
        
        # Description
        ax.text(agent['x'], y_main - 0.5, agent['desc'], 
                fontsize=8, ha='center', va='center',
                color=COLORS['text'], linespacing=1.1)
        
        # Exemple
        ax.text(agent['x'], y_main - box_height/2 - 0.4, f"Ex: {agent['example']}", 
                fontsize=8, ha='center', va='top',
                color='gray', style='italic')
    
    # Flèches de progression
    for i in range(len(agents) - 1):
        x_start = agents[i]['x'] + box_width/2 + 0.1
        x_end = agents[i+1]['x'] - box_width/2 - 0.1
        ax.annotate('', xy=(x_end, y_main), xytext=(x_start, y_main),
                   arrowprops=dict(arrowstyle='->',
                                  color=COLORS['arrow'],
                                  lw=2,
                                  connectionstyle='arc3,rad=0'))
    
    # Flèche de progression globale (en haut)
    ax.annotate('', xy=(11.5, 6.3), xytext=(0.5, 6.3),
               arrowprops=dict(arrowstyle='->',
                              color=COLORS['arrow'],
                              lw=3))
    ax.text(6, 6.6, 'Sophistication croissante', fontsize=11, 
            ha='center', fontweight='bold', color=COLORS['arrow'])
    
    # Encadrés pour les capacités ajoutées
    capacities = [
        {'x': 2.25, 'text': '+ État\ninterne'},
        {'x': 4.75, 'text': '+ Buts\nexplicites'},
        {'x': 7.25, 'text': '+ Fonction\nd\'utilité'},
        {'x': 9.75, 'text': '+ Apprentissage'},
    ]
    
    for cap in capacities:
        ax.text(cap['x'], y_main + 1.5, cap['text'], 
                fontsize=9, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                         edgecolor='gray', alpha=0.8))
    
    # Tableau comparatif en bas
    table_y = 1.2
    headers = ['', 'État\ninterne', 'Buts', 'Utilité', 'Apprend']
    row_labels = ['Réflexe', 'Modèle', 'But', 'Utilité', 'Apprenant']
    
    # Matrice de caractéristiques (1 = oui, 0 = non)
    features = [
        [0, 0, 0, 0],  # Réflexe
        [1, 0, 0, 0],  # Modèle
        [1, 1, 0, 0],  # But
        [1, 1, 1, 0],  # Utilité
        [1, 1, 1, 1],  # Apprenant
    ]
    
    # Dessiner le tableau
    cell_width = 1.2
    cell_height = 0.5
    start_x = 4
    
    # En-têtes
    for j, header in enumerate(headers):
        ax.text(start_x + j * cell_width, table_y + 0.8, header,
               fontsize=8, ha='center', va='center', fontweight='bold')
    
    # Données
    for i, (label, row) in enumerate(zip(row_labels, features)):
        y = table_y - i * cell_height
        ax.text(start_x, y, label, fontsize=8, ha='center', va='center')
        for j, val in enumerate(row):
            symbol = '✓' if val else '—'
            color = '#2E7D32' if val else '#BDBDBD'
            ax.text(start_x + (j+1) * cell_width, y, symbol,
                   fontsize=10, ha='center', va='center', color=color)
    
    # Lignes du tableau
    for i in range(7):
        y = table_y + 0.55 - i * cell_height
        ax.plot([start_x - 0.6, start_x + 5 * cell_width - 0.6], [y, y], 
               'gray', lw=0.5, alpha=0.5)
    
    # Configuration des axes
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-1.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Types d\'Agents : Du Plus Simple au Plus Sophistiqué', 
                fontsize=13, pad=10)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('fig_04_agent_types.pdf')
    fig.savefig('fig_04_agent_types.png')
    plt.close()
    print("Figure 04 générée: fig_04_agent_types.pdf")
