# Inventaire des sources de `_import/` (US-68)

**Relevé du 25 septembre 2026**, sur l'état de `_import/` au commit `65d6892`, **complété le
26 septembre** des arbitrages du PO (§6) et des deux corrections de source qu'il a demandées. Cette story
n'observe que : aucun import, aucune page, aucune figure n'a été produite pour l'écrire.

`_import/` est ignoré par Git (`.gitignore:8`) : rien de ce qui suit n'est versionné. Les chemins
cités sont ceux du disque du PO.

**Ce que le relevé mesure, et ce qu'il ne mesure pas.** Le bilan du Sprint 7 (§3) a mesuré que la
conversion coûte moins d'une demi-seconde par chapitre, decks ou pages rédigées confondus, et que
« la machine ne coûte rien, la décision coûte tout » : le cours d'IA, dont toutes les décisions
étaient prises d'avance, a été migré en cinquante minutes ; le ML, décision par décision, a pris
quinze heures. Les estimations ci-dessous comptent donc **des décisions du PO** — textes alternatifs,
métadonnées, arbitrages — et non des minutes de machine.

---

## 1. Vue d'ensemble

| `_import/` | Cours | Niveau | En ligne | Migrable maintenant | Format des sources | Figures à valider | Estimation |
|---|---|---|---:|---:|---|---:|---:|
| `architectures_logicielles` | Architectures Logicielles Modernes | M1 | 2 séances | **3 séances + 4 labs** | decks Beamer (CM), documents rédigés (labs) | 10 | 8 pts (US-69) |
| `frontend2` | Programmation Frontend 2 | L2, L3 | — | **7 labs** *(labs seuls)* | documents rédigés | **0** | 3 pts (US-70) |
| `frontend1` | Programmation Frontend 1 | L1 | — | **12 séances sur 15** | documents rédigés | **0** | 5 pts |
| `prc` | Programmation par Réutilisation de Composants | L2 | — | **5 CM + 9 labs** | documents rédigés | 19 *(à régénérer)* | 8 pts + 2 de chaîne |
| `Maths_ML` | Mathématiques pour le Machine Learning | M1 | — | **4 modules (+ 2 decks)** | documents rédigés **et** decks | 25, ou 61 avec les decks | 8 pts |
| `devops` | Introduction au DevOps | M1 | — | **1 lab sur 5** *(labs seuls)* | documents rédigés | 9 *(orphelines)* | 2 pts |
| `intro_IA` | Introduction à l'IA | M1 | 5 séances | rien : **cours complet** | documents rédigés | — | **tranché** |
| `ML` | Introduction au Machine Learning | M1 | 9 séances | rien : **séances 1 et 2 hors cours** | decks Beamer + notebooks | — | **tranché** |
| `DSA` | Structures de Données et Algorithmes Avancés | M1 | 4 séances | rien : **séances 5 à 7 à venir** | documents rédigés | — | **tranché** |
| `c-avance` | Programmation C avancée | L3 | 5 chapitres | rien : **complet** | documents rédigés | — | — |
| `python` | Programmation Python | L1 | 9 séances | rien : **complet** | decks Beamer + notebooks | — | — |

**Total migrable sans travail de chaîne : 27 séances**, sur cinq cours dont quatre ne sont pas encore
en ligne. Deux cours (`python`, `c-avance`) sont épuisés : tout ce que `_import/` en contient est
publié. Trois cours en ligne n'attendent rien : le PO a tranché leur cas (§6), et aucun des trois « trous » relevés au premier jet n'en était un.

**Aucun cours de `_import/` ne manque au catalogue.** Les cinq cours non publiés y figurent déjà,
au statut `a-venir` : c'est une réponse au dernier critère d'US-66 — l'inventaire ne révèle aucune
entrée à créer, seulement des entrées à corriger.

---

## 2. Cours dont les sources ne contiennent **que des labs**

Critère d'US-68 : pour ces cours, le lab tient lieu de CM et devient le contenu de la séance.

