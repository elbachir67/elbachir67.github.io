# elbachir67.github.io

[![Déploiement](https://github.com/elbachir67/elbachir67.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/elbachir67/elbachir67.github.io/actions/workflows/deploy.yml)

Sources du site académique personnel de **Dr. El Hadji Bassirou Touré**,
Maître de Conférences Titulaire au DMI / FST / UCAD.

Site statique [Quarto](https://quarto.org) publié sur GitHub Pages
(voir [ADR-0001](_specs/adr/0001-stack-quarto-github-pages.md)).

## Prérequis

- [Quarto](https://quarto.org/docs/get-started/) **1.10.18** : version épinglée dans la CI et le déploiement
  (`QUARTO_VERSION` dans `.github/workflows/ci.yml` et `deploy.yml`). Utiliser la même en local.
- Python ≥ 3.11 (uniquement pour les pages à code exécutable)

## Développement local

```bash
quarto preview                 # aperçu avec rechargement automatique (une seule langue)
python3 scripts/rendre.py      # rendu complet des deux langues dans _site/
```

Pour les pages contenant du code Python :

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Structure

```
_quarto.yml              Configuration du site (navigation, rendu, exécution)
index.qmd                Accueil (FR)
recherche/               Research (EN)
publications/            Publications (page générée, voir ci-dessous)
enseignement/            Catalogue des cours (cours.yml, filtre cours.lua)
cours/<slug>/            Un cours publié : cours.yml, index.qmd, chapitres/NN-<slug>.qmd
blog/                    Articles
cv/                      CV (cv.yml, filtre cv.lua ; page et PDF générés, voir ci-dessous)
assets/                  Images, styles (css/custom.scss, custom-dark.scss) et polices (fonts/)
_extensions/             Extensions Quarto versionnées (academicons, email-protege)
scripts/                 Scripts (rendre.py, publications.py, verifier_*.py)
en/                      Pages anglaises (mêmes données, libellés traduits)
robots.txt               Consignes aux robots d'indexation (publié tel quel)
_specs/                  Backlog, sprints, ADR (non publiés)
_freeze/                 Résultats d'exécution gelés (versionnés)
```

Seuls les fichiers `.qmd` sont rendus ; les `.md` restent des documents de travail.

## Charte graphique

- Thèmes Bootswatch `cosmo` (clair) et `darkly` (sombre), avec bouton de bascule dans la barre de navigation.
- `assets/css/custom.scss` : couleur principale `#1F6FB5`, police Source Sans 3 (repli sur les polices
  système), pied de page. Commun aux deux modes.
- Police **hébergée dans le dépôt** (`assets/fonts/`, woff2, sous-ensembles latin et latin étendu) : aucune requête vers
  Google Fonts. Quarto copie les fichiers dans `site_libs/bootstrap/assets/fonts/`, et la police du texte
  est préchargée (`include-in-header` dans `_quarto.yml`).
- `assets/css/custom-dark.scss` : ajustements du mode sombre uniquement (couleur des liens).
- Icônes Google Scholar, ORCID et Academia : extension [academicons](https://github.com/schochastics/academicons),
  versionnée dans `_extensions/`. Shortcode `{{< ai orcid >}}`, ou classes `ai ai-orcid` en HTML.
- Versions épinglées et licences des composants tiers : [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Publications

La page `publications/index.qmd` est **générée** : ne pas la modifier à la main.

```
publications/sources.toml  --(Crossref)-->  publications/publications.bib  -->  publications/index.qmd
```

- `publications/sources.toml` : liste des publications (`cle`, titre, `event_year`, conférence, ville), reprise des
  sources du PO. Seul fichier à modifier à la main. Une publication dont le `statut` n'est ni `publie` ni
  `a-paraitre` reste dans le `.bib` mais n'apparaît pas sur la page.
- **Publication acceptée sans DOI** : `statut = "a-paraitre"`, avec `auteurs` (« Nom, Initiales ») et
  `editeur` décrits à la main. Elle s'affiche « (à paraître) », sans lien DOI. À chaque exécution, le
  script cherche sa notice dans Crossref. Dès qu'elle existe, les métadonnées de Crossref (DOI compris)
  remplacent la description manuelle, et le script signale qu'on peut retirer le statut.
- `publications/publications.bib` : auteurs complets, DOI, titre publié, actes, éditeur, pages et année
  de publication, récupérés dans l'[API Crossref](https://api.crossref.org). Ce qui est introuvable est
  écrit `TODO(PO): …`, et le script ne complète jamais une donnée manquante.
- **Posters et communications** : `type = "poster"` ou `type = "communication"` (`article` par défaut),
  avec `auteurs`, `evenement`, `lieu` et `date` (`AAAA`, `AAAA-MM` ou `AAAA-MM-JJ`) décrits à la main, et
  `libelle` facultatif (« Communication orale »). Ni DOI, ni PDF, ni recherche Crossref. Dans le `.bib`,
  ce sont des entrées `@misc` avec `entrysubtype`.
- `publications/index.qmd` : section **Articles**, groupée par **année de conférence** (`event_year`, écrite
  `eventdate` dans le `.bib`) décroissante, avec le nom du PO en gras et le lien DOI. L'année de publication
  de Crossref reste dans le champ `year` du `.bib`. Puis section **Posters et communications**, par date
  décroissante.
  Chaque référence a une ancre égale à sa clé BibTeX, par exemple `publications/#toure-lameme-tomcat`.
  La `cle` est choisie dans `sources.toml`, sans année, et **ne change plus** une fois publiée : la page
  Research pointe vers ces ancres. Le script refuse une clé absente, en double, mal formée ou datée.

```bash
python3 scripts/publications.py          # sources.toml -> Crossref -> .bib -> page (réseau requis)
python3 scripts/publications.py page     # régénère seulement la page depuis le .bib (hors ligne)
quarto render
```

Le script n'utilise que la bibliothèque standard de Python (3.11 ou plus récent).

## Enseignement

La page `enseignement/index.qmd` affiche le catalogue des cours sous forme de cartes, groupées par domaine.
Les cartes sont produites **au rendu** depuis `enseignement/cours.yml` par le filtre `enseignement/cours.lua`.

**Ajouter un cours = ajouter une entrée dans `cours.yml`**, sans toucher à `index.qmd` :

```yaml
  - titre: "Intitulé du cours"
    domaine: "IA & Data"          # domaine existant, ou nouveau domaine (nouvelle section)
    niveaux: ["M1"]
    statut: "a-venir"             # carte « Bientôt en ligne », sans lien
    skill: "nom-du-skill"         # facultatif, jamais affiché sur le site
```

- Les domaines apparaissent dans l'ordre de leur première occurrence dans `cours.yml`. Chacun a une
  ancre (par exemple `enseignement/#ia-data`).
- Quand un cours est publié, **son entrée quitte `cours.yml`** : ses métadonnées passent dans
  `cours/<slug>/cours.yml` (voir « Cours » ci-dessous) et le catalogue les lit directement. Un cours
  décrit aux deux endroits fait échouer `quarto render`, pour qu'il n'y ait jamais deux vérités.
- Un statut inconnu, ou un cours en ligne sans `lien`, fait échouer `quarto render` (et donc la CI).

## Cours

Un cours publié est un dossier autonome. Les pages de cours sont **monolingues** : elles sont écrites
dans la langue d'enseignement (le français) et sortent du périmètre bilingue ; le catalogue, lui, est
bilingue et signale la langue des cours au lecteur anglophone.

```
cours/<slug>/
├── cours.yml            Métadonnées : titre, domaine, niveaux, semestre, statut, prérequis, objectifs
├── _metadata.yml        Options communes aux pages du cours (profondeur et titre de la table des matières)
├── index.qmd            Présentation, fiche (générée) et plan (listing des chapitres)
├── chapitres/
│   ├── 01-<slug>.qmd    Le numéro fixe l'ordre de lecture
│   └── 02-<slug>.qmd
├── ressources/          Énoncés distribués aux étudiants : labs, TD, notebooks (publiés)
└── _corriges/           Corrigés : hors du site tant que leur date de publication n'est pas atteinte
```

- `cours.yml` est la **seule source** des métadonnées : la fiche de la page du cours et la carte du
  catalogue en sortent. Le filtre `assets/lua/fiche-cours.lua` remplace le bloc `::: {#fiche} :::`
  de `index.qmd` par les niveaux, le semestre, le domaine, les objectifs et les prérequis.
- Le `titre` de `cours.yml` et le `title` de `index.qmd` doivent coïncider : le rendu échoue sinon.
- Le plan est un listing Quarto sur `chapitres/*.qmd`, trié par nom de fichier : **ajouter un chapitre
  = ajouter un fichier**, rien d'autre à mettre à jour dans la page.
- `_metadata.yml` ne doit déclarer **ni `toc: true` ni un bloc `format:`** : le dossier contient des slides
  revealjs, qui gagneraient une slide de sommaire dans le premier cas et seraient rendues comme des pages
  HTML ordinaires dans le second (constaté). La table des matières des pages HTML vient de `_quarto.yml`.
- La **barre latérale** du cours et les liens **précédent/suivant** viennent de `_quarto-fr.yml`
  (clé `website.sidebar`) : ajouter un cours = y ajouter une barre latérale, avec son `id`, la page de
  présentation et le glob des chapitres. Elle ne s'affiche que sur les pages du cours.

## CV

La page `cv/index.qmd` et le PDF `cv-fr.pdf` sont produits **au rendu** depuis une seule source :

- `cv/cv.yml` : identité, parcours, formation, responsabilités, distinctions et langues, repris des sources
  du PO. Seul fichier à modifier à la main (Markdown en ligne accepté, par exemple `*italique*`).
- `cv/cv.lua` : filtre Quarto qui remplace le bloc `::: {#cv}` de la page par le contenu de `cv.yml`.
  Le même filtre sert à la page web et au PDF Typst (Typst est inclus dans Quarto, sans installation).

```bash
quarto render          # produit _site/cv/index.html et _site/cv/cv-fr.pdf
```

**Aucun numéro de téléphone** : la CI lance `scripts/verifier_telephone.py`, qui échoue si `+221`, `00221`,
un numéro de 9 chiffres ou un numéro sénégalais par groupes apparaît dans `_site/`. Les PDF sont
vérifiés via `pdftotext` (paquet poppler), et `site_libs/` est exclu. Aucun PDF de CV n'est commité
(`cv/*.pdf` est ignoré par Git).

```bash
python3 scripts/verifier_telephone.py    # après quarto render
```

## Référencement

- `_quarto.yml` : `site-url`, `description` du site, image d'aperçu par défaut (`/assets/img/profil.jpg`,
  chemin depuis la racine) et métadonnées de partage Open Graph et Twitter Card (`summary`).
  Quarto en déduit `sitemap.xml`.
- `robots.txt` (à la racine, publié tel quel) : tout le site est indexable, avec l'adresse du sitemap.
- **Chaque page a une `description` propre** dans son en-tête. Celle de la page Publications est écrite par
  `scripts/publications.py`.

La CI lance `scripts/verifier_metadonnees.py`. Il échoue si une page n'a pas de titre ou de description, si
deux pages partagent le même titre ou la même description, si une métadonnée de partage manque, ou si
`sitemap.xml` et `robots.txt` sont incomplets.

```bash
python3 scripts/verifier_metadonnees.py    # après quarto render
```

## Email protégé

L'adresse email n'apparaît jamais en clair dans le HTML généré, pour limiter sa collecte automatique.

- `_quarto.yml`, clé `contact` : adresse découpée en `email-utilisateur` et `email-domaine`, seul endroit où
  la modifier.
- Shortcode `{{< email >}}` (extension locale `_extensions/email-protege/`) : la page contient seulement
  l'adresse inversée puis encodée en base64. Un petit script la reconstruit dans le navigateur (lien
  `mailto:` et infobulle). Arguments facultatifs : `texte="…"` (« Email » par défaut) et `icone="envelope"`.
- **Sans JavaScript**, un repli lisible s'affiche : « utilisateur [arobase] domaine ».
- La CI vérifie par `grep` que l'adresse n'apparaît nulle part dans `_site/`, ni en clair, ni encodée
  (`%40`, `&#64;`, `&#x40;`, `&commat;`), et qu'aucune page ne contient de lien `href="mailto:` écrit en dur.

## Blog

`blog/index.qmd` liste les articles de `blog/posts/`, du plus récent au plus ancien, avec leur date, leurs
catégories, leur extrait et leur temps de lecture. Le flux RSS est produit par Quarto (`blog/index.xml`) et
**annoncé dans l'en-tête de toutes les pages**, dans la langue de la page — c'est `scripts/rendre.py` qui
pose cette balise là où Quarto ne la met pas.

**Écrire un article** : créer `blog/posts/<AAAA-MM-JJ>-<slug>/index.qmd` avec `title`, `description`,
`date` et `categories`. La description sert d'extrait dans la liste et de métadonnée de partage.

**Brouillons** : un article avec `draft: true` **n'est pas publié du tout** (`draft-mode: gone`) — ni page,
ni entrée dans la liste, le flux ou le plan du site. Les contrôles le comptent comme « brouillon non publié
ignoré ». Seul le PO retire cette ligne.

### Commande `/nouvel-article`

`/nouvel-article "<titre>" [--langue fr|en] [--categories a,b]` (définie dans `.claude/commands/`) crée
`blog/posts/<date>-<slug>/index.qmd` : en-tête complet, slug sans accent ni caractère spécial, catégories
déjà employées rappelées en commentaire, `draft: true` et une trame de trois sections. Elle **ne commite ni
ne pousse** : le PO écrit d'abord, et retirer `draft: true` est la seule chose qui publie. Sa partie
mécanique est `scripts/nouvel_article.py`.

### Commande `/resume`

`/resume <fichier.tex|.pdf> [--langue fr|en]` (définie dans `.claude/commands/`) écrit un **brouillon**
d'article à partir d'un document. Elle **refuse** de résumer un travail listé comme non accepté dans
`publications/sources.toml` (CLAUDE.md §7), **demande confirmation** pour un document inconnu du dépôt, et
n'écrit jamais un chiffre absent du document. Sa partie mécanique est `scripts/preparer_resume.py`.

**Traduction facultative** : un article n'existe pas forcément dans les deux langues. Les articles sortent
donc du périmètre bilingue — ni équivalent exigé, ni `hreflang` — tandis que les deux pages `blog/`
restent, elles, appariées.

## Site bilingue (français et anglais)

Le site existe en deux langues : le français à la racine (`/`) et l'anglais sous `/en/`. La mécanique suit
[ADR-0003](_specs/adr/0003-architecture-multilingue.md) : **un profil Quarto par langue**, puis assemblage.

- `_quarto.yml` : tout ce qui ne dépend pas de la langue (thème, formats, référencement, extensions).
- `_quarto-fr.yml` et `_quarto-en.yml` : langue, description du site, navigation, pied de page, pages à
  rendre et dossier de sortie.
- **Rendu** : `python3 scripts/rendre.py` enchaîne les deux profils, copie le site anglais dans `_site/en/`,
  fusionne les plans de site et donne à chaque langue son index de recherche. **C'est la commande à
  utiliser**, en local comme en CI ; `quarto render` seul ne produirait qu'une langue.
- `assets/lua/hreflang.lua` pose les balises `hreflang` (`fr`, `en`, `x-default`) sur chaque page.
- `assets/js/bascule-langue.js` fait pointer le sélecteur de langue vers la **page équivalente**, en lisant
  ces balises. Sans JavaScript, il mène à l'accueil de l'autre langue.

**Adresses** : les dossiers anglais portent un nom anglais quand le mot diffère (`/recherche/` ↔
`/en/research/`, `/enseignement/` ↔ `/en/teaching/`). La correspondance est écrite dans
`assets/lua/hreflang.lua` et dans `scripts/verifier_bilingue.py` ; le sélecteur de langue, lui, n'a rien à
tenir à jour, et la CI échoue si les deux tables divergent.

**Recherche** : chaque langue a son index (`/search.json` et `/en/search.json`). Les pages anglaises sont
rattachées à la racine `/en/` par leur méta `quarto:offset`, ajustée à l'assemblage : une recherche depuis une
page anglaise ne renvoie que des pages anglaises.

**Ajouter une page bilingue** : créer `page/index.qmd` et `en/page/index.qmd`, puis ajouter l'entrée de
navigation dans les deux profils. Si le nom du dossier anglais diffère, l'ajouter aux deux tables de
correspondance ci-dessus. La CI refuse une page qui n'existe que dans une langue.

**Données partagées, libellés traduits** : le CV (`cv/cv.yml`), le catalogue (`enseignement/cours.yml`) et les
publications (`publications/sources.toml`) n'existent qu'en un seul exemplaire. Seuls les libellés d'interface
sont traduits, dans les filtres Lua et dans `scripts/publications.py`.

**Pages monolingues** : les cours (à venir) restent en français ; ils sont exclus de l'appariement par
`scripts/verifier_bilingue.py`.

```bash
python3 scripts/rendre.py               # les deux langues
python3 scripts/rendre.py --propre      # en vidant le cache .quarto
python3 scripts/verifier_bilingue.py    # équivalents FR/EN et hreflang réciproques
```

**Piège** : rendre un fichier isolé (`quarto render page.qmd`) laisse des métadonnées dans le cache
`.quarto` — la page peut ensuite ressortir dans la mauvaise langue — et écrit la page **à côté de sa
source** (`cv/index.html`, `cv/index_files/`). Supprimer ces fichiers, que git ignore, puis relancer
`python3 scripts/rendre.py --propre`.

## Import d'un cours LaTeX

Les cours existent en LaTeX (Beamer). `scripts/importer_chapitre.py` en fait des slides Quarto revealjs :
une `frame` donne une slide, les encadrés `ucad*` deviennent des callouts, les figures sont nettoyées pour
le mode sombre. La table de correspondance complète est dans
[`_specs/contenus/latex-vers-quarto.md`](_specs/contenus/latex-vers-quarto.md).

```bash
python3 scripts/importer_chapitre.py cours/<slug>/_sources/<chapitre>.tex \
    --sortie cours/<slug>/chapitres/01-<slug>.qmd \
    --figures cours/<slug>/figures \
    --rapport cours/<slug>/_sources/rapport-NN-<slug>.md \
    --alt cours/<slug>/_sources/textes-alternatifs.toml \
    --figure-python figA_cout_changement=cours/<slug>/_sources/figs/figA.py \
    --description "Phrase de référencement de la séance."
```

- Le **langage des blocs de code** est celui que le `.tex` déclare (`\lstset{language=…}` ou
  `\lstdefinestyle{…}`), et il est inscrit dans `import.toml` pour que le rejeu de la CI n'ait rien à
  deviner. `--langage-code` le force. Les styles du thème sont respectés : `[style=out]` et `[style=err]`
  donnent un bloc **sans coloration** — une sortie de programme n'est pas du code —, `[style=sh]` du shell.
- Les **macros de `beamerucad.sty`** sont développées avant la conversion : `\figslide{largeur}{fichier}
  {légende}` place la figure **et sa légende**, qui devient son texte alternatif — un deck qui légende ses
  figures n'a donc aucun `TODO(PO)` à remplir. `\resultat` annonce la sortie qui suit.
- Les **sources** (`.tex`, `.sty`, figures d'origine) vivent dans `cours/<slug>/_sources/`. Le préfixe `_`
  les tient hors du site publié, comme `_specs/` ; elles sont commitées pour que la conversion soit rejouable.
  Quand les figures sont **produites par un script** (`make_figs_*.py`), le script est commité avec elles :
  il sort le PDF pour LaTeX et le **SVG** pour le site, et c'est le SVG que la page incorpore.
- **`cours/<slug>/_sources/import.toml` décrit chaque import** (fichier `.tex`, page produite, dossier des
  figures, textes alternatifs, figures calculées, description). `scripts/verifier_conversion.py` rejoue ces
  imports en CI et **échoue si la page ou une figure commitée diffère** de ce que produit le script : une
  conversion oubliée après modification d'un `.tex` ne peut pas passer inaperçue. Le même contrôle échoue si
  une page à code exécutable n'a pas son résultat dans `_freeze/`.

  ```bash
  python3 scripts/verifier_conversion.py    # même contrôle qu'en CI, sans dépendance
  ```
- Le script **n'invente rien** : ce qu'il ne sait pas convertir reste en commentaire `<!-- NON CONVERTI: … -->`
  dans la page et figure dans le rapport, avec les figures, les blocs de code et les tableaux traités.
- Les **figures SVG** sont nettoyées en local (encres et gris en `currentColor`, fonds clairs transparents,
  police héritée) puis commitées : **aucune conversion d'image ne tourne en CI**.
- Le **texte alternatif** vient de la légende du `.tex`, ou du fichier `--alt` quand la figure n'en a pas.
  Sans l'un ni l'autre, la figure part avec un `TODO(PO)` visible.
- Les figures sont **incorporées** à la page par le shortcode `{{< svg … >}}` (extension
  `_extensions/svg-inline`) : c'est la condition pour que `currentColor` suive la couleur du texte.
- Le style des slides est dans `assets/css/slides.scss` (charte d'US-06, couleurs des encadrés d'origine).
  Une slide mesure **1050 × 700 unités** : toutes les hauteurs de cette feuille s'y rapportent, et une
  séance doit tenir dans ce cadre, sans défilement. Après un import, vérifier la slide la plus chargée —
  c'est en général celle qui porte une figure **et** un encadré.
- `--figure-python nom=script.py` remplace une figure importée par un **bloc Python exécuté** : le script
  du cours est inséré tel quel, moins ses lignes d'export (`savefig`, `print`, choix du moteur), la slide
  montre la figure, et le code reste replié sous un « Voir le code de la figure ». Le repli est un
  `<details>` : en revealjs, ni `code-fold` ni un callout `collapse` ne replient quoi que ce soit.

### Capsule vidéo d'une séance

Une séance peut porter une capsule YouTube : ajouter `video = "<identifiant>"` à son entrée dans
`_sources/import.toml` (ou passer `--video` à l'import). Le script écrit alors `video:` dans l'en-tête de la
séance et ajoute une dernière slide « Capsule vidéo » avec le shortcode :

```
{{< capsule <identifiant> titre="Titre de la vidéo" >}}
```

**Rien n'est chargé avant le clic** : la vignette est dessinée par le site — pas de vignette YouTube, qui
serait déjà une requête vers Google — et l'iframe n'est créée qu'au clic, sur `youtube-nocookie.com`. Le
bouton porte un nom explicite, l'iframe reçoit le même titre, et un lien de repli s'affiche sans JavaScript.
L'extension est dans `_extensions/capsule/`.

### Ressources d'une séance

Une séance peut distribuer des énoncés — lab, TD, notebook — et leurs corrigés. Ils se déclarent dans
son entrée de `_sources/import.toml`, une entrée par ressource (ou `--ressource type|fichier|titre[|date]`
à l'import) :

```toml
[[chapitres.ressources]]
type = "lab"                              # lab, td, notebook, ou corrige
fichier = "ressources/lab1-couches.pdf"   # chemin relatif au dossier du cours
titre = "Lab 1 — refactoring vers les couches"

[[chapitres.ressources]]
type = "corrige"
fichier = "_corriges/lab1-corrige.pdf"
titre = "Corrigé du Lab 1"
date = "2026-10-15"                       # obligatoire : le jour où le corrigé rejoint le site
```

Le fichier est **rangé par le PO** dans le dossier du cours, et le type décide où :

| Type | Dossier | Publié ? |
|---|---|---|
| `lab`, `td`, `notebook` | `ressources/` | oui : lien sur la séance et sur la page du cours |
| `corrige` | `_corriges/` | **à partir de sa `date`**, et pas un jour avant |

La liste s'affiche sur la slide de fin de la séance et dans la colonne « Format » de la table des
séances, avec le **type** et le **poids** du fichier. Ces deux pages sont remplies **au rendu** par
`assets/lua/ressources.lua` et `assets/lua/fiche-cours.lua` : le poids se lit sur le fichier, et la date
d'un corrigé se compare au jour même. **Ajouter une ressource ne demande donc aucune modification de
page** — une entrée dans `import.toml`, et l'import rejoué.

**La règle du corrigé tient à quatre verrous**, pas à la vigilance :

1. `_corriges/` commence par `_` : Quarto ne rend pas ce dossier.
2. L'import **refuse** un corrigé sans date de publication valide.
3. `scripts/rendre.py` ne copie dans le site (`cours/<slug>/corriges/`) que les corrigés dont la date
   est atteinte, et les filtres n'affichent que ceux-là : avant la date, ni fichier, ni lien, ni mention.
4. `scripts/verifier_conversion.py` échoue si un corrigé est rangé ailleurs que dans `_corriges/`, s'il
   n'a pas de date, ou si son fichier apparaît dans `_site/` avant cette date.

À savoir : un corrigé rejoint le site au **premier rendu qui suit sa date**, donc au prochain
déploiement — pas à minuit.

Les libellés sont traduits (`TD` → `Tutorial`, `Corrigé` → `Solution`) et suivent la langue de la page
qui les affiche. Les pages de cours étant monolingues (voir « Cours »), ils s'affichent aujourd'hui en
français ; le jour où une page de cours existera en anglais, rien ne sera à changer.

### Figures : ce que la CI vérifie

Une figure publiée vide est un **défaut silencieux** : la page se rend, les liens sont bons, et
l'étudiant voit un cadre blanc. `scripts/verifier_figures.py` (US-54) compare chaque figure publiée à
sa source et échoue si des éléments dessinés ont disparu, si la figure ne dessine plus rien, ou si un
`<use>` porte un préfixe que le HTML ne résout pas.

Ce dernier point mérite d'être connu : matplotlib place ses marqueurs dans `<defs>` et les rappelle
par `<use xlink:href>`. Réécrit `ns4:href`, c'est du **XML valide** — mais la page *incorpore* le SVG,
et l'analyseur HTML n'y résout que `xlink:href` et `href`. Les 45 points d'un nuage avaient ainsi
disparu sans qu'aucun contrôle ne bronche.

### PDF des séances

Chaque séance est imprimée en PDF **au rendu**, à côté de sa page (`…/01-<slug>.pdf`) :
`scripts/generer_pdf.js` ouvre la présentation en mode impression et laisse le navigateur l'imprimer — même
source, même style, texte sélectionnable, figures vectorielles. Le lien de téléchargement apparaît sur la
page du cours et sur la slide de titre.

- L'impression demande les paquets Node (`npm ci`). Sans eux, `scripts/rendre.py` saute cette étape et le
  dit ; le lien de la slide de titre ne s'affiche alors pas, puisqu'il vérifie que le fichier existe.
- Aucune dépendance nouvelle : le Chrome déjà installé suffit (decktape, l'outil habituel pour revealjs,
  aurait téléchargé son propre navigateur).
- Les PDF ne sont pas commités : ils sont refaits à chaque rendu, comme les pages.

### Commande `/importer-chapitre`

`/importer-chapitre <cours-slug> <fichier.tex>` (définie dans `.claude/commands/`) enchaîne tout ce qui
précède : copie des sources, import, nettoyage des figures, rendu, contrôles, branche et PR. Elle s'arrête
pour demander au PO les textes alternatifs des figures sans légende — elle n'en invente jamais — et refuse
d'ouvrir la PR tant qu'un bloc `NON CONVERTI` subsiste. Sa partie mécanique est
`scripts/preparer_chapitre.py`, utilisable seule.

### Code exécuté et figures gelées

Les résultats d'exécution sont **gelés** (`execute: freeze: auto`) et versionnés dans `_freeze/` : la CI ne
réexécute jamais de code, et n'a donc besoin ni de Python ni de matplotlib. Une page à code exécutable n'est
réexécutée que si son code change.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
QUARTO_PYTHON=$PWD/.venv/bin/python quarto render cours/<slug>/chapitres/01-<slug>.qmd --profile fr
git add _freeze                       # le gel accompagne la modification du code
```

- `_freeze/site_libs/` est **ignoré** : ce n'est qu'une copie des bibliothèques livrées avec Quarto (5 Mo
  pour revealjs). Vérifié : un rendu gelé aboutit sans ce dossier et sans Python installé.
- Chaque réexécution change l'identifiant aléatoire de la cellule dans `execute-results/html.json` : un
  rendu sans changement de code ne produit donc pas de différence, mais une réexécution volontaire, si.

## Accessibilité

Le site rendu est audité par [axe-core](https://github.com/dequelabs/axe-core), dans les règles WCAG 2.2
niveaux A et AA. **La CI échoue sur la moindre violation.**

```bash
python3 scripts/rendre.py
npm ci                                    # axe-core et playwright-core, épinglés dans package.json
node scripts/verifier_accessibilite.js
```

- Chaque page rendue est visitée **dans les deux langues**, en mode **clair et sombre** (par le bouton du
  site, comme un visiteur), en **375 px** et en **1440 px**.
- Les séances de cours sont auditées **page entière puis slide par slide** : revealjs n'affiche qu'une
  slide à la fois, et axe ne voit que celle-là. Le mode impression, où toutes les slides sont visibles,
  n'est pas utilisé : il remonterait des défauts de slides masquées que personne ne rencontre.
- Le navigateur est le **Chrome déjà installé** (`channel: "chrome"`) : aucun navigateur n'est téléchargé,
  ni en local ni en CI. Durée : environ 50 secondes pour 109 combinaisons.

## Contribution

`main` est protégée et toujours déployable. Chaque changement passe par une branche
et une pull request (voir [ADR-0002](_specs/adr/0002-workflow-git-ci-cd.md)) :

```bash
git switch -c feat/US-XX-slug-court
# commits au format Conventional Commits, avec la référence (US-XX)
gh pr create
```

Le contrat de travail complet est décrit dans [CLAUDE.md](CLAUDE.md).
