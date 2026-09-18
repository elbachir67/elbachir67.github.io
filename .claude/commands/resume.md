---
description: Transforme un document (.tex ou .pdf) en brouillon d'article de blog, jamais publié directement
argument-hint: <fichier.tex|.pdf> [--langue fr|en]
---

# Résumer un document en article de blog

Arguments reçus : `$ARGUMENTS`

Tu vas écrire un **brouillon** d'article à partir d'un document du PO. Il restera `draft: true` : Quarto ne
publie pas les brouillons, et seul le PO retire cette ligne.

Règles qui priment sur tout le reste : **ne jamais inventer** un chiffre, un résultat ou une conclusion qui
ne sont pas dans le document (CLAUDE.md §7) ; **ne jamais résumer un travail non accepté** ; ne pas commiter
sur `main` ; ne pas merger.

## 1. Vérifier que le document peut être résumé

```bash
python3 scripts/preparer_resume.py <fichier> [--langue fr|en]
```

Le script rapproche le titre du document des publications de `publications/sources.toml`, puis :

- **code 2, refus** : le travail y figure avec un statut autre que publié ou « à paraître ». **S'arrêter
  là**, redire au PO pourquoi (règle « Travaux non acceptés »), et ne rien écrire — pas même un brouillon.
- **code 3, à confirmer** : le document est inconnu du dépôt. **Demander au PO** s'il s'agit d'un travail
  publié ou accepté ; ne reprendre qu'après sa réponse.
- **code 0** : le brouillon est créé dans `blog/posts/<date>-<slug>/` (ou `en/blog/posts/…`), avec la
  citation de la source et `draft: true`.

## 2. Lire le document, puis écrire

Lire le document **en entier** avant d'écrire : c'est la seule source autorisée.

- Remplacer le titre et la description `TODO:` de l'en-tête. La description sert d'extrait dans la liste du
  blog : une phrase, sans promettre plus que le document.
- Écrire l'article à la place du commentaire laissé par le script. Viser 400 à 700 mots : ce qu'on a cherché,
  ce qu'on a trouvé, ce que cela change. Le lecteur n'est pas du domaine.
- **Chaque chiffre, chaque résultat vient du document.** Ce qui manque — une date, un nom d'institution, une
  précision de méthode — reste un `TODO(PO): …` visible, jamais une supposition.
- Garder la citation de la source telle que le script l'a écrite, et laisser `draft: true`.
- Les catégories : celles qui existent déjà sur le blog, sauf si le PO en demande une autre.

## 3. Vérifier

```bash
python3 scripts/rendre.py
python3 scripts/verifier_metadonnees.py && python3 scripts/verifier_bilingue.py
```

Le brouillon **ne doit pas apparaître** dans le site rendu : ni dans `/blog/`, ni dans le flux RSS, ni dans
le plan du site. Les contrôles le comptent comme « brouillon non publié ignoré ».

## 4. Ouvrir la PR

- Un commit, en français : `feat(blog): brouillon d'article — <titre>`.
- `gh pr create` en indiquant : le document résumé, ce que le script a répondu (publication reconnue,
  support de cours, confirmation du PO), les `TODO(PO)` restants, et le fait que l'article est un brouillon.
- **STOP.** Dire au PO en cinq lignes : ce qui a été résumé, ce qu'il doit relire, et que la publication
  passe par le retrait de `draft: true` — par lui.

## Ce que la commande ne fait pas

- Elle ne publie pas : le brouillon reste hors du site tant que le PO n'a pas retiré `draft: true`.
- Elle ne traduit pas : `--langue en` écrit un brouillon en anglais à partir du même document, mais un
  article français n'est pas traduit automatiquement.
- Elle n'ajoute aucune référence bibliographique qui ne soit pas dans le document.
