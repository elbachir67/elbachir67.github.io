# Sprint 8 — Un catalogue juste, des cours liés entre eux, et la migration qui continue

**Objectif :** le catalogue dit la vérité sur l'offre de cours, chaque cours sait de quels autres il
dépend, et trois cours de plus sont en ligne.
**Capacité :** 21 points

## Entrées PO

- [ ] Textes alternatifs des figures sans légende, demandés en une fois par lot de cours.
- [ ] Métadonnées des cours migrés : niveaux, semestre, objectifs, prérequis.
- [ ] Arbitrage sur l'inventaire d'US-68 : quels cours migrer, dans quel ordre.

## Hors périmètre

Nom de domaine (US-05) : reporté, décision du PO. Tuteur IA (EP6) : toujours sans sprint.

## Ordre d'exécution

US-68 → US-66 → US-67 → US-69 → US-70.

---

### US-68 — Inventaire des sources disponibles (2 pts)

En tant que PO, je veux savoir ce qui est migrable dès maintenant,
afin de décider sur des faits plutôt que de mémoire.

- [ ] `_import/` passé au crible : pour chaque cours, ce qui existe (CM, labs, TD, notebooks, figures), le format des sources (deck Beamer ou document rédigé), et ce qui manque.
- [ ] Les cours dont les sources ne contiennent **que des labs** sont signalés : pour eux, le lab tient lieu de CM et devient le contenu de la séance.
- [ ] Rapport dans la PR, cours par cours, avec une estimation de migration pour chacun.
- [ ] Aucun import : cette story n'observe que.

### US-66 — Un catalogue sans doublon ni confusion (3 pts)

En tant qu'étudiant, je veux une carte par cours,
afin de ne pas hésiter entre deux entrées qui désignent la même chose.

- [ ] « Introduction à l'IA : logique mathématique et calcul formel » et « Introduction à l'IA » sont **un seul cours** : une seule carte, celle du cours en ligne.
- [ ] « Structures de Données & Algorithmes Avancés » n'apparaît qu'une fois : la carte en double disparaît.
- [ ] « IPDL 1 » et « IPDL 2 » deviennent **un seul cours**, « Ingénierie des Processus de Développement Logiciel », avec ses deux niveaux (L3, M1).
- [ ] Les cours ajoutés depuis la dernière mise à jour du catalogue (Programmation Frontend 1 et 2, Introduction au DevOps, et ce que révèle US-68) sont présents, au bon domaine et au bon niveau.
- [ ] Un contrôle en CI échoue si deux entrées du catalogue portent le même titre, ou si un cours est décrit à la fois dans `enseignement/cours.yml` et dans `cours/<slug>/cours.yml`.
- [ ] Le PO valide le catalogue final, cours par cours, dans la PR.

### US-67 — Les cours se lient entre eux (5 pts)

En tant qu'étudiant, je veux savoir ce qu'il faut avoir suivi avant un cours et ce qu'il ouvre,
afin de me situer dans le cursus.

- [ ] Champ `prerequis-cours` dans `cours.yml` : une liste de slugs d'autres cours du site, distincte des prérequis en texte libre, qui restent.
- [ ] La page d'un cours affiche ses prérequis en **liens cliquables** vers les cours concernés, et la relation inverse : « Ce cours prépare à : … », calculée, jamais saisie deux fois.
- [ ] Un prérequis qui désigne un cours non encore en ligne s'affiche sans lien, en texte simple.
- [ ] La CI échoue sur un slug inexistant et sur tout cycle dans le graphe.
- [ ] Premières relations posées, à valider par le PO : Introduction au Machine Learning dépend de Programmation Python, de Structures de Données et d'Introduction à l'IA ; Programmation Frontend 2 dépend de Frontend 1 ; les autres selon l'inventaire.
- [ ] Le graphe complet est listé dans la PR pour validation.

### US-69 — Architectures Logicielles Modernes, séances suivantes (8 pts)

En tant qu'étudiant de M1, je veux la suite de mon cours en ligne,
afin de ne pas m'arrêter à la séance 2.

- [ ] Toutes les séances dont les sources sont dans `_import/` sont importées, une PR, un commit par séance.
- [ ] Labs attachés en ressources, selon ce que révèle US-68.
- [ ] Textes alternatifs demandés au PO en une fois, brouillons proposés (US-58).
- [ ] Vérification en ligne, captures de chaque figure comprises (règle de `CLAUDE.md`).

### US-70 — Un lot de cours à labs seuls (3 pts)

En tant qu'étudiant d'un cours sans CM rédigé, je veux quand même trouver mon cours en ligne,
afin d'accéder aux labs depuis le site.

- [ ] Pour un cours dont les sources ne comportent que des labs, chaque lab devient une séance : son contenu est converti comme un document rédigé, et le PDF compilé est attaché en ressource.
- [ ] Éprouvé sur un cours réel, choisi par le PO d'après l'inventaire (Programmation par Réutilisation de Composants, Frontend 1 ou 2, ou Introduction au DevOps).
- [ ] La page du cours indique la nature de ses séances, sans formule inventée sur ce qu'il contient.
- [ ] Si la conversion révèle un manque de la chaîne, il est signalé et estimé, jamais contourné.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-08-bilan.md` (CLAUDE.md §11).
Il indiquera combien de cours restent migrables sans travail de chaîne supplémentaire, et lesquels
demandent une capacité nouvelle.
