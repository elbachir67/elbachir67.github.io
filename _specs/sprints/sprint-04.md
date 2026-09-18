# Sprint 4 — Chaîne de publication et blog

**Objectif :** publier une séance de cours ou un article devient une commande, relue puis mergée,
et les contrôles faits à la main jusqu'ici tournent en CI.
**Capacité :** 23 points

## Entrée PO

Aucune. Les commandes sont testées sur des sources déjà présentes dans le dépôt ;
si un test demande un nouveau `.tex`, la PR le demande explicitement.

## Ordre d'exécution

US-42 → US-41 → US-20 → US-17 → US-19 → US-25 → US-21 → US-22.

---

### US-42 — Accessibilité vérifiée en CI (3 pts)

En tant que PO, je veux que l'audit d'accessibilité tourne automatiquement,
afin qu'il ne dépende plus d'un audit manuel à chaque PR.

- [ ] axe-core exécuté en CI sur les pages du site et les slides, dans les deux langues, en mode clair et sombre, en largeur mobile et desktop.
- [ ] La CI échoue sur toute violation WCAG A ou AA ; le rapport est lisible dans le journal.
- [ ] Durée d'exécution mesurée et indiquée dans la PR ; si elle dépasse trois minutes, réduire l'échantillon en le justifiant.
- [ ] Preuve d'échec : une PR brouillon avec un contraste cassé, fermée sans merge.

### US-41 — Conversion et gel vérifiés en CI (2 pts)

En tant que PO, je veux être sûr que les pages publiées correspondent à leurs sources,
afin qu'une conversion oubliée ne passe pas inaperçue.

- [ ] La CI rejoue l'import de chaque chapitre disposant de sources et échoue si le `.qmd` commité en diffère (hors identifiants de cellule aléatoires, documentés).
- [ ] La CI échoue si un bloc exécutable n'a pas son entrée dans `_freeze/`.
- [ ] Aucune dépendance Python ajoutée à la CI (contrainte d'US-18 conservée).

### US-20 — Commande `/importer-chapitre` (5 pts)

En tant que PO, je veux publier une nouvelle séance en une commande,
afin que migrer mes 20 cours restants reste réaliste.

- [ ] Commande Claude Code `/importer-chapitre <cours-slug> <fichier.tex>` documentée dans `.claude/commands/`.
- [ ] Elle enchaîne : copie des sources dans `cours/<slug>/_sources/`, import, nettoyage des SVG, rendu local, rapport de conversion, branche et PR.
- [ ] Elle s'arrête et demande au PO tout texte alternatif manquant, plutôt que d'écrire un `TODO(PO)`.
- [ ] Elle refuse de créer la PR si le rapport contient un bloc non converti ; le PO décide alors.
- [ ] Testée sur une séance réelle du cours pilote : la PR produite est mergeable telle quelle.
- [ ] Le README décrit la commande en cinq lignes.

### US-17 — PDF d'une séance généré automatiquement (5 pts)

En tant qu'étudiant sans connexion fiable, je veux télécharger la séance en PDF,
afin de la lire hors ligne.

- [ ] Un PDF par séance, généré depuis les mêmes sources, sans impression manuelle par le navigateur.
- [ ] Bouton de téléchargement sur la page du cours et sur la première slide.
- [ ] Les figures SVG et la figure Python gelée apparaissent correctement ; le texte est sélectionnable.
- [ ] La génération tourne en local (comme les SVG) ou en CI si elle n'ajoute pas de dépendance lourde : le choix est justifié dans la PR.
- [ ] Le poids du PDF est indiqué ; au-delà de 5 Mo, compresser ou justifier.

### US-19 — Intégration des capsules vidéo (1 pt)

En tant qu'étudiant, je veux voir la vidéo associée à une séance,
afin de revoir l'explication après le cours.

- [ ] Shortcode d'intégration YouTube, en chargement différé (pas de requête vers Google avant le clic).
- [ ] Champ `video` facultatif dans les métadonnées d'une séance.
- [ ] Titre accessible sur l'iframe ; rendu correct à 375 px.

### US-25 — Blog : listing, catégories, RSS (2 pts)

En tant que lecteur, je veux suivre les publications du site,
afin de ne pas avoir à revenir le consulter.

- [ ] Listing trié par date, avec catégories et extrait.
- [ ] Flux RSS valide, annoncé dans l'en-tête des pages.
- [ ] Le blog existe dans les deux langues ; un article n'est pas obligatoirement traduit, et son absence dans l'autre langue ne fait pas échouer le contrôle bilingue.
- [ ] Un premier article réel, fourni ou validé par le PO, remplace la page « En construction ».

### US-21 — Commande `/resume` (3 pts)

En tant que PO, je veux transformer un document en article de blog,
afin de valoriser mes travaux sans repartir de zéro.

- [ ] Commande `/resume <fichier.tex|.pdf> [--langue fr|en]` : produit un brouillon d'article dans `blog/posts/`, jamais publié directement.
- [ ] L'article cite sa source et n'invente aucun chiffre ni résultat absent du document.
- [ ] La commande refuse de résumer un travail non accepté (règle de `CLAUDE.md` §7) et le dit clairement.
- [ ] Le brouillon est marqué `draft: true` tant que le PO ne l'a pas relu.
- [ ] Testée sur un document réel du dépôt.

### US-22 — Commande `/nouvel-article` (2 pts)

En tant que PO, je veux créer un article vide correctement structuré,
afin de ne pas recopier l'en-tête à chaque fois.

- [ ] Commande `/nouvel-article "<titre>" [--langue]` : crée le dossier, l'en-tête YAML (date, catégories, description, `draft: true`) et une trame.
- [ ] Le slug est dérivé du titre, sans accent ni caractère spécial.
- [ ] La commande ne commite ni ne pousse : le PO écrit d'abord.

---

## Propositions reportées au backlog, sans sprint

Module de style matplotlib accordé à la charte, notes du présentateur, numérotation
automatique des chapitres, index de recherche par langue côté Quarto.

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-04-bilan.md` (CLAUDE.md §11).
