# ADR-0004 — Architecture du tuteur : contexte injecté et mis en cache

**Statut :** Proposé · **Décideur :** PO · **Story :** US-26 (Sprint 5)

## Contexte

Le Sprint 5 ouvre un tuteur sur les séances du cours pilote : un étudiant pose une question, le tuteur
répond à partir du cours, sans jamais donner de corrigé. Le site est **statique et public**, hébergé sur
GitHub Pages ; l'appel au modèle passera par un service intermédiaire (US-27), parce qu'une clé d'API ne
peut pas vivre dans une page.

Trois contraintes tiennent le dessin de cette architecture :

- **le coût doit être connu d'avance**, et plafonné : le tuteur est public, n'importe qui peut consommer
  le budget ;
- **le corpus est petit** : deux séances aujourd'hui, une quinzaine à terme pour ce cours ;
- **le site doit rester utilisable sans le tuteur** : service indisponible ou plafond atteint, la page de
  la séance fonctionne normalement.

Les chiffres ci-dessous sont **mesurés sur les séances réelles du dépôt**, et reproductibles :

```bash
python3 scripts/estimer_cout_tuteur.py --plafond 10
```

| Séance | Caractères | Jetons (tokeniseur Haiku) |
|---|---|---|
| Séance 1 — Du chaos aux couches | 13 040 | ≈ 3 520 |
| Séance 2 — L'hexagone | 8 131 | ≈ 2 200 |

Une séance tient donc dans **deux à quatre mille jetons** : c'est petit. Tout le raisonnement qui suit
découle de cette mesure.

## Options évaluées

### Option A — Le contexte de la séance dans le prompt, mis en cache

À chaque question, le service envoie le texte complet de la séance, marqué comme cache. La première
question d'une session écrit le cache (1,25 × le prix d'entrée) ; les suivantes le lisent (0,1 ×).

- **Ce qui marche** : aucune infrastructure en plus ; le tuteur voit la séance entière, donc il ne rate
  pas un encadré ou un bout de code qu'une recherche aurait écarté ; le contexte est **produit au rendu**,
  donc toujours à jour (US-28).
- **Ce qu'il faut savoir** : le cache de cinq minutes couvre une session de questions, pas une journée ;
  la première question de chaque session coûte plus cher que les suivantes.

### Option B — Recherche vectorielle (RAG)

Découper les séances en extraits, les indexer par plongements, et n'envoyer au modèle que les trois ou
quatre extraits les plus proches de la question.

- **Ce qui marche** : le coût par question ne dépend plus de la taille du cours — décisif sur un corpus
  de centaines de pages.
- **Ce qui bloque ici** : il faut un modèle de plongements (donc un second fournisseur, ou un modèle
  embarqué), un index à construire au rendu et à héberger, et une étape de recherche dans le service.
  Surtout, **sur un corpus de cette taille, cela coûte plus cher** : les extraits ne bénéficient pas du
  cache, alors que la séance entière, elle, en bénéficie.

### Option C — Pas de tuteur, une FAQ statique par séance

Écrire à l'avance les questions fréquentes et leurs réponses, sans modèle.

- **Ce qui marche** : coût nul, aucune dépendance, aucune surprise.
- **Ce qui bloque** : cela ne répond pas à la question d'un étudiant à 23 h, qui est précisément l'objet
  du sprint. Option gardée comme **repli** : si le plafond est atteint, le widget renvoie à l'enseignant.

## Comparaison

Coût par question, mesuré sur la séance 1 (la plus longue), dans une session de cinq questions :

| | Haiku 4.5 | Sonnet 5 |
|---|---|---|
| **A — contexte mis en cache** | 1re question 0,659 ¢ · suivantes **0,246 ¢** · moyenne **0,329 ¢** | 1re 1,714 ¢ · suivantes 0,640 ¢ · moyenne **0,855 ¢** |
| A sans mise en cache | 0,608 ¢ | 1,582 ¢ |
| **B — recherche vectorielle** | 0,376 ¢ | 0,978 ¢ |

Trois enseignements :

1. **La mise en cache divise le coût par deux** (0,246 ¢ contre 0,608 ¢ pour une question de suite).
2. **Le RAG est plus cher que le contexte complet** sur ce corpus : 0,376 ¢ contre 0,246 ¢. La lecture de
   cache coûte 0,1 × le prix d'entrée, ce que des extraits envoyés à plein tarif ne rattrapent pas.
3. **Haiku 4.5 coûte 2,6 fois moins cher que Sonnet 5**, tokeniseur compris — les modèles postérieurs à
   Claude 4.6 découpent le même texte en environ 30 % de jetons supplémentaires.

| Critère | A — contexte + cache | B — RAG | C — FAQ statique |
|---|---|---|---|
| Coût par question | **0,246 ¢** | 0,376 ¢ | 0 |
| Infrastructure ajoutée | aucune | plongements + index + recherche | aucune |
| Le tuteur voit tout le cours | ✅ | ❌ extraits seulement | — |
| Tient quand le cours grossit | jusqu'à ~15 séances par cours | ✅ au-delà | — |
| Répond à une question nouvelle | ✅ | ✅ | ❌ |

## Décision

**Option A : le contexte de la séance, injecté et mis en cache, avec Claude Haiku 4.5.**

- **Une séance par requête**, pas le cours entier : la question est posée depuis une page de séance, et
  l'étudiant y cherche cette séance-là. Le contexte reste sous 4 000 jetons et le cache sert à plein.
