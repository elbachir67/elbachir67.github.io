# Bilan du Sprint 2 — Vitrine académique

**Objectif du sprint :** un visiteur (collègue, partenaire, étudiant) trouve en ligne les travaux de recherche,
les publications, le CV et le catalogue des cours, dans une charte graphique cohérente.

**Période :** du commit `63108a3` (16/09/2026 18:57 UTC, fin du Sprint 1) au commit `34fff17`
(17/09/2026 19:42 UTC). 12 commits sur `main`, soit un par pull request mergée : chaque PR est écrasée
en un seul commit au merge, si bien que les commits de branche ne figurent pas dans l'historique de `main`.
Ce bilan cite donc le numéro de PR et le commit correspondant sur `main`.

**Sources :** historique Git, pull requests (`gh pr list --state all`), issues de la milestone « Sprint 2 »
et exécutions GitHub Actions (`gh run list`). Chaque fait ci-dessous cite sa source.

## 1. Stories livrées

Les 8 stories du sprint sont livrées, et leurs issues sont fermées.

| Story | Titre | PR | Commit sur `main` | Merge (UTC) | Issue |
|---|---|---|---|---|---|
| US-34 | Montée de version Quarto 1.10 | #27 | `9d36b16` | 16/09 19:38 | #19 |
| US-06 | Charte graphique | #28 | `d8d034b` | 16/09 20:54 | #20 |
| US-09 | Publications générées depuis BibTeX | #29 | `4b2132c` | 17/09 00:38 | #21 |
| US-08 | Page Research en anglais | #30 | `739fc35` | 17/09 01:06 | #22 |
| US-11 | Catalogue des cours | #35 | `ebd2947` | 17/09 13:45 | #24 |
| US-10 | CV en ligne généré depuis une source unique | #32 | `e3942cf` | 17/09 15:47 | #23 |
| US-13 | SEO et métadonnées | #36 | `b20e4d6` | 17/09 16:03 | #25 |
| US-12 | Email protégé | #38 | `86756e4` | 17/09 19:41 | #26 |

