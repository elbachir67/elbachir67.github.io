# Tuteur IA du cours pilote — spécification en attente de planification

> **Reporté — décision du PO, 19/09/2026.** Le tuteur IA (EP6) attend une planification : US-27, US-28,
> US-29, US-30 et US-31 sont au backlog, sans sprint, telles qu'elles sont décrites ici. Ce document a
> d'abord été le sprint 5 ; il est conservé **mot pour mot** comme spécification de référence, le Sprint 5
> ayant reçu une autre composition.
>
> **US-26 a été livrée** et n'est pas à refaire : [ADR-0004](../adr/0004-architecture-tuteur.md) **reste
> valable**. Il fixe l'architecture (contexte de la séance injecté et mis en cache, Haiku 4.5), le coût
> par question mesuré sur les séances réelles, et la stratégie anti-abus. Le seul point resté ouvert est
> le **plafond mensuel**, proposé à 10 $ : il se tranchera quand le tuteur reviendra.
>
> Le reste de ce document est celui du sprint d'origine, sans modification.

**Objectif :** sur les séances du cours pilote, un étudiant peut poser une question et obtenir
une réponse ancrée dans le cours, encadrée, à un coût maîtrisé et connu d'avance.
**Capacité :** 22 points

## Entrées PO

- [ ] Clé API Anthropic (jamais commitée : secret Cloudflare et GitHub Secret).
- [ ] Compte Cloudflare pour le Worker.
- [ ] **Plafond de dépense mensuel**, en dollars : c'est la donnée qui dimensionne tous les garde-fous.
- [ ] **Code d'accès** du cours pilote pour le semestre en cours (choisi par le PO, communiqué en amphi).

## Principes non négociables

- **Accès par code, pas par compte.** Le tuteur s'ouvre avec un code donné en amphi, valable un
  semestre et changeable en une commande. Aucune inscription, aucun email, aucun mot de passe,
  aucune base d'utilisateurs : le site reste statique et sans données personnelles.
- **Activé cours par cours.** Un champ dans `cours.yml` décide si un cours a un tuteur ; par défaut, non.
- Le tuteur **ne donne jamais** le corrigé d'un exercice, d'un TD ou d'un examen : il guide par questions.
- Il répond **uniquement** à partir du contenu du cours ; hors sujet, il le dit et renvoie à l'enseignant.
- Il **dit qu'il est une IA** et peut se tromper ; l'enseignant reste la référence.
- **Aucune donnée personnelle** n'est demandée ni stockée dans ce sprint (la journalisation est US-32).
- Le site reste **utilisable sans le tuteur** : si le service est indisponible ou le plafond atteint, la page fonctionne normalement.

## Ordre d'exécution

US-26 → US-27 → US-31 → US-28 → US-30 → US-29.

---

### US-26 — Spike + ADR-0004 : architecture du tuteur (2 pts)

En tant que PO, je veux une décision documentée avant d'écrire le service,
afin de ne pas découvrir la facture ou une faille après coup.

- [ ] Options comparées : contenu du cours injecté dans le contexte avec mise en cache des prompts, contre recherche vectorielle (RAG). Critères : coût par question, complexité, qualité attendue sur un corpus de deux séances.
- [ ] Modèle choisi et justifié (famille Haiku ou Sonnet), avec le **coût estimé par question** et le nombre de questions que permet le plafond mensuel.
- [ ] Stratégie anti-abus décidée : le tuteur est public, n'importe qui peut consommer le budget.
- [ ] `_specs/adr/0004-architecture-tuteur.md` : contexte, options, décision, conséquences, coûts.
- [ ] Livré en PR de specs, sans code de service.

### US-27 — Service proxy sécurisé (5 pts)

En tant que PO, je veux que la clé API ne soit jamais exposée,
afin qu'un site statique public puisse appeler un modèle sans risque.

