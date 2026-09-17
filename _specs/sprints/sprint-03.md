# Sprint 3 — Bilingue et premier cours natif

**Objectif :** le site est navigable en français et en anglais, et le premier chapitre d'un cours
est lisible en ligne, généré depuis les sources LaTeX existantes.
**Capacité :** 30 points

## Entrée PO

- **Cours pilote** : à choisir avant US-16 (voir la question posée dans l'issue). Le cours doit avoir des sources LaTeX existantes avec encadrés `tcolorbox` et au moins une figure.

## Périmètre linguistique (décision PO)

- **Bilingues** : Accueil, Research, Publications, Enseignement, CV, Contact, Blog (index).
- **Monolingues** : les pages de cours, dans leur langue d'enseignement (français). Le catalogue est bilingue, les cours ne le sont pas. Une note l'indique au visiteur anglophone.

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

### US-15 — Correspondance LaTeX → Quarto (8 pts)

En tant que PO, je veux convertir mes cours LaTeX sans les réécrire à la main,
afin que la migration des 21 cours reste réaliste.

- [ ] Table de correspondance documentée dans `_specs/contenus/latex-vers-quarto.md` : chaque environnement `tcolorbox` du cours pilote (définition, intuition, exemple, piège, exercice…) vers un callout Quarto nommé.
- [ ] Style CSS des callouts, cohérent avec la charte d'US-06, en mode clair et sombre.
- [ ] Script `scripts/importer_chapitre.py` : `.tex` → `.qmd`, avec les maths (`$…$`, `align`, `equation`) préservées, les `listings` en blocs de code, et les références croisées converties.
- [ ] Figures TikZ compilées en SVG, avec texte alternatif `TODO(PO)` si aucune légende n'est disponible.
- [ ] Tout élément non converti est laissé en commentaire HTML `<!-- NON CONVERTI: … -->`, jamais supprimé silencieusement ; la conversion produit un rapport listant ces éléments.
- [ ] Testé sur un chapitre réel ; le rapport et une comparaison PDF/HTML figurent dans la PR.
- [ ] Aucune dépendance lourde ajoutée sans justification (pandoc est déjà présent avec Quarto).

### US-18 — Figures Python exécutées et gelées (2 pts)

En tant que PO, je veux des figures générées par le code du cours,
afin qu'elles restent cohérentes avec le contenu.

- [ ] Un chapitre contient un bloc Python exécuté produisant une figure.
- [ ] `freeze: auto` actif ; `_freeze/` commité ; la CI ne réexécute pas le code.
- [ ] Le code est masqué par défaut, avec un bouton pour l'afficher.
- [ ] Les figures ont une légende et un texte alternatif.
- [ ] Une modification du code entraîne bien la régénération : preuve dans la PR.

### US-16 — Migration du premier chapitre du cours pilote (5 pts)

En tant qu'étudiant, je veux lire le premier chapitre en ligne,
afin de ne plus dépendre d'un PDF.

- [ ] Chapitre converti avec le script d'US-15, relu par le PO dans la PR.
- [ ] Aucun `TODO(PO)` ni bloc `NON CONVERTI` restant à la fin.
- [ ] Le cours passe au statut `en-ligne` et devient accessible depuis le catalogue.
- [ ] Le PDF du chapitre reste téléchargeable, généré depuis les mêmes sources.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-03-bilan.md` (CLAUDE.md §11).
