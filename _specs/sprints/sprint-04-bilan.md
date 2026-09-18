# Bilan du Sprint 4 — Chaîne de publication et blog

**Objectif du sprint :** publier une séance de cours ou un article devient une commande, relue puis mergée,
et les contrôles faits à la main jusqu'ici tournent en CI.

**Période :** du commit `1aa516b` (18/09/2026 19:27 UTC, première PR du sprint) au commit `a85044e`
(18/09/2026 23:24 UTC). 10 commits sur `main`, soit un par pull request mergée : chaque PR est écrasée en un
seul commit au merge, si bien que les commits de branche ne figurent pas dans l'historique de `main`. Ce
bilan cite donc le numéro de PR et le commit correspondant sur `main`.

**Sources :** historique Git, pull requests (`gh pr list --state all`), issues de la milestone « Sprint 4 »
et exécutions GitHub Actions (`gh run list`). Chaque fait ci-dessous cite sa source.

## 1. Stories livrées

Les 8 stories du sprint sont livrées, et leurs issues sont fermées.

| Story | Titre | PR | Commit sur `main` | Merge (UTC) | Issue |
|---|---|---|---|---|---|
| US-42 | Accessibilité vérifiée en CI | #65 | `1aa516b` | 18/09 19:27 | #56 |
| US-41 | Conversion et gel vérifiés en CI | #67 | `b2434a8` | 18/09 19:42 | #57 |
| US-20 | Commande `/importer-chapitre` | #68 | `aa0d543` | 18/09 20:17 | #58 |
| US-17 | PDF d'une séance généré automatiquement | #69 | `4d9b059` | 18/09 20:52 | #59 |
| US-19 | Intégration des capsules vidéo | #70 | `9b82fdd` | 18/09 21:11 | #60 |
| US-25 | Blog : listing, catégories, RSS | #72 | `d689fbc` | 18/09 22:43 | #61 |
| US-21 | Commande `/resume` | #73 | `587e1de` | 18/09 23:11 | #62 |
| US-22 | Commande `/nouvel-article` | #74 | `62f0b28` | 18/09 23:23 | #63 |

### Pull requests hors story

| PR | Objet | Commit | Merge (UTC) |
|---|---|---|---|
| #71 | Séance 2 du cours pilote, importée par `/importer-chapitre` — la preuve d'usage réel qu'attendait US-20 | `128e26e` | 18/09 22:14 |
| #64 | Specs du sprint : `sprint-04.md`, backlog (US-44 à US-50), décisions du PO | `a85044e` | 18/09 23:24 |
| #66 | **Preuve d'échec** du contrôle d'accessibilité (contraste cassé volontairement) : **fermée sans merge**, branche supprimée | — | — |
| #55 | Mise en page des slides (centrage, taille, largeur de ligne) : mergée à 18:43, **juste avant l'ouverture du sprint**, et rattachée au Sprint 3 | `cc50ebb` | 18/09 18:43 |

## 2. Points

| | Points |
|---|---|
| Engagés (8 stories du sprint) | **23** |
| Livrés | **23** |
| Écart | **0** |

Détail : US-42 (3) + US-41 (2) + US-20 (5) + US-17 (5) + US-19 (1) + US-25 (2) + US-21 (3) + US-22 (2).

## 3. Écarts

### Critères satisfaits après coup, ou autrement

- **US-20** : le critère « testée sur une séance réelle, la PR produite étant mergeable telle quelle » ne
  pouvait pas l'être au moment de la story — le dépôt ne contenait qu'une séance, déjà importée. Comme
  `sprint-04.md` le prévoit (« si un test demande un nouveau `.tex`, la PR le demande explicitement »), la
  PR l'a demandé ; le PO a déposé les sources de la séance 2, et la commande a été déroulée pour de vrai
  dans #71. Elle s'est arrêtée d'elle-même sur trois figures sans légende, a attendu les phrases du PO, puis
  a produit une PR mergeable.
- **US-19** : le mécanisme est livré, mais **aucune capsule n'est publiée** : le PO n'a pas fourni
  d'identifiant de vidéo, et rien n'est inventé. Le champ `video` attend une ligne dans `import.toml`.
- **US-25** : le critère demandait « un premier article réel, fourni ou validé par le PO ». Aucun n'ayant
  été fourni, un article a été écrit et proposé ; le PO l'a **remplacé par son propre texte**, repris au
  caractère près. La version anglaise reste une traduction, à relire.
- **US-21** : le brouillon produit lors du test (résumé de la séance 2) **reste dans le dépôt, non publié**.
  Il porte un `TODO(PO)` là où le document ne dit rien.

### Décisions du PO pendant le sprint

