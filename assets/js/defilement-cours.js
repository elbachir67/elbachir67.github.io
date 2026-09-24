// Zones défilantes d'un chapitre de cours rédigé (US-59).
//
// Un tableau de dump mémoire, un bloc de code long : plus larges qu'un téléphone, ils défilent
// horizontalement dans leur cadre. Une telle zone doit être atteignable au clavier, sans quoi un
// lecteur qui n'emploie pas la souris ne peut pas en voir la fin (WCAG 2.1.1, règle
// « scrollable-region-focusable » d'axe-core).
//
// Le réglage est **inconditionnel**, et c'est une leçon du Sprint 6 : mesurer si la zone déborde
// vraiment dépend des métriques de la police, qui diffèrent entre ma machine et le Linux de
// l'intégration continue. Un bloc tenait chez moi et débordait en CI. Quelques tabulations de plus
// sur une page de chapitre, mais jamais un tableau qu'on ne peut pas atteindre au clavier.
(() => {
  if (!document.body.classList.contains("cours-page")) return;

  const ZONES = "table, pre, div.sourceCode, .math.inline mjx-container";
  const ETIQUETTE = document.documentElement.lang === "en"
    ? "Horizontally scrollable region"
    : "Zone défilante horizontalement";

  // Le <pre> d'un bloc de code coloré est traité **comme son conteneur**, et non ignoré : les deux
  // défilent, et axe-core signale celui qui n'est pas focalisable. Deux arrêts de tabulation valent
  // mieux qu'une zone dont on ne peut pas atteindre la fin.
  const regler = () => {
    for (const zone of document.querySelectorAll(ZONES)) {
      zone.setAttribute("tabindex", "0");
      zone.setAttribute("role", "region");
      zone.setAttribute("aria-label", ETIQUETTE);
    }
  };

  regler();
  // MathJax compose dans le navigateur, **après** ce script : ses conteneurs n'existent pas encore au
  // premier passage. Une formule en ligne trop longue défile, et doit donc être atteignable elle
  // aussi — d'où un second passage une fois la composition terminée.
  if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
    window.MathJax.startup.promise.then(regler).catch(() => {});
  } else {
    window.addEventListener("load", regler);
  }
})();
