# Sprint 5 — Du contenu

**Objectif :** le site cesse d'être une vitrine avec un cours de démonstration : un deuxième cours
y est en ligne, et les labs et TD accompagnent les séances.

> **Décision du PO, 19/09/2026 :** le **nom de domaine est reporté**. US-05 quitte le sprint et retourne
> au backlog, sans sprint ; la capacité passe de 19 à 17 points. Le titre du sprint, « Du contenu, et un
> nom à soi », devient « Du contenu ».

**Capacité :** 17 points

## Entrées PO

- [ ] **Deuxième cours à migrer** : ses sources LaTeX (séances, et labs si disponibles), déposées dans `_import/`.
- [ ] **Labs, TD, notebooks** du cours pilote, pour US-49 et US-50.

## Ordre d'exécution

US-49 → US-48 → US-43 → US-51 → US-50. (US-51 passe avant US-50 : décision du PO — les
notebooks seront d'abord téléchargeables, et deviendront des pages ensuite.)

---

### US-49 — Ressources par séance (3 pts)

En tant qu'étudiant, je veux trouver le lab et le TD à côté de la séance,
afin de ne pas chercher ailleurs ce qui va ensemble.

- [ ] Champ `ressources` dans `_sources/import.toml` : chaque entrée a un type (`lab`, `td`, `notebook`, `corrige`), un titre et un fichier.
- [ ] Fichiers rangés dans le dossier du cours ; liste affichée sur la page de la séance et sur la page du cours, dans les deux langues, avec le type et le poids du fichier.
- [ ] **Un corrigé n'est jamais publié à côté de son énoncé** : le type `corrige` exige une date de publication, et la ressource reste absente du site avant cette date. La CI échoue si un corrigé est publiable sans date.
- [ ] Ajouter une ressource ne demande aucune modification de page.

### US-48 — Page de garde des PDF (2 pts)

En tant qu'étudiant qui reçoit un PDF par messagerie, je veux savoir d'où il vient,
afin de retrouver le cours en ligne.

- [ ] Première page : titre du cours, titre et numéro de la séance, nom et affiliation de l'enseignant, URL de la séance, date de génération.
- [ ] Style accordé à la charte ; la pagination reste correcte.

### US-43 — Contrôle de débordement des slides (2 pts)

En tant que PO, je veux qu'une slide trop chargée soit signalée à l'import,
afin de ne pas la découvrir en amphi.

- [ ] Contrôle exécuté en CI : échec si une slide dépasse la hauteur du cadre, avec le numéro et le titre de la slide.
- [ ] La commande `/importer-chapitre` fait le même contrôle et le signale avant d'ouvrir la PR.
- [ ] Testé sur une slide volontairement trop longue.

### US-50 — Notebooks rendus en page (5 pts)

En tant qu'étudiant, je veux lire un lab de mon cours d'IA sans rien installer,
afin de le consulter depuis mon téléphone.

- [ ] Un `.ipynb` déclaré comme ressource est rendu en page HTML : code coloré, sorties, figures.
- [ ] Deux boutons : télécharger le notebook, ouvrir dans Google Colab.
- [ ] Les sorties viennent du notebook tel quel : rien n'est réexécuté en CI (règle du gel d'US-18).
- [ ] Rendu correct à 375 px ; tableaux et sorties larges défilent dans leur cadre ; axe-core sans violation.

### US-51 — Migration d'un deuxième cours (5 pts)

En tant qu'étudiant d'un autre cours, je veux aussi trouver mes séances en ligne,
afin que le site serve à toute ma promotion.

- [ ] Cours créé avec son `cours.yml` (niveaux, semestre, objectifs, prérequis fournis par le PO).
- [ ] Séances importées avec `/importer-chapitre`, une PR par séance, les textes alternatifs demandés au PO.
- [ ] Le cours passe au statut `en-ligne` et apparaît dans le catalogue, dans les deux langues.
- [ ] Tout élément que la chaîne ne sait pas encore convertir est signalé, jamais converti à la main en silence : c'est ce qui fera évoluer le script.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-05-bilan.md` (CLAUDE.md §11).
Il indiquera en particulier le **temps réel de migration d'une séance**, donnée qui dimensionnera
les sprints de contenu suivants.
