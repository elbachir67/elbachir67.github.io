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

## À reprendre tel quel dans le bilan

Le PO l'a demandé explicitement, et cela ne doit pas se perdre :

> Ma vérification dans Chrome n'a jamais regardé les images. Elle mesurait des largeurs, des
> débordements, des attributs `aria-label`, des zones défilantes — jamais un pixel de figure. J'ai
> rapporté « aucune figure sans texte alternatif » et « rendu vérifié à 375 px et 1440 px », et
> c'était vrai ; cela laissait entendre que les figures avaient été regardées, et elles ne l'avaient
> pas été.

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-07-bilan.md` (CLAUDE.md §11).
Il indiquera le **temps de validation par le PO** d'un lot de textes alternatifs, à comparer au
temps d'écriture : c'est ce qui dira si US-58 a atteint son but.