**Ordre d'exécution.** Le sprint prévoyait US-34 → US-06 → US-09 → US-08 → US-10 → US-11 → US-13 → US-12.
US-11 (#35) a été mergée avant US-10 (#32), sur décision du PO : US-10 attendait sa validation, puis une
mise à jour avec `main`.

**US-13 et la vérification en ligne.** La PR #36 référençait l'issue par `Refs #25`, comme le prévoit
CLAUDE.md §6 pour un critère vérifiable seulement après déploiement. Après le merge (déploiement
[run 35244252048](https://github.com/elbachir67/elbachir67.github.io/actions/runs/35244252048), publication
Pages [run 35244353130](https://github.com/elbachir67/elbachir67.github.io/actions/runs/35244353130)), les
preuves ont été postées sur #25, qui a été fermée le 17/09 16:06 UTC.

### Pull requests hors story

| PR | Objet | Commit | Merge (UTC) |
|---|---|---|---|
| #18 | Specs du sprint : `sprint-02.md`, sources de contenu, règles de `CLAUDE.md`, backlog | `34fff17` | 17/09 19:42 |
| #31 | Cadre du projet AI4Nieup (page Research) et article CNRIA 2026 à paraître | `be9d7e3` | 17/09 01:43 |
| #34 | Section « Posters et communications » (un poster, deux communications) | `6cdf102` | 17/09 13:22 |
| #37 | Trois cours ajoutés au catalogue | `63c36a5` | 17/09 15:47 |
| #33 | Preuve du contrôle anti-téléphone (numéros factices) : **fermée sans merge**, branche supprimée | — | — |

## 2. Points

| | Points |
|---|---|
| Engagés (8 stories du sprint) | **17** |
| Livrés | **17** |
| Écart | **0** |

Détail : US-34 (1), US-06 (3), US-09 (3), US-08 (3), US-10 (2), US-11 (2), US-13 (2), US-12 (1).

Les quatre PR hors story (#18, #31, #34, #37) ne sont pas estimées en points : ce sont des demandes du PO
arrivées pendant le sprint, sur des stories déjà livrées.

## 3. Écarts

### Par rapport aux critères d'acceptation

| Story | Critère d'origine | Ce qui a été livré | Source |
|---|---|---|---|
| US-09 | « `publications.bib` construit à partir de la liste des sources (**8 références**) » | 12 entrées : 9 articles (dont l'article CNRIA 2026 accepté, à paraître) et 3 posters et communications | #31 (`be9d7e3`), #34 (`6cdf102`) |
| US-09 | Décision PO attendue sur ICECET 2026 | Confirmée publiée par le PO, affichée | #29 (`4b2132c`) |
| US-09 | Page « groupée par année décroissante » | Groupée par **année de conférence** (`event_year`), et non par année de publication de Crossref, qui reste dans le `.bib` | #29 (`4b2132c`) |
| US-09 | — | Clés BibTeX et ancres **stables, sans année**, pour les liens d'US-08 | #29 (`4b2132c`) |
| US-08 | « Lien vers `consistency-debt` **uniquement si** le PO le confirme » | Décision anticipée du PO : **aucun lien** vers un dépôt lié à un travail non publié. La règle « Travaux non acceptés » de `CLAUDE.md` est étendue, et le critère aligné | #18 (`34fff17`) |
| US-10 | « La version anglaise est reportée (US-35, Could, 2 pts) » | US-35 **fusionnée dans US-36** (site bilingue, Sprint 3) et retirée du backlog | #18 (`34fff17`) |
| US-11 | « un cours par entrée (titre, domaine, niveaux, **établissement**, statut) » | Champ **établissement retiré** par le PO, champ `skill` ajouté (jamais affiché) | #35 (`ebd2947`), specs dans #18 (`34fff17`) |
| US-11 | Catalogue des sources (14 cours) | Catalogue **remplacé** par le PO (18 cours), puis porté à **21** | #35 (`ebd2947`), #37 (`63c36a5`) |
| US-06 | — | Proposition de la PR acceptée : sous-ensemble **latin étendu** de la police, livré pendant US-09 | #29 (`4b2132c`) |

Aucun critère n'est resté non satisfait, et aucune story n'a été reportée.

### Par rapport à l'objectif du sprint

L'objectif est atteint : les pages Research, Publications, Enseignement et CV sont en ligne, dans la charte
graphique d'US-06. Deux ajouts vont au-delà de l'objectif, à la demande du PO : la section « Posters et
communications » (#34) et le PDF du CV téléchargeable, généré depuis la même source que la page (#32).

### Règles de travail modifiées pendant le sprint

Toutes dans #18, à la demande du PO :

- **Travaux non acceptés** (`CLAUDE.md` §7) : d'abord étendue aux liens vers les dépôts de travaux non
  publiés, puis aux travaux **acceptés**, qui peuvent apparaître avec la mention « (à paraître) ».
- **Backlog** : US-36 (site bilingue FR/EN, 8 pts) et US-37 (spike et ADR-0003, 2 pts) ajoutées en tête du
  Sprint 3, dans l'epic EP1. Le Sprint 3 passe de 20 à **30 points** : son contenu est à arbitrer au
  prochain planning.

### Qualité : contrôles ajoutés à la CI

Trois contrôles nouveaux, tous écrits avec la bibliothèque standard de Python ou `grep` :

| Contrôle | Story | Ce qu'il empêche |
|---|---|---|
| `scripts/verifier_telephone.py` | US-10 | Un numéro de téléphone publié, y compris dans le texte des PDF |
| `scripts/verifier_metadonnees.py` | US-13 | Une page sans titre ou description unique, sans métadonnées de partage, absente du sitemap |
| `grep` sur l'email (`ci.yml`) | US-12 | L'adresse en clair ou encodée, et tout lien `mailto:` écrit en dur |

## 4. Blocages

| Blocage | Effet | Comment il a été levé |
|---|---|---|
| **Démarrage du sprint** : la PR #27 était annoncée mergée mais encore ouverte, et Quarto 1.9.38 était installé au lieu de 1.10.18 | Arrêt avant US-06 | Question au PO (CLAUDE.md §6, étape 2), puis merge de #27 par le PO et installation de Quarto 1.10.18 depuis l'archive officielle, empreinte SHA-256 vérifiée, ancienne version conservée |
| **DBLP** : HTTP 429 puis connexions coupées | Métadonnées des publications | Crossref seul, ce que le critère d'US-09 autorise ; les 8 notices ont été trouvées |
| **IEEE Xplore** : HTTP 202, page anti-robot | Statut d'ICECET 2026 non vérifiable | Le PO a confirmé la publication et fourni le lien des actes (#29) |
| **cnria.org** : la page « Accepted Papers » ne publie pas la liste | Acceptation de l'article CNRIA 2026 non vérifiable | Déclaration du PO. L'édition, la ville et l'éditeur des actes viennent du site (2026) et de l'appel à communications EasyChair (2019) |
| **PyYAML absent** en local | US-10 et US-11 devaient lire du YAML | Filtres Lua lus par Quarto au rendu : aucune dépendance ajoutée, et aucun fichier généré à re-synchroniser |
| **Shortcode non exécuté** quand du HTML brut le précède dans une valeur YAML | Bouton « Email » de l'accueil (US-12) | Le shortcode produit lui-même l'icône |
| **CI en échec** sur #32 après mise à jour avec `main` : le contrôle du téléphone prenait 9 chiffres d'une empreinte de nom de fichier CSS pour un numéro | PR bloquée | Motif corrigé (aucune lettre ni chiffre autour), 8 cas testés, dans #32 (`e3942cf`). C'est le seul échec de CI non voulu du sprint ([run 35232097528](https://github.com/elbachir67/elbachir67.github.io/actions/runs/35232097528)) ; l'autre ([run 35174441537](https://github.com/elbachir67/elbachir67.github.io/actions/runs/35174441537)) était la preuve volontaire de #33 |
| **Conflits de fusion** sur #32 et #36, après les merges de #34, #35 et #37 | Deux PR validées non mergeables | Fusion de `main` dans chaque branche (sans réécriture d'historique) et résolution : les sections ajoutées de part et d'autre ont été conservées |
| **Métadonnées de partage cassées** : l'image d'aperçu des sous-pages pointait vers un chemin inexistant | US-13 | Chemin d'image donné depuis la racine du site |

**Stabilité de la CI et du déploiement.** Sur la période : 33 exécutions de la CI, dont 31 en succès et
2 en échec (celles ci-dessus), et **13 déploiements, tous en succès**.

## 5. Propositions

Reprises des sections « Propositions » des PR du sprint. Les propositions déjà acceptées et livrées
(latin étendu dans #29, règles et sources dans #18) ne sont pas répétées.

### Qualité et outillage

- **Accessibilité en CI** (#28) : axe-core sert déjà à chaque story en local, avec 0 violation sur
  24 combinaisons page × mode × largeur. L'ajouter à la CI éviterait une régression de contraste.
- **Cohérence de la page Publications** (#29) : lancer `python3 scripts/publications.py page` puis
  `git diff --exit-code` en CI, pour échouer si le `.bib` change sans que la page soit régénérée.
- **Ancres vérifiées** (#30) : activer la vérification des fragments de lychee (`--include-fragments`),
  pour qu'un lien vers une ancre supprimée ou renommée fasse échouer la CI.
- **Contrôle du téléphone au déploiement** (#32) : rejouer la même étape dans `deploy.yml`, en défense
  en profondeur.
- **Mise en commun des filtres Lua** (#35) : le CV et le catalogue lisent chacun un YAML avec quelques
  lignes identiques, qui pourraient tenir dans une petite extension partagée.

### Contenu et référencement

- **Publications antérieures sur la page Research** (#30) : les articles de 2012 à 2019 ne sont rattachés à
  aucun projet actif. Le PO peut indiquer quel article rattacher à quel domaine.
- **Téléchargement du BibTeX** (#29) : publier une copie du `.bib` filtrée sur le statut, pour que les
  collègues puissent citer directement.
- **`canonical` et `og:url`** (#36) : Quarto ne les produit pas ; utile surtout avec un nom de domaine
  personnalisé (US-05).
- **Image d'aperçu dédiée** (#36) : une image 1200 × 630 permettrait la carte `summary_large_image`.
- **Police du PDF et publications dans le CV** (#32) : aligner la police du PDF sur celle du site demanderait
  environ 1 Mo de fontes ; le `publications.bib` pourrait alimenter une section du PDF.
- **Contact sur la page CV** (#38) : le shortcode email peut servir ailleurs que sur l'accueil.

### Suite du sprint

- **US-05 (nom de domaine)** reste sans sprint, en attente de décision du PO.
- **Sprint 3** : US-37 (spike et ADR-0003) puis US-36 (site bilingue) sont en tête, avant les stories de
  cours natifs. Avec 30 points, son contenu est à arbitrer au planning.
