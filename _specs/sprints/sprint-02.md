# Sprint 2 — Vitrine académique

**Objectif :** un visiteur (collègue, partenaire, étudiant) trouve en ligne les travaux de recherche,
les publications, le CV et le catalogue des cours, dans une charte graphique cohérente.
**Capacité :** 17 points · **Source des contenus :** `_specs/contenus/sprint-02-sources.md`

## Règles ajoutées à `CLAUDE.md` (PR de specs du sprint)

- **Travaux non acceptés :** aucun article soumis ou en évaluation n'apparaît sur le site
  (ni titre, ni lieu, ni résumé, ni billet). Seuls les travaux listés comme publiés dans les sources
  peuvent être cités. En cas de doute : `TODO(PO)`.
- **Données personnelles :** le PDF du CV du PO n'est jamais commité (il contient un numéro de téléphone).
  Le CV du site est régénéré depuis les sources.

## Entrées PO

Aucune fiche à remplir. Deux décisions sont posées dans les PR concernées :
- statut de la publication ICECET 2026 (US-09) ;
- nom de domaine (US-05, hors sprint tant que non décidé).

## Ordre d'exécution

US-34 → US-06 → US-09 → US-08 → US-10 → US-11 → US-13 → US-12.

---

### US-34 — Montée de version Quarto 1.10 (1 pt)

En tant que PO, je veux la dernière version stable de Quarto, afin de ne pas accumuler de dette d'outillage.

- [ ] Version épinglée mise à jour dans `ci.yml` et `deploy.yml`, et documentée dans le `README.md`.
- [ ] `quarto render` sans erreur ni avertissement ; CI verte.
- [ ] Notes de version parcourues : tout changement cassant est signalé dans la PR.

### US-06 — Charte graphique (3 pts)

En tant que visiteur, je veux un site sobre et lisible, afin de percevoir un profil académique sérieux.

- [ ] Thème Bootswatch `cosmo` (clair) + `darkly` (sombre) avec bascule clair/sombre.
- [ ] Couleur principale `#1F6FB5` (bleu du CV), surchargée dans `assets/css/custom.scss`.
- [ ] Typographie : une police sans-serif pour le texte, avec pile de repli système.
- [ ] Icônes académiques (Google Scholar, ORCID, Academia) via l'extension Quarto *academicons*,
      en remplacement des icônes génériques d'US-07. Dépendance justifiée dans la PR.
- [ ] Pied de page sur toutes les pages : « © 2026 El Hadji Bassirou Touré · DMI/FST/UCAD », liens Scholar / ORCID / GitHub.
- [ ] Contraste texte/fond conforme WCAG AA dans les deux modes (outil de mesure cité dans la PR).
- [ ] Rendu vérifié à 375 px et en desktop, en mode clair et sombre.

### US-09 — Publications générées depuis BibTeX (3 pts)

En tant que collègue, je veux la liste de toutes les publications, afin de citer ou lire ces travaux.

- [ ] `publications/publications.bib` construit à partir de la liste des sources (8 références).
- [ ] Auteurs complets et DOI récupérés via l'API Crossref ou DBLP. Toute donnée non trouvée : `TODO(PO)`, jamais inventée.
- [ ] Page `publications/index.qmd` générée depuis le `.bib` : groupée par année décroissante, lien DOI quand il existe.
- [ ] Le nom du PO est mis en gras dans chaque référence.
- [ ] Entrée « Publications » ajoutée à la navigation, entre Research et Enseignement.
- [ ] **Décision PO dans la PR :** ICECET 2026 est-elle acceptée/publiée ? Si non, retirer l'entrée.
- [ ] Script de génération rejouable, documenté dans le `README.md`.

### US-08 — Page Research en anglais (3 pts)

En tant que partenaire international, je veux comprendre le programme de recherche, afin d'identifier des collaborations.

- [ ] Ouverture : le fil conducteur (section « Research narrative » des sources), 3–4 phrases.
- [ ] Axes de recherche et projets actifs, repris des sources, traduits en anglais.
- [ ] Chaque projet peut pointer vers ses publications (ancre de la page Publications) ; aucun lien vers un travail non accepté.
- [ ] Lien vers le dépôt public `github.com/elbachir67/consistency-debt` **uniquement si** le PO le confirme dans la PR.
- [ ] Texte relu par le PO dans la PR avant merge.

### US-10 — CV en ligne généré depuis une source unique (2 pts)

En tant que visiteur, je veux consulter et télécharger le CV, afin d'évaluer le parcours.

- [ ] `cv/cv.yml` : données structurées extraites des sources (formation, parcours, responsabilités, distinctions).
- [ ] Page `cv/index.qmd` générée depuis `cv.yml`.
- [ ] PDF français généré par Quarto (Typst) depuis la même source et proposé au téléchargement.
- [ ] Titre « Maître de Conférences Titulaire ». Aucun numéro de téléphone (test automatique dans la CI : échec si un motif `+221` ou un numéro à 9 chiffres apparaît dans `_site/`).
- [ ] La version anglaise est reportée (nouvelle story au backlog : US-35, Could, 2 pts).

### US-11 — Catalogue des cours (2 pts)

En tant qu'étudiant, je veux voir les cours enseignés, afin de retrouver le mien.

- [ ] `enseignement/cours.yml` : un cours par entrée (titre, domaine, niveaux, établissement, statut).
- [ ] Page `enseignement/index.qmd` : cartes groupées par domaine (Génie Logiciel & Architecture, IA & Data, Programmation/Web/Mobile).
- [ ] Statut `a-venir` affiché « Bientôt en ligne », sans lien (les cours natifs arrivent au Sprint 3).
- [ ] Ajouter un cours = ajouter une entrée YAML, sans toucher au `.qmd` (documenté dans le `README.md`).

### US-13 — SEO et métadonnées (2 pts)

En tant que PO, je veux que le site soit bien indexé et partagé, afin d'en faire mon point d'entrée principal.

- [ ] `site-url`, `description` et image Open Graph / Twitter Card configurés dans `_quarto.yml`.
- [ ] `sitemap.xml` et `robots.txt` présents dans `_site/`.
- [ ] Chaque page a un titre et une description uniques.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

### US-12 — Email protégé (1 pt)

En tant que PO, je veux limiter la collecte automatique de mon email, afin de réduire le spam.

- [ ] L'adresse n'apparaît jamais en clair dans le HTML généré (vérifié par `grep` dans la CI).
- [ ] Elle reste cliquable et lisible pour un humain (reconstruction JavaScript, avec repli accessible).

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-02-bilan.md` (voir CLAUDE.md §11).
