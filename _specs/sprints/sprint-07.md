# Sprint 7 — Achever le C, publier le ML, préparer les cours rédigés

**Objectif :** le cours de Programmation C avancée est complet en ligne, le cours d'Introduction au
ML y rejoint Python, et la chaîne sait traiter ce que demandent Structures de Données et
Introduction à l'IA. La part du PO passe de l'écriture à la validation.
**Capacité :** 20 points

## Constat du Sprint 6

La machine travaille quatre minutes par chapitre ; le reste est de la lecture et des décisions du
PO (textes alternatifs, correspondance des encadrés). Ce sprint déplace cette part : la chaîne
propose, le PO valide.

## Entrées PO

- [ ] Validation, en bloc, des brouillons de textes alternatifs (US-58).
- [ ] Validation de la table des encadrés de Structures de Données et d'Introduction à l'IA (US-61).
- [ ] Métadonnées du cours d'Introduction au ML (US-60).
- [ ] Vérifier `_import/` : les séances S03 (Hachage) et S04 (Arbres et tas) de Structures de Données n'y contiennent qu'un fichier `A_DEPOSER_ICI.txt`.

## Ordre d'exécution

US-58 → US-59 → US-60 → US-61.

---

### US-58 — Brouillons de textes alternatifs (2 pts)

En tant que PO, je veux valider des textes alternatifs plutôt que les écrire,
afin que 33 schémas ne me coûtent pas une soirée.

- [ ] Pour chaque figure sans légende, `/importer-chapitre` rédige un brouillon à partir de la source de la figure (libellés, boîtes, flèches d'un TikZ ; titre, axes, séries d'une figure matplotlib) et du texte qui l'entoure.
- [ ] Les brouillons sont présentés au PO **en une seule fois**, figure par figure, avec le titre de la slide ou de la section et le brouillon proposé.
- [ ] Rien n'est écrit dans le site sans validation explicite : le PO accepte, corrige ou réécrit chaque brouillon.
- [ ] Un brouillon ne décrit que ce que la source contient : aucune interprétation, aucun chiffre absent de la figure.
- [ ] Le manifeste enregistre l'origine de chaque texte : légende du `.tex`, brouillon validé, ou texte du PO.

### US-59 — Cours de C, chapitres 0 à 3 (8 pts)

En tant qu'étudiant de L3, je veux tout le cours de C en ligne,
afin de réviser un chapitre sans ouvrir de PDF.

- [ ] Les trois manques repérés au bilan sont traités dans la chaîne, pas à la main : l'accolade non fermée du chapitre 2, `\begin{verbatim}`, `\begin{cases}` et les symboles (`\rightarrow`, `\checkmark`).
- [ ] Les tableaux du chapitre 2, dumps hexadécimaux compris, restent alignés en police à chasse fixe et défilent à 375 px.
- [ ] Les 33 schémas TikZ compilés, avec leurs textes alternatifs validés via US-58.
- [ ] Chaque chapitre porte son PDF d'origine et ses TD/TP en ressources, s'ils sont fournis.
- [ ] Les critères d'US-40 non démontrés au Sprint 6 (code, mathématiques, tableaux) le sont ici.
- [ ] Une PR pour les quatre chapitres, un commit par chapitre, base `main`.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

### US-60 — Migration d'Introduction au ML (5 pts)

En tant qu'étudiant de M1, je veux trouver mon cours de ML en ligne,
afin d'y retrouver séances et notebooks comme en Python.

- [ ] Cours créé avec son `cours.yml` (métadonnées fournies par le PO).
- [ ] Les onze séances importées depuis leurs decks, avec `/importer-chapitre`.
- [ ] Notebooks rendus en page (US-50) avec téléchargement et ouverture dans Colab.
- [ ] Toute construction LaTeX inconnue est signalée, jamais convertie à la main.
- [ ] Si la charge dépasse le sprint, s'arrêter à une séance complète et noter le reste au backlog.

### US-61 — Flottants et mathématiques hors ligne (5 pts)

En tant que PO, je veux que la chaîne traite les flottants et les équations,
afin d'ouvrir Structures de Données et Introduction à l'IA.

- [ ] Les environnements `figure` et `table` deviennent des figures et tableaux Quarto, avec légende, numérotation et références croisées (`\ref`, `\label`).
- [ ] Les mathématiques hors ligne (`equation`, `align`, `\[ … \]`) sont préservées, numérotées quand la source les numérote.
- [ ] Table des encadrés proposée au PO pour les deux cours (dix types pour Structures de Données, ceux d'Introduction à l'IA à relever) : le PO décide du sens de chacun.
- [ ] Éprouvé sur une séance réelle de Structures de Données et un CM réel d'Introduction à l'IA, convertis dans un dossier temporaire : rapport de conversion joint à la PR, sans publication.
- [ ] Tout reste non traité est listé dans la PR, avec l'estimation de ce qu'il faudrait pour le traiter.

---

## Table des encadrés, validée par le PO (US-61)

Elle pilotera l'import des deux cours. Les six corrections du PO sont appliquées ; le reste est
validé tel quel.

### Structures de Données — 13 types

| Environnement | Fois | Callout |
|---|---:|---|
| `appliboxQ` | 18 | `tip` — Mini-exercice |
| `appliboxR` | 18 | **omis** (réponses) |
| `attentionbox` | 12 | `warning` — Attention |
| `lienbox` | 11 | `note` — Lien avec le cours |
| `exercicebox` | 8 | `tip` — Vérification |
| `prereqbox` | 6 | `note` — **Navigation conceptuelle** |
| `infobox` | 6 | `note` — Pour comprendre |
| `definition` | 4 | `note` — Définition |
| `retenirbox` | 2 | `important` — À retenir |
| `objectifbox` | 2 | **`important`** — Objectifs |
| `example` | 2 | `tip` — Exemple |
| `proposition` | 1 | `note` — Proposition |
| `theorembox` | 1 | `important` — Théorème |

