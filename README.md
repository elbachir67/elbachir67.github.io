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
enseignement/            Catalogue des cours
blog/                    Articles
cv/                      CV
assets/                  Images et styles
_specs/                  Backlog, sprints, ADR (non publiés)
_freeze/                 Résultats d'exécution gelés (versionnés)
```

Seuls les fichiers `.qmd` sont rendus ; les `.md` restent des documents de travail.

## Contribution

`main` est protégée et toujours déployable. Chaque changement passe par une branche
et une pull request (voir [ADR-0002](_specs/adr/0002-workflow-git-ci-cd.md)) :

```bash
git switch -c feat/US-XX-slug-court
# commits au format Conventional Commits, avec la référence (US-XX)
gh pr create
```

Le contrat de travail complet est décrit dans [CLAUDE.md](CLAUDE.md).
