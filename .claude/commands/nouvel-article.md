---
description: Crée un article de blog vide, avec son en-tête et une trame — sans rien commiter
argument-hint: "<titre>" [--langue fr|en] [--categories a,b]
---

# Nouvel article de blog

Arguments reçus : `$ARGUMENTS`

Tu crées **le fichier**, pas l'article : le PO écrit. La commande ne commite pas, ne pousse pas, n'ouvre pas
de PR.

## 1. Créer le fichier

```bash
python3 scripts/nouvel_article.py "<titre>" [--langue fr|en] [--categories a,b] [--date AAAA-MM-JJ]
```

Le script crée `blog/posts/<date>-<slug>/index.qmd` (ou `en/blog/posts/…`) avec :

- le **titre** donné, et un slug dérivé sans accent ni caractère spécial ;
- une **description** en `TODO(PO)` : c'est l'extrait qui s'affichera dans la liste du blog ;
- la **date** du jour, les **catégories** demandées, et un rappel de celles déjà employées sur le blog ;
- **`draft: true`** : tant que cette ligne est là, l'article n'est pas publié — ni page, ni entrée dans la
  liste, le flux ou le plan du site ;
- une **trame** de trois sections, à changer ou à supprimer.

Si le dossier existe déjà, le script s'arrête sans rien écrire : proposer alors un autre titre ou une autre
date au PO.

## 2. Dire au PO ce qui l'attend

En trois lignes : le chemin du fichier, ce qu'il doit remplir (description, catégories, texte), et le fait
que **retirer `draft: true` est la seule chose qui publie** — et que cela lui revient.

Proposer, s'il le souhaite, de prévisualiser l'article sans le publier :

```bash
quarto render blog/posts/<date>-<slug>/index.qmd --profile fr -M draft:false
python3 -m http.server 4321 --directory _site
```

Rappeler alors que ce rendu isolé laisse des traces dans le cache `.quarto`, et qu'un
`python3 scripts/rendre.py --propre` remet tout d'aplomb.

## Ce que la commande ne fait pas

- Elle n'écrit pas l'article, ne propose pas de plan de contenu, n'invente pas de titre.
- Elle ne commite ni ne pousse : le dépôt reste propre tant que le PO n'a pas écrit.
- Elle ne publie rien : `draft: true` reste, et seul le PO le retire.