- **Haiku 4.5** parce que la tâche est bornée : répondre à partir d'un texte fourni, en français, en
  quelques phrases, sans corrigé. Ce n'est pas une tâche de raisonnement long. Si les questions pièges
  d'US-30 montrent que la posture socratique tient mal, **passer à Sonnet 5 est un changement de
  variable** — le plafond achètera alors 2,6 fois moins de questions.
- **Cache de cinq minutes**, pas d'une heure : une session d'étudiant dure quelques minutes, et l'écriture
  d'un cache d'une heure coûte 2 × l'entrée au lieu de 1,25 ×.
- **Le RAG est écarté aujourd'hui, pas pour toujours** : le jour où un cours dépassera une quinzaine de
  séances et où l'on voudra que le tuteur cherche dans tout le cours, cet ADR sera à rouvrir.

### Ce que le plafond achète

| Plafond mensuel | Haiku 4.5 | Sonnet 5 |
|---|---|---|
| 5 $ | ≈ 1 500 questions | ≈ 580 |
| **10 $** | **≈ 3 040 questions** (≈ 100 par jour) | ≈ 1 170 |
| 20 $ | ≈ 6 080 questions | ≈ 2 340 |
| 50 $ | ≈ 15 200 questions | ≈ 5 850 |

À comparer à l'usage attendu :

| Promotion | 10 questions par étudiant et par mois | Coût (Haiku 4.5) |
|---|---|---|
| 20 étudiants | 200 questions | 0,66 $ |
| 40 étudiants | 400 questions | 1,32 $ |
| 80 étudiants | 800 questions | 2,63 $ |

**Proposition au PO : un plafond de 10 $ par mois**, soit environ 3 000 questions — sept fois ce qu'une
promotion de 40 étudiants consommerait à dix questions chacun. La marge n'est pas du luxe : elle absorbe
la veille d'examen, et surtout elle laisse le temps de voir venir un abus sans couper le service en
pleine séance. Le PO tranche dans la PR ; tout le dimensionnement d'US-30 en découle.

## Stratégie anti-abus

Le tuteur est public : sans garde-fous, un lien partagé suffit à vider le budget. Quatre lignes de
défense, de la plus douce à la plus brutale, à mettre en œuvre en US-27 et US-30 :

1. **Code d'accès** (US-27) : donné en amphi, vérifié par le service contre un secret, échangé contre un
   jeton de session de durée limitée. Il écarte le passant, pas l'étudiant qui partage son code.
2. **Quotas par code** : un nombre de questions par session et par jour. Ils répartissent l'usage sans
   arbitrer le budget.
3. **Plafond global quotidien**, aligné sur le plafond mensuel — avec 10 $ par mois, environ **0,35 $ par
   jour**, soit une centaine de questions. Il **prime sur tout le reste** : atteint, le tuteur répond
   qu'il est indisponible jusqu'au lendemain, et la page reste intacte.
4. **Interrupteur** : une variable du service désactive le tuteur immédiatement, sans redéploiement du
   site.

S'y ajoutent des limites de forme, qui coûtent peu et évitent les abus les plus simples : longueur
maximale d'une question, limitation par adresse IP au niveau de Cloudflare, refus de toute tentative de
fixer le modèle ou le prompt système depuis la page, et refus des questions manifestement hors cours.

**Ce que ces défenses ne couvrent pas**, et qu'il faut dire : un étudiant qui diffuse le code à un forum
public fera atteindre le plafond quotidien. Le service tiendra — c'est le rôle du plafond global — mais le
tuteur sera indisponible pour les autres ce jour-là. La parade est de changer le code, en une commande
(US-27).

## Conséquences

- (+) **Aucune infrastructure nouvelle** : pas d'index vectoriel, pas de second fournisseur, pas de base.
  Le contexte est un fichier produit au rendu, comme les PDF des séances.
- (+) **Le coût est connu d'avance** et mesurable : le script d'estimation vit dans le dépôt et sera
  rejoué quand le contexte réel existera (US-28).
- (+) **Le tuteur voit la séance entière** : aucun encadré, aucun bout de code n'échappe à sa lecture.
- (−) **Le coût croît avec la taille de la séance.** Une séance deux fois plus longue coûte environ deux
  fois plus cher par question. Le seuil de bascule vers le RAG se mesurera avec le script, pas au jugé.
- (−) **La première question d'une session coûte 2,7 fois les suivantes** (écriture du cache). Un usage
  fait d'une seule question par visiteur est le cas le plus cher ; c'est aussi le cas le plus probable
  hors révisions.
- (−) **Le tuteur ne sait rien des autres séances** : une question qui relie deux séances recevra une
  réponse partielle. C'est un choix, réversible en envoyant deux contextes — au prix de deux fois le coût.
- (−) **Dépendance à un fournisseur** : le service parle à l'API d'Anthropic. Le site, lui, n'en dépend
  pas : sans tuteur, il fonctionne.

## Ce que cet ADR ne décide pas

- Le **plafond mensuel** : proposé à 10 $, tranché par le PO.
- Le **prompt système** et la posture socratique : US-30, où il sera versionné et relu.
- La **forme du contexte** (titres, encadrés, code, légendes) : US-28, qui le produira depuis les sources.
- L'**hébergement du service** : Cloudflare Worker, déjà fixé par le sprint (US-27, US-31).
