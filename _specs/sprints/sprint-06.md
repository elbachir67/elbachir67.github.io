# Sprint 6 — Les cours rédigés entrent dans la chaîne

**Objectif :** un CM LaTeX rédigé, avec ses figures TikZ, devient une page de cours lisible en ligne,
comme un deck devient des slides. Le premier chapitre de Programmation C avancée le prouve.
**Capacité :** 26 points

## Pourquoi ce sprint

Onze séances sont en ligne, toutes issues de decks Beamer. Les cours de Programmation C avancée,
Structures de Données et Introduction à l'IA sont des documents rédigés : la chaîne ne sait pas les
traiter, et ils représentent une grande partie du corpus. Ce sprint lève ce blocage.

Le cours d'Introduction au ML, déjà en decks Beamer, ne demande aucune capacité nouvelle : sa
migration est une répétition de ce que fait `/importer-chapitre`, et elle peut intervenir à tout
moment, sans attendre ce sprint.

## Entrées PO

- [ ] Sources du **chapitre 1 de Programmation C avancée** : le `.tex` du CM, son préambule ou `.sty`, et ses figures.
- [ ] Textes alternatifs pour les figures TikZ sans légende (demandés en une fois, comme d'habitude).

## Ordre d'exécution

US-57 → US-40 → US-55 → US-56 → US-50.

---

### US-57 — Catalogue des cours : cartes lisibles et distinctes (3 pts)

En tant qu'étudiant qui cherche son cours parmi vingt et un,
je veux repérer le mien d'un coup d'œil, afin de ne pas lire toutes les cartes.

- [ ] Chaque domaine a sa couleur, dérivée de la charte et déclinée en clair et en sombre : Génie Logiciel & Architecture, IA & Data, Programmation/Web/Mobile.
- [ ] La couleur ne porte jamais seule l'information : le domaine reste écrit, et le statut garde son libellé (« En ligne » / « Bientôt en ligne »).
- [ ] Une carte de cours en ligne se distingue nettement d'une carte à venir, et indique le nombre de séances publiées.
- [ ] Niveau et statut lisibles sans ouvrir la carte ; hiérarchie visuelle claire entre titre, niveau et domaine.
- [ ] Grille régulière : aucune carte orpheline sur sa ligne à 375, 768 et 1440 px.
- [ ] Contraste WCAG AA vérifié pour chaque couleur de domaine, dans les deux modes ; axe-core sans violation.
- [ ] Deux propositions visuelles soumises au PO avant de figer les valeurs, captures à l'appui.

### US-40 — Conversion d'un CM rédigé en page de cours (8 pts)

En tant qu'étudiant, je veux lire un chapitre de cours dans mon navigateur,
afin de ne pas dépendre d'un PDF de cinquante pages sur un téléphone.

- [ ] Nouvelle cible de `/importer-chapitre` : `--cible page`, en plus de la cible slides existante. La cible est enregistrée dans `import.toml` et rejouée par le contrôle de conversion.
- [ ] Structure du document préservée : sections et sous-sections deviennent les titres de la page, avec une table des matières latérale et des ancres stables.
- [ ] Les environnements du cours (définition, théorème, exemple, exercice, remarque, `tcolorbox`) deviennent des callouts nommés, selon la table de correspondance étendue.
- [ ] Mathématiques préservées, en ligne et hors ligne, numérotation et références croisées comprises.
- [ ] `lstlisting` et `verbatim` deviennent des blocs de code, langage déduit comme pour les decks.
- [ ] Les tableaux, y compris les dumps mémoire en hexadécimal, restent alignés : police à chasse fixe conservée, défilement horizontal si nécessaire.
- [ ] Un chapitre long reste navigable : titres cliquables, retour en haut, lecture correcte à 375 px.
- [ ] Le PDF d'origine, compilé par LaTeX, est attaché comme ressource de la séance (US-49) : on ne régénère pas un PDF depuis le HTML.
- [ ] Une page rédigée et un deck cohabitent dans le même cours, chacun avec sa mise en page.

### US-55 — Conversion des figures TikZ (5 pts)

En tant que PO, je veux que mes schémas TikZ deviennent des images web,
afin que mes cours de systèmes soient publiables sans les redessiner.

- [ ] Chaque `tikzpicture` est compilé en SVG en local (jamais en CI, comme les figures matplotlib), et le SVG est commité.
- [ ] Le nettoyage existant s'applique : encres et gris en `currentColor`, fonds transparents, police héritée du site.
- [ ] Le texte du schéma reste du texte, sélectionnable : si la chaîne de compilation le transforme en tracés, le signaler et proposer une alternative plutôt que de livrer une image morte.
- [ ] Le contrôle « figure vide » d'US-54 couvre ces figures.
- [ ] Les dépendances LaTeX nécessaires sont documentées dans le README, avec la commande exacte.
- [ ] Texte alternatif : la légende quand elle existe, sinon demande au PO, jamais de `TODO(PO)`.

### US-56 — Migration du premier chapitre de Programmation C avancée (5 pts)

En tant qu'étudiant de L3, je veux lire le premier chapitre de C en ligne,
afin de réviser sans ouvrir un PDF.

- [ ] Cours créé avec son `cours.yml` (niveaux, semestre, objectifs, prérequis fournis par le PO).
- [ ] Chapitre 1 converti par la chaîne, relu par le PO dans la PR, sans aucun `TODO(PO)` ni bloc non converti.
- [ ] Le cours passe au statut `en-ligne` et apparaît dans le catalogue, dans les deux langues.
- [ ] TD et TP du chapitre attachés en ressources si le PO les fournit.
- [ ] Tout ce que la chaîne ne sait pas encore traiter est signalé, jamais bricolé à la main.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

### US-50 — Notebooks rendus en page (5 pts)

En tant qu'étudiant, je veux lire un notebook de TP sans rien installer,
afin de le consulter depuis mon téléphone.

- [ ] Un `.ipynb` déclaré comme ressource est rendu en page HTML : code coloré, sorties, figures.
- [ ] Deux boutons : télécharger le notebook, ouvrir dans Google Colab.
- [ ] Les sorties viennent du notebook tel quel : rien n'est réexécuté en CI (règle du gel d'US-18).
- [ ] Rendu correct à 375 px ; tableaux et sorties larges défilent dans leur cadre ; axe-core sans violation.

---

## Hors sprint, à faire quand le PO le souhaite

Migration d'Introduction au ML (decks Beamer et notebooks) : aucune capacité nouvelle requise,
une PR par lot de séances. **Les sources sont déjà dans `_import/`** : à lancer dès qu'une
respiration se présente dans le sprint, ou juste après.

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-06-bilan.md` (CLAUDE.md §11).
Il indiquera le **temps de migration d'un chapitre rédigé**, à comparer aux 12 minutes d'une séance
en slides : c'est ce chiffre qui dira si les cours de C, de Structures de Données et d'Introduction
à l'IA peuvent suivre.
