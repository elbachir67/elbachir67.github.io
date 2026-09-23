#!/usr/bin/env python3
"""
Génère toutes les figures pour la Séance 1
"""

import subprocess
import sys
import os

# S'assurer qu'on est dans le bon répertoire
os.chdir(os.path.dirname(os.path.abspath(__file__)))

figures = [
    'fig_01_ai_timeline.py',
    'fig_02_ai_ml_dl_venn.py',
    'fig_03_agent_environment.py',
    'fig_04_agent_types.py',
    'fig_05_ai_branches.py',
]

print("=" * 50)
print("Génération des figures pour la Séance 1")
print("=" * 50)

for fig in figures:
    print(f"\nGénération de {fig}...")
    result = subprocess.run([sys.executable, fig], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ Succès")
    else:
        print(f"  ✗ Erreur: {result.stderr}")

print("\n" + "=" * 50)
print("Génération terminée!")
print("=" * 50)
