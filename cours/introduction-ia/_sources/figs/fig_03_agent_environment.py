#!/usr/bin/env python3
"""
Figure 03: Schéma Agent-Environnement
Chapitre: S01 - Qu'est-ce que l'IA ?

Le cycle perception-action entre un agent et son environnement.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# Configuration globale
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'figure.figsize': (10, 7),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Couleurs
COLORS = {
    'agent': '#2E86AB',
    'agent_light': '#B8D4E3',
    'env': '#A23B72',
    'env_light': '#E3B8CF',
    'sensor': '#28A745',
    'actuator': '#F18F01',
    'arrow': '#343A40',
    'text': '#212121',
}

def create_figure():
    fig, ax = plt.subplots()
    
    # Agent (rectangle arrondi à gauche)
    agent_box = FancyBboxPatch((0.5, 2.5), 3.5, 3,
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                facecolor=COLORS['agent_light'],
                                edgecolor=COLORS['agent'],
                                linewidth=3)
    ax.add_patch(agent_box)
    ax.text(2.25, 5.2, 'AGENT', fontsize=14, fontweight='bold',
            ha='center', color=COLORS['agent'])
    
    # Composants internes de l'agent
    # Capteurs
    sensor_box = FancyBboxPatch((0.8, 4.3), 1.2, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor='white',
                                 edgecolor=COLORS['sensor'],
                                 linewidth=2)
    ax.add_patch(sensor_box)
    ax.text(1.4, 4.7, 'Capteurs', fontsize=10, ha='center', color=COLORS['sensor'])
    
    # Fonction de décision
    decision_box = FancyBboxPatch((1.5, 3.0), 1.5, 1.0,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white',
                                   edgecolor=COLORS['agent'],
                                   linewidth=2)
    ax.add_patch(decision_box)
    ax.text(2.25, 3.5, 'Fonction\nde décision', fontsize=9, ha='center', 
            color=COLORS['agent'], linespacing=0.9)
    
    # Actuateurs
    actuator_box = FancyBboxPatch((2.5, 4.3), 1.2, 0.8,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white',
                                   edgecolor=COLORS['actuator'],
                                   linewidth=2)
    ax.add_patch(actuator_box)
    ax.text(3.1, 4.7, 'Actuateurs', fontsize=10, ha='center', color=COLORS['actuator'])
    
    # Flèches internes à l'agent
    ax.annotate('', xy=(2.0, 4.0), xytext=(1.6, 4.3),
                arrowprops=dict(arrowstyle='->', color=COLORS['sensor'], lw=1.5))
    ax.annotate('', xy=(2.8, 4.3), xytext=(2.5, 4.0),
                arrowprops=dict(arrowstyle='->', color=COLORS['actuator'], lw=1.5))
    
    # Environnement (rectangle arrondi à droite)
    env_box = FancyBboxPatch((5.5, 2.5), 3.5, 3,
                              boxstyle="round,pad=0.1,rounding_size=0.3",
                              facecolor=COLORS['env_light'],
                              edgecolor=COLORS['env'],
                              linewidth=3)
    ax.add_patch(env_box)
    ax.text(7.25, 5.2, 'ENVIRONNEMENT', fontsize=14, fontweight='bold',
            ha='center', color=COLORS['env'])
    
    # État dans l'environnement
    state_box = FancyBboxPatch((6.2, 3.2), 2.0, 1.6,
                                boxstyle="round,pad=0.05",
                                facecolor='white',
                                edgecolor=COLORS['env'],
                                linewidth=2)
    ax.add_patch(state_box)
    ax.text(7.2, 4.0, 'État', fontsize=11, ha='center', color=COLORS['env'])
    
    # Flèche Perception (de l'environnement vers l'agent)
    ax.annotate('', xy=(0.8, 4.7), xytext=(5.5, 4.7),
                arrowprops=dict(arrowstyle='<-',
                               connectionstyle='arc3,rad=0.3',
                               color=COLORS['sensor'],
                               lw=2.5))
    ax.text(3.0, 6.2, 'Perception', fontsize=12, fontweight='bold',
            ha='center', color=COLORS['sensor'])
    
    # Flèche Action (de l'agent vers l'environnement)
    ax.annotate('', xy=(5.5, 3.3), xytext=(3.7, 3.3),
                arrowprops=dict(arrowstyle='->',
                               connectionstyle='arc3,rad=0.3',
                               color=COLORS['actuator'],
                               lw=2.5))
    ax.text(4.6, 1.5, 'Action', fontsize=12, fontweight='bold',
            ha='center', color=COLORS['actuator'])
    
    # Annotations explicatives
    ax.text(0.3, 1.8, "• Perçoit l'environnement\n• Décide de l'action\n• Exécute l'action",
            fontsize=9, color=COLORS['agent'], va='top')
    
    ax.text(5.3, 1.8, "• Reçoit l'action\n• Change d'état\n• Génère nouvelle perception",
            fontsize=9, color=COLORS['env'], va='top')
    
    # Encadré PEAS
    peas_text = ("PEAS Framework:\n"
                 "P = Performance (mesure de succès)\n"
                 "E = Environment (contexte)\n"
                 "A = Actuators (moyens d'action)\n"
                 "S = Sensors (moyens de perception)")
    bbox_props = dict(boxstyle="round,pad=0.4", facecolor='#F5F5F5', 
                      edgecolor='gray', alpha=0.9)
    ax.text(4.75, 0.3, peas_text, fontsize=9, ha='center', va='bottom',
            bbox=bbox_props, linespacing=1.3)
    
    # Configuration des axes
    ax.set_xlim(0, 9.5)
    ax.set_ylim(0, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Le Cycle Agent-Environnement', fontsize=14, pad=15)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('fig_03_agent_environment.pdf')
    fig.savefig('fig_03_agent_environment.png')
    plt.close()
    print("Figure 03 générée: fig_03_agent_environment.pdf")
