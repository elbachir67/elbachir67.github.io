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
| US-05 | EP1 | Nom de domaine personnalisé + HTTPS | S | 2 | 2 |
| US-06 | EP1 | Charte graphique (thème, typo, mode sombre) | S | 3 | 2 |
| US-08 | EP2 | Page Recherche en anglais (axes, projets) | M | 3 | 2 |
| US-09 | EP2 | Publications générées depuis BibTeX | M | 3 | 2 |
| US-10 | EP2 | Page CV avec PDF FR/EN | M | 2 | 2 |
| US-11 | EP2 | Page Enseignement : catalogue généré depuis les métadonnées des cours | M | 2 | 2 |
| US-12 | EP2 | Contact (email protégé, sans téléphone) | S | 1 | 2 |
| US-13 | EP2 | SEO et métadonnées (Open Graph, sitemap) | S | 2 | 2 |
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
| US-34 | EP1 | Montée de version Quarto 1.10 | S | 1 | — |

## Roadmap

| Sprint | Objectif | Pts |
|---|---|---|
| 1 | Site minimal en ligne, déployé automatiquement | 11 |
| 2 | Vitrine académique complète | 15 |
| 3 | Premier chapitre de cours natif | 20 |
| 4 | Chaîne de publication assistée + blog | 18 |
| 5 | Tuteur IA MVP sur le cours pilote | 22 |
| 6 | Automatisation avancée + analytics | 21 |

Durée d'un sprint : 1 semaine, ajustable par le PO selon la charge d'enseignement.
