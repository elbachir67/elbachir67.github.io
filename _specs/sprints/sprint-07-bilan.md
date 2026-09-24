# Bilan du Sprint 7

**Objectif du sprint :** le cours de Programmation C avancée est complet en ligne, le cours
d'Introduction au ML y rejoint Python, et la chaîne sait traiter ce que demandent Structures de
Données et Introduction à l'IA.

**Objectif tenu, et dépassé :** les deux cours que le sprint devait seulement *préparer* sont en
ligne. Au merge du bilan du Sprint 6 (`8d2008a`), le site portait **trois cours, 12 chapitres et 31
figures** ; il en porte aujourd'hui **six, 34 et 249**.

Sources : historique Git, `gh pr list --state all`, `gh run list`. Chaque fait cite la sienne.

---

## 1. Stories livrées

| Story | Titre | PR | Mergée le |
|---|---|---|---|
| US-58 | Brouillons de textes alternatifs soumis au PO | #132, #133 | 21/09 15:39, 17:29 |
| US-59 | Programmation C avancée, chapitres 0 à 3 | #134, #135, #136 | 21/09 19:24, 19:53, 21:35 |
| US-60 | Introduction au Machine Learning, neuf séances | #137, #140 | 21/09 22:47, 22/09 17:51 |
| US-61 | Flottants, mathématiques numérotées et renvois | #143 | 22/09 21:43 |
| US-64 | `\multicolumn` et équations à étiquettes multiples | #150 | 23/09 22:30 |
| US-65 | Le site sert ce qu'il promet | #151 | 23/09 22:47 |

**Hors story, sur décision du PO en cours de sprint :**

| Livrable | PR | Mergée le |
|---|---|---|
| Structures de Données, quatre séances | #148, #149 | 23/09 20:07, 21:46 |
| Introduction à l'IA, cinq séances | #150 | 23/09 22:30 |

**Correctifs du sprint**, tous nés d'un défaut trouvé en ligne ou en revue : #138 (identifiants de
glyphes), #139 (contrôle d'unicité), #141 (aucun corrigé publié ni versionné), #142 et #146
(MathJax), #144 (sept fiches de TD manquantes), #145 (petites matrices), #147 (contrôle des
formules composées).

## 2. Points

| | Points |
|---|---:|
| Capacité annoncée | 20 |
| Engagés (US-58, 59, 60, 61) | 20 |
| Livrés | 20 |
| Livrés en plus (US-64, US-65) | 5 |
| **Écart** | **+5** |

Les deux migrations hors story — Structures de Données et Introduction à l'IA — ne sont pas
chiffrées : le PO les a demandées en cours de sprint sans les estimer. **Proposition** : leur donner
un identifiant avant le prochain sprint, faute de quoi le plus gros du travail de ce sprint
n'apparaît dans aucun compte.

## 3. Combien coûte la migration d'un cours

Le Sprint 6 avait mesuré « quatre minutes par chapitre ». Ce sprint permet de dire où passent ces
minutes, et surtout ce qui n'en est pas.

**Le temps machine, mesuré en rejouant chaque import** (34 chapitres, même machine) :

| Cours | Cible | Chapitres | Conversion | Par chapitre |
|---|---|---:|---:|---:|
| Introduction au ML | decks | 9 | 3,6 s | 0,4 s |
| Programmation Python | decks | 9 | 0,4 s | < 0,1 s |
| Architectures logicielles | decks | 2 | 0,1 s | < 0,1 s |
| Introduction à l'IA | pages | 5 | 1,5 s | 0,3 s |
| Programmation C avancée | pages | 5 | 0,8 s | 0,2 s |
| Structures de Données | pages | 4 | 0,7 s | 0,2 s |

