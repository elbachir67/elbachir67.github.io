# Sprint 3 — Bilingue et premier cours natif

**Objectif :** le site est navigable en français et en anglais, et le premier chapitre d'un cours
est lisible en ligne, généré depuis les sources LaTeX existantes.
**Capacité :** 30 points

## Entrée PO

- **Cours pilote** : « Architectures Logicielles Modernes » (M1 SIR), décision du PO (#45). Sources LaTeX fournies avant US-15.
- **Nature des sources (décision PO, #43)** : les cours sont des `.tex` autonomes, avec les schémas en **TikZ inline**, sans fichier d'image externe.
- **Sources du chapitre 1, déposées dans `_import/` (décision PO sur #49)** : `cm1_archi_seance1.tex` et `beamerucad.sty`. Ce n'est pas un document rédigé mais un **deck Beamer de 20 frames** (5 sections, 17 frames titrées), avec 7 environnements `ucad*` définis dans `beamerucad.sty`, 2 blocs `lstlisting` (du Java, une commande shell) et 5 figures externes du dossier `figs/`. **Ce deck ne contient aucun TikZ** : la règle TikZ → SVG reste écrite pour les cours qui en contiennent, mais elle n'est pas exercée ici.
- **Cible de la conversion (décision PO)** : un `.qmd` **revealjs**, une frame donnant une slide. US-16 livre donc les **slides** du chapitre 1, et non une page rédigée.
- **Figures (décision PO)** : 4 figures fournies en SVG — `fig1_god_controller`, `fig2_couches`, `fig3_chemin_tags`, `figB_couplage` — à intégrer en convertissant noirs et gris en `currentColor` (mode sombre) et avec un texte alternatif tiré de la légende du `.tex`. La cinquième, `figA_cout_changement`, n'est **pas** copiée en image : son script matplotlib (`figA.py`) est intégré en bloc Python exécuté (US-18).

## Périmètre linguistique (décision PO)

- **Bilingues** : Accueil, Research, Publications, Enseignement, CV, Contact, Blog (index).
- **Monolingues** : les pages de cours, dans leur langue d'enseignement (français). Le catalogue est bilingue, les cours ne le sont pas. Une note l'indique au visiteur anglophone.

**Décisions du PO sur la PR #48 :**

- **Contact** : la page n'existe pas encore sur le site. Elle sort du périmètre d'US-36 et devient US-38 au backlog (Should, 2 pts, sans sprint).
- **Adresses anglaises** : le dossier porte un nom anglais quand le mot diffère — `/en/research/`, `/en/teaching/`. Les adresses françaises ne changent pas.
- **Recherche** : un index par langue ; une recherche depuis une page anglaise ne propose pas de pages françaises, et réciproquement.
- **Données du CV et du catalogue** : elles restent en français sur les pages anglaises (seuls les libellés sont traduits). Leur traduction devient US-39 au backlog (Should, 3 pts, sans sprint).

**Décisions du PO sur la PR #46 :**

- **Figures SVG** : fonds blancs rendus transparents, police du site à la place de DejaVu Sans, couleurs d'accent conservées.
- **Deck seul pour l'instant** : la navigation entre chapitres passe par la page du cours. Une page rédigée en complément du deck devient US-40 au backlog (Should, 5 pts, sans sprint).
- **Sources LaTeX commitées** sous `cours/<slug>/_sources/` — non publié, comme `_specs/` — avec `beamerucad.sty` et les figures d'origine, pour que la conversion soit rejouable.
- **PDF du chapitre** : impression du deck depuis le navigateur (`?print-pdf`) ; la génération automatisée reste US-17 (Sprint 4).
- **Contrôle « aucun numéro de téléphone »** : si l'expression régulière du chapitre le déclenche, l'exception est **limitée aux blocs de code**.
- **Textes alternatifs de `fig2_couches` et `figB_couplage`** : attendus du PO. `TODO(PO)` dans la page tant qu'ils ne sont pas fournis.

## Ordre d'exécution

US-37 → US-36 → US-14 → US-15 → US-18 → US-16.

---

### US-37 — Spike + ADR-0003 : architecture multilingue (2 pts)

En tant que PO, je veux une décision documentée sur la mécanique multilingue,
afin de ne pas refaire l'arborescence du site dans six mois.

- [ ] Trois options évaluées : arborescence parallèle maison, profils Quarto, babelquarto.
- [ ] Critères : pas de R en CI, maintenance par une seule personne, URL stables, compatibilité avec les filtres Lua existants (CV, cours), coût d'ajout d'une page.
- [ ] Une maquette jetable de deux pages pour l'option retenue, non commitée dans le site.
- [ ] `_specs/adr/0003-architecture-multilingue.md` : contexte, options, décision, conséquences.
- [ ] Livré en PR de specs, sans modification du site.

### US-36 — Site bilingue FR/EN (8 pts)

En tant que partenaire international, je veux lire tout le site en anglais,
afin de ne pas dépendre d'une traduction automatique.

- [ ] Chaque page du périmètre bilingue existe en FR et en EN.
- [ ] URL stables : `/` pour le français, `/en/` pour l'anglais.
- [ ] Sélecteur de langue dans la barre de navigation, menant à la page équivalente (et non à l'accueil).
- [ ] `lang` correct sur chaque page ; balises `hreflang` réciproques, plus `x-default` vers le français.
- [ ] La page Research actuelle devient la version anglaise de la page Recherche ; sa version française est rédigée.
- [ ] Le CV existe dans les deux langues, page et PDF, depuis `cv/cv.yml` (libellés traduits, données non dupliquées).
- [ ] Les données partagées (publications, catalogue des cours) ne sont pas dupliquées : seuls les libellés d'interface sont traduits.
- [ ] La CI échoue si une page du périmètre bilingue n'a pas son équivalent, ou si un `hreflang` est manquant ou asymétrique.
- [ ] Le contrôle de référencement d'US-13 couvre les deux langues.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

### US-14 — Gabarit de cours (5 pts)

En tant qu'étudiant, je veux naviguer dans un cours chapitre par chapitre,
afin de retrouver rapidement la notion qui me manque.

- [ ] Structure : `cours/<slug>/index.qmd` (présentation, objectifs, prérequis, plan) et `chapitres/NN-<slug>.qmd`.
- [ ] Métadonnées du cours dans `cours/<slug>/cours.yml` : titre, niveaux, domaine, semestre, prérequis, statut.
- [ ] Barre latérale propre au cours, navigation précédent/suivant, table des matières par chapitre.
- [ ] Le catalogue d'US-11 lit ces métadonnées : un cours au statut `en-ligne` affiche un lien vers sa page, à la place du badge « Bientôt en ligne ». Le double référencement dans `enseignement/cours.yml` disparaît.
- [ ] Un cours de démonstration à deux chapitres courts sert de test, puis est retiré ou remplacé par le cours pilote.
- [ ] Rendu vérifié à 375 px et en desktop, en mode clair et sombre ; axe-core sans violation.

### US-15 — Conversion du deck Beamer en slides Quarto (8 pts)

En tant que PO, je veux convertir mes cours LaTeX sans les réécrire à la main,
afin que la migration des 21 cours reste réaliste.

- [ ] Table de correspondance documentée dans `_specs/contenus/latex-vers-quarto.md` : les sept environnements `ucad*` (`ucaddef`, `ucadret`, `ucadpiege`, `ucadex`, `ucadrec`, `ucadform`, `ucadfront`), **lus dans `beamerucad.sty`**, vers des callouts Quarto nommés ; le titre optionnel de l'environnement (`\begin{ucaddef}[Dette architecturale]`) devient le titre du callout.
- [ ] Style CSS des callouts, cohérent avec la charte d'US-06, en mode clair et sombre, et lisible en projection.
- [ ] Script `scripts/importer_chapitre.py` : `.tex` → `.qmd` **revealjs**, une `frame` par slide (titre de frame → titre de slide, `\section` → slide de section), maths préservées, `lstlisting` en blocs de code avec le bon langage (Java pour le code, shell pour les commandes), références croisées converties.
- [ ] Les 4 SVG fournis sont copiés dans le cours et nettoyés **en local** : noirs, encres et gris en `currentColor`, fonds blancs rendus transparents, police du site à la place de DejaVu Sans ; les couleurs d'accent (orange, vert, violet, jaune) sont conservées. Les SVG nettoyés sont commités, et **aucune conversion d'image ne tourne en CI**.
- [ ] Texte alternatif repris de la légende du `.tex` ; `TODO(PO)` quand la figure n'en a pas — c'est le cas de `fig2_couches` et de `figB_couplage`.
- [ ] `figA_cout_changement` n'est pas importée en image : elle est produite par le bloc Python d'US-18.
- [ ] Les sources d'origine (`.tex`, `beamerucad.sty`, figures) sont commitées sous `cours/<slug>/_sources/`, non publié, pour que la conversion soit rejouable.
- [ ] Tout élément non converti est laissé en commentaire HTML `<!-- NON CONVERTI: … -->`, jamais supprimé silencieusement ; la conversion produit un rapport listant ces éléments.
- [ ] Testé sur le deck du chapitre 1 ; le rapport et une comparaison PDF Beamer / slides figurent dans la PR.
- [ ] Aucune dépendance lourde ajoutée sans justification (pandoc est déjà présent avec Quarto).

### US-18 — Figures Python exécutées et gelées (2 pts)

En tant que PO, je veux des figures générées par le code du cours,
afin qu'elles restent cohérentes avec le contenu.

- [ ] Le bloc Python exécuté du chapitre 1 est `figA.py`, fourni par le PO : il produit la figure du coût du changement, à la place de `figA_cout_changement.pdf` (aucune image importée).
- [ ] `freeze: auto` actif ; `_freeze/` commité ; la CI ne réexécute pas le code.
- [ ] Le code est masqué par défaut, avec un bouton pour l'afficher.
- [ ] Les figures ont une légende et un texte alternatif.
- [ ] Une modification du code entraîne bien la régénération : preuve dans la PR.

### US-16 — Migration du cours pilote : slides du chapitre 1 (5 pts)

En tant qu'étudiant, je veux suivre le chapitre 1 en ligne,
afin de ne plus dépendre d'un PDF.

- [ ] `cours/<slug>/` créé à partir du gabarit d'US-14 : `cours.yml`, `index.qmd` et le chapitre 1 dans `chapitres/`.
- [ ] Le chapitre 1 est un **deck revealjs** produit par le script d'US-15, puis relu : les 20 slides, dans l'ordre du deck Beamer, avec les 7 types d'encadrés, les 2 blocs de code, les 4 figures SVG et la figure calculée d'US-18.
- [ ] Aucun `TODO(PO)` ni bloc `NON CONVERTI` restant à la fin, sauf textes alternatifs validés par le PO.
- [ ] Le cours apparaît au catalogue avec un lien vers sa page ; le cours de démonstration d'US-14 est retiré.
- [ ] Relu par le PO dans la PR, et vérifié à 375 px, en desktop et en projection (16:9), en mode clair et sombre.
- [ ] Le contrôle « aucun numéro de téléphone » reste vert malgré l'expression régulière `^7[05678][0-9]{7}$` du code du chapitre ; s'il se déclenche, l'exception ajoutée à `scripts/verifier_telephone.py` est limitée aux blocs de code.
- [ ] Le PDF reste disponible en imprimant le deck depuis le navigateur (`?print-pdf`) ; sa génération automatisée reste US-17 (Sprint 4).
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-03-bilan.md` (CLAUDE.md §11).
