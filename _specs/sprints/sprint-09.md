# Sprint 9 — Trois cours de plus, et des PDF qui disent la vérité

**Objectif :** Programmation Frontend 1, Programmation par Réutilisation de Composants et
Mathématiques pour le Machine Learning sont en ligne, et plus aucun PDF servi ne diverge de sa
source sans que la CI le dise.
**Capacité :** 26 points — sous la vitesse mesurée au Sprint 8 (31 livrés), pour garder de la marge.

## Règle de sprint

Aucun ajout en cours de route. Un blocage se traite par **échange** : une story entre, une autre
sort, et la capacité ne monte pas.

## Entrées PO

- [ ] Métadonnées des trois cours : niveaux, objectifs, prérequis en texte libre.
- [ ] Mathématiques pour le ML : quel périmètre publier — les quatre modules seuls, ou avec les deux decks (25 ou 61 figures selon l'inventaire).
- [ ] Textes alternatifs des figures sans légende, brouillons validés en une fois par cours.
- [ ] Arbitrage sur les PDF que US-76 trouvera divergents.

## Ordre d'exécution

US-79 → US-76 → US-80 → US-81.

---

### US-79 — Programmation Frontend 1 (5 pts)

En tant qu'étudiant de L1, je veux trouver mon cours de web en ligne,
afin de suivre les séances et leurs labs depuis le site.

- [ ] Les séances dont les sources sont dans `_import/frontend1/` importées, une PR, un commit par séance ; labs en ressources.
- [ ] Le prérequis de Frontend 2 vers Frontend 1 devient un lien cliquable.
- [ ] Les trois séances absentes de l'inventaire sont signalées, sans être comblées.
- [ ] Vérification en ligne, captures de chaque figure comprises.

### US-76 — Une ressource est ce que sa source produit (5 pts)

En tant que PO, je veux savoir quand un PDF servi ne correspond plus à sa source,
afin qu'un défaut corrigé à la source ne reste pas en ligne dans l'ancienne version.

- [ ] Chaque ressource issue d'un `.tex` est recompilée avec le moteur que sa source exige — `fontspec` impose LuaLaTeX, sinon pdflatex —, deux passes.
- [ ] Le texte extrait du PDF recompilé est comparé à celui du PDF servi ; tout écart est rapporté, ressource par ressource, avec un extrait.
- [ ] Une ressource dont seule la mise en forme diffère est remplacée par sa recompilation. Une ressource dont **le texte** diffère n'est jamais remplacée sans l'accord du PO : elle est listée pour arbitrage.
- [ ] Les six labs de Frontend 2 qui portent encore « École Supérieure Polytechnique » en page de titre sont traités ici.
- [ ] Le contrôle tourne en local, pas en CI — il exige la distribution LaTeX du PO. La CI vérifie seulement qu'aucune ressource n'est plus ancienne que sa source.

### US-80 — Programmation par Réutilisation de Composants (8 pts)

En tant qu'étudiant de L2, je veux trouver mon cours en ligne,
afin d'y retrouver CM, labs et figures.

- [ ] Les cinq CM importés, figures générées par les scripts d'US-73.
- [ ] Les neuf labs en ressources de leur séance.
- [ ] Textes alternatifs des 19 figures : brouillons proposés, validés par le PO en une fois.
- [ ] Prérequis du cours posés dans le graphe d'US-67, à valider par le PO.
- [ ] Vérification en ligne, captures de chaque figure comprises.

### US-81 — Mathématiques pour le Machine Learning (8 pts)

En tant qu'étudiant de M1, je veux les mathématiques du ML en ligne,
afin de les revoir avant le cours d'Introduction au ML.

- [ ] Le périmètre choisi par le PO importé, modules et éventuels decks.
- [ ] Le cours devient prérequis d'Introduction au Machine Learning dans le graphe d'US-67.
- [ ] Mathématiques hors ligne numérotées et référencées (US-61).
- [ ] Textes alternatifs des figures : brouillons proposés, validés par le PO en une fois.
- [ ] Vérification en ligne, captures de chaque figure comprises.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-09-bilan.md` (CLAUDE.md §11).
Il indiquera combien de PDF US-76 a trouvés divergents, et combien de cours restent au catalogue
sans page.
