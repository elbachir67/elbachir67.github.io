# Bilan du Sprint 3 — Bilingue et premier cours natif

**Objectif du sprint :** le site est navigable en français et en anglais, et le premier chapitre d'un cours
est lisible en ligne, généré depuis les sources LaTeX existantes.

**Période :** du commit `67ed169` (17/09/2026 21:45 UTC, première PR du sprint) au commit `9bb7b3e`
(18/09/2026 01:47 UTC). 8 commits sur `main`, soit un par pull request mergée : chaque PR est écrasée en un
seul commit au merge, si bien que les commits de branche ne figurent pas dans l'historique de `main`. Ce
bilan cite donc le numéro de PR et le commit correspondant sur `main`.

**Sources :** historique Git, pull requests (`gh pr list --state all`), issues de la milestone « Sprint 3 »
et exécutions GitHub Actions (`gh run list`). Chaque fait ci-dessous cite sa source.

## 1. Stories livrées

Les 6 stories du sprint sont livrées, et leurs issues sont fermées.

| Story | Titre | PR | Commit sur `main` | Merge (UTC) | Issue |
|---|---|---|---|---|---|
| US-37 | Spike + ADR-0003 : architecture multilingue | #47 | `67ed169` | 17/09 21:45 | #40 |
| US-36 | Site bilingue FR/EN avec sélecteur de langue | #48 | `a8957ff` | 17/09 23:41 | #41 |
| US-14 | Gabarit de cours | #49 | `2a0e5a2` | 18/09 01:02 | #42 |
| US-15 | Conversion du deck Beamer en slides Quarto | #50 | `c1775c5` | 18/09 01:02 | #43 |
| US-18 | Figures Python exécutées et gelées | #51 | `96995c2` | 18/09 01:27 | #44 |
| US-16 | Migration du cours pilote : slides du chapitre 1 | #52 | `a8d942e` | 18/09 01:40 | #45 |

Deux stories portaient des critères vérifiables seulement après déploiement (règle `Refs #N`, CLAUDE.md §6) :
les preuves ont été postées sur #41 et #45 après mise en ligne, et les issues fermées ensuite.

### Pull requests hors story

| PR | Objet | Commit | Merge (UTC) |
|---|---|---|---|
| #46 | Specs du sprint : `sprint-03.md`, décisions du PO, backlog (US-38, US-39, US-40), règle de langue de `CLAUDE.md` | `a9232fa` | 18/09 01:41 |
| #53 | Complément d'US-16 : semestre, prérequis et objectifs du cours, fournis par le PO après le merge de #52 | `9bb7b3e` | 18/09 01:47 |

## 2. Points

| | Points |
|---|---|
| Engagés (6 stories du sprint) | **30** |
| Livrés | **30** |
| Écart | **0** |

Détail : US-37 (2) + US-36 (8) + US-14 (5) + US-15 (8) + US-18 (2) + US-16 (5).

## 3. Écarts

### Par rapport au périmètre annoncé

- **La page Contact n'existait pas.** Le périmètre linguistique de `sprint-03.md` la citait parmi les pages
  bilingues, mais aucune page Contact n'était publiée : le contact vit dans le pied de page et sur l'accueil.
  Elle est sortie du périmètre d'US-36 et devient **US-38** au backlog (Should, 2 pts, sans sprint), décision
  du PO sur #48, consignée dans #46.
- **US-15 et US-16 ont changé de cible en cours de sprint.** Les sources déposées par le PO (`_import/`)
  sont un **deck Beamer de 20 frames**, et non un document rédigé. Sur décision du PO, la conversion vise un
  `.qmd` **revealjs** — une frame par slide — et US-16 livre les slides du chapitre 1, et non une page
  rédigée. Les critères ont été réécrits dans #46 avant l'implémentation.
- **La conversion TikZ → SVG n'a pas été exercée.** Le critère, écrit d'après la description initiale des
  sources, reste au sprint pour les cours qui en contiennent : le deck du chapitre 1 n'a aucun TikZ (#46).
- **Une page rédigée par chapitre**, en complément du deck, devient **US-40** (Should, 5 pts, sans sprint),
  décision du PO sur #46.

