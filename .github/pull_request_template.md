## Story liée

Closes #

<!-- US-XX — titre de la story (sprint N). Changement hors story : expliquer pourquoi. -->

## Changements

-

<!--
Signaler ici, le cas échéant :
- toute nouvelle dépendance, avec sa justification (CLAUDE.md §7) ;
- chaque contenu manquant marqué TODO(PO) dans les pages.
-->

## Comment tester

```bash
git switch <branche>
quarto render
quarto preview
```

<!-- Ce que le PO doit vérifier, page par page. -->

## Checklist DoD

- [ ] Tous les critères d'acceptation satisfaits
- [ ] `quarto render` sans erreur ni avertissement
- [ ] CI verte sur la PR
- [ ] Rendu vérifié en largeur mobile (375 px) et desktop
- [ ] Aucun lien interne cassé
- [ ] PR liée à l'issue (`Closes #N`), template rempli
- [ ] Validée par le PO, mergée, déployée et visible en ligne

## Propositions

<!-- Idées hors périmètre, pour le backlog. Écrire « Aucune » sinon. -->
