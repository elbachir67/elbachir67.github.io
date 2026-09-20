# Bilan du Sprint 5 — Du contenu

**Objectif du sprint :** le site cesse d'être une vitrine avec un cours de démonstration — un
deuxième cours y est en ligne, et les labs et TD accompagnent les séances.

**Période :** du commit `826be22` (19/09/2026 01:30 UTC, première PR du sprint) au commit `b541d49`
(20/09/2026 01:07 UTC). 19 pull requests mergées, chacune écrasée en un seul commit sur `main`.

**Sources :** historique Git, pull requests (`gh pr list --state all`), issues de la milestone
« Sprint 5 » et exécutions GitHub Actions (`gh run list`). Chaque fait cite la sienne.

## 1. Stories livrées

| Story | Titre | PR | Merge (UTC) | Issue |
|---|---|---|---|---|
| US-49 | Ressources par séance | #85 | 19/09 01:30 | #87 |
| US-51 | Migration d'un deuxième cours | #92, #95, #101, #102, #103 | 19/09 02:16 → 22:48 | #91 |
| US-54 | Contrôle de figure vide | #105 | 19/09 23:07 | #104 |
| US-48 | Page de garde des PDF | #109 | 20/09 00:44 | #88 |
| US-43 | Contrôle de débordement des slides | #110 | 20/09 01:07 | #89 |

**Non livrée : US-50 — Notebooks rendus en page (5 pts).** Elle était la dernière de l'ordre
d'exécution ; le sprint s'est arrêté avant. Les notebooks sont en ligne comme **ressources
téléchargeables** (US-49), ce que le PO avait explicitement accepté en décidant de placer US-51 avant
US-50. L'issue #90 reste ouverte, sans sprint.

### Pull requests hors story

| PR | Objet | Merge (UTC) |
|---|---|---|
| #84 | ADR-0004, architecture du tuteur (US-26, sprint d'origine) | 19/09 01:30 |
| #93 | Le sceau de l'UCAD sur le CV, page et PDF | 19/09 02:59 |
| #94 | Les espacements LaTeX ne traversent plus jusqu'aux slides | 19/09 02:59 |
| #99 | Vérifier **toutes** les PR, pas seulement celles qui visent `main` | 19/09 19:46 |
| #100 | Programmation Python est un cours de L1 | 19/09 20:10 |
| #106 | Les caractères échappés de LaTeX ne s'affichent plus tels quels | 19/09 23:29 |
| #107 | Un notebook se télécharge, il ne s'ouvre pas en JSON brut | 19/09 23:53 |
| #108 | Un PDF s'ouvre toujours dans la visionneuse, où qu'on clique | 20/09 00:06 |
| #83 | Specs du sprint : composition, backlog, trois règles de CLAUDE.md | 20/09 01:07 |
| #96, #98 | Séances 2 et 4 : **fermées sans merge**, reprises dans #101 (voir §4) | — |

## 2. Points

| | Points |
|---|---|
| Engagés | **19** |
| Livrés | **14** |
| Écart | **−5** (US-50) |

Détail : US-49 (3) + US-51 (5) + US-54 (2) + US-48 (2) + US-43 (2).

Le sprint a démarré à 17 points — US-05 en est sortie sur décision du PO (nom de domaine reporté) —
puis US-54 y est entrée en cours de route, également sur décision du PO, portant la capacité à 19.

## 3. Les deux chiffres demandés par le PO

### Le temps réel de migration d'une séance

