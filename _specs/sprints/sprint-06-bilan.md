# Bilan du Sprint 6 — Les cours rédigés entrent dans la chaîne

**Objectif du sprint :** un CM LaTeX rédigé, avec ses figures TikZ, devient une page de cours lisible
en ligne, comme un deck devient des slides. Le premier chapitre de Programmation C avancée le prouve.

**Période :** du commit `78ba5f4` (21/09/2026 00:10 UTC, premier merge du sprint) au commit `688ae96`
(21/09/2026 14:03 UTC). 8 pull requests mergées.

**Sources :** historique Git, pull requests (`gh pr list --state all`), issues de la milestone
« Sprint 6 » et exécutions GitHub Actions (`gh run list`). Chaque fait cite la sienne.

## 1. Stories livrées

**Les cinq stories du sprint sont livrées : 26 points sur 26.**

| Story | Titre | PR | Merge (UTC) | Issue |
|---|---|---|---|---|
| US-57 | Catalogue : cartes lisibles et distinctes | #119 | 21/09 00:10 | #114 |
| US-40 | Conversion d'un CM rédigé en page de cours | #120 | 21/09 06:46 | #115 |
| US-55 | Conversion des figures TikZ | #122 | 21/09 07:25 | #116 |
| US-56 | Migration du premier chapitre de C | #123 | 21/09 08:17 | #117 |
| US-50 | Notebooks rendus en page | #125 | 21/09 14:03 | #118 |

### Pull requests hors story

| PR | Objet | Merge (UTC) |
|---|---|---|
| #121 | La page Enseignement va droit aux cartes | 21/09 07:25 |
| #124 | Les pages disent ce que le lecteur ne voit pas déjà | 21/09 08:17 |
| #113 | Specs du sprint : composition, backlog, issues | 21/09 14:03 |

## 2. Points

| | Points |
|---|---|
| Engagés | **26** |
| Livrés | **26** |
| Écart | **0** |

Détail : US-57 (3) + US-40 (8) + US-55 (5) + US-56 (5) + US-50 (5).

## 3. Le chiffre demandé par le PO : migrer un chapitre rédigé

### 22 minutes, contre 12 pour une séance en slides

Mesuré sur le chapitre d'introduction de Programmation C avancée : de la création de la branche — au
merge d'US-55, 07:25:08 — à l'ouverture de la PR #123, 07:47:01.

**Ces 22 minutes contiennent plus qu'une migration** : la création du cours, sa fiche, sa barre
latérale, son départ du catalogue d'attente, et **trois ajustements de la chaîne** que ce premier
cours rédigé a révélés — le bouton PDF qui n'a pas lieu d'être, le type de ressource « pdf », le mot
« chapitre » à la place de « séance ».

Un chapitre suivant, dans un cours qui existe, n'en garde que la conversion et la relecture.

### Où passe le temps

| Étape | Durée mesurée |
|---|---|
| Import mécanique d'un chapitre (`.tex` → page) | **0,1 s** |
| Compilation des schémas TikZ | **0,7 s par schéma** (5 en 3,5 s ; 16 en 11,6 s) |
| Rendu complet des deux langues | 60 s |
| Suite des contrôles, audit d'accessibilité compris | ~200 s |

La machine travaille **quatre minutes**. Le reste est de la lecture : vérifier que le texte tient
debout, demander les textes alternatifs, écrire la PR.

**Un chapitre rédigé coûte donc à peine plus qu'une séance en slides** — l'écart tient aux schémas
TikZ à compiler et à une page plus longue à relire, pas à la conversion.

## 4. Le second chiffre : ce que coûterait la suite

Chaque `.tex` restant a été **converti pour de vrai** dans un dossier temporaire, et ce qui en sort
est compté. Ce ne sont donc pas des estimations à vue.

### Programmation C avancée — 4 chapitres restants

| Chapitre | Volume | Ce que la chaîne ne sait pas encore |
|---|---|---|
| **Ch00** Fondamentaux | 1204 lignes, 43 encadrés, **38 blocs de code** | **rien** : 43 callouts et 76 blocs produits, aucun reste |
| **Ch01** Représentation numérique | 641 lignes, **16 schémas TikZ** | `\begin{cases}` (×2), `\rightarrow`, `\checkmark` |
| **Ch02** Organisation mémoire | 872 lignes, 6 tableaux | **l'import échoue** : « accolade non fermée » — un défaut du lecteur, à corriger |
| **Ch03** Structures et unions | 839 lignes, 12 schémas | `\begin{verbatim}` (×1) |