### Introduction à l'IA — 37 types

| Environnement | Fois | Callout |
|---|---:|---|
| `exemplebox` | 132 | `tip` — Exemple |
| `definitionbox` | 123 | `note` — Définition |
| `exercicebox` | 62 | `tip` — Exercice |
| `attentionbox` | 56 | `warning` — Attention |
| `feynbox` | 43 | `note` — Autrement dit |
| `retenirbox` | 37 | `important` — À retenir |
| `theorembox` | 31 | `important` — Propriété |
| `etapebox` | 29 | `note` — Étape |
| `defbox` | 28 | `note` — Définition |
| `keybox` | 22 | `important` — Interprétation |
| `prereqbox` | 20 | `note` — **Navigation conceptuelle** |
| `recipebox` | 19 | `tip` — Recette |
| `intubox` | 15 | `note` — Intuition |
| `rappelbox` | 14 | `note` — Rappel |
| `correctionbox` | 13 | **omis** |
| `attbox` | 13 | `warning` — Attention |
| `calcbox` | 13 | `note` — Démonstration |
| `livrerefbox` | 10 | `note` — Référence |
| `methodebox` | 10 | `tip` — Méthode |
| `intuitionbox` | 10 | **`tip` — Réflexion personnelle** |
| `proposition` | 10 | `note` — Proposition |
| `corrbox` | 10 | **omis** |
| `exobox` | 10 | **`note` — Contexte** |
| `linkbox` | 9 | `note` — Lien |
| `defibox` | 7 | `tip` — Défi |
| `pointclebox` | 6 | `important` — Points clés |
| `definition` | 5 | `note` — Définition |
| `exbox` | 5 | `tip` — Exemple |
| `solbox` | 5 | **omis** |
| `resbox` | 5 | `important` — Conclusion |
| `coursrefbox` | 2 | `note` — Cours de référence |
| `conceptbox` | 2 | `note` — Lectures complémentaires |
| `synthesebox` | 2 | `important` — Synthèse |
| `erreurbox` | 1 | `warning` — Erreurs fréquentes |
| `bayesbox` | 1 | **`important` — Théorème de Bayes** |
| `bridgebox` | 1 | `note` — Passerelle |
| `pontbox` | 1 | `note` — Fil conducteur |

**`tcolorbox` sort de la table.** Vérification faite à la demande du PO : les quatre occurrences
sont **une seule et même macro de préambule**, `\espaceReponse`, qui dessine un cadre **vide** à
lignes pour que l'étudiant écrive. Aucune n'est une boîte de réponse au sens d'un corrigé, et
aucune n'atteint la conversion — l'import part de `\begin{document}`. Ce qui l'atteint, c'est la
**commande** `\espaceReponse`, employée 41 fois dans quatre feuilles d'énoncés : un cadre vide
n'ayant pas de sens sur une page, elle sera simplement écartée.

## À reprendre tel quel dans le bilan

Le PO l'a demandé explicitement, et cela ne doit pas se perdre :

> Ma vérification dans Chrome n'a jamais regardé les images. Elle mesurait des largeurs, des
> débordements, des attributs `aria-label`, des zones défilantes — jamais un pixel de figure. J'ai
> rapporté « aucune figure sans texte alternatif » et « rendu vérifié à 375 px et 1440 px », et
> c'était vrai ; cela laissait entendre que les figures avaient été regardées, et elles ne l'avaient
> pas été.

Et, du même ordre, ce que le PO a demandé de noter :

> `verifier_debordement.js` mesurait **à zéro les slides empilées depuis sa création** (US-43). Le
> contrôle affiche chaque slide le temps de la mesurer, mais une slide empilée vit dans une section
> que reveal cache : un ancêtre en `display: none` met toute la descendance à zéro. Sur la séance 6
> du cours de ML, il ne mesurait vraiment que **quatre slides sur soixante-sept** et déclarait les
> soixante-trois autres conformes. Ses « 1023 slides tiennent dans le cadre », annoncés PR après PR
> pendant tout l'import du cours, ne valaient rien. Le défaut n'a été trouvé qu'en cherchant
> pourquoi une figure PNG s'affichait avec une hauteur nulle — c'est-à-dire en **regardant** une
> slide, une fois de plus. Réparé, le contrôle a immédiatement trouvé trois slides trop chargées.

Et deux écarts que la vérification en ligne du cours de ML a trouvés **dans les sources du PO**, à
reprendre par lui :

> **`f5_fit`, séance 5.** La slide s'intitule « Deux droites, et le résidu qui les départage » et sa
> légende parle de « deux droites de qualités différentes » et d'un « carré ŷᵢ posé sur la droite ».
> La figure, elle, s'intitule « Une droite qui suit le nuage de points » et montre **une** droite
> avec des marqueurs **ronds**. La figure des deux droites existe pourtant : c'est `f5_two_lines`,
> employée deux slides plus loin avec son propre texte. La conversion a fidèlement reporté la
> source ; c'est la source qu'il faut reprendre.
>
> **`f11_workflow`, séance 11.** Les cases ④ « Baseline » et ⑤ « Comparer les modèles » sont coupées
> au bord droit de la figure. Le **PDF source l'est aussi**, vérifié en le rasterisant : le cadrage
> est trop étroit à la source, et non perdu à la conversion.

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-07-bilan.md` (CLAUDE.md §11).
Il indiquera le **temps de validation par le PO** d'un lot de textes alternatifs, à comparer au
temps d'écriture : c'est ce qui dira si US-58 a atteint son but.