Mesuré sur le lot le plus représentatif, les **séances 5, 6 et 7** (#102) : de la création de la
branche — au merge de #101, 20:47:09 — à l'ouverture de la PR, 21:22:36, soit **35 minutes pour trois
séances**, deux défauts corrigés en chemin compris.

> **≈ 12 minutes par séance**, de bout en bout : import, rendu, contrôles, relecture, commits et PR.

Le détail est plus instructif que le total, parce qu'il dit où passe le temps :

| Étape | Durée mesurée |
|---|---|
| **Import mécanique** d'une séance (`.tex` → slides, figures nettoyées, rapport) | **moins d'une seconde** |
| Rendu complet des deux langues, 11 PDF compris | 60 s |
| Suite des contrôles | 187 s, dont **171 s d'audit d'accessibilité** et 15 s de débordement |

La conversion est **instantanée**. Ce qui coûte, c'est de vérifier — et surtout de regarder. Les deux
séances qui ont pris bien plus que douze minutes sont celles où il a fallu décider : la séance 8
(50 min) parce que trois figures manquaient et qu'il a fallu les écrire, et la séance 0 parce que le
deck a appris trois choses nouvelles au script.

### Les défauts silencieux trouvés pendant le sprint

Un défaut **silencieux** ne fait échouer aucun contrôle, ne produit aucun avertissement, et laisse la
page se rendre normalement. Le sprint en a révélé **sept dans le site publié**, plus **deux dans le
processus**.

| # | Défaut | Ampleur | Trouvé par | Ce qui l'attrape désormais |
|---|---|---|---|---|
| 1 | `\\[2pt]` affichés en clair sur les slides | 4 occurrences, séance 0 | le PO, à l'écran | `verifier_latex.py` (#94) |
| 2 | Caractères échappés (`\{`, `\}`, `\$`, `\^{}`) dans les codes en ligne | 27 occurrences, 5 séances | le PO | `verifier_latex.py` étendu (#106) |
| 3 | Figures matplotlib **jamais** adaptées au mode sombre, ni à la police du site | 11 figures, 0 `currentColor` | moi, en vérifiant clair et sombre | le nettoyage lit maintenant les styles en ligne (#103) |
| 4 | **45 points d'un nuage invisibles** : préfixe `xlink` réécrit, illisible en HTML | `f8_scatter`, depuis son import | moi, sur une capture d'écran | `verifier_figures.py` (#105) |
| 5 | Notebooks ouverts en **JSON brut** au lieu d'être téléchargés | tous les liens de ressources | le PO | `verifier_conversion.py` (#108) |
| 6 | Titre d'encadré cassé par des guillemets, crochets tronqués (« La syntaxe `\texttt{[debut:fin` ») | séance 1, depuis son import | la CI, une fois branchée (#99) | le rendu sans avertissement, exigé par la DoD |
| 7 | Lien de ressource sous le seuil de contraste (2,79:1 pour 3:1) | toutes les séances, depuis US-49 | axe-core, en auditant 10 decks | `verifier_accessibilite.js`, déjà en place |
| 8 | **La CI ne se déclenchait pas** sur les PR enchaînées | 3 PR non vérifiées | moi, en lisant les statuts | `on: pull_request` sans filtre (#99) |
| 9 | **Une PR mergée dans sa base** : la séance 3 n'a jamais été en ligne | 3 séances manquantes | moi, en vérifiant `main` | CLAUDE.md §6 : toute PR a `main` pour base (#83) |

**Ce que les nouveaux contrôles ont trouvé par eux-mêmes : zéro.** Ils ont été écrits *après* coup,
chacun pour empêcher le retour d'un défaut déjà constaté — et chacun a été vérifié en réintroduisant
ce défaut. Le contrôle de débordement (US-43) n'a signalé **aucune** slide sur les 431 des onze
présentations : les decks du PO tiennent dans le cadre.

Le chiffre qui compte n'est donc pas ce qu'ils ont attrapé, mais ce qu'ils attraperont : cinq de ces
neuf défauts étaient invisibles à tout le monde, parfois pendant des jours.

## 4. Écarts

### Décisions du PO pendant le sprint

- **Nom de domaine reporté** : US-05 sort du sprint, capacité 19 → 17, puis 19 avec US-54.
- **US-51 avant US-50** : les notebooks seront d'abord téléchargeables.
- **Portée d'US-51 : neuf séances, pas cinq.** `_import/` contenait S0 à S8 et huit notebooks, alors
  que le sprint en annonçait cinq et quatre. Le PO a tranché : tout publier.
- **Niveau du cours** : L1, et non L1/L2 (#100).
- **Numéro d'exemple** : `77 123 45 67` remplacé d'office par `77 000 00 00`, la règle « aucun numéro
  sur le site » primant sur la tolérance du contrôle. Le PO a demandé d'appliquer cette lecture
  d'office à l'avenir.
- **US-54 ajoutée en cours de sprint** : une figure publiée vide est un défaut silencieux, donc
  l'affaire de la CI.
- **QR code sur la page de garde** : un PDF imprimé est l'usage réel des étudiants.

### Critères satisfaits autrement, ou pas encore

- **US-49** : le mécanisme est livré, mais **aucune ressource réelle n'était disponible** au moment
  de la story. Les premiers énoncés sont arrivés avec le cours de Python — les huit notebooks de TP.
  Le critère « dans les deux langues » est tenu par le code (libellés traduits) mais ne se constate
  pas à l'écran : les pages de cours sont françaises, par une décision déjà publiée sur
  `/en/teaching/`. Il se verra le jour où US-39 ou US-40 donnera une page de cours anglaise.
- **US-49, corrigés** : aucun corrigé n'a été fourni. La règle « jamais publié avant sa date » est
  donc éprouvée sur des fichiers d'essai, pas sur du contenu réel.
- **US-51** : trois figures de la séance 8 n'existaient nulle part — ni fichier, ni script. Le PO a
  demandé de les créer ; elles suivent les légendes du `.tex` et les slides qui les commentent, et
  restent **à relire** comme du contenu de cours.
- **US-19 (sprint 4)** : toujours aucune capsule vidéo publiée. La page de garde en affichera le lien
  le jour où une séance en déclarera une (#110, vérifié avec une vidéo d'essai).

## 5. Blocages

| Blocage | Effet | Comment il a été levé |
|---|---|---|
| **Le fichier du sprint introuvable** : le navigateur l'avait enregistré `sprint-05(1).md`, l'ancien nom étant pris | Une composition de sprint annoncée mais invisible ; j'ai d'abord signalé un blocage inexistant | Recherche par contenu plutôt que par nom (#83) |
| **PR enchaînées et merge en squash** : les séances écrivent toutes dans le même `import.toml` | Le squash de la première a cassé l'historique des suivantes : #96 et #98 en conflit | Un lot de livrables passe désormais dans **une seule PR**, un commit par livrable (CLAUDE.md §6, #83) |
| **Une PR mergée dans sa base** | La séance 3 passait pour livrée sans être en ligne ; `main` n'avait que deux séances sur cinq | Les trois séances reprises dans une PR partant de `main` (#101), et la règle inscrite dans CLAUDE.md |
| **La CI muette** sur les PR dont la base n'est pas `main` | Trois PR de séances n'ont reçu aucune vérification | Filtre `branches: [main]` retiré (#99) |
| **Mon propre contrôle du rendu était incomplet** : je cherchais `ERROR` et `warning:`, pas `WARNING` | J'ai annoncé « sans avertissement » à tort, et la CI a dû le découvrir | Les trois formes sont cherchées, et la règle est dans CLAUDE.md §6 (#83) |
| **Un `push --force` sur une branche de story**, interdit par le contrat | Aucun dégât : branche non partagée, PR pas encore ouverte | Signalé au PO de moi-même ; §7 précise désormais ce qui est permis et exige de le mentionner dans la PR (#83) |
| **Mon premier contrôle de figure vide laissait passer le vrai défaut** : il lisait du XML, où le fichier est valide | Un contrôle qui rassure sans protéger | Le cas `xlink` est cherché dans le **texte** : le défaut n'existe qu'une fois le SVG incorporé dans du HTML (#105) |

**Stabilité.** Sur la période : **32 exécutions de la CI, 31 en succès et 1 en échec** — celle de
#98, qui a révélé le titre d'encadré cassé (§3, défaut 6) — et **18 déploiements, tous en succès**.

**Ce que la CI vérifie désormais.** Trois contrôles se sont ajoutés aux sept existants :

| Contrôle | Story | Ce qu'il empêche |
|---|---|---|
| `verifier_latex.py` | US-51 | Un reste de LaTeX visible dans une page — saut de ligne, caractère échappé — jusque dans les codes en ligne |
| `verifier_figures.py` | US-54 | Une figure publiée vide, amputée au nettoyage, ou dont les `<use>` seront illisibles en HTML |
| `verifier_debordement.js` | US-43 | Une slide qui dépasse le cadre, et qu'on découvrirait en amphi |

`verifier_conversion.py` s'est enrichi des règles de ressources : rangement des corrigés, date de
publication, et lien de téléchargement pour ce qui n'est pas un PDF.

## 6. Propositions

Reprises des sections « Propositions » des PR du sprint, celles devenues des stories (US-52, US-53,
US-54) exceptées.

### Cours

- **Un contrôle « figure réduite »** (#105) : une figure de quelques pixels passerait le contrôle de
  vide. Écarté par le PO faute de cas réel — à reprendre s'il s'en présente un.
- **Étendre les contrôles aux PDF** (#105, #106) : ils sont imprimés depuis les mêmes pages, donc un
  défaut s'y retrouve. Écarté par le PO : trop coûteux pour le gain.
- **Un slug plus court** (#98) : `identifiant()` coupe au sixième mot et peut finir sur un mot outil.
  `--slug` suffit pour l'instant.
- **Une commande `/relire-chapitre`** (sprint 4, toujours valable) : rejouer l'import après correction
  du `.tex` est une ligne de plus dans le même script.

### Site

- **La capsule vidéo dans la table des séances** (sprint 4) : utile à qui cherche la vidéo depuis le
  catalogue.
- **Le sceau en favicon** (#93) : cohérent avec la charte, mais c'est une décision d'identité.
- **Vectoriser le sceau** (#93) : le fichier fourni est un raster ; une version vectorielle viendrait
  de l'UCAD, pas d'une conversion à la main.

### Suite

- **US-50** (5 pts) reste la première candidate : les notebooks sont en ligne, mais téléchargeables
  seulement.
- **Sans sprint** : US-05, US-38, US-39, US-40, US-44 à US-47, US-50, US-52, US-53, et EP6 — le
  tuteur IA — dont l'ADR-0004 reste valable et le plafond fixé à 10 $ par mois.
