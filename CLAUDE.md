# CLAUDE.md — site-perso (Dr. El Hadji Bassirou TOURÉ)

Ce fichier est ton contrat de travail. Lis-le entièrement avant toute action.

## 1. Rôles

| Rôle | Qui | Responsabilité |
|---|---|---|
| Product Owner (PO) | Bachir | Priorise, fournit le contenu, valide chaque story, merge les PR |
| Architecte / rédacteur des specs | Claude (chat) | Backlog, sprints, critères d'acceptation, ADR |
| Équipe de développement | Claude Code (toi) | Implémente les stories du sprint courant, rien d'autre |

## 2. Vision produit

Site académique personnel servant de hub central : vitrine de recherche, cours publiés
nativement en HTML (et non en PDF), publication de contenus assistée par Claude,
et, à terme, un tuteur IA par cours pour les étudiants.

## 3. Sources de vérité

- Backlog : `_specs/product-backlog.md`
- Sprint courant : `_specs/sprints/sprint-XX.md` (le numéro le plus élevé)
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

## 7. Règles impératives

- Jamais de commit direct sur `main`, jamais de `push --force`, jamais de merge de PR.
- **Ne jamais inventer de contenu académique** (publications, dates, titres, projets, chiffres).
  Si l'information manque : `TODO(PO): <ce qui manque>` visible dans la page et listé dans la PR.
- Aucun numéro de téléphone sur le site.
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
- [ ] PR liée à l'issue (`Closes #N`), template rempli
- [ ] Validée par le PO, mergée, déployée et visible en ligne

## 10. Commandes utiles

```bash
quarto preview                 # aperçu local avec rechargement
quarto render                  # rendu complet
gh issue list --milestone "Sprint 1"
gh pr create --fill
```
