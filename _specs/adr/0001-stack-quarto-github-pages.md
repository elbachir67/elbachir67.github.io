# ADR-0001 — Stack : Quarto + GitHub Pages

**Statut :** Accepté · **Décideur :** PO

## Contexte
Remplacer Academia.edu Premium (~150 $/an) par un site maîtrisé, peu coûteux, adapté à du
contenu scientifique (maths, code, figures Python) et maintenu par une seule personne assistée par Claude.

## Décision
Site statique Quarto hébergé sur GitHub Pages, sources en `.qmd`, exécution Python gelée (`freeze`).

## Alternatives écartées
- Wix / Squarespace : payant, pas de contrôle, pas de code exécutable.
- WordPress : maintenance et sécurité trop coûteuses.
- al-folio (Jekyll) : très bon pour les publications, mais chaîne Ruby fragile et faible support Jupyter.
- Hugo Blox : ruptures de version fréquentes.
- Next.js : surdimensionné pour du contenu ; réservé aux besoins dynamiques (voir tuteur, EP6).

## Conséquences
- (+) Coût quasi nul, sources texte versionnées, idéal pour la génération par Claude Code.
- (+) Un même contenu produit HTML et PDF.
- (−) Aucune logique serveur : le tuteur IA nécessitera un service séparé (ADR dédié au Sprint 5).