### Par rapport aux critères d'acceptation

- **US-36** : les données partagées (CV, catalogue) restent en français sur les pages anglaises, comme le
  critère « données non dupliquées » le prévoyait ; leur traduction devient **US-39** (#46). Les adresses
  anglaises portent un nom anglais (`/en/research/`, `/en/teaching/`) plutôt que le miroir du français, et
  chaque langue a reçu **son propre index de recherche** : deux décisions du PO prises pendant la revue de
  #48, mises en œuvre dans la même PR.
- **US-14** : le cours de démonstration à deux chapitres, exigé par un critère, a été publié le temps de
  valider le gabarit (décision du PO : le garder en ligne jusqu'à US-16), puis supprimé par #52.
- **US-16** : le critère « le PDF du chapitre reste téléchargeable » est satisfait par l'impression du deck
  depuis le navigateur (`?print-pdf`, 25 pages, une par slide) ; la génération automatisée reste US-17
  (Sprint 4), comme #46 l'a acté.
- **US-16** : le cours a d'abord été publié sans semestre, prérequis ni objectifs — ces données ne figurent
  dans aucune source fournie, et la règle « ne jamais inventer de contenu académique » (CLAUDE.md §7) les
  interdisait. Le PO les a données après le merge, et #53 les a ajoutées.

### Règles et documentation mises à jour

- **CLAUDE.md §7** : la règle de langue décrivait « tout en français sauf la page Recherche ». Elle décrit
  désormais un site bilingue (pages françaises à la racine, pages anglaises sous `en/`, cours monolingues,
  specs et messages de commit en français), et l'arborescence du §5 montre les profils et le dossier `en/`
  (#46).
- **ADR-0003** (#47) fixe l'architecture multilingue : profils Quarto, deux rendus, assemblage.
- **`_specs/contenus/latex-vers-quarto.md`** (#50) documente la correspondance LaTeX → Quarto, y compris ce
  que la conversion ne fait pas.

## 4. Blocages

| Blocage | Effet | Comment il a été levé |
|---|---|---|
| **Deux rendus dans le même dossier s'écrasent** : chaque rendu nettoie sa sortie (constaté au spike US-37) | Le site bilingue perdait une langue sur deux | Un dossier de sortie par langue, puis copie de `_site-en/en/` dans `_site/en/`, scriptée dans `scripts/rendre.py` (#47, #48) |
| **`lang: en` réécrit par Quarto en `../../en`**, chemin qui entrait en collision avec le dossier `en/` | Échec du rendu Typst du CV anglais | `lang: en-US` dans le profil anglais (#48) |
| **`site-url` absent des métadonnées vues par le filtre** | Les balises `hreflang` ne pouvaient pas être calculées | Ancre YAML au niveau du projet, lue par le filtre (#48) |
| **Titres identiques entre langues** refusés par le contrôle de référencement | Contrôle en échec en local, avant la première exécution de la CI | Unicité vérifiée **par langue**, la langue étant lue dans `<html lang>` (#48) |
| **Un seul index de recherche pour les deux langues** | Une recherche en anglais proposait des pages françaises | Un index par langue, les pages anglaises étant rattachées à la racine `/en/` par leur méta `quarto:offset`, ajustée à l'assemblage (#48) |
| **Contrastes insuffisants sur les pages de cours** en mode sombre (fil d'Ariane 4,4:1, liens précédent/suivant 3,39:1) et cibles de 20 px à 375 px | Violations axe-core | Sélecteurs reprenant ceux du thème avec une classe de plus, sans `!important` (#49) |
| **Police des slides ramenée à du Times** : `Source Sans 3` perdait ses guillemets dans le CSS produit, et un nom de famille commençant par un chiffre rend la déclaration invalide | Slides hors charte | `unquote()` dans la feuille de style des slides (#50) |
| **Titres d'encadrés à 3,9:1**, encore atténués par l'opacité de 85 % appliquée par Quarto | Violations axe-core sur les slides | Une teinte assombrie par encadré (au moins 5,9:1) et `opacity: 1` (#50) |
| **`aria-label` interdit** sur les ancres de numérotation des lignes de code | Violation axe-core | Numérotation désactivée, comme dans le deck d'origine (#50) |
| **revealjs n'écrit pas la balise `description`** | Le contrôle de référencement échouait sur les slides | Filtre Lua déclaré au niveau du projet, actif pour les seules slides (#50) |
| **Ni `code-fold` ni un callout `collapse` ne replient quoi que ce soit en revealjs** | Le critère « code masqué, avec un bouton pour l'afficher » (US-18) | Repli `<details>` généré par le script d'import, dont Quarto colore le contenu (#51) |
| **`_metadata.yml` s'applique aussi aux slides** : `toc: true` ajoutait une slide de sommaire, et nommer un format y faisait rendre la séance comme une page HTML ordinaire | Deck dénaturé | Le fichier ne porte plus que la profondeur et le titre de la table des matières ; le piège est documenté dans le README (#52) |
| **Cache `.quarto` pollué et page rendue à côté de sa source** (`cv/index.html`), après un rendu manuel d'un fichier isolé | Pages françaises ressorties en `lang="en"`, contrôle de référencement en échec | Fichier supprimé, rendu relancé avec `--propre`, pages rendues désormais ignorées par git, piège décrit dans le README (#53) |

**Stabilité de la CI et du déploiement.** Sur la période : **16 exécutions de la CI, toutes en succès**, et
**8 déploiements, tous en succès**. Aucun échec de CI n'est survenu pendant le sprint ; les échecs corrigés
ci-dessus l'ont été avant la première exécution distante, en local.

**Un point de méthode.** La CI et le déploiement installaient `requirements.txt` à chaque exécution alors que
les résultats d'exécution sont gelés. Leur présence aurait permis à un gel oublié de passer inaperçu : Quarto
aurait réexécuté le code et publié autre chose que ce qui est commité. Ces installations ont été retirées
(#51), et le journal de la CI le confirme : plus aucune trace de `matplotlib` ni de `jupyter`.

## 5. Propositions

Reprises des sections « Propositions » des PR du sprint. Les propositions déjà acceptées et transformées en
stories (US-38, US-39, US-40) ne sont pas répétées.

### Qualité et outillage

- **Vérifier la conversion en CI** (#50, #51) : rejouer l'import d'un chapitre et échouer si le `.qmd`
  commité en diffère. La CI garantirait que les slides — et leur gel — restent le reflet exact des sources.
- **Accessibilité en CI** (rappel du Sprint 2, toujours valable) : axe-core sert à chaque story en local, et
  couvre désormais 52 combinaisons de pages plus les 25 slides. L'ajouter à la CI éviterait une régression.
- **Index de recherche par langue côté Quarto** (#48) : le rattachement actuel passe par la méta
  `quarto:offset`, ajustée à l'assemblage. Une option native rendrait l'astuce inutile.
- **Module de style matplotlib partagé** (#51) : couleurs de la charte, police, absence de cadre, pour que
  toutes les figures calculées des cours se ressemblent.

### Cours et contenus

- **Notes du présentateur** (#50) : `\note{}` se convertirait en `::: {.notes}` ; le deck du chapitre 1 n'en
  contient pas.
- **Numérotation automatique des chapitres** (#49) à partir du nom de fichier, pour ne pas écrire « 1. » dans
  chaque titre — utile à partir d'une dizaine de chapitres.
- **Image de partage par cours** (#49) : les pages de cours héritent de la photo du site.
- **Fil d'Ariane des séances** (#49) : il reprend le nom du dossier `chapitres`. Un libellé plus parlant
  demanderait un titre de section dans la barre latérale.
- **Couleurs des encadrés dans `custom.scss`** (#50) : pour qu'une page rédigée (US-40) les affiche comme les
  slides.
- **Séances suivantes** (#52) : le chemin est le même — déposer le `.tex` et ses figures, rejouer l'import.

### Suite

- **US-17** (PDF du cours généré depuis les mêmes sources) est au Sprint 4 : le `?print-pdf` du navigateur
  tient lieu de solution en attendant.
- **US-38, US-39, US-40** et **US-05** restent au backlog sans sprint, en attente d'arbitrage du PO.
