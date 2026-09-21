---
description: Importe une séance de cours LaTeX (Beamer) en slides Quarto et ouvre la PR
argument-hint: <cours-slug> <fichier.tex> [--figures-source <dossier>]
---

# Importer une séance de cours

Arguments reçus : `$ARGUMENTS`

Tu vas transformer un deck Beamer en séance publiée, puis ouvrir la PR. Le travail mécanique est dans
`scripts/preparer_chapitre.py` ; ce qui suit décrit ce que **toi** tu décides, vérifies et racontes au PO.

Règles qui priment sur tout le reste : **ne jamais inventer de contenu académique** (CLAUDE.md §7), ne
jamais commiter sur `main`, ne jamais merger la PR.

## 1. Préparer le terrain

- Vérifier que l'arbre est propre et que `main` est à jour (`git switch main && git pull`).
- Créer la branche `feat/cours-<cours-slug>-<numéro de séance>`, par exemple `feat/cours-archi-02`.
- Si le cours n'existe pas encore (`cours/<slug>/cours.yml` absent), **s'arrêter** : le créer relève
  d'une story, pas de cette commande.

## 2. Importer

```bash
python3 scripts/preparer_chapitre.py <cours-slug> <fichier.tex> [--figures-source <dossier>]
```

Le script copie les sources dans `cours/<slug>/_sources/`, importe la séance en slides, nettoie les SVG,
écrit le rapport de conversion et l'entrée de `_sources/import.toml` que la CI rejouera (US-41).

**Code de sortie 2 : il manque une entrée du PO.** Deux cas, et dans les deux on s'arrête :

- **Texte alternatif manquant** : une figure n'a pas de légende dans le `.tex`. Le script affiche alors
  un **brouillon par figure** (US-58), rédigé à partir de la source de la figure — libellés et flèches
  d'un TikZ, titre, axes et séries d'un script matplotlib — avec le titre de la section où elle
  apparaît. **Présenter au PO la liste entière en une seule fois**, sans en écrire aucune dans le
  site : il accepte, corrige ou réécrit. Relancer ensuite la même commande avec
  `--alt 'nom_de_la_figure=phrase validée'` (une fois par figure). Ne jamais écrire de `TODO(PO)` à sa
  place, et ne jamais prendre un brouillon pour une validation : la story l'interdit.
  Le brouillon seul se relit avec `python3 scripts/brouillons_alt.py <fichier.tex> --prefixe NN-slug`.
- **Bloc non converti** (`<!-- NON CONVERTI: … -->` dans la page, listé dans le rapport) : montrer au PO
  l'extrait LaTeX concerné et lui demander quoi en faire — l'écrire autrement dans le `.tex`, l'abandonner,
  ou étendre `scripts/importer_chapitre.py`. **Ne pas ouvrir la PR tant qu'il en reste un.**

Si une figure doit être calculée plutôt qu'importée (script matplotlib fourni), ajouter
`--figure-python nom_de_la_figure=_sources/figs/<script>.py`, et rendre une fois en local avec
l'environnement Python (`QUARTO_PYTHON=$PWD/.venv/bin/python`) pour produire le gel.

## 3. Vérifier

```bash
python3 scripts/rendre.py                 # les deux langues
python3 scripts/verifier_conversion.py    # la page correspond à ses sources, et son gel existe
node scripts/verifier_accessibilite.js    # WCAG A et AA, pages et slides
python3 scripts/verifier_metadonnees.py && python3 scripts/verifier_bilingue.py && python3 scripts/verifier_telephone.py
python3 scripts/verifier_latex.py        # aucun reste de LaTeX dans les pages
python3 scripts/verifier_figures.py      # aucune figure vidée en chemin
node scripts/verifier_debordement.js     # aucune slide ne dépasse le cadre
```

Le contrôle de débordement mesure lui-même les slides : quand il en signale une, **ne pas ouvrir la
PR** — alléger une slide trop chargée est une décision pédagogique, qui revient au PO.

Regarder ensuite la séance dans un navigateur : les encadrés doivent porter les bonnes couleurs, les
figures s'afficher, et le repli du code s'ouvrir.

## 4. Ouvrir la PR

- Commits séparés, en français, format Conventional Commits : les sources (`feat(cours): sources de la
  séance N`), puis la séance et ses figures (`feat(cours): séance N — <titre>`), puis le gel s'il change.
- `gh pr create` avec le template du dépôt, en indiquant :
  - le nombre de slides, d'encadrés, de blocs de code, de figures ;
  - le rapport de conversion (`_sources/rapport-NN-<slug>.md`) : ce qui a été ignoré, ce qui a été traduit ;
  - la provenance de chaque texte alternatif, telle que `[chapitres.origine_alt]` l'enregistre :
    légende du `.tex`, brouillon validé, ou texte du PO ;
  - les résultats des contrôles ci-dessus ;
  - `Closes #<issue>` si une issue suit cette séance, sinon rien.
- **STOP.** Donner au PO : cinq lignes de résumé, le lien de la PR, et ce qu'il doit relire — le contenu de
  la séance, que la conversion ne relit pas.

## Ce que la commande ne fait pas

- Elle ne merge pas, ne pousse pas sur `main`, ne ferme pas d'issue.
- Elle ne corrige pas le texte du cours : les coquilles du `.tex` se retrouvent dans les slides, et c'est au
  PO de les corriger à la source.
- Elle n'invente ni description de figure, ni objectif, ni prérequis.
