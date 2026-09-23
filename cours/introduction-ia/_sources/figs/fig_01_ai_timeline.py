#!/usr/bin/env python3
"""
Figure 01: Timeline des trois vagues de l'Intelligence Artificielle
Chapitre: S01 - Qu'est-ce que l'IA ?
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Configuration globale
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'figure.figsize': (12, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Couleurs
COLORS = {
    'wave1': '#2E86AB',      # Bleu - IA symbolique
    'wave2': '#A23B72',      # Rose - Connexionniste
    'wave3': '#28A745',      # Vert - Deep Learning
    'winter': '#E8E8E8',     # Gris clair - Hivers
    'dark': '#343A40',
}

def create_figure():
    fig, ax = plt.subplots()
    
    # Axe temporel
    years = np.arange(1950, 2030, 10)
    ax.set_xlim(1950, 2025)
    ax.set_ylim(0, 4)
    
    # Les trois vagues (hauteurs différentes pour montrer l'intensité)
    # Vague 1 : IA Symbolique (1956-1980)
    wave1_x = np.linspace(1956, 1987, 100)
    wave1_y = 2.5 * np.exp(-((wave1_x - 1970)**2) / 200) + 0.5
    ax.fill_between(wave1_x, 0, wave1_y, alpha=0.6, color=COLORS['wave1'], label='IA Symbolique')
    
    # Vague 2 : IA Connexionniste (1986-2012)
    wave2_x = np.linspace(1986, 2015, 100)
    wave2_y = 2.2 * np.exp(-((wave2_x - 1998)**2) / 180) + 0.5
    ax.fill_between(wave2_x, 0, wave2_y, alpha=0.6, color=COLORS['wave2'], label='IA Connexionniste / ML classique')
    
    # Vague 3 : Deep Learning (2010-présent)
    wave3_x = np.linspace(2010, 2025, 100)
    wave3_y = 3.5 * (1 - np.exp(-0.15*(wave3_x - 2010))) + 0.5
    ax.fill_between(wave3_x, 0, wave3_y, alpha=0.6, color=COLORS['wave3'], label='Deep Learning')
    
    # Hivers de l'IA (zones grisées)
    ax.axvspan(1974, 1980, alpha=0.3, color=COLORS['winter'], zorder=0)
    ax.axvspan(1987, 1993, alpha=0.3, color=COLORS['winter'], zorder=0)
    
    # Labels pour les hivers
    ax.text(1977, 3.7, "1er Hiver\nde l'IA", ha='center', va='top', fontsize=8, color='gray')
    ax.text(1990, 3.7, "2e Hiver\nde l'IA", ha='center', va='top', fontsize=8, color='gray')
    
    # Événements clés
    events = [
        (1956, 0.3, "Dartmouth\n(naissance IA)", 'left'),
        (1966, 1.8, "ELIZA", 'center'),
        (1976, 2.2, "MYCIN", 'center'),
        (1986, 1.0, "Backprop\nredécouverte", 'center'),
        (1997, 2.0, "Deep Blue\nbat Kasparov", 'center'),
        (2012, 1.5, "AlexNet", 'center'),
        (2016, 2.5, "AlphaGo", 'center'),
        (2022, 3.5, "ChatGPT", 'right'),
    ]
    
    for year, y, label, ha in events:
        ax.plot(year, y, 'ko', markersize=5, zorder=5)
        offset = 5 if ha == 'left' else (-5 if ha == 'right' else 0)
        ax.annotate(label, (year, y), textcoords="offset points", 
                   xytext=(offset, 10), ha=ha, fontsize=8, 
                   arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
    
    # Configuration des axes
    ax.set_xlabel('Année')
    ax.set_ylabel('Activité / Intérêt')
    ax.set_title('Les Trois Vagues de l\'Intelligence Artificielle')
    
    ax.set_xticks([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020])
    ax.set_yticks([])
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Annotations pour les périodes
    ax.annotate('', xy=(1956, 3.3), xytext=(1985, 3.3),
                arrowprops=dict(arrowstyle='<->', color=COLORS['wave1'], lw=2))
    ax.text(1970, 3.45, 'Vague 1: Symbolique', ha='center', fontsize=9, color=COLORS['wave1'])
    
    ax.annotate('', xy=(1986, 3.0), xytext=(2012, 3.0),
                arrowprops=dict(arrowstyle='<->', color=COLORS['wave2'], lw=2))
    ax.text(1999, 3.15, 'Vague 2: Connexionniste', ha='center', fontsize=9, color=COLORS['wave2'])
    
    ax.annotate('', xy=(2010, 2.7), xytext=(2025, 2.7),
                arrowprops=dict(arrowstyle='<->', color=COLORS['wave3'], lw=2))
    ax.text(2017, 2.85, 'Vague 3: Deep Learning', ha='center', fontsize=9, color=COLORS['wave3'])
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    fig = create_figure()
    fig.savefig('fig_01_ai_timeline.pdf')
    fig.savefig('fig_01_ai_timeline.png')
    plt.close()
    print("Figure 01 générée: fig_01_ai_timeline.pdf")