| Cours | Labs | CM | Conséquence |
|---|---:|---:|---|
| **Programmation Frontend 2** | 7 | **0** | chaque lab devient une séance ; c'est le cours entier |
| **Introduction au DevOps** | 1 sur 5 | 0 | le plan existe, un seul lab est récupérable |

Deux autres cours en comptent beaucoup sans être dans ce cas, parce qu'ils ont des CM :
**Frontend 1** (8 labs pour 3 CM) et **PRC** (9 labs pour 5 CM). Leurs labs restent des
ressources de séance, comme ceux de Structures de Données.

**US-70 : Programmation Frontend 2**, retenu par le PO sur cette recommandation. C'est le seul cours à labs seuls qui soit
complet, ses sept labs couvrent tout le cours, et il ne porte **aucune figure** — donc aucun texte
alternatif à écrire ni à valider, c'est-à-dire aucune des décisions qui ont coûté quinze heures au
ML. DevOps éprouverait la même chaîne sur un cours qui n'offrirait qu'une séance sur cinq.

---

## 3. Cours par cours

### `architectures_logicielles` — Architectures Logicielles Modernes (M1, en ligne)

Cible d'**US-69**. Le cours compte cinq séances ; deux sont en ligne.

| Séance | CM | Lab | Figures | État |
|---|---|---|---:|---|
| 1 — Du chaos aux couches | `cm1_archi_seance1.tex` (deck) | **absent** | 5 | **en ligne** (`01-du-chaos-aux-couches.qmd`) |
| 2 — L'hexagone | `cm2_archi_seance2.tex` (deck) | `lab2_hexagone.tex` dans `seance2_sources(1).zip` | 4 | **en ligne**, lab **non attaché** |
| 3 — Le monolithe modulaire | `seance3_sources/cm3_archi_seance3.tex` (deck, 15 frames) | `seance3_sources/lab3_modulith.tex` | 3 | **à migrer** |
| 4 — L'extraction d'un microservice | `seance4_sources.zip` → `cm4_archi_seance4.tex` (deck, 19 frames) | `lab4_extraction.tex` | 4 | **à migrer** |
| 5 — L'asynchrone (RabbitMQ) | `seance5_sources.zip` → `cm5_archi_seance5.tex` (deck, 18 frames) | `lab5_asynchrone.tex` | 3 | **à migrer** |

**Complet et prêt.** Les dix figures des séances 3 à 5 existent en SVG **et** en PDF, aux noms
exacts que les `.tex` appellent (`figG` à `figP`) : rien à compiler, rien à régénérer. Les séances 4
et 5 sont dans des zips, les sources de la séance 3 sont déjà déposées à plat.

**Ce qu'il faut du PO.** Aucune des dix figures ne porte de légende dans le `.tex` : les dix textes
alternatifs seront des brouillons à valider (US-58), comme pour les séances 1 et 2, dont le
manifeste enregistre cinq alt « texte du PO » sur neuf.

**Ce qui manque.** Le **lab 1** n'existe nulle part dans `_import/` — ni source, ni PDF. Les labs 2 à
5 sont des sources `.tex` sans PDF compilé : les attacher en ressource demande de les compiler, ce
que la chaîne fait déjà pour les quatre labs de Structures de Données.

**Estimation : 8 points**, conforme à US-69. Trois séances, quatre labs à compiler et attacher, dix
textes alternatifs.

### `frontend2` — Programmation Frontend 2 : frameworks (L2, L3, pas en ligne)

**Cours à labs seuls**, et complet : sept labs, aucun CM. Retenu pour **US-70**.

**Niveau tranché par le PO (26/09) : L2 et L3.** Le `README.txt` du dossier dit « L3 » ; il est
périmé, et le catalogue dit juste. À reprendre dans `cours.yml` au moment de l'import.

