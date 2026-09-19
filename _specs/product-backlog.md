# Product Backlog — site-perso

Priorité : MoSCoW (M = Must, S = Should, C = Could). Estimation : points Fibonacci.
Les critères d'acceptation détaillés sont rédigés au sprint planning (affinage progressif), dans
`_specs/sprints/sprint-XX.md`.

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
| US-37 | EP1 | Spike + ADR-0003 : architecture multilingue Quarto (avant US-36) | M | 2 | 3 |
| US-36 | EP1 | Site bilingue FR/EN avec sélecteur de langue (inclut l'ex-US-35, CV anglais) | M | 8 | 3 |
| US-14 | EP3 | Gabarit de cours (structure, métadonnées, navigation chapitres) | M | 5 | 3 |
| US-15 | EP3 | Conversion du deck Beamer en slides Quarto (ucad* → callouts, code, figures) | M | 8 | 3 |
| US-18 | EP3 | Figures Python exécutées et gelées (`freeze`) | M | 2 | 3 |
| US-16 | EP3 | Migration du cours pilote : slides du chapitre 1 | M | 5 | 3 |
| US-42 | EP1 | Accessibilité vérifiée en CI (axe-core sur les pages et les slides) | S | 3 | 4 |
| US-41 | EP1 | Conversion et gel vérifiés en CI | S | 2 | 4 |
| US-17 | EP3 | PDF du cours généré depuis les mêmes sources | S | 5 | 4 |
| US-19 | EP3 | Intégration des capsules YouTube | C | 1 | 4 |
| US-20 | EP4 | Commande Claude Code `/importer-chapitre` (.tex → .qmd) | M | 5 | 4 |
| US-21 | EP4 | Commande `/resume` (.tex/.pdf → article résumé) | M | 3 | 4 |
| US-22 | EP4 | Commande `/nouvel-article` (blog) | S | 2 | 4 |
| US-25 | EP5 | Blog : listing, catégories, flux RSS | S | 2 | 4 |
| US-26 | EP6 | Spike + ADR-0004 : architecture du tuteur (coût par question, anti-abus) | M | 2 | livrée |
| US-27 | EP6 | Service proxy sécurisé (Worker, clé en secret, CORS, code d'accès) | M | 5 | — |
| US-28 | EP6 | Contexte d'une séance produit au rendu, corrigés exclus | M | 5 | — |
| US-29 | EP6 | Widget de discussion sur les pages de séance (code d'accès, accessible) | M | 3 | — |
| US-30 | EP6 | Garde-fous pédagogiques et budgétaires (plafond global prioritaire) | M | 5 | — |
| US-31 | EP6 | Déploiement continu du Worker | M | 2 | — |
| US-23 | EP4 | GitHub Action Claude : issue labellisée → PR | C | 5 | 6 |
| US-24 | EP4 | Aperçu déployé par PR | C | 3 | 6 |
| US-32 | EP6 | Journalisation anonymisée des questions + consentement | S | 5 | 6 |
| US-33 | EP6 | Tableau de bord enseignant (concepts bloquants) | C | 8 | 6 |
| US-05 | EP1 | Nom de domaine personnalisé + HTTPS | S | 2 | — |
| US-38 | EP2 | Page Contact bilingue (formulaire non requis : email protégé, affiliations) | S | 2 | — |
| US-39 | EP1 | Traduire les données du CV et du catalogue des cours (et non les seuls libellés) | S | 3 | — |
| US-40 | EP3 | Page rédigée par chapitre, en complément du deck de slides | S | 5 | — |
| US-43 | EP3 | Contrôle de débordement des slides (échec si une slide dépasse le cadre) | S | 2 | 5 |
| US-44 | EP3 | Style matplotlib accordé à la charte, partagé par les cours | C | 2 | — |
| US-45 | EP3 | Notes du présentateur (`\note{}` → `::: {.notes}`) | C | 1 | — |
| US-46 | EP3 | Numérotation automatique des chapitres depuis le nom de fichier | C | 1 | — |
| US-47 | EP1 | Index de recherche par langue, sans ajustement du décalage Quarto | C | 2 | — |
| US-48 | EP3 | Page de garde des PDF de séance | S | 2 | 5 |
| US-49 | EP3 | Ressources par séance (lab, TD, notebook, corrigé) | M | 3 | 5 |
| US-50 | EP3 | Notebooks de lab rendus en page, avec téléchargement et ouverture dans Colab | S | 5 | 5 |
| US-51 | EP3 | Migration d'un deuxième cours : Programmation Python (L1) | M | 5 | 5 |
| US-52 | EP1 | Déploiement quotidien programmé (les dates de publication s'appliquent seules) | C | 1 | — |

### Stories décrites par le PO

Les critères d'acceptation d'**US-49**, **US-50** et **US-51** sont dans
[`sprint-05.md`](sprints/sprint-05.md) : ce qui suit n'est que le contexte que le PO a donné en plus.

**US-51 — Migration d'un deuxième cours.** Le cours retenu est **Programmation Python (L1)** : decks
Beamer avec le thème `beamerucad` et **notebooks Jupyter exécutés**, dont le PO fournira les sources.
C'est le même chemin d'import que le cours pilote, plus les notebooks (US-50).

**US-52 — Déploiement quotidien programmé.** Un corrigé rejoint le site au premier rendu qui suit sa
date de publication (US-49), donc au prochain déploiement, et non à minuit. Le PO a accepté ce
fonctionnement : la date reste manuelle pour l'instant. Une exécution programmée du déploiement la
rendrait automatique — un `schedule:` dans le workflow, rien de plus.

**Cours faits de CM rédigés.** *Programmation C avancée* et *Structures de Données* ne sont pas
candidats à US-51 : ce sont des **CM rédigés**, et non des decks. Ils attendent deux choses, dans un
sprint ultérieur : **US-40** (page rédigée par chapitre, en complément du deck) et la **conversion des
figures TikZ**, que la chaîne d'import ne sait pas encore faire.

## Roadmap

| Sprint | Objectif | Pts |
|---|---|---|
| 1 | Site minimal en ligne, déployé automatiquement | 11 |
| 2 | Vitrine académique complète | 17 |
| 3 | Bilingue et premier cours natif | 30 |
| 4 | Chaîne de publication et blog | 23 |
| 5 | Du contenu : un deuxième cours en ligne (nom de domaine et tuteur IA reportés) | 17 |
| 6 | Automatisation avancée + analytics | 21 |

Durée d'un sprint : 1 semaine, ajustable par le PO selon la charge d'enseignement.
