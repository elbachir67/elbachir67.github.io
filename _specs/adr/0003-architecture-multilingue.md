# ADR-0003 — Architecture multilingue : profils Quarto et arborescence `/en/`

**Statut :** Accepté · **Décideur :** PO · **Story :** US-37 (Sprint 3)

## Contexte

Le site doit devenir bilingue français / anglais (US-36) : chaque page du périmètre bilingue existe dans les
deux langues, avec des URL stables (`/` en français, `/en/` en anglais), un sélecteur de langue qui mène à la
page équivalente, et des balises `hreflang` réciproques.

**Quarto n'a pas de support multilingue natif**, y compris en 1.10.18 : aucune option de projet ne décline un
site en plusieurs langues. Les projets existants utilisent soit les profils de projet, soit le paquet R
babelquarto ([discussion Quarto #2876](https://github.com/quarto-dev/quarto-cli/discussions/2876),
[discussion #12874](https://github.com/orgs/quarto-dev/discussions/12874)).

**Contraintes du projet, rappelées par le sprint :**

- **pas de R en CI** (la chaîne est Quarto + Python, voir ADR-0001) ;
- **maintenance par une seule personne**, qui n'est pas développeur à plein temps ;
- **URL stables**, car les liens du CV papier et des profils académiques pointeront vers ces adresses ;
- **compatibilité avec les filtres Lua existants** : `cv/cv.lua` et `enseignement/cours.lua` lisent des
  données YAML au rendu ;
- **coût d'ajout d'une page** le plus faible possible.

## Options évaluées

Chaque option a été mesurée sur une maquette jetable de deux pages par langue (accueil et CV), avec un filtre
Lua lisant un YAML partagé. La maquette a servi au spike puis a été supprimée : elle n'est pas commitée.

### Option A — Arborescence parallèle, un seul `_quarto.yml`

Pages françaises à la racine, pages anglaises dans `en/`, une seule configuration.

- **Ce qui marche :** URL `/` et `/en/` obtenues directement ; un seul rendu ; les filtres Lua fonctionnent,
  y compris en lisant les mêmes données et en changeant de libellés selon `lang` (vérifié : la même page CV
  affiche « Parcours » en français et « Positions » en anglais).
- **Ce qui ne marche pas :** la barre de navigation et le pied de page sont définis une seule fois pour tout
  le projet. Sur les pages anglaises, les entrées restaient en français (« Accueil », « CV »). Il n'existe pas
  de configuration de navigation par dossier.

### Option B — Profils Quarto, une configuration par langue

`_quarto.yml` commun, plus `_quarto-fr.yml` et `_quarto-en.yml` : chacun apporte sa navigation traduite, sa
langue et sa liste de fichiers à rendre. Deux rendus, puis assemblage.

- **Ce qui marche (vérifié sur la maquette) :**
  - navigation entièrement traduite par langue ;
  - URL `/` et `/en/` stables ;
  - filtres Lua inchangés, avec les mêmes données YAML ;
  - **sélecteur de langue vers la page équivalente** : l'entrée de navigation porte `rel: alternate`, et un
    script de quelques lignes remplace sa cible par le chemin équivalent. Testé dans Chrome : depuis
    `/cv.html` il mène à `/en/cv.html`, et inversement ; depuis `/` il mène à `/en/` ;
  - **`hreflang` réciproques** : un filtre Lua calcule les adresses depuis le chemin du fichier source et
    ajoute `hreflang="fr"`, `hreflang="en"` et `x-default`. Vérifié sur les quatre pages de la maquette.
- **Ce qu'il faut savoir :**
  - **deux rendus dans le même dossier ne cohabitent pas.** Rendu français puis anglais dans `_site` : la
    page CV française avait disparu, car chaque rendu nettoie la sortie. Il faut donc un dossier de sortie par
    langue (`_site` et `_site-en`), puis copier `_site-en/en/` dans `_site/en/`. Les liens et les chemins
    `site_libs` des pages anglaises restent valides après la copie (vérifié) ;
  - **Quarto rend toujours la page d'accueil du projet**, même si la liste de rendu ne la contient pas ;
  - **les exclusions de la liste de rendu s'appliquent au nom de fichier** : `!index.qmd` exclut aussi
    `en/index.qmd`. Il faut écrire `!en/**` côté français et ne pas exclure par nom court ;
  - **le schéma refuse les attributs libres** sur une entrée de navigation (`data-…` est rejeté,
    `aria-label` est accepté mais n'est pas écrit dans le HTML). `rel` fonctionne, et `rel="alternate"` a le
    sens attendu ici.

### Option C — babelquarto

Paquet R de rOpenSci, qui rend un projet Quarto multilingue à partir de fichiers `index.qmd`, `index.en.qmd`,
et ajoute un bouton de langue ([documentation](https://docs.ropensci.org/babelquarto/)).

- **Ce qui marche :** convention de nommage simple, bouton de langue fourni, projet maintenu par rOpenSci.
- **Ce qui bloque :** **c'est un paquet R**, appelé par `babelquarto::render_book()`. Il faudrait installer R
  en local et en CI, ce que la contrainte du sprint exclut, et ce qui contredit ADR-0001 (chaîne Quarto +
  Python). L'option n'a pas été maquettée : la contrainte est éliminatoire.

## Comparaison

| Critère | A — Arborescence seule | B — Profils | C — babelquarto |
|---|---|---|---|
| Pas de R en CI | ✅ | ✅ | ❌ **éliminatoire** |
| Navigation traduite | ❌ impossible | ✅ | ✅ |
| URL stables `/` et `/en/` | ✅ | ✅ | ✅ (`/en/` selon convention) |
| Filtres Lua existants | ✅ | ✅ | non vérifié |
| Sélecteur vers la page équivalente | script à écrire | ✅ script de 5 lignes, testé | fourni |
| Rendu | 1 commande | 2 commandes + copie | 1 fonction R |
| Coût d'ajout d'une page | 2 fichiers | 2 fichiers | 2 fichiers |
| Dépendances ajoutées | aucune | aucune | R + paquets |

## Décision

**Option B : profils Quarto, pages françaises à la racine et pages anglaises dans `en/`.**

Mise en œuvre prévue pour US-36 :

1. `_quarto.yml` garde ce qui ne dépend pas de la langue (thème, formats, référencement, extensions).
   `_quarto-fr.yml` et `_quarto-en.yml` portent `lang`, la navigation, le pied de page et la liste de rendu.
2. Rendu en deux temps : `quarto render --profile fr` vers `_site`, `quarto render --profile en` vers
   `_site-en`, puis copie de `_site-en/en/` dans `_site/en/`. Cette séquence est écrite une fois dans un
   script, utilisé en local comme en CI.
3. Sélecteur de langue : entrée de navigation avec `rel: alternate`, dont la cible est corrigée par un petit
   script, plus un repli sans JavaScript vers l'accueil de l'autre langue.
4. `hreflang` : filtre Lua calculant les adresses depuis le chemin du fichier source, avec `x-default` vers
   le français.
5. Contenus partagés (publications, catalogue des cours, CV) : **les données restent uniques** ; seuls les
   libellés d'interface sont traduits, dans les filtres Lua existants, en fonction de `lang`.
6. La CI vérifie que chaque page du périmètre bilingue a son équivalent et que les `hreflang` sont réciproques
   (critère d'US-36), et le contrôle de référencement d'US-13 couvre les deux langues.

## Conséquences

- (+) Aucune dépendance nouvelle : Quarto, Lua et Python suffisent.
- (+) Navigation, pied de page et libellés réellement traduits, sans dupliquer les données.
- (+) URL stables et compatibles avec le référencement déjà en place.
- (−) Deux rendus au lieu d'un, donc un temps de build à peu près doublé, et une étape d'assemblage à ne pas
  oublier : elle est donc scriptée et jouée en CI.
- (−) Les pages existent en double, une par langue : c'est le prix d'un site bilingue, mais la CI empêche
  qu'une version parte sans l'autre.
- (−) Le sélecteur « page équivalente » dépend de JavaScript ; sans JavaScript, il mène à l'accueil de
  l'autre langue.
- **Cours monolingues** (décision PO du Sprint 3) : les pages de cours restent en français et sortent du
  périmètre bilingue. Le contrôle de la CI ne doit donc pas exiger d'équivalent pour elles, et une note
  indiquera la langue du cours au visiteur anglophone.