| Lab | Source | Lignes | Blocs de code |
|---|---|---:|---:|
| Lab 1 — Des fonctions JS à React | `labs/Lab_JS_React.tex` | 961 | 22 |
| Lab 2 — Composants, props, CSS Modules | `labs/Lab_02_Composants_Props_CSS_Modules.tex` | 942 | 19 |
| Lab 2bis — L'état React en profondeur | `labs/Lab_02bis_Etat_React.tex` | 802 | 14 |
| Lab 3 — `useEffect`, cycle de vie | `labs/Lab_03_useEffect_Cycle_Vie.tex` | 917 | 14 |
| Lab 4 — Formulaires et React Router | `labs/Lab_04_Formulaires_React_Router.tex` | 1058 | 16 |
| Lab 5 — Next.js App Router | `labs/Lab_05_NextJS_App_Router.tex` | 1629 | 24 |
| Lab 6 — API Django | `labs/Lab_06_API_Django.tex` | 918 | 19 |

Documents rédigés (`article`), chacun avec son PDF compilé : les PDF sont directement attachables en
ressource, sans compilation. **Aucune figure dans les sept labs** — donc aucun texte alternatif.

**À ne pas publier, et présent dans le dossier :**

- `evaluation/questions.json` — banque de 67 QCM d'examen ;
- `evaluation/lots_examen.txt` — la répartition nominative des 67 étudiants en quatre groupes ;
- `scripts/*.sh` — scripts de vérification de l'enseignant ; `setup_django.sh` **contient un
  identifiant et un mot de passe** de compte de démonstration.

Ces fichiers ne passent pas par l'import. La banque de QCM et les lots d'examen sont des documents
réservés à l'enseignant au sens de `CLAUDE.md` §7.

**Corrigé à la source le 26/09**, sur instruction du PO : `Lab_06_API_Django.tex` portait le sigle
**GLSI** en trois endroits — non pas en en-tête, mais comme valeur d'exemple du champ `filiere`. Les
trois sont retirées.

**Repéré pour US-70, à traiter à l'import :** trois numéros de téléphone d'exemple dorment dans les
labs — `77 123 45 67` dans `Lab_04` et `Lab_05` (un gabarit de formulaire), et `1-770-736-8031` dans
`Lab_JS_React.tex`, qui recopie les données d'exemple d'une API publique. Aucun numéro ne paraît sur
le site (`CLAUDE.md` §7) : ils seront remplacés par des numéros fictifs à l'import.

**Estimation : 3 points**, conforme à US-70. Sept séances, sept PDF à attacher, aucune figure, une
correction de source.

### `frontend1` — Programmation Frontend 1 : HTML, CSS, JavaScript (L1, pas en ligne)

Le plan (`Plan_Cours_JangAfrig.tex` §« Plan des 15 séances ») annonce quinze séances autour du projet
fil rouge *Jàng Afrig*. **Douze sont récupérables.**

| Présent | Manquant |
|---|---|
| Lab 0 (mise en route), CM1 (Le Web et HTML), Lab 1, Lab 2, CM2 (CSS), Lab 3, Lab 4, CM4 (Le Web moderne : APIs, JSON, asynchrone), Lab 8 (Fetch), Lab 9 (modes de jeu), Lab 10 (`localStorage`), séance 15 (mise en ligne) | **CM3 — JavaScript**, **Lab 5** (JS pratique), **Lab 6** (tableaux et objets), **Lab 7** (DOM et événements) |

Les quatre absents forment le bloc JavaScript, séances 7 à 10 du plan : le cours serait en ligne avec
un trou au milieu, du CSS aux APIs. Le plan et les PDF compilés de tout le reste sont là.

Documents rédigés, PDF compilés présents, **aucune figure** : c'est, avec Frontend 2, le cours le
moins coûteux en décisions de tout l'inventaire.

**Estimation : 5 points** pour les douze séances, plus la décision du PO sur le trou du bloc JS :
publier avec le trou, ou attendre les quatre documents.

### `prc` — Programmation par Réutilisation de Composants (L2, pas en ligne)

