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
| US-23 | EP4 | GitHub Action Claude : issue labellisée → PR | C | 5 | — |
| US-24 | EP4 | Aperçu déployé par PR | C | 3 | — |
| US-32 | EP6 | Journalisation anonymisée des questions + consentement | S | 5 | — |
| US-33 | EP6 | Tableau de bord enseignant (concepts bloquants) | C | 8 | — |
| US-05 | EP1 | Nom de domaine personnalisé + HTTPS | S | 2 | — |
| US-38 | EP2 | Page Contact bilingue (formulaire non requis : email protégé, affiliations) | S | 2 | — |
| US-39 | EP1 | Traduire les données du CV et du catalogue des cours (et non les seuls libellés) | S | 3 | — |
| US-40 | EP3 | Conversion d'un CM rédigé en page de cours (structure, maths, callouts) | M | 8 | livrée |
| US-43 | EP3 | Contrôle de débordement des slides (échec si une slide dépasse le cadre) | S | 2 | livrée |
| US-44 | EP3 | Style matplotlib accordé à la charte, partagé par les cours | C | 2 | — |
| US-45 | EP3 | Notes du présentateur (`\note{}` → `::: {.notes}`) | C | 1 | — |
| US-46 | EP3 | Numérotation automatique des chapitres depuis le nom de fichier | C | 1 | — |
| US-47 | EP1 | Index de recherche par langue, sans ajustement du décalage Quarto | C | 2 | — |
| US-48 | EP3 | Page de garde des PDF de séance | S | 2 | livrée |
| US-49 | EP3 | Ressources par séance (lab, TD, TP, notebook, PDF du cours) | M | 3 | livrée |
| US-50 | EP3 | Notebooks de lab rendus en page, avec téléchargement et ouverture dans Colab | S | 5 | livrée |
| US-51 | EP3 | Migration d'un deuxième cours : Programmation Python (L1) | M | 5 | livrée |
| US-52 | EP1 | Déploiement quotidien programmé (les dates de publication s'appliquent seules) | C | 1 | — |
| US-53 | EP3 | Un manifeste d'import par séance (séances vraiment indépendantes) | C | 3 | — |
| US-54 | EP3 | Contrôle de figure vide (écart d'éléments dessinés, références illisibles) | M | 2 | livrée |
| US-55 | EP3 | Conversion des figures TikZ en SVG nettoyé | M | 5 | livrée |
| US-56 | EP3 | Migration du premier chapitre de Programmation C avancée | M | 5 | livrée |
| US-57 | EP2 | Catalogue des cours : cartes lisibles et distinctes (couleur par domaine) | S | 3 | livrée |
| US-58 | EP4 | Brouillons de textes alternatifs soumis à la validation du PO | M | 2 | 7 |
| US-59 | EP3 | Cours de Programmation C avancée, chapitres 0 à 3 | M | 8 | 7 |
| US-60 | EP3 | Migration d'Introduction au ML (onze séances en decks) | M | 5 | 7 |
| US-61 | EP3 | Flottants et mathématiques hors ligne (ouvre SD et Intro IA) | M | 5 | 7 |
| US-62 | EP3 | Contrôle des figures par comparaison des références de glyphes | S | 3 | — |
| US-63 | EP3 | Audit d'accessibilité ciblé sur la PR, audit complet hebdomadaire sur `main` | M | 3 | livrée |
| US-64 | EP3 | Cellules de tableau étendues (`\multicolumn`) et équations à étiquettes multiples | S | 3 | livrée |
| US-65 | EP3 | Le site sert ce qu'il promet : page de cours, lien interne, ressource du manifeste | M | 2 | livrée |
| US-66 | EP2 | Un catalogue sans doublon ni confusion (fusion des entrées, contrôle en CI) | M | 3 | 8 |
| US-67 | EP3 | Les cours se lient entre eux (prérequis en liens, relation inverse calculée) | M | 5 | 8 |
| US-68 | EP3 | Inventaire des sources disponibles dans `_import/` | M | 2 | 8 |
| US-69 | EP3 | Architectures Logicielles Modernes, séances suivantes | M | 8 | 8 |
| US-70 | EP3 | Un lot de cours à labs seuls (le lab tient lieu de séance) | M | 3 | 8 |

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

**US-53 — Un manifeste d'import par séance.** Aujourd'hui, toutes les séances d'un cours sont
décrites dans un seul `_sources/import.toml` : deux séances importées en parallèle entrent en conflit
sur ce fichier, ce qui a conduit à enchaîner leurs PR, avec les dégâts constatés au Sprint 5. Un
fichier par séance supprimerait la cause. Il faudrait adapter `preparer_chapitre.py`,
`verifier_conversion.py` et `rendre.py`, qui lisent tous le manifeste.

**US-50 — Notebooks rendus en page.** Dernière de l'ordre d'exécution du Sprint 5, elle n'a pas été
atteinte. Les huit notebooks du cours de Python sont **en ligne comme ressources téléchargeables**
(US-49) : il manque la page HTML, avec le téléchargement et l'ouverture dans Colab. Première
candidate pour le sprint suivant (voir [le bilan](sprints/sprint-05-bilan.md)).

**Cours faits de CM rédigés.** *Programmation C avancée*, *Structures de Données* et *Introduction à
l'IA* sont des **documents rédigés**, et non des decks : la chaîne ne savait pas les traiter. Le
**Sprint 6** a levé ce blocage — US-40 pour la conversion d'un CM en page, US-55 pour ses figures
TikZ, US-56 pour le premier chapitre de C, qui sert de preuve. Le **Sprint 7** achève le cours de C
(US-59) et traite ce qui manque encore aux deux autres cours : flottants et mathématiques hors ligne
(US-61).

**Introduction au ML entre au Sprint 7 (US-60).** Ce cours-là est déjà en decks Beamer : sa migration
ne demande aucune capacité nouvelle, c'est une répétition de `/importer-chapitre`. **Ses sources sont
déjà dans `_import/ML/`** (onze séances). Il était hors sprint depuis le Sprint 6, faute de
respiration ; le Sprint 7 lui en donne une.

**Automatisation avancée et analytics : au backlog, sans sprint.** US-23 (Action Claude :
issue → PR), US-24 (aperçu déployé par PR), US-32 (journalisation anonymisée) et US-33 (tableau de
bord enseignant) forment ce thème, 21 points au total — c'est lui qui occupait la ligne 7 de la
roadmap. Le PO a tranché : **ce n'est pas une priorité**. Les quatre stories repassent donc « sans
sprint », et aucune issue ne leur est ouverte.

**US-62 — Comparer les glyphes, et non les pixels.** La comparaison d'images d'une figure à son PDF
a été écrite, calibrée et mesurée : elle ne sépare pas le signal du bruit. Sur trois figures du
chapitre 2 du cours de C, l'écart entre une figure brouillée et la même figure juste va de 0 à 7
points, quand l'écart dû au rendu seul — anticrénelage, encres du mode sombre, mise à l'échelle — en
vaut le double. L'angle proposé est exact et sans seuil : comparer les **références de glyphes**
d'une figure incorporée à celles que sa source définit. `verifier_identifiants.py` couvre déjà la
famille de défauts qui a frappé ; celle-ci irait plus loin. Pas une priorité (US-59).

**La publication datée des corrigés est supprimée (US-49).** Décision du PO : aucun corrigé, aucune
piste, aucune indication de correction n'est publié ni versionné — sans date, sans délai, sans
exception. Trois « pistes de résolution » et le corrigé d'un devoir surveillé étaient en ligne,
déclarés comme des TP. La machinerie d'US-49 disparaît (dossier `_corriges/`, date sur une
ressource, type `corrige`), et trois barrières la remplacent : l'import refuse, la conversion
refuse, et `verifier_non_publiable.py` refuse — dans le dépôt autant que dans le site. La règle est
écrite dans CLAUDE.md §7.

**US-63 — L'accessibilité ne peut plus être vérifiée en entier à chaque PR. Livrée** (#154), en
urgence : la CI du bilan du Sprint 7 a été **annulée au plafond de quarante minutes**, l'audit
occupant à lui seul 1 461 s des 2 148 s du job.

Deux régimes. **Sur une PR, l'audit ne porte que sur les pages touchées** :
`scripts/pages_touchees.js` traduit les fichiers modifiés en adresses du site. Une séance donne sa
page et celle du cours ; une figure, une ressource ou `cours.yml` donnent les pages du cours et les
deux catalogues ; une feuille de style, un filtre Lua, un profil Quarto ou un script d'import
donnent **tout le site** — et **tout fichier de portée inconnue aussi**. Le doute mène toujours au
tout : un audit complet de trop coûte vingt minutes, un audit manquant laisse passer un défaut.

**Sur `main`, l'audit complet tourne une fois par semaine** — `accessibilite.yml`, lundi 5 h UTC,
lançable à la main. Un défaut peut apparaître sans qu'aucune page ne change. Son échec **ouvre une
issue**, parce que personne ne lit les journaux d'un job programmé.

**Mesuré en production**, sur les deux PR qui ont suivi : #153 ajoute un script dont la portée
n'est pas décidable et retombe sur le régime complet — **1 606 s** ; #155 ne touche qu'un cours et
audite **8 pages en 77 s**. Vingt et une fois moins. Le plafond du job de CI est monté de 40 à
60 minutes : c'est désormais la PR rare, celle qui touche au rendu entier, qui le borne.

**US-64 — Ce qu'US-61 laissait de côté. Livrée avec la migration d'Introduction à l'IA**, le PO
ayant préféré la traiter plutôt que de publier cinq tableaux mal rendus.

**`\multicolumn`** : cinq occurrences. La cellule garde son contenu et la ligne se complète de
cellules vides. Elle ne s'**étend** plus, faute d'équivalent en Markdown : produire un tableau HTML
aurait demandé que `cellules_de_tableau()` rende la structure plutôt qu'une liste de cellules, pour
un gain que le rendu ne montre pas. **`\multirow` sort de la story** : il n'est utilisé nulle part
dans les sources des cinq cours — seul `\usepackage{multirow}` y apparaît.

**Plusieurs `\label` dans un même `align`** : trois occurrences, dans la séance 2 d'Introduction à
l'IA. LaTeX numérote chaque ligne, Quarto numérote le bloc : seule la première étiquette survivait,
et le rendu signalait « Unable to resolve crossref @eq-r2 » — le lecteur lisait « (?) ». Chaque
ligne étiquetée devient une équation numérotée ; l'alignement d'une ligne à l'autre se perd, ce
qu'une page web ne montrait de toute façon pas.

**`\qquad` hors formule** : une espace. Dans une formule, il n'est pas touché — une substitution
globale, tentée au Sprint 6, avait cassé les mathématiques de huit chapitres publiés.

**US-65 — Le site sert ce qu'il promet. Livrée** après le 404 de Structures de Données, à la
demande du PO. Trois promesses : un dossier de `cours/` promet une page d'accueil, un lien interne
promet une page, une ressource du manifeste promet un fichier servi.

La leçon tient en une phrase : **un dossier existant était tenu pour une cible valide**. Le contrôle
des liens internes existait et tournait ; `lychee --offline` a dit OK sur le run qui a livré le
cours en 404, parce que `_site/cours/structures-de-donnees/` existait — il contenait `chapitres/` —
sans porter d'`index.html`. `scripts/verifier_publication.py` fait la différence : chez lui, un
dossier vaut son `index.html`.

**La part du PO, et US-58.** Le bilan du Sprint 6 a mesuré que la machine travaille quatre minutes
par chapitre : le reste est de la lecture et des **décisions du PO** — 33 textes alternatifs pour les
seuls chapitres de C, une table d'encadrés par cours rédigé. US-58 déplace cette part : la chaîne
rédige un brouillon à partir de la source de la figure, le PO valide, corrige ou réécrit.

## Roadmap

| Sprint | Objectif | Pts |
|---|---|---|
| 1 | Site minimal en ligne, déployé automatiquement | 11 |
| 2 | Vitrine académique complète | 17 |
| 3 | Bilingue et premier cours natif | 30 |
| 4 | Chaîne de publication et blog | 23 |
| 5 | Du contenu : un deuxième cours en ligne | 14 livrés sur 19 |
| 6 | Les cours rédigés entrent dans la chaîne | 26 livrés sur 26 |
| 7 | Achever le C, publier le ML, préparer les cours rédigés | 28 livrés sur 20 |
| 8 | Un catalogue juste, des cours liés entre eux, et la migration qui continue | 21 |

Durée d'un sprint : 1 semaine, ajustable par le PO selon la charge d'enseignement.
