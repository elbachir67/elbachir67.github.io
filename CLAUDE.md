# CLAUDE.md — site-perso (Dr. El Hadji Bassirou TOURÉ)

Ce fichier est ton contrat de travail. Lis-le entièrement avant toute action.

## 1. Rôles

| Rôle | Qui | Responsabilité |
|---|---|---|
| Product Owner (PO) | Bachir | Priorise, fournit le contenu, valide chaque story, merge les PR |
| Architecte / rédacteur des specs | Claude (chat) | Backlog, sprints, critères d'acceptation, ADR |
| Équipe de développement | Claude Code (toi) | Implémente les stories du sprint courant et rédige le bilan de sprint, rien d'autre |

## 2. Vision produit

Site académique personnel servant de hub central : vitrine de recherche, cours publiés
nativement en HTML (et non en PDF), publication de contenus assistée par Claude,
et, à terme, un tuteur IA par cours pour les étudiants.

## 3. Sources de vérité

- Backlog : `_specs/product-backlog.md`
- Sprint courant : `_specs/sprints/sprint-XX.md` (le numéro le plus élevé)
- Bilans de sprint : `_specs/sprints/sprint-XX-bilan.md` (rédigés par toi, voir §11)
- Décisions d'architecture : `_specs/adr/`
- Suivi d'exécution : issues GitHub + milestone du sprint

Tu n'implémentes **que** les stories du sprint courant. Toute idée hors périmètre
va dans la section « Propositions » de ta PR, jamais dans le code.

## 4. Stack (voir ADR-0001)

Quarto (site web) · Python (figures, `freeze`) · GitHub Actions (CI/CD) · GitHub Pages (hébergement).

## 5. Arborescence cible

```
/
├── _quarto.yml
├── index.qmd                  # Accueil (FR)
├── recherche/index.qmd        # Research (EN)
├── publications/              # index.qmd + publications.bib
├── enseignement/index.qmd     # Catalogue des cours
├── cours/<slug>/              # Un cours = un sous-dossier
├── blog/posts/<date-slug>/
├── cv/                        # cv-fr.pdf, cv-en.pdf
├── assets/                    # img/, css/
├── _specs/                    # Specs (ignoré par Quarto car préfixe _)
├── _freeze/                   # Résultats d'exécution (commité)
└── .github/                   # workflows/, templates
```

Pages uniquement en `.qmd`. Les `.md` ne sont pas rendus (`render` restreint dans `_quarto.yml`).

## 6. Workflow par story (GitHub Flow)

1. Lire la story et ses critères d'acceptation dans le sprint courant.
2. Vérifier la Definition of Ready. Si une ambiguïté ou une entrée PO manque : **s'arrêter et poser la question**.
3. Créer la branche `feat/US-XX-slug-court` (ou `fix/`, `docs/`, `ci/`) depuis `main` à jour.
4. Implémenter par petits commits au format Conventional Commits :
   `feat(accueil): ajoute la section affiliations (US-07)`
5. Vérifier localement : `quarto render` sans erreur ni avertissement.
6. Pousser, puis `gh pr create` en remplissant le template (story, changements, checklist DoD).
7. **STOP.** Donner au PO : résumé en 5 lignes max, lien de la PR, comment tester.
   Pas de story suivante sans validation explicite du PO.

**Corrections de specs** (backlog, sprint, ADR) : les petites corrections d'un sprint sont
regroupées dans une seule PR `docs/sprint-XX-specs`, ouverte à la première correction puis
complétée au fil du sprint, et mergée par le PO avant le bilan. Exception : une correction
qui bloque une story a sa propre PR.

**Critères vérifiables seulement après déploiement** : la PR référence l'issue avec `Refs #N`,
et non `Closes #N`, pour que le merge ne la ferme pas. Après le merge et le déploiement, faire
les vérifications en ligne et poster les preuves sur l'issue. Si tout est conforme, fermer
l'issue soi-même ; sinon, la laisser ouverte et prévenir le PO.

## 7. Règles impératives

- Jamais de commit direct sur `main`, jamais de `push --force`, jamais de merge de PR.
- **Ne jamais inventer de contenu académique** (publications, dates, titres, projets, chiffres).
  Si l'information manque : `TODO(PO): <ce qui manque>` visible dans la page et listé dans la PR.
- **Travaux non acceptés :** aucun article soumis ou en évaluation n'apparaît sur le site
  (ni titre, ni lieu, ni résumé, ni billet). Seuls les travaux listés comme publiés dans les sources
  peuvent être cités. En cas de doute : `TODO(PO)`.
- Aucun numéro de téléphone sur le site.
- **Données personnelles :** le PDF du CV du PO n'est jamais commité (il contient un numéro de téléphone).
  Le CV du site est régénéré depuis les sources.
- Aucun secret, clé ou token dans le dépôt. Secrets uniquement via GitHub Secrets.
- Aucune nouvelle dépendance sans justification dans la PR.
- Code exécutable : `execute: freeze: auto` ; le dossier `_freeze/` est commité.
- Images : texte alternatif obligatoire, poids < 300 Ko.
- Langue : contenu et messages de commit en français, sauf la page Recherche (anglais).

## 8. Definition of Ready (story)

- Format « En tant que… je veux… afin de… »
- Critères d'acceptation vérifiables
- Entrées PO disponibles (contenus, fichiers, décisions)
- Estimée en points

## 9. Definition of Done (story)

- [ ] Tous les critères d'acceptation satisfaits
- [ ] `quarto render` sans erreur ni avertissement
- [ ] CI verte sur la PR
- [ ] Rendu vérifié en largeur mobile (375 px) et desktop
- [ ] Aucun lien interne cassé
- [ ] PR liée à l'issue (`Closes #N`, ou `Refs #N` : voir §6), template rempli
- [ ] Validée par le PO, mergée, déployée et visible en ligne

## 10. Commandes utiles

```bash
quarto preview                 # aperçu local avec rechargement
quarto render                  # rendu complet
gh issue list --milestone "Sprint 1"
gh pr create --fill
```

## 11. Bilan de fin de sprint

Quand la dernière story du sprint est mergée, rédiger `_specs/sprints/sprint-XX-bilan.md`.
Le PO ne remplit aucune fiche : ce bilan remplace la revue et la rétrospective.

**Sources, exclusivement :** historique Git, PR (`gh pr list --state all`) et CI (`gh run list`).
Chaque fait cite sa source (SHA, numéro de PR ou de run). Rien d'inventé.

**Contenu :**

1. **Stories livrées** : identifiant, titre, PR, date de merge.
2. **Points** : engagés, livrés, écart.
3. **Écarts** : par rapport à l'objectif du sprint et aux critères d'acceptation
   (critère modifié par le PO, story reportée, critère non satisfait).
4. **Blocages** : ce qui a ralenti ou arrêté une story, et comment il a été levé.
5. **Propositions** : reprises des sections « Propositions » des PR du sprint.

Livraison : branche `docs/sprint-XX-bilan`, PR, puis **STOP** (comme §6, étape 7).
