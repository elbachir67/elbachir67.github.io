#!/usr/bin/env python3
"""
Synthèse Figure 04: Types d'Agents - Progression
Inspiré des figures du chapitre 2 d'AIMA
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.figsize': (14, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_figure():
    fig, ax = plt.subplots()
    
    # Définition des types d'agents
    agents = [
        {
            'name': 'Réflexe Simple',
            'x': 1, 'color': '#ff7043',
            'components': ['Règles\ncondition-action'],
            'percept': 'Percept actuel',
            'example': 'Thermostat',
            'limits': 'Env. pleinement observable'
        },
        {
            'name': 'Basé sur Modèle',
            'x': 4, 'color': '#ffa726',
            'components': ['État interne', 'Modèle du monde'],
            'percept': 'Percept + Historique',
            'example': 'Robot aspirateur',
            'limits': 'Nécessite modèle correct'
        },
        {
            'name': 'Basé sur Buts',
            'x': 7, 'color': '#66bb6a',
            'components': ['But explicite', 'Planification'],
            'percept': 'Percept + But',
            'example': 'GPS navigation',
            'limits': 'Objectif binaire'
        },
        {
            'name': 'Basé sur Utilité',
            'x': 10, 'color': '#42a5f5',
            'components': ['Fonction d\'utilité', 'Maximisation'],
            'percept': 'Percept + Préférences',
            'example': 'Taxi autonome',
            'limits': 'Calcul coûteux'
        },
        {
            'name': 'Apprenant',
            'x': 13, 'color': '#ab47bc',
            'components': ['Apprentissage', 'Exploration', 'Critique'],
            'percept': 'Percept + Feedback',
            'example': 'AlphaGo',
            'limits': 'Nécessite expérience'
        }
    ]
    
    y_base = 4
    box_width = 2.2
    box_height = 3
    
    for agent in agents:
        x = agent['x']
        color = agent['color']
        
        # Boîte principale
        box = FancyBboxPatch((x - box_width/2, y_base - box_height/2), 
                              box_width, box_height,
                              boxstyle="round,pad=0.03,rounding_size=0.2",
                              facecolor=color, alpha=0.2,
                              edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Nom de l'agent
        ax.text(x, y_base + 1.2, agent['name'], ha='center', va='center',
                fontsize=10, fontweight='bold', color=color)
        
        # Composants
        y_comp = y_base + 0.5
        for comp in agent['components']:
            ax.text(x, y_comp, comp, ha='center', va='center',
                    fontsize=8, style='italic')
            y_comp -= 0.5
        
        # Exemple
        ax.text(x, y_base - 1.0, f"Ex: {agent['example']}", ha='center',
                va='center', fontsize=8, color='#666',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                         edgecolor='#ddd', alpha=0.8))
    
    # Flèches de progression
    for i in range(len(agents) - 1):
        x1 = agents[i]['x'] + box_width/2 + 0.1
        x2 = agents[i+1]['x'] - box_width/2 - 0.1
        ax.annotate('', xy=(x2, y_base), xytext=(x1, y_base),
                    arrowprops=dict(arrowstyle='->', color='#666', lw=2))
    
    # Axe de complexité
    ax.annotate('', xy=(14.5, y_base - 2), xytext=(0.5, y_base - 2),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    ax.text(7.5, y_base - 2.5, 'Complexité croissante', ha='center',
            fontsize=10, fontweight='bold')
    
    # Tableau des capacités
    cap_y = 0.5
    capacities = ['Mémoire', 'Planification', 'Utilité', 'Apprentissage']
    
    ax.text(0.5, cap_y, 'Capacités:', ha='left', va='center',
            fontsize=10, fontweight='bold')
    
    cap_matrix = [
        ['Non', 'Oui', 'Oui', 'Oui', 'Oui'],  # Mémoire
        ['Non', 'Non', 'Oui', 'Oui', 'Oui'],  # Planification
        ['Non', 'Non', 'Non', 'Oui', 'Oui'],  # Utilité
        ['Non', 'Non', 'Non', 'Non', 'Oui'],  # Apprentissage
    ]
    
    for i, cap in enumerate(capacities):
        ax.text(0.5, cap_y - 0.5 - i * 0.4, cap, ha='left', va='center',
                fontsize=8)
        for j, val in enumerate(cap_matrix[i]):
            x = agents[j]['x']
            color = '#28A745' if val == 'Oui' else '#dc3545'
            ax.text(x, cap_y - 0.5 - i * 0.4, val, ha='center', va='center',
                    fontsize=7, color=color, fontweight='bold')
    
    # Environnements appropriés
    env_y = -1.5
    ax.text(7.5, env_y, 'Environnements appropriés:', ha='center',
            fontsize=10, fontweight='bold')
    
    envs = [
        'Plein. obs.\nDéterministe',
        'Partiellement\nobservable',
        'Buts\nexplicites',
        'Multi-objectifs\nIncertitude',
        'Inconnu\nAdaptation'
    ]
    
    for i, env in enumerate(envs):
        ax.text(agents[i]['x'], env_y - 0.6, env, ha='center', va='center',
                fontsize=7, color=agents[i]['color'])
    
    # Configuration
    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-3, 7)
    ax.axis('off')
    
    ax.set_title('Progression des Types d\'Agents (AIMA Ch.2, §2.4)\n'
                 'Du plus simple au plus sophistiqué',
                 fontsize=12, fontweight='bold', pad=15)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('synth_fig_04_agent_types.pdf')
    fig.savefig('synth_fig_04_agent_types.png')
    plt.close()
    print("Figure générée: synth_fig_04_agent_types.pdf")
