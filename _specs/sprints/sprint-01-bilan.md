# Bilan — Sprint 1 : Socle en ligne

Rédigé par Claude Code (CLAUDE.md §11) à partir de l'historique Git de `main`, des PR et issues
GitHub et des exécutions GitHub Actions. Toutes les heures sont en UTC, le 2026-09-16.
Les SHA cités sans autre précision sont ceux de `main`.

## Synthèse

- **Objectif atteint** : le site est en ligne sur https://elbachir67.github.io. Il est déployé
  automatiquement à chaque merge sur `main` (3 déploiements sur 3 réussis) et sa page d'accueil
  est réelle (#16, vérifiée en ligne sur #9).
- **5 stories sur 5 livrées, 11 points sur 11.**
- **PR** : 9 mergées (#1, #2, #3, #4, #10, #11, #12, #15, #16) et 2 PR de preuve fermées sans merge
  (#13, #14).
- **CI** : 9 runs, dont 7 succès et 2 échecs, tous deux volontaires (preuves d'US-02).
- **Durée** : sprint prévu sur 1 semaine, réalisé en environ 3 h 10, du commit d'amorçage `f76d451`
  (14:45) au dernier merge `7858c19` (17:56).

## 1. Stories livrées

| Story | Titre | Pts | PR | Merge | Commit | Issue |
|---|---|---|---|---|---|---|
| US-01 | Initialiser le dépôt et le projet Quarto | 3 | #1, puis #2 (spec) | 15:17 | `19c981f` | #5, fermée à 16:01 (créée après le merge) |
| US-04 | Gouvernance du dépôt | 1 | #10 | 16:10 | `8ce9b63` | #6, fermée par #10 |
| US-02 | Intégration continue | 3 | #12 | 17:22 | `e06625a` | #7, fermée par #12 |
| US-03 | Déploiement continu | 2 | #15 | 17:23 | `5bebe4f` | #8, fermée à 17:39 après les vérifications en ligne (règle `Refs`) |
| US-07 | Page d'accueil | 2 | #16 | 17:56 | `ca60b3e` | #9, fermée par #16 |

L'ordre d'exécution prévu (US-01 → US-04 → US-02 → US-03 → US-07) est respecté, d'après les heures
de merge. Milestone « Sprint 1 » : 0 élément ouvert, 13 fermés (5 issues, 8 PR).

**Chaîne CI/CD observée :**

| Workflow | Run | Commit | Résultat | Contexte |
|---|---|---|---|---|
| CI | 35120881846 | `39fa729` | ✅ | #12, premier run |
| CI | 35121061781 | `65efd82` | ❌ volontaire | #13 : lien interne cassé |
| CI | 35121210940 | `6ae3d61` | ✅ + avertissement | #13 : lien externe cassé seul |
| CI | 35122173431 | `bc6f1a9` | ✅ | #12, version finale |
| CI | 35122358569 | `6594299` | ❌ volontaire | #14 : avertissement de `quarto render` |
| CI | 35127760976 | `f16b768` | ✅ | #15, après `gh pr update-branch` |
| CI | 35127840187 | `913116d` | ✅ | #11, après `gh pr update-branch` |
| CI | 35130068346 | `b7f9bde` | ✅ + avertissement | #16 : faux positifs 403 (Scholar, Academia) |
| CI | 35130710482 | `b709721` | ✅ | #16, avec `.lycheeignore` |
| Déploiement | 35127865286 | `5bebe4f` | ✅ | merge de #15, premier déploiement |
| Déploiement | 35131251462 | `ca60b3e` | ✅ | merge de #16 |
| Déploiement | 35131264498 | `7858c19` | ✅ | merge de #11 |

## 2. Points

| Engagés | Livrés | Écart |
|---|---|---|
| 11 | 11 | 0 |

Ajouté au backlog pendant le sprint, sans être planifié : **US-34 — Montée de version Quarto 1.10**
(EP1, Should, 1 pt), via #12.

## 3. Écarts

### Objectif du sprint

Aucun écart. La chaîne « modification sur une branche → PR → CI verte → merge → visible en ligne » a
été constatée de bout en bout sur #16 : CI 35130710482 ✅, merge `ca60b3e`, déploiement 35131251462 ✅,
build Pages 35131335818 ✅, contenu vérifié en ligne (commentaire sur #9).

### Critères d'acceptation

| Story | Écart | Décision | Source |
|---|---|---|---|
| US-01 | L'entrée de navigation « Recherche » devient « Research » | PO | #1, spec alignée dans #2 (`5815536`) |
| US-04 | « Check CI requis » non applicable avant l'existence de la CI : reporté à US-02 | PO | #10 ; appliqué dans #12 (check `rendu-et-liens`) |
| US-04 | Protection avec 0 approbation requise (compte GitHub unique) | PO | #10 ; ADR-0002 mis à jour dans #11 |
| US-02 | Ajouts hors critères : échec sur tout avertissement de `quarto render`, Dependabot (actions GitHub, mensuel, groupé), `strict: false` | PO | #12 |
| US-03 | Critère ajouté : « Site en ligne vérifié dans Chrome à 375 px et en desktop » | PO | #4 (`c2103b1`) |
| US-03 | Critère « Instructions au PO : Settings → Pages » remplacé par une configuration via `gh api` | PO | #11 (`7858c19`), issue #8 mise à jour |
| US-07 | Ajout d'un `.lycheeignore` (modification de la CI) dans la PR d'une story de contenu | PO | #16 (`b709721`) |

### Definition of Done

- **« CI verte sur la PR »** : non applicable pour #1, #2, #3, #4 et #10, mergées avant que la CI
  existe (merge de #12 à 17:22).
- **Vérification visuelle dans Chrome** : la fenêtre pilotée était rendue en arrière-plan, avec un
  viewport figé à 1440 px. Les contrôles à 375 px ont donc été faits dans une iframe de largeur exacte
  (`innerWidth` = 375), et non en redimensionnant la fenêtre (#8, #16). Après le merge de #16,
  l'extension Chrome n'était plus connectée : la vérification en ligne d'US-07 a été faite en HTTP
  (#9).

### Processus

- **Commit direct sur `main`** : `f76d451`, commit d'amorçage d'un dépôt vide, sur lequel aucune PR
  ne pouvait être ouverte. Décision validée par le PO dans #1.
- **Changements de configuration hors diff**, tous faits via `gh` et tracés dans les PR et issues :
  - labels, milestone, issues et protection de `main` (#10, #12) ;
  - suppression des 10 labels par défaut (#11) ;
  - création de la branche `gh-pages` (`2d12618`) et bascule de la source de Pages (#15, #8).
- **Règles de processus adoptées pendant le sprint** :
  - bilan rédigé par Claude Code à la place de la revue et de la rétrospective (#3) ;
  - regroupement des petites corrections de specs dans une PR par sprint (#11) ;
  - `Refs #N` quand un critère ne se vérifie qu'après le déploiement (#11) ;
  - ADR-0002 aligné (#11).
- **PR hors story** : #3 (processus), #11 (specs du sprint), #13 et #14 (preuves, fermées).
  #2 et #4 étaient des corrections de specs séparées, antérieures à la règle de regroupement.

## 4. Blocages

| Blocage | Effet | Résolution | Source |
|---|---|---|---|
| Dépôt GitHub vide | Impossible d'ouvrir la première PR | Commit d'amorçage `f76d451` limité aux fichiers du PO | #1 |
| PR #1 mergée avant l'ajout d'un commit demandé | Le commit ne pouvait plus y entrer | PR séparée #2 | #2 |
| Check CI obligatoire impossible avant US-02 | Il aurait bloqué tous les merges, dont US-04 | Report décidé par le PO, activation dans #12 | #10, #12 |
| #11 et #15 ouvertes avant la CI | Bloquées (`BLOCKED`) par le check obligatoire | `gh pr update-branch` (runs 35127840187, 35127760976) | #11, #15 |
| Le PO n'a pas accès au site GitHub | Critère « Settings → Pages » irréalisable | Toute la configuration faite via `gh` ; critère reformulé | #10, #11 |
| Premier `quarto publish gh-pages` interactif (`Confirm.prompt`) | Échec probable du premier déploiement en CI | Branche `gh-pages` créée à l'avance via l'API (`2d12618`) | #15 |
| Pages activé d'office sur `main` avec Jekyll | README et `CLAUDE.md` (`/CLAUDE.html`) publiés à la place du site | Bascule de la source sur `gh-pages` : ces pages renvoient 404 | #15, #8 |
| La bascule de source n'a pas lancé de build | Ancien contenu servi | Build demandé via l'API (run 35129157827). Les builds suivants sont automatiques (35131335818, 35131417213) | #8 |
| `quarto render` sort avec le code 0 malgré ses avertissements, messages colorés en ANSI | La DoD « sans avertissement » n'était pas vérifiée par la CI | Filtre des lignes `WARN`, après retrait des codes ANSI, dans `ci.yml` | #12, #14 |
| Google Scholar et Academia renvoient 403 aux runners | Avertissement permanent sur les PR | `.lycheeignore` limité à ces deux domaines | #16 |
| Fenêtre Chrome en arrière-plan, puis extension déconnectée | Viewport non redimensionnable, puis aucun accès au navigateur | Iframe de 375 px, puis contrôle HTTP | #8, #16, #9 |

## 5. Propositions

**Reprises des sections « Propositions » des PR :**

| Proposition | PR d'origine | Statut |
|---|---|---|
| Ajouter « Publications » à la navigation avec US-09 | #1 | **En attente** (Sprint 2) |
| Pied de page (mentions, année, lien vers le dépôt) avec US-06 | #1 | **En attente** (Sprint 2) |
| Vérification du site en ligne sur mobile comme critère d'US-03 | #3 | Acceptée, intégrée (#4) |
| Configuration de Pages via `gh api` | #10 | Acceptée, intégrée (#11) |
| Mettre ADR-0002 à jour (bilan de sprint) | #10 | Acceptée, intégrée (#11) |
| Supprimer les labels par défaut de GitHub | #10 | Acceptée, faite (#11) |
| Faire échouer la CI sur un avertissement de `quarto render` | #12 | Acceptée, intégrée (#12) |
| Dependabot | #12 | Acceptée pour les actions GitHub seulement (#12) ; Quarto passe par US-34 |
| Exclure Scholar et Academia de lychee | #16 | Acceptée, intégrée (#16) |

**Points signalés dans le corps des PR, sans proposition formelle :**

- Les icônes génériques de Scholar, ORCID et Academia sont à revoir avec la charte graphique, US-06 (#16).
- Les liens `mailto:` ne sont pas vérifiés par lychee (#12) : l'email de l'accueil n'est contrôlé que
  manuellement. À garder en tête pour US-12 (email protégé).
