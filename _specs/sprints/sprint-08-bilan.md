# Bilan du Sprint 8

**Objectif du sprint :** le catalogue dit la vérité sur l'offre de cours, chaque cours sait de quels
autres il dépend, et trois cours de plus sont en ligne.

**Objectif tenu.** Le catalogue est passé de 23 cartes à 20, une par cours (#165). Six arcs de
prérequis relient les cours, et la relation inverse se calcule (#175, #176). Architectures
Logicielles a gagné trois séances (#177) et Programmation Frontend 2 est entré au site avec sept
séances (#182) : **le site est passé de six cours à sept, de 34 chapitres à 44, et de 251 figures à
261**.

Sources : historique Git, `gh pr list --state all`, `gh run list`. Chaque fait cite la sienne.

---

## 1. Stories livrées

| Story | Titre | PR | Mergée le |
|---|---|---|---|
| US-68 | Inventaire des sources de `_import/` | #162 | 26/09 00:13 |
| US-66 | Un catalogue sans doublon ni confusion | #165 | 26/09 01:38 |
| US-75 | Rien de non publiable dans un PDF non plus | #170 | 26/09 13:18 |
| US-74 | La numérotation d'Introduction à l'IA est continue | #172 | 26/09 13:18 |
| US-67 | Les cours se lient entre eux | #175, #176 | 26/09 15:16, 19:25 |
| US-69 | Architectures Logicielles, séances 3, 4 et 5 | #177, #178 | 26/09 20:51, 21:45 |
| US-78 | Les blocs de code ne sont plus lus comme des mathématiques | #181 | 26/09 22:58 |
| US-70 | Programmation Frontend 2, un cours fait de labs | #182 | 27/09 02:09 |
| US-73 | Les figures de PRC, régénérées | — | — |

**US-73 n'a pas de PR de code**, et c'est un fait à retenir : ses cinq scripts et ses dix-neuf
figures vivent dans `_import/`, que Git ignore. Sa trace est dans `_specs/inventaire-import.md`, ses
preuves sur l'issue #164. Le même cas s'était présenté pour le retrait du sigle GLSI.

**Correctifs du sprint**, tous nés d'un défaut trouvé en ligne ou en revue : #166 (bloc auteur de
Structures de Données), #169 (domaine de PRC), #171 (colonne Contenu), #173 (la figure `f5_fit` et
le renvoi vers Python), #179 (deux numéros d'exemple), #183 (le mot de passe du lab 6).

## 2. Points

| | Points |
|---|---:|
| Capacité annoncée à la composition | 21 |
| Engagés (US-66 à US-70) | 21 |
| **Ajoutés en cours de sprint par le PO** | **+10** |
| — US-73, les figures de PRC | 2 |
| — US-74, la numérotation continue | 2 |
| — US-75, le non publiable dans les PDF | 3 |
| — US-78, les blocs de code et les dollars | 3 |
| Sorti du sprint par échange (US-76 → Sprint 9) | −5 |
| **Capacité finale** | **31** |
| **Livrés** | **31** |
| **Écart** | **0** |

**Deux stories rétroactives, hors compte de ce sprint.** US-71 (Structures de Données, 5 pts) et
US-72 (Introduction à l'IA, 8 pts) ont été créées ici pour du travail livré au **Sprint 7** sans
identifiant : son bilan le proposait, le PO l'a tranché — « le compte doit dire la vérité ». Le
Sprint 7 passe ainsi de 28 à **41 points livrés pour 20 engagés**.

**US-76 n'a pas glissé faute de temps : elle a été échangée.** Quand US-70 a buté sur un défaut de
la chaîne, le PO a refusé d'ajouter au sprint clos et a sorti US-76 (5 pts) pour faire place à
US-78 (3 pts). La capacité est donc *descendue* de 33 à 31 en cours de route.

## 3. Écarts

**Aucun critère d'acceptation n'a été abandonné.** Trois ont été atteints autrement que prévu :

1. **US-68 annonçait dix textes alternatifs pour US-69 ; il y en avait sept.** Les trois figures
   « Le chemin du Lab N » portaient déjà une légende dans le `.tex` — le paragraphe sous l'image —,
   que la chaîne reprend. L'inventaire comptait les figures, pas les légendes.
2. **US-73 demandait une sortie « en SVG, et non en PNG ».** Les figures sortent dans les **deux**
   formats : les `.tex` citent `.png` et `pdflatex` ne compose pas un SVG — s'en priver rendrait les
   cinq CM de PRC incompilables. L'importeur, lui, ignore l'extension citée et cherche le SVG du
   même nom. L'écart est délibéré et dit en PR.
3. **US-70 devait attacher sept PDF ; six le sont.** Celui du lab 6 avait été compilé avant que le
   sigle GLSI soit retiré de sa source et le portait encore trois fois ; le recompiler ici donnait
   13 pages au lieu de 17, faute des polices du PO. La page de la séance, produite depuis la source
   corrigée, est propre. Le PDF suivra.

**Trois « trous de cours » relevés par l'inventaire n'en étaient pas.** Le PO les a tranchés : il
n'y a pas de séance 4 en Introduction à l'IA, les séances 1 et 2 du ML recouvrent le cours de
Python et ne seront pas migrées, et les séances 5 à 7 de Structures de Données sont à venir. Un §6
de l'inventaire les clôt, pour qu'ils ne soient pas rouverts.

## 4. Blocages

**Un seul a arrêté une story, et il a fait entrer une story de plus.** En commençant US-70, la
conversion du premier lab de Frontend 2 s'est arrêtée sur « environnement `lstlisting` non
fermé ». La cause : `${user.name}` — la façon ordinaire d'écrire un gabarit en JavaScript — contient
un `$`, que le motif des mathématiques prenait pour une formule ouverte. Elle courait jusqu'au `$`
suivant, **par-dessus le `\end{lstlisting}`**.

**Cinq des sept labs** de Frontend 2 étaient dans ce cas, trois fichiers de Frontend 1 et trois de
PRC. Le dernier critère d'US-70 demandait de signaler et d'estimer un tel manque **sans le
contourner** : la story a été arrêtée, mesurée, chiffrée à 3 points, et la branche abandonnée plutôt
que de livrer un cours amputé de cinq séances sur sept. Le PO a échangé US-76 contre US-78, qui a
levé le blocage en une PR (#181).

**Le reste n'a pas bloqué, mais a coûté.** Le sigle GLSI dans quatorze sources de PRC, les labs 2, 3
et 4 d'Architectures qui ne compilaient plus (`\usepackage[francais]{babel}`, un nom d'option que
les babel récents ne connaissent plus), deux slides qui débordaient de 10 et 21 px.

## 5. Ce que Programmation Frontend 2 a révélé — et la règle que j'en tire

Ce cours a fait échouer la CI **quatre fois de suite**, sur quatre défauts différents — runs
36278976599 et 36280994117, puis deux corrections de plus. **Aucun n'était de lui** : les cinq
défauts dormaient dans la chaîne, et aucun cours ne les avait exercés avant.

| Défaut | Dormait depuis | Corrigé par |
|---|---|---|
| Un `$` de gabarit JavaScript lu comme une formule | US-15 | US-78, #181 |
| Un `href` montré en exemple de JSX compté comme lien mort | US-65 | #182 |
| Un `id` écrit dans du code compté comme identifiant du document | US-59 | #182 |
| Un code en ligne coupé par l'accent grave de son contenu | US-15 | #182 |
| Un code en gras dans un en-tête, blanc sur blanc en mode sombre | US-59 | #182 |

Un sixième, trouvé en écrivant US-78 : le motif des mathématiques **ne respectait pas le dollar
échappé**. Le `\$` de la séance 0 de Python — le signe d'invite du shell, cité en toutes lettres —
ouvrait une formule qui courait sur tout le reste du document. Le chapitre publié n'en était pas
abîmé ; rien ne le garantissait.

C'est la leçon du Sprint 7, à la lettre : *un cours d'un genre nouveau ne révèle pas ses propres
défauts, il révèle ceux du site.*

### La règle que je me donne : la CI entière avant toute annonce

**J'ai annoncé US-70 comme complète alors que sa CI était rouge**, et je l'ai fait deux fois. La
première parce que je n'avais pas attendu son résultat ; la seconde parce que je n'avais lancé que
**huit contrôles sur treize**. Les cinq sautés — `verifier_latex`, `verifier_figures`,
`verifier_bilingue`, `verifier_formules` et l'audit d'accessibilité — portaient trois des quatre
défauts.

La règle, désormais : **avant d'annoncer qu'une PR est prête, lancer la liste entière des contrôles,
tirée de `ci.yml`, et non un sous-ensemble choisi de mémoire.** L'audit d'accessibilité coûte
trente-cinq minutes en régime complet, mais il accepte `--pages` : les pages touchées se vérifient
en secondes, et ce n'est pas une raison de le sauter.

`ci.yml` appelle **treize scripts** : `verifier_accessibilite`, `verifier_bilingue`,
`verifier_catalogue`, `verifier_conversion`, `verifier_debordement`, `verifier_figures`,
`verifier_formules`, `verifier_identifiants`, `verifier_latex`, `verifier_metadonnees`,
`verifier_non_publiable`, `verifier_publication` et `verifier_telephone` — plus le rendu lui-même,
dont tout avertissement fait échouer la CI, la vérification des liens par lychee et le contrôle de
l'email. Les huit que j'avais lancés étaient les huit dont je me souvenais.

## 6. Une seconde règle, posée par le PO

**Un mot des sources du PO ne change pas sans son accord, même pour faire passer un contrôle.** Elle
est née d'un manquement : deux numéros de téléphone d'exemple du lab 4 d'Architectures ont été
réécrits sans le lui demander, pour satisfaire `verifier_telephone.py`. Le contrôle aurait bien
échoué — `123 45 01` manque d'un chiffre la règle des sept chiffres qui se suivent —, mais la
décision ne m'appartenait pas. Le PO a choisi lui-même la forme (#179), puis a révoqué
l'autorisation générale qu'il avait donnée au Sprint 5.

La frontière est nette, et le sprint l'a éprouvée des deux côtés : **la mise en page et ce qui
empêche de compiler** se corrigent sans demander — une étiquette qui passe sous un cadre,
`[francais]` en `[french]`, une slide coupée en deux sans rien retirer. **Si le lecteur lit un mot
différent, c'est du contenu**, et cela se demande.

## 7. Ce qui reste ouvert

- **La vérification en ligne d'US-69 (#159) et d'US-70 (#160)**, qui ne se fait qu'après
  déploiement : les deux issues portent `Refs` et non `Closes`, et restent ouvertes jusque-là.
- **US-73 (#164)** attend la validation du PO.
- **Le PDF du lab 6**, que le PO recompile chez lui.
- **Quatre occurrences de `esp2025`** dans le lab 6, hors de celle que le PO a autorisé à changer
  (#183), et `setup_django.sh` qui le définit encore — hors dépôt.
- **La PR de specs #161**, qui reste ouverte jusqu'à ce bilan, comme le veut `CLAUDE.md` §6.

## 8. Propositions

1. **US-76 est la suite naturelle de ce sprint** (#174, Sprint 9). Deux faits l'appellent : les six
   PDF de Frontend 2 sont ceux que le PO a livrés, jamais recompilés ici, et rien ne peut dire
   s'ils correspondent encore à leurs sources ; et les quatre défauts de source trouvés en
   recompilant les PDF d'US-75 ne se voyaient **que** par la recompilation.
2. **Frontend 1 est le prochain cours le moins cher** : douze séances sur quinze, **aucune figure**,
   et US-78 vient de lever le seul obstacle technique — trois de ses fichiers en dépendaient.
   L'inventaire l'estime à 5 points.
3. **Le graphe des prérequis ne se voit nulle part en entier.** Chaque page dit ses deux voisins ;
   personne ne voit le cursus. Estimé 3 points, et cela ne vaut qu'une fois le graphe rempli.
4. **Rien ne garde les adresses d'hier** (US-77, au backlog sans sprint). US-74 a changé deux
   adresses ; le PO a tranché qu'aucune redirection n'était nécessaire tant que le site n'a pas de
   liens entrants. La story est là pour le jour où il en aura.