Le cours le plus complet de ceux qui ne sont pas en ligne : cinq CM et neuf labs, tous en source
`.tex` **et** en PDF compilé (`prc/pdf/`).

| CM | Labs |
|---|---|
| CM1 Pourquoi réutiliser · CM2 Le composant React · CM3 Consommer des APIs · CM4 APIs tierces · CM5 Documenter et déployer | Lab 1 Setup React/Git · Lab 2 Composants statiques · Lab 3 État et recherche · Lab 4 API Flask · Lab 5 Connecter React à Flask · Lab 6 Carte Leaflet · Lab 7 Météo et incidents · Lab 8 Docker · Lab 9 Assemblage final |

**Deux obstacles, tous deux réels :**

1. **Les 19 figures des CM sont absentes.** Les cinq CM appellent 19 fichiers PNG ; aucun n'est dans
   `_import/`. Les cinq scripts `gen_figures_cm*.py` sont là et produisent **exactement** ces 19 noms
   — vérifié un par un —, mais ils écrivent en PNG vers un chemin absolu d'une autre machine
   (`/home/claude/cmN/figures/`). Les figures du site sont des SVG : 249 des 251 figures en ligne le
   sont. Adapter les cinq scripts (chemin de sortie, `savefig` en `.svg`) est un travail de chaîne à
   part entière, à faire **à la source**, et il n'est pas couvert par une story du Sprint 8.
2. **Le sigle GLSI est dans 14 des 14 sources** — les cinq CM et neuf des labs. À corriger à la
   source avant l'import, sans quoi `scripts/verifier_non_publiable.py` échoue en CI.

Le découpage en séances est une décision du PO : rien dans `_import/` ne dit comment les cinq CM et
les neuf labs se répartissent sur le semestre.

**Estimation : 8 points** pour les cinq séances et les neuf labs — **reportés au Sprint 9** par le
PO —, **plus 2 points de chaîne** pour la régénération des figures en SVG, qui entrent au Sprint 8
sous **US-73** : la chaîne d'abord, le cours ensuite. Les 19 textes alternatifs suivront les
figures, pas avant.

**Domaine tranché par le PO (26/09) : « Programmation, Web & Mobile »**, et non plus « Génie
Logiciel & Architecture » — les neuf labs sont du React, du Flask, du Leaflet et du Docker.

**Le sigle GLSI a été retiré des quatorze sources le 26/09**, à la source, sur instruction du PO :
33 occurrences en tout, dans les pieds de page (`ESP/UCAD --- L2 GLSI`), les dates
(`L2 GLSI / DUT-INFO2`) et deux mentions en clair de `Lab_PRC08_Docker.tex`.

### `Maths_ML` — Mathématiques pour le Machine Learning (M1, pas en ligne)

Quatre modules, dans **deux formats concurrents** pour deux d'entre eux.

| Module | Document rédigé | Deck Beamer | Figures | TD |
|---|---|---|---:|---|
| Math1 — Algèbre linéaire pour le ML | `CM_S0_Math1.tex` (1877 l.) | — | 6 | `.tex` dans `S0_Math1_TD_package.zip` |
| Math2 — Calcul différentiel et optimisation | `CM_S0_Math2.tex` (1899 l.) | — | 6 | `TD_S0_Math2.tex` |
| Math3 — Probabilités | `CM_S0_Math3.tex` (2158 l.) | `SLIDES_MATH3.tex` (17 fig.) | 8 | `TD_S0_Math3.tex` |
| Math4 — Statistiques, MLE, MAP | `CM_S0_Math4.tex` (1872 l.) | `SLIDES_MATH4.tex` (19 fig.) | 5 | `TD_S0_Math4.tex` |

