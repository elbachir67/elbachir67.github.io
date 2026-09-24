#!/usr/bin/env python3
"""
Synthèse Figure 01: Histoire de l'Intelligence Artificielle
Timeline détaillée avec les trois vagues et les jalons majeurs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'figure.figsize': (14, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def create_figure():
    fig, ax = plt.subplots()
    
    # Axe du temps
    years = np.arange(1940, 2030, 10)
    ax.set_xlim(1940, 2028)
    ax.set_ylim(-0.5, 3.5)
    
    # Ligne du temps
    ax.axhline(y=0, color='#343A40', linewidth=2, zorder=1)
    
    # Hivers de l'IA (zones grisées)
    winters = [(1974, 1980, 'Premier hiver'), (1987, 1993, 'Second hiver')]
    for start, end, label in winters:
        ax.axvspan(start, end, alpha=0.3, color='#6c757d', zorder=0)
        ax.text((start + end) / 2, 3.3, label, ha='center', fontsize=8, 
                style='italic', color='#495057')
    
    # Les trois vagues
    waves = [
        (1956, 1974, 'IA Symbolique', '#2E86AB', 0.5),
        (1980, 1987, 'Systèmes Experts', '#A23B72', 0.5),
        (2010, 2025, 'Deep Learning', '#28A745', 0.5)
    ]
    
    for start, end, label, color, height in waves:
        rect = mpatches.FancyBboxPatch((start, -0.1), end - start, height,
                                        boxstyle="round,pad=0.02",
                                        facecolor=color, alpha=0.3,
                                        edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text((start + end) / 2, height / 2 - 0.1, label, ha='center', 
                va='center', fontsize=9, fontweight='bold', color=color)
    
    # Jalons majeurs
    milestones = [
        (1943, 'McCulloch-Pitts\n(neurone)', 1.0),
        (1950, 'Turing\n"Computing..."', 1.5),
        (1956, 'Dartmouth\nNaissance IA', 2.0),
        (1958, 'Perceptron\n(Rosenblatt)', 1.2),
        (1966, 'ELIZA\n(Weizenbaum)', 1.8),
        (1969, 'Perceptrons\n(Minsky)', 2.3),
        (1973, 'Rapport\nLighthill', 1.5),
        (1980, 'MYCIN\nXCON', 1.3),
        (1986, 'Backprop\n(Hinton)', 2.0),
        (1997, 'Deep Blue\nvs Kasparov', 1.5),
        (2012, 'AlexNet\nImageNet', 2.2),
        (2016, 'AlphaGo\nvs Lee Sedol', 2.8),
        (2017, 'Transformer\nAttention', 1.8),
        (2022, 'ChatGPT\nGPT-4', 2.5)
    ]
    
    for year, label, y in milestones:
        ax.plot(year, 0, 'o', markersize=8, color='#343A40', zorder=3)
        ax.plot([year, year], [0, y - 0.2], '-', color='#adb5bd', linewidth=1, zorder=2)
        ax.text(year, y, label, ha='center', va='bottom', fontsize=7,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                         edgecolor='#dee2e6', alpha=0.9))
    
    # Configuration
    ax.set_xlabel('Année', fontsize=10)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_title('Histoire de l\'Intelligence Artificielle : Trois Vagues et Deux Hivers',
                 fontsize=12, fontweight='bold', pad=15)
    
    # Légende
    legend_elements = [
        mpatches.Patch(color='#2E86AB', alpha=0.3, label='Vague 1: IA Symbolique'),
        mpatches.Patch(color='#A23B72', alpha=0.3, label='Vague 2: Systèmes Experts'),
        mpatches.Patch(color='#28A745', alpha=0.3, label='Vague 3: Deep Learning'),
        mpatches.Patch(color='#6c757d', alpha=0.3, label='Hivers de l\'IA')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('synth_fig_01_ai_history.pdf')
    fig.savefig('synth_fig_01_ai_history.png')
    plt.close()
    print("Figure générée: synth_fig_01_ai_history.pdf")
