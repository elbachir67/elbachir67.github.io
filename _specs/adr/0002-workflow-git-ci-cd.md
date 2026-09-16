# ADR-0002 — Workflow : Scrum allégé, GitHub Flow, CI/CD

**Statut :** Accepté · **Décideur :** PO

## Contexte
Un seul humain (PO) et deux agents IA (Claude chat pour les specs, Claude Code pour le développement).
Risque principal : du code ou du contenu produit sans contrôle.

## Décision
- **Scrum allégé** : backlog versionné, sprints d'une semaine, validation PO à chaque story, revue et rétrospective en fin de sprint.
- **GitHub Flow** : `main` protégée et toujours déployable ; une branche et une PR par story.
- **Conventional Commits** avec référence à la story (`US-XX`).
- **CI** sur chaque PR : rendu Quarto + vérification des liens.
- **CD** au merge sur `main` : publication automatique sur `gh-pages`.
- Seul le PO merge.

## Conséquences
- (+) Traçabilité complète story → issue → PR → commit → déploiement.
- (+) Aucun changement non relu en production.
- (−) Chaque story impose un point d'arrêt : c'est volontaire.