- [ ] Cloudflare Worker dans `worker/`, appelant l'API Anthropic ; la clé vient d'un secret Cloudflare, jamais du dépôt.
- [ ] CORS limité au domaine du site ; toute autre origine reçoit un refus.
- [ ] Code d'accès exigé avant la première question : le Worker le vérifie contre un secret Cloudflare et renvoie un jeton de session de durée limitée ; le code n'est jamais dans le dépôt ni dans le site.
- [ ] Changer le code se fait en une commande, sans redéploiement du site ; les sessions en cours expirent normalement.
- [ ] Le Worker n'accepte que les champs attendus (question, identifiant de séance) et rejette toute tentative de fixer le prompt système ou le modèle depuis le client.
- [ ] Réponse en flux si possible ; sinon délai maximal fixé et message d'attente côté page.
- [ ] Erreurs distinctes et lisibles : service indisponible, quota atteint, question refusée.
- [ ] Un contrôle de la CI échoue si une chaîne ressemblant à une clé API apparaît dans le dépôt.

### US-31 — Déploiement continu du Worker (2 pts)

En tant que PO, je veux que le service se déploie comme le site,
afin de ne pas avoir de manipulation manuelle à retenir.

- [ ] Workflow déclenché sur les changements de `worker/**`, déploiement par wrangler, jeton en GitHub Secret.
- [ ] Le déploiement du site et celui du Worker sont indépendants : un échec de l'un ne bloque pas l'autre.
- [ ] Environnement de test séparé de la production, ou justification de son absence.

### US-28 — Contexte du cours (5 pts)

En tant qu'étudiant, je veux que le tuteur parle de ma séance,
afin de ne pas recevoir des généralités trouvées ailleurs.

- [ ] Le rendu produit, pour chaque séance, un fichier de contexte (titre, plan, texte des slides, encadrés, code, légendes des figures) consommé par le Worker.
- [ ] Le contexte est construit depuis les sources du site : aucune ressaisie, et il se met à jour au déploiement.
- [ ] La taille du contexte et le coût associé sont mesurés et indiqués dans la PR.
- [ ] La mise en cache des prompts est activée et son effet sur le coût est mesuré.
- [ ] Les corrigés éventuels sont exclus du contexte, par construction.

### US-30 — Garde-fous pédagogiques et budgétaires (5 pts)

En tant qu'enseignant, je veux que le tuteur aide sans faire le travail à la place,
et qu'il ne puisse pas dépasser mon budget.

- [ ] Prompt système : posture socratique, réponses courtes, en français, ancrées dans le contexte fourni, renvoi à l'enseignant hors sujet. Le prompt est versionné et relu par le PO.
- [ ] Refus des demandes de corrigé, reformulées en questions guidantes ; testé sur une liste d'au moins dix questions pièges, jointe à la PR.
- [ ] Limite de questions par session et par jour, par code d'accès, plus un **plafond global quotidien** aligné sur le budget mensuel ; au-delà, message clair et site intact.
- [ ] Un code diffusé largement ne peut pas faire exploser le budget : le plafond global prime sur tout le reste.
- [ ] Compteur de consommation consultable par le PO (page ou commande), sans données personnelles.
- [ ] Le Worker refuse les questions manifestement hors cours et les tentatives de détourner le prompt.

### US-29 — Widget de discussion (3 pts)

En tant qu'étudiant sur mon téléphone, je veux poser ma question sans quitter la séance,
afin d'obtenir une explication au moment où je bloque.

- [ ] Widget présent uniquement sur les pages de séance des cours dont `cours.yml` active le tuteur ; absent partout ailleurs.
- [ ] Première ouverture : demande du code d'accès, avec un message expliquant où l'obtenir (en cours). Code refusé : message clair, sans blocage de la page.
- [ ] Utilisable au clavier, annoncé aux lecteurs d'écran, lisible en mode clair et sombre, correct à 375 px ; axe-core sans violation.
- [ ] Mention visible : réponses produites par une IA, pouvant contenir des erreurs, l'enseignant reste la référence.
- [ ] Aucun appel réseau avant que l'étudiant n'ouvre le widget.
- [ ] La conversation reste dans la page : rien n'est stocké côté serveur dans ce sprint.
- [ ] Vérification en ligne après déploiement (règle `Refs #N`).

---

## Hors périmètre, au backlog

Journalisation anonymisée des questions et consentement (US-32), tableau de bord enseignant (US-33),
extension du tuteur à un second cours, et rapprochement éventuel avec IA4Nieup lorsque la plateforme
sera opérationnelle (le tuteur du site reste volontairement léger et sans comptes).

## Bilan

Rédigé par Claude Code en fin du sprint qui portera ces stories (CLAUDE.md §11).
