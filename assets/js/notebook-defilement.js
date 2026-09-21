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
  // La zone qui défile n'est pas toujours la même : selon le bloc, c'est le <pre>, le div que
  // Quarto met autour pour le bouton de copie, ou la sortie elle-même.
  const ZONES = ".cell-output, .cell pre, div.sourceCode, .code-with-copy";
  const ETIQUETTE = document.documentElement.lang === "en"
    ? "Horizontally scrollable region"
    : "Zone défilante horizontalement";

  // Quelques conteneurs portent « overflow: auto » en permanence : axe-core les signale dès lors,
  // que leur contenu déborde ou non. Ceux-là sont rendus atteignables une fois pour toutes.
  const TOUJOURS = ".code-with-copy";

  function ajuster() {
    for (const zone of document.querySelectorAll(ZONES)) {
      const deborde = zone.matches(TOUJOURS)
        || zone.scrollWidth > zone.clientWidth + 1;
      if (deborde) {
        zone.setAttribute("tabindex", "0");
        zone.setAttribute("role", "region");
        zone.setAttribute("aria-label", ETIQUETTE);
      } else {
        zone.removeAttribute("tabindex");
        zone.removeAttribute("role");
        zone.removeAttribute("aria-label");
      }
    }
  }

  // Une page sans cellule de notebook n'est pas concernée : le script s'arrête aussitôt.
  if (!document.querySelector(".cell")) return;

  ajuster();
  window.addEventListener("resize", ajuster);
})();
