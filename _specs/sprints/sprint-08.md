# Sprint 8 — Un catalogue juste, des cours liés entre eux, et la migration qui continue

**Objectif :** le catalogue dit la vérité sur l'offre de cours, chaque cours sait de quels autres il
dépend, et trois cours de plus sont en ligne.
**Capacité :** 33 points — 21 à la composition, puis les ajouts du PO en cours de sprint : US-73 (2), US-74 (2), US-75 (3) et US-76 (5)

## Entrées PO

- [ ] Textes alternatifs des figures sans légende, demandés en une fois par lot de cours.
- [ ] Métadonnées des cours migrés : niveaux, semestre, objectifs, prérequis.
- [x] Arbitrage sur l'inventaire d'US-68 : quels cours migrer, dans quel ordre. **Rendu** — US-70
  porte sur **Programmation Frontend 2** ; la migration de PRC attend le Sprint 9 et son travail de
  chaîne entre dans ce sprint (US-73).

## Hors périmètre

Nom de domaine (US-05) : reporté, décision du PO. Tuteur IA (EP6) : toujours sans sprint.
**Migration de Programmation par Réutilisation de Composants** : reportée au Sprint 9, décision du
PO. Seul son travail de chaîne (US-73) entre dans ce sprint, parce que la migration en dépend.

## Ordre d'exécution

US-68 → US-66 → US-75 → US-74 → US-67 → US-76 → US-69 → US-70 → US-73.

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
- [ ] Éprouvé sur un cours réel, choisi par le PO d'après l'inventaire : **Programmation Frontend 2**. Sept labs, aucun CM, aucune figure — donc aucun texte alternatif à valider. Les sept PDF sont déjà compilés.
- [ ] La page du cours indique la nature de ses séances, sans formule inventée sur ce qu'il contient.
- [ ] Si la conversion révèle un manque de la chaîne, il est signalé et estimé, jamais contourné.

### US-73 — Les figures de PRC, régénérées en SVG (2 pts)

En tant qu'équipe de développement, je veux que les figures d'un cours se régénèrent au bon format
et au bon endroit, afin que la migration de PRC ne bute pas dessus au Sprint 9.

- [ ] Les dix-neuf figures des cinq CM de Programmation par Réutilisation de Composants sont
      produites par les scripts `gen_figures_cm1.py` à `gen_figures_cm5.py`, **corrigés à la
      source** : sortie en SVG, et non en PNG, dans un chemin relatif au dossier du cours et non
      dans `/home/claude/cmN/figures/`.
- [ ] Les dix-neuf noms produits sont exactement ceux que les `.tex` appellent, vérifié fichier par
      fichier.
- [ ] Aucune migration : cette story prépare, elle ne publie pas.
- [ ] Les figures produites sont montrées au PO — **en les regardant**, règle de `CLAUDE.md` §7.

### US-74 — La numérotation des séances est continue (2 pts)

En tant qu'étudiant, je veux que les séances d'un cours se suivent sans trou,
afin de ne pas croire qu'il en manque une.

- [ ] Introduction à l'IA affiche **1, 2, 3, 4, 5** et non 1, 2, 3, 5, 6. Le cours compte cinq
      séances : la numérotation des dossiers de `_import/` ne suivait pas celle des séances
      (§6 de l'inventaire).
- [ ] La correction se fait **à la source** — les `.tex` de `_sources/` et leurs copies
      d'`_import/` — puis l'import est rejoué : descriptions de page et renvois d'une séance à
      l'autre compris.
- [ ] Les fichiers, le manifeste et les ressources suivent la même numérotation.
- [ ] Les adresses des deux dernières séances changent : la PR dit lesquelles, et vérifie
      qu'aucun lien du site n'y menait.

### US-75 — Rien de non publiable dans un PDF non plus (3 pts)

En tant que PO, je veux que le contrôle du non publiable lise aussi les PDF,
afin qu'un terme interdit ne parte pas en ligne dans une pièce jointe.

- [ ] `scripts/verifier_non_publiable.py` extrait le **texte des PDF** servis par le site et y
      cherche les mêmes termes que dans les pages. `pdftotext` est déjà installé par la CI, une
      étape plus haut, pour le contrôle des numéros de téléphone.
- [ ] Le contrôle est écrit **avant** les corrections : il doit d'abord échouer sur les huit PDF
      fautifs, et la PR le montre.
- [ ] `lab-4-arbres-et-tas.pdf` et `projet-3-tas-binaire.pdf` sont **retirés du site** — leurs
      sources ont divergé, le PO les reprendra (noté dans #163). Rien n'est recompilé pour eux.
- [ ] `tp-1-mise-en-place.pdf` est recompilé après correction de la séquence UTF-8 invalide de sa
      source (ligne 189) : c'est un défaut de source, pas de contenu.
- [ ] Les cinq PDF du cours de C sont traités selon ce que dit leur source : recompilés si elle est
      saine, signalés sinon.

### US-76 — Une ressource est ce que sa source produit (5 pts)

En tant qu'équipe de développement, je veux que la CI recompile les ressources d'un cours et les
compare aux PDF commités, afin qu'un document publié ne dérive plus de sa source sans que personne
le voie.

- [ ] Chaque ressource PDF déclarée au manifeste d'un cours est **recompilée depuis sa source**
      et comparée au fichier commité : le contrôle dit lesquelles ont divergé.
- [ ] Le contrôle échoue sur une source qui **ne compile pas**, et la CI compile avec
      `-halt-on-error` : un document abîmé ne s'installe plus en ligne en silence.
- [ ] La comparaison porte sur le **texte extrait**, et non sur les octets : deux compilations d'une
      même source ne donnent pas le même fichier.
- [ ] Le contrôle nomme, pour chaque écart, ce qui diffère — et non seulement qu'il diffère.
- [ ] La chaîne LaTeX entre en CI : la PR dit ce qu'elle coûte en minutes, et ce qu'elle installe.
- [ ] Les sources hors d'atteinte — celles qu'`_import/` ne contient pas — sont **signalées, et non
      tues** : une ressource sans source vérifiable est un fait à connaître.

---

## Bilan

Rédigé par Claude Code en fin de sprint : `_specs/sprints/sprint-08-bilan.md` (CLAUDE.md §11).
Il indiquera combien de cours restent migrables sans travail de chaîne supplémentaire, et lesquels
demandent une capacité nouvelle.
