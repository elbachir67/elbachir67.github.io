# Sprint 9 — Trois cours de plus, et des PDF qui disent la vérité

**Objectif :** Programmation Frontend 1, Programmation par Réutilisation de Composants et
Mathématiques pour le Machine Learning sont en ligne, plus aucun PDF servi ne diverge de sa
source sans que la CI le dise, et le site répond à son propre nom de domaine.
**Capacité :** 28 points — 26 à la rédaction, sous la vitesse mesurée au Sprint 8 (31 livrés), pour
garder de la marge ; puis US-05 (2), ajoutée par le PO à la composition, avant le début du sprint.

## Règle de sprint

Aucun ajout en cours de route. Un blocage se traite par **échange** : une story entre, une autre
sort, et la capacité ne monte pas.

## Entrées PO

- [ ] Métadonnées des trois cours : niveaux, objectifs, prérequis en texte libre.
  **Frontend 1 : rendu** — celles du plan du cours (`Plan_Cours_JangAfrig.tex`), mot pour mot. Structure à quatre séances (CM1, CM2, CM4, S15), labs en ressources : Lab 0 à 2 → CM1, Lab 3 et 4 → CM2, Lab 8 et 9 → CM4, Lab 10 → S15 ; plan du cours en ressource de la page du cours.
- [x] Mathématiques pour le ML : quel périmètre publier — les quatre modules seuls, ou avec les deux decks (25 ou 61 figures selon l'inventaire).
  **Rendu** — **les quatre modules seuls** ; les deux decks passent au Sprint 10.
- [x] Nom de domaine (US-05) : **`ebtoure.sn`**, actif chez Wanekoo, gestion DNS incluse,
  renouvellement automatique activé. Le PO saisit les enregistrements DNS dans son espace Wanekoo.
- [ ] Textes alternatifs des figures sans légende, brouillons validés en une fois par cours.
- [ ] Arbitrage sur les PDF que US-76 trouvera divergents.

## Ordre d'exécution

US-05 → US-79 → US-76 → US-80 → US-81. US-05 commence la première, parce que la propagation DNS
prend du temps : les enregistrements sont saisis, US-79 avance pendant la propagation, et US-05 se
termine — GitHub Pages, HTTPS, `site-url` — quand le domaine répond.

---

### US-05 — Nom de domaine et HTTPS (2 pts)

En tant que PO, je veux diffuser une adresse qui m'appartienne,
afin que mon site survive à un changement de compte ou d'hébergeur.

- [ ] Domaine configuré sur GitHub Pages (fichier `CNAME`, enregistrements DNS documentés dans le README).
- [ ] HTTPS actif, redirection depuis `elbachir67.github.io` vérifiée.
- [ ] `site-url` mis à jour partout : sitemap, flux RSS, métadonnées de partage, liens absolus.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`), sur les deux langues.

### US-79 — Programmation Frontend 1 (5 pts)

En tant qu'étudiant de L1, je veux trouver mon cours de web en ligne,
afin de suivre les séances et leurs labs depuis le site.

- [ ] Les séances dont les sources sont dans `_import/frontend1/` importées, une PR, un commit par séance ; labs en ressources.
- [ ] Le prérequis de Frontend 2 vers Frontend 1 devient un lien cliquable.
- [ ] Les **quatre** séances absentes de l'inventaire — CM3 (JavaScript), labs 5, 6 et 7, le bloc JS entier — sont signalées, sans être comblées. Le PO les cherche de son côté ; s'il les trouve, elles entreront par la suite.
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

- [ ] Le périmètre choisi par le PO importé : **les quatre modules**. Les deux decks n'en font pas
      partie — ils passent au Sprint 10, décision du PO.
- [ ] Le cours devient prérequis d'Introduction au Machine Learning dans le graphe d'US-67.
- [ ] Mathématiques hors ligne numérotées et référencées (US-61).
- [ ] Textes alternatifs des figures : brouillons proposés, validés par le PO en une fois.
- [ ] Vérification en ligne, captures de chaque figure comprises.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-09-bilan.md` (CLAUDE.md §11).
Il indiquera combien de PDF US-76 a trouvés divergents, et combien de cours restent au catalogue
sans page.
