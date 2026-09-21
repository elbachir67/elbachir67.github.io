// Zones défilantes d'un notebook rendu en page (US-50).
//
// Un bloc de code ou une sortie plus large que l'écran défile horizontalement. Une telle zone doit
// être atteignable au clavier, sans quoi un lecteur qui n'emploie pas la souris ne peut pas en voir
// la fin (WCAG 2.1.1, règle « scrollable-region-focusable » d'axe-core).
//
// Ce réglage se fait ici, et non dans le balisage, parce qu'il dépend de la **largeur de l'écran** :
// la même sortie défile sur un téléphone et tient sur un grand écran. Le script ajoute donc
// `tabindex` aux seules zones qui défilent vraiment, et le retire quand elles cessent de déborder.
(() => {
  // Ces conteneurs portent « overflow: auto » : ils défilent dès que leur contenu dépasse. Savoir
  // *s'ils* dépassent dépend de la largeur de la fenêtre et des métriques de la police — qui
  // diffèrent d'une machine à l'autre, au point qu'un bloc tenait sur mon écran et débordait en
  // intégration continue. Le réglage est donc **inconditionnel** : quelques tabulations de plus sur
  // une page de notebook, mais jamais un bloc qu'on ne peut pas atteindre au clavier.
  const ZONES = ".cell-output, .cell pre, div.sourceCode, .code-with-copy";
  const ETIQUETTE = document.documentElement.lang === "en"
    ? "Horizontally scrollable region"
    : "Zone défilante horizontalement";

  // Une page sans cellule de notebook n'est pas concernée : le script s'arrête aussitôt.
  if (!document.querySelector(".cell")) return;

  for (const zone of document.querySelectorAll(ZONES)) {
    zone.setAttribute("tabindex", "0");
    zone.setAttribute("role", "region");
    zone.setAttribute("aria-label", ETIQUETTE);
  }
})();
