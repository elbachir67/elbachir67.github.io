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
quarto preview                 # aperçu avec rechargement automatique
quarto render                  # rendu complet dans _site/
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
blog/                    Articles
cv/                      CV (cv.yml, filtre cv.lua ; page et PDF générés, voir ci-dessous)
assets/                  Images, styles (css/custom.scss, custom-dark.scss) et polices (fonts/)
_extensions/             Extensions Quarto versionnées (academicons)
scripts/                 Scripts (publications.py, verifier_telephone.py, verifier_metadonnees.py)
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
- Quand la version en ligne d'un cours est publiée, passer `statut: "en-ligne"` et ajouter
  `lien: "../cours/<slug>/index.qmd"` : la carte devient un lien.
- Un statut inconnu, ou un cours en ligne sans `lien`, fait échouer `quarto render` (et donc la CI).

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

## Contribution

`main` est protégée et toujours déployable. Chaque changement passe par une branche
et une pull request (voir [ADR-0002](_specs/adr/0002-workflow-git-ci-cd.md)) :

```bash
git switch -c feat/US-XX-slug-court
# commits au format Conventional Commits, avec la référence (US-XX)
gh pr create
```

Le contrat de travail complet est décrit dans [CLAUDE.md](CLAUDE.md).
