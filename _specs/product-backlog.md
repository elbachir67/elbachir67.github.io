# Product Backlog — site-perso

Priorité : MoSCoW (M = Must, S = Should, C = Could). Estimation : points Fibonacci.
Les critères d'acceptation détaillés sont rédigés au sprint planning (affinage progressif).

## Objectif produit

Un hub académique en ligne, maintenable par un seul enseignant-chercheur, où les cours
sont publiés nativement, où Claude assiste la publication, et où chaque cours dispose
d'un tuteur IA encadré.

## Epics

| Epic | Titre | Valeur |
|---|---|---|
| EP1 | Socle et CI/CD | Livrer vite et sans casse |
| EP2 | Vitrine académique | Visibilité recherche et institutionnelle |
| EP3 | Cours natifs | Remplacer les PDF par des pages vivantes |
| EP4 | Publication assistée par Claude | Réduire le coût de publication |
| EP5 | Blog | Vulgarisation, rayonnement |
| EP6 | Tuteur IA par cours | Accompagnement des étudiants + données de recherche AI4Ed |

## Backlog

| ID | Epic | User story (résumé) | Prio | Pts | Sprint |
|---|---|---|---|---|---|
| US-01 | EP1 | Initialiser le dépôt et le projet Quarto | M | 3 | 1 |
| US-02 | EP1 | Intégration continue sur chaque PR (rendu + liens) | M | 3 | 1 |
| US-03 | EP1 | Déploiement continu sur GitHub Pages au merge | M | 2 | 1 |
| US-04 | EP1 | Gouvernance du dépôt (protection `main`, templates, labels, issues) | M | 1 | 1 |
| US-07 | EP2 | Page d'accueil réelle (bio, photo, affiliations, liens) | M | 2 | 1 |
| US-06 | EP1 | Charte graphique (thème, typo, mode sombre) | S | 3 | 2 |
| US-08 | EP2 | Page Recherche en anglais (axes, projets) | M | 3 | 2 |
| US-09 | EP2 | Publications générées depuis BibTeX | M | 3 | 2 |
| US-10 | EP2 | Page CV avec PDF FR (version anglaise : US-36) | M | 2 | 2 |
| US-11 | EP2 | Page Enseignement : catalogue généré depuis les métadonnées des cours | M | 2 | 2 |
| US-12 | EP2 | Contact (email protégé, sans téléphone) | S | 1 | 2 |
| US-13 | EP2 | SEO et métadonnées (Open Graph, sitemap) | S | 2 | 2 |
| US-34 | EP1 | Montée de version Quarto 1.10 | S | 1 | 2 |
| US-37 | EP2 | Spike + ADR-0003 : architecture multilingue Quarto (avant US-36) | M | 2 | 3 |
| US-36 | EP2 | Site bilingue FR/EN avec sélecteur de langue (inclut l'ex-US-35, CV anglais) | M | 8 | 3 |
| US-14 | EP3 | Gabarit de cours (structure, métadonnées, navigation chapitres) | M | 5 | 3 |
| US-15 | EP3 | Correspondance LaTeX → Quarto (tcolorbox → callouts, TikZ → SVG, code) | M | 8 | 3 |
| US-16 | EP3 | Migration du cours pilote : chapitre 1 | M | 5 | 3 |
| US-18 | EP3 | Figures Python exécutées et gelées (`freeze`) | M | 2 | 3 |
| US-17 | EP3 | PDF du cours généré depuis les mêmes sources | S | 5 | 4 |
| US-19 | EP3 | Intégration des capsules YouTube | C | 1 | 4 |
| US-20 | EP4 | Commande Claude Code `/importer-chapitre` (.tex → .qmd) | M | 5 | 4 |
| US-21 | EP4 | Commande `/resume` (.tex/.pdf → article résumé) | M | 3 | 4 |
| US-22 | EP4 | Commande `/nouvel-article` (blog) | S | 2 | 4 |
| US-25 | EP5 | Blog : listing, catégories, flux RSS | S | 2 | 4 |
| US-26 | EP6 | Spike + ADR architecture du tuteur | M | 2 | 5 |
| US-27 | EP6 | Proxy API sécurisé (Cloudflare Worker, clé en secret, CORS restreint) | M | 5 | 5 |
| US-28 | EP6 | Contexte du cours généré au build (index JSON du contenu) | M | 5 | 5 |
| US-29 | EP6 | Widget de chat sur les pages de cours | M | 3 | 5 |
| US-30 | EP6 | Garde-fous (limite de requêtes, posture socratique, refus des corrigés) | M | 5 | 5 |
| US-31 | EP6 | Déploiement continu du Worker | M | 2 | 5 |
| US-23 | EP4 | GitHub Action Claude : issue labellisée → PR | C | 5 | 6 |
| US-24 | EP4 | Aperçu déployé par PR | C | 3 | 6 |
| US-32 | EP6 | Journalisation anonymisée des questions + consentement | S | 5 | 6 |
| US-33 | EP6 | Tableau de bord enseignant (concepts bloquants) | C | 8 | 6 |
| US-05 | EP1 | Nom de domaine personnalisé + HTTPS | S | 2 | — |

## Critères d'acceptation fixés par le PO avant le sprint planning

### US-36 — Site bilingue FR/EN avec sélecteur de langue (Must, 8 pts, Sprint 3, après US-37)

Décision du PO : site bilingue FR/EN. Jusqu'au Sprint 3, rien ne change : chaque page reste dans sa
langue actuelle (Recherche en anglais, le reste en français).

- [ ] Chaque page existe en français et en anglais.
- [ ] Un sélecteur de langue dans la barre de navigation mène à la page équivalente dans l'autre langue.
- [ ] Les URL sont stables : `/` pour le français, `/en/` pour l'anglais.
- [ ] Les attributs `lang` et `hreflang` sont corrects.
- [ ] La CI échoue si une page n'a pas son équivalent dans l'autre langue.
- [ ] Reprend l'ex-US-35 (version anglaise du CV, fusionnée et retirée) : le CV existe aussi en anglais.

### US-37 — Spike + ADR-0003 : architecture multilingue Quarto (Must, 2 pts, Sprint 3, avant US-36)

- [ ] Comparaison de trois options : arborescences parallèles maison, profils Quarto, babelquarto.
- [ ] Contraintes prises en compte : pas de R en CI, maintenance par un seul PO.
- [ ] Décision consignée dans `_specs/adr/0003-*.md` (ADR-0003), avant le démarrage d'US-36.

## Roadmap

| Sprint | Objectif | Pts |
|---|---|---|
| 1 | Site minimal en ligne, déployé automatiquement | 11 |
| 2 | Vitrine académique complète | 17 |
| 3 | Premier chapitre de cours natif | 30 |
| 4 | Chaîne de publication assistée + blog | 18 |
| 5 | Tuteur IA MVP sur le cours pilote | 22 |
| 6 | Automatisation avancée + analytics | 21 |

Durée d'un sprint : 1 semaine, ajustable par le PO selon la charge d'enseignement.