**La conversion elle-même ne coûte rien** — moins d'une demi-seconde par chapitre, decks ou pages
rédigées confondus. Une page rédigée n'est pas plus chère qu'un deck : elle est plus longue (152
sections pour la séance 3 d'IA, contre une quarantaine de slides), mais le travail est le même.

Ce qui coûte est autour :

| Étape | Durée | Où |
|---|---:|---|
| Compilation des schémas TikZ | 8,4 s pour 11 schémas | préparation, jamais en CI |
| Conversion PDF → SVG | 0,4 s pour 9 figures | préparation, jamais en CI |
| Rendu du site entier | **174 s** | CI, run 35927211747 |
| Contrôle des formules composées | **234 s** | CI, même run |
| Contrôle de débordement | 37 s | CI, même run |
| **Audit d'accessibilité** | **1 461 s** | CI, même run |

**L'audit d'accessibilité consomme 76 % de la CI** — vingt-quatre minutes sur trente-deux. C'est le
prix d'un site qui grandit : il visite chaque page dans deux langues, deux modes et deux largeurs,
soit 2 148 combinaisons. US-63, déjà au backlog, le réduira à la seule PR.

**Ce que Git mesure, et ce qu'il ne mesure pas.** D'un premier commit au merge :

| Cours | Cible | Livré | Commits | Horloge (1er commit → merge) |
|---|---|---|---:|---:|
| Programmation C avancée | pages | chapitres 0 à 3 | 9, en 1 h 18 | 1 h 39 |
| Introduction au ML | decks | 9 séances | 14, en deux passes séparées de 7 h 30 | 15 h 30 |
| Structures de Données | pages | 4 séances | 2 en 8 min, puis 2 le lendemain soir | 17 h 45 |
| Introduction à l'IA | pages | 5 séances | 3, en 50 min | 1 h 21 |

Ces chiffres **ne mesurent pas la migration** : ils mesurent l'attente. Les trous entre les
commits — sept heures et demie pour le ML, une nuit pour Structures de Données — sont des
allers-retours avec le PO :
validation des textes alternatifs, de la table des encadrés, des métadonnées, des arbitrages de
conversion. Le cours d'IA, dont toutes les décisions étaient prises d'avance, a été migré en
**cinquante minutes**. Le même travail, décision par décision, prend une journée.

**La conclusion du Sprint 6 tient donc toujours, et plus nettement : la machine ne coûte rien, la
décision coûte tout.** US-58 a déplacé une partie de cette charge — le PO valide au lieu d'écrire —
et l'effet se mesure : 57 textes alternatifs pour le cours de C, 61 pour le ML, 11 pour l'IA, tous
rédigés par la chaîne et validés en bloc.

## 4. Les défauts latents révélés par un nouveau type de contenu

Un cours d'un genre nouveau ne révèle pas ses propres défauts : il révèle **ceux du site**. Douze
défauts de ce sprint étaient déjà dans du code mergé et vert, invisibles faute d'un contenu qui les
exerce.

| # | Défaut | Dormait depuis | Réveillé par | Corrigé en |
|---|---|---|---|---|
| 1 | `restaurer()` en une passe perdait les blocs imbriqués — **treize figures** remplacées par un « 5 » | US-15 | une figure dans une colonne, cours de ML | #140 |
| 2 | Reveal centre une slide **avant** le chargement des images différées | US-19 | deux figures PNG, séance 6 de ML | #140 |
| 3 | Le contrôle de débordement mesurait les **slides empilées à zéro** — 63 sur 67 | US-43, sa création | les decks de ML | #140 |
| 4 | Les **identifiants de glyphes** se répètent d'une figure à l'autre : dix-neuf figures écrivaient avec les lettres de la première | US-55 | vingt figures PDF sur une même page, cours de C | #138 |
| 5 | Quarto **fige MathJax 2.7.9** sur les présentations, qui ignore `mathtools` | US-15 | `psmallmatrix`, séance 10 de ML | #145, #146 |
| 6 | La **légende d'un tableau** est composée à 4,39:1 sur blanc, sous le seuil WCAG | toujours | les premiers tableaux légendés du site, Structures de Données | #148 |
| 7 | La **légende d'une figure**, même gris, même seuil | toujours | les premières légendes de figure, Introduction à l'IA | #150 |
| 8 | La carte d'un cours au **domaine inconnu** retombe sur une couleur illisible en mode sombre | US-57 | un cours dont le domaine attendait la réponse du PO | #148 |
| 9 | Une **liste imbriquée** cassait la conversion : le découpage sur `\item` coupait la liste intérieure en deux | US-15 | une recette numérotée, séance 3 d'IA | #150 |
| 10 | **Pandoc refuse une formule en ligne suivie d'un chiffre** : `3$\times$3` s'affichait `3$$3` | toujours | « une grille 3×3 », séance 3 d'IA | #150 |
| 11 | Les **lettres grecques disparaissaient des textes alternatifs** : « Value Iteration (=0,9) » | depuis que l'alt vient de la légende | les légendes mathématiques d'IA — et la correction répare **quatre chapitres déjà en ligne** | #150 |
| 12 | `figures_tikz` refusait un **schéma sans texte** en croyant le texte perdu en tracés | US-55 | un arbre aux nœuds vides, séance 3 d'IA | #150 |

Deux d'entre eux méritent d'être lus deux fois.

**Le onzième répare l'existant.** La table de lecture à voix haute, écrite pour l'IA, a changé
quatre chapitres déjà publiés : les séances 10 et 11 du ML et les séances 2 et 3 de Structures de
Données disaient « a = (0,5) », « 4 3 = 12 poids », « ReLU ((0,z)) », « _2 n 664 ». Un défaut que
personne n'avait vu parce que personne n'écoute un texte alternatif.

**Le septième était déjà corrigé — pour l'autre moitié.** #148 avait réparé la légende de tableau ;
la légende de figure portait le même gris, et il a fallu qu'un second cours arrive pour la voir.
Corriger un défaut ne corrige pas sa famille.

## 5. La leçon du 404

Le cours de Structures de Données est parti en ligne **sans page d'accueil**. La carte du catalogue
menait à un 404, et le TP de mise en place, commité et déclaré, n'a jamais été copié dans `_site/`.
La CI était **verte**.

Elle l'était parce que **le contrôle des liens internes tient un dossier existant pour une cible
valide**. Il existe, il tourne, et il a dit `success` sur le run 35910909262 :
`_site/cours/structures-de-donnees/` existait — il contenait `chapitres/` — sans porter
d'`index.html`. `lychee --offline` vérifie qu'un chemin existe ; il ne vérifie pas qu'il se sert.

C'est la leçon du sprint, et elle vaut au-delà des liens : **un contrôle qui vérifie l'existence
d'un chemin ne vérifie pas qu'une promesse est tenue.** `scripts/verifier_publication.py` (US-65)
fait la différence — chez lui, un dossier vaut son `index.html` —, et il y ajoute les deux autres
promesses du même genre : un dossier de `cours/` promet une page, une ressource du manifeste promet
un fichier servi.

## 6. Écarts

- **Deux migrations hors périmètre.** Structures de Données et Introduction à l'IA n'étaient pas au
  sprint : US-61 devait seulement « ouvrir » ces deux cours. Le PO a demandé la migration en cours
  de sprint. Elles représentent le plus gros du travail livré et ne comptent pour aucun point.
- **US-49 renversée.** La publication datée des corrigés, livrée au Sprint 5, est remplacée par une
  règle sans exception : aucun corrigé n'est publié **ni versionné** (#141). Trois pistes de
  résolution et un corrigé de DS étaient en ligne sous le type `tp`.
- **Deux séances non migrées.** S00 de Structures de Données n'a pas de CM — c'est une
  configuration d'environnement, et son TP est attaché au cours entier. Introduction à l'IA n'a
  pas de séance 4.
- **Les fiches de TD du ML manquaient** : sept séances sur neuf n'avaient pas la leur, alors que les
  fichiers étaient dans `_import/` (#144). Découvert par le PO, pas par un contrôle — c'est ce trou
  qu'US-65 ferme.

## 7. Blocages

- **Les sources de deux séances manquaient au début du sprint.** L'entrée PO du sprint le notait :
  S03 et S04 de Structures de Données ne contenaient qu'un `A_DEPOSER_ICI.txt`. Levé par le dépôt
  des sources en cours de sprint ; S04 est arrivée la veille de sa migration.
- **La CI dure trente-deux minutes**, dont vingt-quatre d'audit d'accessibilité. Chaque correctif
  d'un défaut d'accessibilité coûte donc une demi-heure avant d'être confirmé — et ce sprint en a
  eu trois (#148, #150). US-63 traite exactement cela.
- **Un délai de CI a dû être porté à quarante minutes** pour laisser l'audit finir (commit du
  22/09 08:47).
- **Un corrigé de TP est entré dans le dépôt** avec les figures de la séance 3 de Structures de
  Données : `figures_pdf.py` convertit *tous* les PDF d'un dossier. Aucune page ne le liait, mais la
  règle dit « ni publié ni versionné ». Sorti en #148, et le contrôle sait maintenant reconnaître
  l'abréviation `corr`.

## 8. Ce que le PO doit reprendre dans ses sources

La vérification en ligne a regardé **les 75 figures** des deux nouveaux cours, une par une. Aucune
n'est vide, aucune n'a perdu son texte, aucune n'est sans texte alternatif. Neuf défauts restent, et
ils sont **tous dans les sources**, aucun dans la chaîne.

**Structures de Données**

- *Séance 1, figure 3 (trace de la pile).* La légende verte « Pile vide à la fin → expression
  équilibrée » est posée à la hauteur des numéros d'étape et **recouvre les numéros 1, 2 et 3**.
  Dans `gen_figures_S01.py`, la légende est en `y = 0,15` et les numéros en `y = 0,2`.

**Introduction à l'IA**

- *Séance 1, figure 5 (branches de l'IA).* Le titre dit « et leur couverture dans le cursus
  **M1 IABD** ». Le sigle a été retiré des en-têtes et des dates des `.tex`, mais celui-ci est
  **dans un PDF déjà compilé**, hors de portée.
- *Séance 1, figure 3 (cycle agent-environnement).* La flèche verte « Perception » passe **sur le
  mot AGENT**.
- *Séance 1, figure 4 (types d'agents).* Le libellé « Environnements appropriés : » **chevauche la
  rangée d'étiquettes** qu'il annonce.
- *Séance 2, figure 4 (règles d'inférence).* Le symbole « donc » (∴) s'affiche en **carré vide**,
  dans les deux encadrés de forme logique. Vérifié : **le carré est déjà dans le PDF source**, ce
  n'est pas la conversion. La même police compose le ∴ correctement plus bas, à côté des pointillés.
- *Séance 2, figure 7 (raisonnement pas à pas).* Le titre « Étape 3 : Visite de (1,2) » est
  **recouvert par l'encadré rouge**.
- *Séance 3, schéma 4 (mémoire de BFS).* L'arbre déclare quatre feuilles de frontière ; **deux se
  superposent exactement** et on n'en voit que trois. `sibling distance=1.2cm` est trop petit pour
  un arbre binaire à deux niveaux. Le texte alternatif validé annonce quatre feuilles : soit la
  figure est élargie, soit la phrase est réécrite.
- *Séance 3, schéma 11 (tableau comparatif).* Le libellé « + coût g » **chevauche le cadre d'A\***.
- *Séance 6, figures matplotlib.* Aucun caractère accentué : « recompenses », « present »,
  « prevoyant », « a t=5 ». Le PO a demandé que la chaîne les corrige, comme pour Structures de
  Données.

**Un dixième constat, qui est un trou de contrôle.** `verifier_telephone.py` **ne lit pas le texte
d'une figure** : la figure de chaînage de la séance 3 de Structures de Données porte cinq numéros —
tous factices (`555`, `123 45 67`, `111 22 33`), de la même nature que les dix déjà tolérés dans les
blocs de code. C'est le même angle mort que celui des textes alternatifs, et il est traité à la
suite de ce bilan.

## 9. Propositions

Reprises des sections « Propositions » des PR du sprint.

- **Donner un identifiant de story aux deux migrations** (#148, #150), pour qu'elles comptent.
- **`figures_pdf.py` pourrait refuser un PDF dont le nom est réservé**, plutôt que de le convertir
  et de compter sur un contrôle en aval (#148).
- **Le contrôle des figures par comparaison des références de glyphes** — US-62, déjà au backlog :
  il aurait vu le défaut #4 sans qu'on ait à regarder la page.
- **L'audit d'accessibilité ciblé sur la PR** — US-63, déjà au backlog : vingt-quatre minutes sur
  trente-deux.
- **Étendre `verifier_telephone.py` au texte des figures**, comme `verifier_latex.py` l'a été aux
  textes alternatifs.
- **Refuser tout fichier de plus de 2 Mo non déclaré** dans `_import/` : un manuel sous copyright de
  5,4 Mo y dormait.