**Les 25 figures des quatre documents existent toutes**, en PDF, avec leurs scripts `fig_all.py`.
Attention à l'endroit : celles de Math1 et Math4 ne sont que dans `S0_Math*_package.zip`, et les deux
dernières de Math3 (`fig_07_ellipses_covariance`, `fig_08_dependances_conditionnelles`) ne sont que
dans `Math3_v5_final.zip` — le dossier `S0_Maths3/figures/` n'en contient que six sur huit. Les deux
decks ont aussi les leurs, en PDF et parfois en PNG.

**Arbitrage attendu du PO :** pour Math3 et Math4, publier le document rédigé ou le deck. Les deux
disent la même matière sous deux formes, et le site n'a jamais publié un cours dans les deux.

**À ne pas importer :** les huit `CORR_*` (corrigés des quatre TD) et `CORR_EXOS_MATH4.pdf`. Ils sont
refusés par `scripts/verifier_non_publiable.py`, et leur place n'est pas dans le dépôt.

**Estimation : 8 points** pour les quatre modules rédigés — quatre documents de près de 2 000 lignes
chacun, le plus gros volume rédigé de l'inventaire — avec 25 textes alternatifs. Les decks
ajouteraient 36 figures et donc 36 décisions de plus.

### `intro_IA` — Introduction à l'IA (M1, en ligne) — **tranché : cours complet**

Cinq séances en ligne. Les TD de quatre d'entre elles et le notebook de la première sont attachés.

**Tranché par le PO (26/09) : il n'y a pas de séance 4.** La numérotation des dossiers de
`_import/intro_IA/` ne suit pas celle des séances — `Ch04/` contient `CM_S05_IA_qui_Doute.tex`. Le
cours compte **cinq séances**, et le site les porte toutes : rien à combler, rien à signaler.

