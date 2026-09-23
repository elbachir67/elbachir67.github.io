#!/usr/bin/env python3
"""
Synthèse Figure 03: Le cycle Agent-Environnement
Inspiré de AIMA Figure 2.1 avec détails sur PEAS
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.figsize': (12, 7),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_figure():
    fig, ax = plt.subplots()
    
    # Boîte Agent
    agent_box = FancyBboxPatch((1, 2), 3, 2.5,
                                boxstyle="round,pad=0.05,rounding_size=0.3",
                                facecolor='#e3f2fd', edgecolor='#2E86AB',
                                linewidth=3, zorder=2)
    ax.add_patch(agent_box)
    ax.text(2.5, 3.8, 'AGENT', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#2E86AB')
    ax.text(2.5, 3.2, 'Fonction d\'agent:\nf : P* → A', ha='center', va='center',
            fontsize=10, family='monospace')
    ax.text(2.5, 2.5, '(programme + architecture)', ha='center', va='center',
            fontsize=8, style='italic', color='#666')
    
    # Boîte Environnement
    env_box = FancyBboxPatch((6, 1.5), 4, 3.5,
                              boxstyle="round,pad=0.05,rounding_size=0.3",
                              facecolor='#fce4ec', edgecolor='#A23B72',
                              linewidth=3, zorder=2)
    ax.add_patch(env_box)
    ax.text(8, 4.3, 'ENVIRONNEMENT', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#A23B72')
    ax.text(8, 3.5, 'État du monde', ha='center', va='center', fontsize=10)
    ax.text(8, 2.8, '• Observable / Partiellement', ha='center', va='center', fontsize=8)
    ax.text(8, 2.4, '• Déterministe / Stochastique', ha='center', va='center', fontsize=8)
    ax.text(8, 2.0, '• Statique / Dynamique', ha='center', va='center', fontsize=8)
    
    # Capteurs (Sensors)
    sensor_box = FancyBboxPatch((3.5, 4.8), 1.5, 0.8,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#fff3e0', edgecolor='#F18F01',
                                 linewidth=2)
    ax.add_patch(sensor_box)
    ax.text(4.25, 5.2, 'Capteurs', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#e65100')
    
    # Actuateurs
    actuator_box = FancyBboxPatch((3.5, 0.8), 1.5, 0.8,
                                   boxstyle="round,pad=0.02",
                                   facecolor='#e8f5e9', edgecolor='#28A745',
                                   linewidth=2)
    ax.add_patch(actuator_box)
    ax.text(4.25, 1.2, 'Actuateurs', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#2e7d32')
    
    # Flèches
    # Percepts (Env -> Capteurs -> Agent)
    ax.annotate('', xy=(5, 5.2), xytext=(6, 5.2),
                arrowprops=dict(arrowstyle='->', color='#F18F01', lw=2))
    ax.annotate('', xy=(3.5, 4.5), xytext=(4.25, 4.8),
                arrowprops=dict(arrowstyle='->', color='#F18F01', lw=2))
    ax.text(5.5, 5.5, 'Percepts', ha='center', fontsize=9, color='#F18F01',
            fontweight='bold')
    
    # Actions (Agent -> Actuateurs -> Env)
    ax.annotate('', xy=(5, 1.2), xytext=(4, 1.2),
                arrowprops=dict(arrowstyle='->', color='#28A745', lw=2))
    ax.annotate('', xy=(6, 1.2), xytext=(5, 1.2),
                arrowprops=dict(arrowstyle='->', color='#28A745', lw=2))
    ax.text(5.5, 0.7, 'Actions', ha='center', fontsize=9, color='#28A745',
            fontweight='bold')
    
    # Mesure de performance
    perf_box = FancyBboxPatch((0.2, 5.5), 2.5, 0.8,
                               boxstyle="round,pad=0.02",
                               facecolor='#f3e5f5', edgecolor='#7b1fa2',
                               linewidth=2)
    ax.add_patch(perf_box)
    ax.text(1.45, 5.9, 'Performance', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#7b1fa2')
    ax.annotate('', xy=(2.5, 5.5), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle='->', color='#7b1fa2', lw=1.5,
                               connectionstyle='arc3,rad=0.3'))
    
    # Cadre PEAS en bas
    peas_y = -0.5
    ax.text(5, peas_y, 'Cadre PEAS (Russell & Norvig, AIMA Ch.2)', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    peas_items = [
        ('P', 'Performance', 'Comment mesurer le succès?', '#7b1fa2'),
        ('E', 'Environment', 'Dans quel monde opère l\'agent?', '#A23B72'),
        ('A', 'Actuators', 'Comment agir?', '#28A745'),
        ('S', 'Sensors', 'Comment percevoir?', '#F18F01'),
    ]
    
    for i, (letter, name, desc, color) in enumerate(peas_items):
        x = 1 + i * 2.5
        ax.text(x, peas_y - 0.6, f'{letter}', ha='center', va='center',
                fontsize=12, fontweight='bold', color=color)
        ax.text(x, peas_y - 1.0, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color=color)
        ax.text(x, peas_y - 1.4, desc, ha='center', va='center',
                fontsize=7, color='#666')
    
    # Configuration
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-2.5, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('Le Cycle Perception-Action et le Cadre PEAS\n'
                 '(Inspiré de AIMA Figure 2.1, p.37)',
                 fontsize=12, fontweight='bold', pad=10)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('synth_fig_03_agent_env.pdf')
    fig.savefig('synth_fig_03_agent_env.png')
    plt.close()
    print("Figure générée: synth_fig_03_agent_env.pdf")
