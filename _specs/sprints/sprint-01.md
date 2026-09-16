# Sprint 1 — Socle en ligne

**Objectif :** le site minimal est en ligne, déployé automatiquement à chaque merge sur `main`,
avec une page d'accueil réelle.
**Capacité :** 11 points · **Durée :** 1 semaine

## Entrées PO requises (avant démarrage)

- [x] Compte GitHub : `elbachir67` → dépôt `elbachir67.github.io`
- [x] Photo : `assets/img/profil.jpg` (800×800, fournie)
- [x] Bio courte en français → `_specs/contenus/bio-fr.md` (à reprendre mot pour mot)
- [x] Email public : `elhadjibassirou.toure@ucad.edu.sn`
- [x] Titre : « Maître de Conférences Titulaire, DMI/FST/UCAD »
- [x] Google Scholar : https://scholar.google.com/citations?user=JsZhGvQAAAAJ
- [x] ORCID : https://orcid.org/0009-0008-8554-8425
- [x] Academia : https://universitecheikhantadiopdedakar.academia.edu/ElHadjiBassirouToure
- [x] GitHub : https://github.com/elbachir67
- [x] LinkedIn : aucun (ne pas afficher)

## Ordre d'exécution

US-01 → US-04 → US-02 → US-03 → US-07. Arrêt pour validation PO après chaque story.

---

### US-01 — Initialiser le dépôt et le projet Quarto (3 pts)

En tant que PO, je veux un projet Quarto structuré et versionné,
afin de disposer d'une base saine pour toutes les stories suivantes.

**Critères d'acceptation**
- [ ] Dépôt `elbachir67.github.io` initialisé, branche par défaut `main`.
- [ ] `_quarto.yml` : `type: website`, `output-dir: _site`, `lang: fr`,
      `render` limité à `**/*.qmd`, `execute: freeze: auto`.
- [ ] Barre de navigation : Accueil, Recherche, Enseignement, Blog, CV.
- [ ] Une page `.qmd` par entrée ; les pages non traitées affichent « En construction ».
- [ ] Fichiers présents : `.gitignore` (`_site/`, `.quarto/`, `.venv/`, `__pycache__/`),
      `requirements.txt` (jupyter, numpy, matplotlib), `README.md`.
- [ ] `CLAUDE.md` et `_specs/` commités à la racine.
- [ ] `quarto render` sans erreur ni avertissement.

### US-04 — Gouvernance du dépôt (1 pt)

En tant que PO, je veux des règles et des modèles standard,
afin que chaque changement soit traçable et relu.

**Critères d'acceptation**
- [ ] `.github/pull_request_template.md` : Story liée, Changements, Comment tester, Checklist DoD, Propositions.
- [ ] `.github/ISSUE_TEMPLATE/` : `user-story.md` et `bug.md`.
- [ ] Labels créés via `gh` : `epic:EP1`…`epic:EP6`, `type:feature`, `type:bug`, `type:ci`, `prio:M/S/C`.
- [ ] Milestone « Sprint 1 » créé ; une issue par story du sprint, labellisée.
- [ ] Protection de `main` (PR obligatoire, check CI requis, pas de force push) :
      commande `gh api` fournie au PO ou appliquée si les droits le permettent.

### US-02 — Intégration continue (3 pts)

En tant que PO, je veux que chaque PR soit vérifiée automatiquement,
afin de ne jamais publier un site cassé.

**Critères d'acceptation**
- [ ] `.github/workflows/ci.yml` déclenché sur `pull_request` vers `main`.
- [ ] Étapes : checkout, installation de Quarto (version épinglée), Python + `requirements.txt`, `quarto render`.
- [ ] Vérification des liens sur `_site/` (lychee) : liens internes cassés = échec ; liens externes = avertissement.
- [ ] Cache pip activé.
- [ ] Une PR volontairement cassée fait échouer la CI (preuve dans la PR).

### US-03 — Déploiement continu (2 pts)

En tant que PO, je veux que chaque merge sur `main` mette le site en ligne,
afin de publier sans manipulation manuelle.

**Critères d'acceptation**
- [ ] `.github/workflows/deploy.yml` déclenché sur `push` vers `main`.
- [ ] Publication sur la branche `gh-pages` via `quarto-dev/quarto-actions/publish`.
- [ ] Permissions minimales (`contents: write`).
- [ ] Instructions au PO pour la configuration unique : Settings → Pages → source `gh-pages`.
- [ ] Site accessible sur `https://elbachir67.github.io`.
- [ ] Badge de statut du déploiement dans le `README.md`.

### US-07 — Page d'accueil (2 pts)

En tant que visiteur (étudiant, collègue, partenaire), je veux identifier en quelques
secondes qui est l'enseignant et comment le joindre, afin d'accéder à ses travaux.

**Critères d'acceptation**
- [ ] Gabarit Quarto `about` (trestles ou jolla) avec photo et texte alternatif.
- [ ] Nom, titre « Maître de Conférences Titulaire », DMI / FST / UCAD.
- [ ] Bio fournie par le PO, **sans reformulation** des faits.
- [ ] Liens : Google Scholar, ORCID, GitHub, Academia, email (pas de LinkedIn).
- [ ] Aucun numéro de téléphone.
- [ ] Rendu vérifié à 375 px et en desktop.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-01-bilan.md` (voir CLAUDE.md §11).