- **Page de garde des PDF** : retenue, mais hors sprint — **US-48** au backlog (#64).
- **PDF dans le plan du site** : **non**, le `sitemap.xml` reste réservé aux pages HTML (#64).
- **Numéro d'exemple d'une séance** : `771112233` ressemblait à un vrai abonné sénégalais ; remplacé par
  `770000000` dans le `.tex`, l'exception du contrôle restant en place pour les cas futurs (#71).
- **Deux stories décrites et ajoutées au backlog** : **US-49** « Ressources par séance » (Must, 3 pts) et
  **US-50** « Notebooks rendus en page » (Should, 5 pts), avec leur description sous le tableau (#64).

## 4. Blocages

| Blocage | Effet | Comment il a été levé |
|---|---|---|
| **Un contrôle qui ment** : le serveur de fichiers de l'audit comparait un chemin relatif à un chemin absolu, et renvoyait 404 pour tout | L'audit « passait » en signalant partout la même absence de titre — c'est-à-dire rien | Chemin résolu une fois pour toutes ; les 404 ont disparu et les vraies violations sont apparues (#65) |
| **Auditer le mode impression** remonte les défauts de slides masquées et du menu replié | 5 violations que personne ne rencontre | Les présentations sont auditées comme les voit un visiteur : page entière, puis slide par slide (#65) |
| **Deux défauts réels, invisibles jusqu'ici** : zoom désactivé sur les présentations (`user-scalable=no`), menu du deck sans nom accessible ni accès clavier | Texte non agrandissable sur téléphone (WCAG 1.4.4) | Zoom rétabli à l'assemblage, menu corrigé par un script chargé par les slides (#65) |
| **Le listing Quarto ne sait pas mettre un lien dans une colonne** | Pas de bouton PDF par séance | La table des séances est produite par le filtre Lua, qui lit les en-têtes des chapitres (#69) |
| **Exception « téléphone » trop large** : un numéro toléré dès qu'il apparaissait dans un bloc de code **quelque part** | Un numéro en clair dans une page serait passé | Dans une page, les blocs de code sont retirés puis le reste est vérifié sans exception ; la tolérance ne sert qu'au PDF et à l'index, où la structure est perdue. Vérifié dans les deux sens (#71) |
| **Listing anglais vide** : Quarto avertit quand un listing ne trouve rien | Avertissement au rendu, interdit par la DoD | Le premier article a été traduit (#72) |
| **Catégories du blog sous le seuil de contraste** (3,5:1 en clair, 3,4:1 en sombre, texte de 11 px) | Violations axe-core | Elles reprennent la couleur du texte (#72) |
| **`draft-mode: gone` laisse une page vide** à la place du brouillon | Les contrôles de référencement et d'accessibilité échouaient sur une page sans titre | Les deux contrôles reconnaissent cette page et l'ignorent, en la comptant (#73) |

**Stabilité de la CI et du déploiement.** Sur la période : **14 exécutions de la CI, 13 en succès et 1 en
échec** — celle de #66, l'échec **voulu** qui prouve que le contrôle d'accessibilité arrête une régression
([run 35384643482](https://github.com/elbachir67/elbachir67.github.io/actions/runs/35384643482)) — et
**10 déploiements, tous en succès**.

**Ce que la CI vérifie désormais.** Trois contrôles se sont ajoutés aux quatre existants :

| Contrôle | Story | Ce qu'il empêche |
|---|---|---|
| `scripts/verifier_accessibilite.js` | US-42 | Une violation WCAG A ou AA, sur une page ou une slide, dans les deux langues, en clair comme en sombre |
| `scripts/verifier_conversion.py` | US-41 | Une page de cours qui ne correspond plus à ses sources, ou un bloc exécutable sans résultat gelé |
| PDF produits **avant** le contrôle des liens | US-17 | Un PDF de séance manquant : le lien de téléchargement serait cassé, et le contrôle des liens internes le verrait |

La CI passe d'environ une minute à deux minutes vingt : l'audit d'accessibilité en prend 68 secondes, pour
109 combinaisons — sous le budget de trois minutes fixé par la story.

## 5. Propositions

Reprises des sections « Propositions » des PR du sprint. Celles déjà devenues des stories (US-48, US-49,
US-50) ne sont pas répétées.

### Contrôles

- **Vérifier le gel comme la conversion** (#67) : le contrôle rejoue l'import, mais ne compare pas le
  contenu du gel. Une réexécution volontaire change un identifiant de cellule, ce qui rendrait la
  comparaison bruyante — à traiter si le besoin apparaît.
- **US-43 sur le script d'accessibilité** (#69) : le débordement d'une slide se mesure là où le navigateur
  est déjà piloté.
- **Signaler les contrastes « incomplets »** d'axe (#65) : MathJax et dégradés ne sont pas des violations,
  mais un rappel en fin de rapport éviterait de les redécouvrir.

### Cours

- **Page de garde des PDF** : devenue US-48.
- **Commande jumelle `/relire-chapitre`** (#68) : rejouer l'import d'une séance après correction du `.tex`
  serait une ligne de plus dans le même script.
- **Capsule dans la table des séances** (#70) : utile quand un étudiant cherche la vidéo depuis le
  catalogue, sans ouvrir le deck.
- **Shortcode `capsule` pour un autre hébergeur** (#70) : un paramètre suffirait pour Vimeo ou PeerTube.
- **Identifiant explicite de publication dans un `.tex`** (#73) : `% publication: toure-microflex` serait
  plus sûr que le rapprochement par titre.

### Blog

- **Commande `/publier`** (#74) : retirer `draft: true` après un dernier contrôle — description remplie,
  catégorie choisie, aucun `TODO(PO)` — ferait de la publication un geste unique et vérifié.
- **Catégories dans un fichier** (#74) : pour éviter « retour d'expérience » et « retours d'expérience ».
- **Traduction d'un article** (#73) : `/resume --langue en` écrit un brouillon anglais depuis un document,
  mais ne traduit pas un article existant. Une commande `/traduire` serait un autre outil.
- **Flux complet** (#72) : `feed: full` mettrait le texte entier dans le RSS, si le PO préfère que ses
  lecteurs lisent dans leur agrégateur.

### Suite

- **Sprint 5** : le tuteur IA (EP6, 22 points) est le prochain jalon de la roadmap, avec US-26 (spike et
  ADR) en tête.
- **Sans sprint** : US-05, US-38, US-39, US-40, US-43 à US-50 attendent un arbitrage du PO.