Les **16 schémas du chapitre 1 compilent déjà**, sans une seule erreur : la chaîne TikZ tient sur un
chapitre qu'elle n'a jamais vu.

> **Estimation : 3 à 4 heures de travail**, dont **1 à 2 heures** pour le défaut de lecture du Ch02 et
> les quatre constructions manquantes, puis ~15 minutes par chapitre.
>
> **La vraie contrainte n'est pas là** : ces chapitres portent **33 schémas TikZ sans légende**, donc
> 33 phrases à demander au PO. C'est son temps, pas celui de la machine.

### Structures de Données — 2 séances déposées sur 4

`S03_Hachage` et `S04_Arbres_Tas` ne contiennent qu'un fichier `A_DEPOSER_ICI.txt` : **le cours est à
moitié fourni**. Les deux séances présentes ont chacune un CM et un Lab, soit 4 documents de 700 à
800 lignes.

Ce que la conversion d'essai révèle :

- **dix types d'encadrés** propres à ce cours (`prereqbox`, `appliboxQ`, `appliboxR`, `retenirbox`,
  `theorembox`, `objectifbox`, `lienbox`, `exercicebox`, `attentionbox`, `infobox`). Ils ne sont pas
  un travail de chaîne : c'est une **table de correspondance à décider par le PO**, comme pour le
  cours de C ;
- des environnements `figure` et `table` (5 et 2 par chapitre), que la chaîne ne traite pas encore ;
- des mathématiques hors ligne (`align*`), et des commandes de mise en page à ignorer
  (`tableofcontents`, `newpage`, `thispagestyle`, `addcontentsline`).

> **Estimation : 4 à 6 heures** pour les deux séances déposées, dont **2 à 3 heures** de chaîne —
> flottants, mathématiques hors ligne — et une demi-heure d'aller-retour sur la table des encadrés.
> Les séances 3 et 4 s'ajouteront quand leurs sources arriveront, à ~30 minutes par document une fois
> la chaîne prête.

### Et le troisième cours

`_import/intro_IA/` contient **sept CM d'Introduction à l'IA**, du même moule que Structures de
Données : mêmes encadrés, mêmes flottants, plus de figures et davantage de mathématiques. Le travail
de chaîne fait pour Structures de Données le servira presque entièrement.

## 5. Écarts

### Ce qui a été livré autrement que prévu

- **US-40 n'a pas pu prouver trois de ses critères.** Le chapitre d'introduction du cours de C **ne
  contient ni bloc de code, ni formule mathématique, ni tableau** — or la story les mentionne. Le PO
  a tranché (option a) : livrer ce qui est prouvé, signaler le reste. Le test de conversion du §4
  lève une partie du doute : le **Ch00 et ses 38 blocs de code passent sans reste**.