**Une suite, et une seule :** la numérotation affichée doit être **continue**, sans saut visible.
Le site affiche aujourd'hui 1, 2, 3, **5**, 6 — dans les descriptions de page (« Séance 5
d'Introduction à l'IA… ») et dans les renvois d'une séance à l'autre. Le catalogue, lui, liste les
séances par leur titre et ne montre aucun numéro. Portée mesurée : **22 occurrences dans les cinq
`.tex` de `_sources/`** (la correction se fait là, puis l'import est rejoué), deux lignes
d'`import.toml`, deux fichiers à renommer, une ressource à renommer, et les adresses des deux
dernières séances qui changent. Estimé **2 points**, hors périmètre du Sprint 8.

**Disponible et non publié, si le PO le veut :** quatre synthèses de séance (`SYNTH_S01`, `SYNTH_S02`,
`SYNTH_S03`, `SYNTH_S05`) et une fiche de référence (`REF_S01`), tous en `.tex` et en PDF. Ce sont
des documents d'étudiant, attachables en ressource comme les TD.

**À ne pas importer :** le devoir (`Ch02/devoir/`), l'examen final (`examen/`), les corrigés de TD
(`TD_S01_..._CORR.tex`, `CORR_S5A`, `CORR_S5B`) et le PDF de réponses du jeu « 4 à la suite »
(`Ch01/QPUC1/4_a_la_suite_S01_reponses.pdf`).

### `ML` — Introduction au Machine Learning (M1, en ligne) — **tranché : séances 1 et 2 hors cours**

Neuf séances en ligne (3 à 11), avec leurs neuf notebooks et neuf fiches d'exercices. `_import/ML/`
ne contient que `Seance3` à `Seance11`.

**Tranché par le PO (26/09) : les séances 1 et 2 recouvrent le cours de Programmation Python et ne
seront pas migrées.** Le cours commence à la séance 3, et c'est voulu. La page du cours le dit
déjà : « Le cours commence à la séance 3 : les deux premières recouvrent le cours de Programmation
Python, qui en est le prérequis », avec le lien vers ce cours.

**Réserve, à la demande du PO :** cette phrase n'est que sur la page du cours. Un étudiant qui
arrive **directement** sur la séance 3 — par une recherche, un lien partagé — lit « Introduction au
ML — Séance 3 » sans rien qui explique où sont les deux premières. Une phrase sur la première
diapositive de la séance 3 le dirait ; c'est du contenu, donc une décision du PO.

**À ne pas importer :** les six `CORR_EXOS_S*` qui restent dans le dossier (séances 3 et 5), déjà connus du contrôle.

### `DSA` — Structures de Données et Algorithmes Avancés (M1, en ligne) — **tranché : 5 à 7 à venir**

Quatre séances en ligne, avec leurs quatre labs, le projet P3 et le TP de mise en place. Le `README.md`
du dossier le dit lui-même : « CM et Labs des **quatre premières** séances ».

**Tranché par le PO (26/09) : les séances 5 à 7 sont à venir et seront fournies.** Le cours affiche
quatre séances pour l'instant, et **rien n'indique qu'il en manque** — c'est l'état voulu, pas un
défaut. Rien à migrer avant les nouvelles sources.

**À ne pas importer :** `Lab_S03_Tables_Hachage_corr.*` et `CORR_Lab_S04_Arbres_et_Tas.pdf`.

### `c-avance` — Programmation C avancée (L3, en ligne) — **épuisé**

Les cinq chapitres sont en ligne avec leurs dix-sept ressources (plan, CM, TD, TP). Ce qui reste dans
`_import/` n'est pas publiable : les contrôles continus et leurs corrigés (`cc/`, `ds/`), les trois
variantes de TP guidé par groupe (`tp_mémoire_guidé/`, dont les noms portent les sigles de filière) et
l'archive de l'image Docker du cours. **Rien à faire.**

### `python` — Programmation Python (L1, en ligne) — **épuisé**

Les neuf decks `SLIDES_S0` à `SLIDES_S8` et les huit notebooks sont tous en ligne. **Rien à faire.**

---

## 4. Ce que l'inventaire dit aux autres stories du sprint

**Pour US-66.** Aucune entrée n'est à créer au catalogue : les cinq cours non publiés de `_import/` y
sont déjà, au statut `a-venir`. Les doublons que la story cite sont bien réels et se lisent dans les
fichiers : `enseignement/cours.yml` décrit « Introduction à l'IA : logique mathématique et calcul
formel » et « Structures de Données & Algorithmes Avancés » alors que `cours/introduction-ia/cours.yml`
et `cours/structures-de-donnees/cours.yml` décrivent les mêmes cours, en ligne, sous les titres
« Introduction à l'IA » et « Structures de Données et Algorithmes Avancés ».

**Pour US-67.** Deux dépendances sont écrites dans les sources elles-mêmes, et non déduites :
Frontend 1 annonce « **aucun prérequis** — les technologies sont toutes enseignées dans le Lab 0 »
(`Plan_Cours_JangAfrig.tex`), et Frontend 2 part de « des fonctions JS à React », donc après le bloc
JavaScript de Frontend 1. Tout le reste du graphe est une décision du PO : aucune autre source de
`_import/` ne nomme un cours du site comme prérequis.

**Pour US-69.** Les sources des trois séances sont complètes, figures comprises. Le seul manque est le
lab 1, qui n'existe pas.

**Pour US-70.** Frontend 2, **retenu par le PO** : complet, sept séances, aucune figure.

## 5. Manques de chaîne révélés par l'inventaire

Un seul, et il est chiffré. Il est devenu **US-73** au Sprint 8 : **les figures de PRC sont en PNG
et pointent vers un chemin absolu étranger**. Les cinq scripts qui les produisent sont présents et
corrects quant aux noms ; il manque de les faire écrire des SVG au bon endroit. Estimé
**2 points**, à la source. Sans cela, les cinq CM
de PRC ne peuvent pas être migrés, ou le seraient avec dix-neuf figures manquantes.

Les neuf SVG du Lab 0 de DevOps posent une question voisine mais plus petite : elles existent et
`lab0_git.tex` **ne les appelle pas** — zéro `includegraphics` dans le document. Soit elles ont été
dessinées pour une version ultérieure du lab, soit leurs appels ont été perdus. Le PO seul peut dire
où chacune va, et dans quel ordre.

## 6. Arbitrages du PO — tranchés le 26 septembre 2026

Ce qui suit est clos. Les trois « trous » du premier relevé n'en étaient pas : le PO les a
expliqués, et la liste est ici pour qu'ils ne soient pas rouverts au prochain inventaire.

| Point | Décision | Suite |
|---|---|---|
| **Introduction à l'IA, « séance 4 »** | Il n'y a pas de séance 4 : la numérotation des dossiers de `_import/` ne suit pas celle des séances. Le cours en compte cinq, toutes en ligne. | Rien à combler, rien à signaler sur le site. La numérotation **affichée** doit être continue : 22 occurrences dans les `.tex`, deux renommages, estimé 2 pts, hors Sprint 8. |
| **Introduction au ML, séances 1 et 2** | Elles recouvrent le cours de Programmation Python et **ne seront pas migrées**. Le cours commence à la séance 3, et c'est voulu. | La page du cours le dit et renvoie à Python. Reste la question d'un étudiant qui arrive directement sur la séance 3 : décision de contenu du PO. |
| **Structures de Données, séances 5 à 7** | Elles sont **à venir** et seront fournies par le PO. | Le cours affiche quatre séances, et rien n'indique qu'il en manque. C'est l'état voulu. |
| **US-70, cours à labs seuls** | **Programmation Frontend 2**, sur la recommandation de cet inventaire. | Sept labs, aucune figure ; trois numéros de téléphone d'exemple à remplacer à l'import. |
| **PRC** | Migration **reportée au Sprint 9**. Seul son travail de chaîne entre au Sprint 8, sous **US-73**. | La capacité du Sprint 8 passe de 21 à 23 points. |
| **Programmation Frontend 2, niveau** | **L2 et L3.** Le `README.txt` du cours, qui dit « L3 », est périmé. | Le catalogue est juste ; `cours.yml` reprendra L2 et L3 à l'import (US-70). |
| **PRC, domaine** | **« Programmation, Web & Mobile »**, et non « Génie Logiciel & Architecture ». | Corrigé au catalogue. |
| **PDF publiés portant « GLSI »** | Le contrôle doit lire le texte des PDF : **US-75**, 3 pts, dans ce sprint, le contrôle d'abord. | `lab-4` et `projet-3` sont **retirés du site** — sources divergentes, le PO les reprendra (#163). `tp-1` est recompilé après correction de son encodage. |
| **Skills portant « GLSI »** | **Part du PO**, hors dépôt. | Noté dans #163. |
| **Numérotation d'Introduction à l'IA** | Continue : **US-74**, livrée. Le cours affiche 1 à 5. | Deux adresses changent ; pas de redirection (US-77 au backlog, sans sprint). |
| **Les 22 autres `.tex` d'`_import/intro_IA`** | **Laissés tels quels**, décision du PO : examens et TD circulent en PDF avec leur propre numérotation, et les renuméroter décalerait ce que les étudiants ont déjà. | Divergence assumée, notée dans #163. |
| **Sigle GLSI** | Retiré **à la source**, dès maintenant. | 33 occurrences dans les 14 sources de PRC, 3 dans `Lab_06_API_Django.tex`. `_import/` est ignoré par Git : la correction vit sur le disque du PO, pas dans une PR. |

**Un risque qui reste, et qui n'est pas dans `_import/`.** Le sigle GLSI est aussi dans les skills
qui produisent ces cours — `reutilisation-composants/SKILL.md` et `frontend-react-nextjs/SKILL.md`,
entre autres, sous `~/.claude/skills/synced/`. Tant qu'il y est, **il reviendra** au prochain
document généré, exactement comme `CLAUDE.md` §7 le prévoit. Ces fichiers sont synchronisés depuis
le compte du PO : **il les corrigera lui-même**, et c'est noté dans #163.