- **US-40 réestimée de 5 à 8 points** avant le sprint : l'estimation d'origine visait « une page en
  complément d'un deck », la story demandait la conversion d'un CM entier (#113).
- **US-55 n'applique pas le nettoyage prévu.** La story demandait « encres en `currentColor`, police
  héritée du site ». Appliqué tel quel, ce nettoyage **casse** les schémas : substituer la police
  décale chaque glyphe, et `currentColor` rend le texte illisible dans une boîte claire. Les deux ont
  été constatés à l'écran. La story prévoyait ce cas — « signaler et proposer une alternative » : le
  schéma garde ses couleurs et se pose sur une planche claire en mode sombre, ce que le PO a validé.

### Décisions du PO pendant le sprint

- **Cartes du catalogue** : proposition A, « filet de domaine », retenue sur deux soumises.
- **Encadrés du cours de C** : `techbox` devient un callout « important » et non « tip », pour ne pas
  se confondre avec `examplebox`.
- **« Chapitre -1 »** n'est pas une coquille : c'est le chapitre d'introduction, avant le chapitre 0.
  La page s'appelle « Introduction », sans numéro, et la chaîne accepte qu'un cours commence à -1.
- **Type de ressource « tp »** ajouté après coup — « TP » en français, « Lab » en anglais.
- **Les pages du site** disent ce que le lecteur ne voit pas déjà (#121, #124).

## 6. Blocages

| Blocage | Effet | Comment il a été levé |
|---|---|---|
| **Le texte d'un schéma TikZ, ou le dessin — mais pas les deux.** `latex` + `dvisvgm` perd le dessin (pgf écrit du PostScript) ; `pdflatex` + `pdftocairo` transforme le texte en tracés | Une image morte, ni sélectionnable ni lisible aux lecteurs d'écran | Le **pilote dvisvgm de pgf** écrit du SVG dans le DVI, et `lualatex` + `fontspec` compose **dans la police du site** : le dessin et le texte (#122) |
| **Un `---` en tête de cellule Markdown fait tomber le rendu du projet entier** : Quarto y lit un bloc YAML | Pire que la panne : **l'erreur désigne un autre fichier** que celui en cause. J'ai cherché du côté de la configuration, du cache et de `_metadata.yml` avant de comprendre | 55 séparateurs normalisés en `***`, et un **contrôle ajouté** pour que personne ne recommence cette recherche (#125, puis ce bilan) |
| **Un défaut mesuré chez moi, absent en CI** : mon réglage clavier des zones défilantes dépendait de la largeur des blocs, qui dépend des **métriques de la police** — différentes entre macOS et le Linux de la CI | Un bloc tenait en local et débordait en CI : la CI a échoué sur une PR que je croyais verte | Le réglage est devenu **inconditionnel** : quelques tabulations de plus, jamais un bloc inatteignable, et plus de surprise selon la machine (#125) |
| **Le domaine se repliait sur seize cartes à 768 px** — la grille à deux colonnes serre plus que celle à trois | Le PO demandait de vérifier 375 px ; c'est 768 qui était en faute | Corps et interlettrage réglés, et **mesure aux trois largeurs** plutôt qu'à une seule (#119) |
| **46 figures de notebook sans texte alternatif** | Autant de violations WCAG | Elles disent **d'où elles viennent**, et non ce qu'elles montrent : les décrire reviendrait à inventer, et le code est juste au-dessus (#125) |

**Stabilité.** Sur la période : **9 exécutions de la CI, 8 en succès et 1 en échec** — celle décrite
ci-dessus, qui a trouvé un vrai défaut — et **8 déploiements, tous en succès**.

**Ce que la CI vérifie désormais.** Le contrôle des ressources s'étend, et un contrôle naît de ce
sprint :

| Contrôle | Ce qu'il empêche |
|---|---|
| `verifier_conversion.py` · notebooks lisibles | Un `---` en tête de cellule, qui fait tomber le rendu du projet entier |
| `verifier_conversion.py` · liens de ressources | Un lien qui télécharge ce qui devrait s'ouvrir, ou l'inverse |

## 7. Propositions

Reprises des sections « Propositions » des PR du sprint.

### Chaîne de conversion

- **Le défaut de lecture du Ch02** (« accolade non fermée ») est le seul obstacle dur au reste du
  cours de C : à corriger en premier.
- **Les flottants `figure` et `table`**, et les **mathématiques hors ligne**, sont ce qui manque pour
  Structures de Données et Introduction à l'IA — un travail qui servira aux deux cours.
- **Une table d'encadrés par cours**, dans `import.toml` plutôt qu'en ligne de commande : dix types
  pour Structures de Données, cela fait une commande longue.

### Site

- **Un filtre par domaine ou par niveau** au catalogue (#119) : à vingt et un cours, les couleurs
  suffisent ; au-delà de trente, un filtre deviendra plus utile qu'une teinte de plus.
- **Le sceau en favicon** (#93, toujours valable) : décision d'identité.

### Suite

- **Le cours de C**, chapitres 0 à 3 : 3 à 4 heures, et 33 textes alternatifs à demander au PO.
- **Structures de Données**, 2 séances sur 4 déposées : 4 à 6 heures.
- **Introduction au ML**, hors sprint depuis le Sprint 6 : decks Beamer, aucune capacité nouvelle,
  onze séances déjà dans `_import/ML/`.
