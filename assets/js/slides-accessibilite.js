// Deux défauts du menu de revealjs, corrigés au chargement des slides (US-42).
//
// Le plugin construit son menu après le rendu : son bouton est un lien sans texte, donc sans nom pour un
// lecteur d'écran, et son panneau est une zone défilable qu'on ne peut pas atteindre au clavier. Les deux
// sont signalés par axe-core (link-name, scrollable-region-focusable).
(() => {
  const corriger = () => {
    const bouton = document.querySelector(".slide-menu-button > a");
    if (bouton && !bouton.getAttribute("aria-label")) {
      bouton.setAttribute("aria-label", "Menu des slides");
    }
    for (const panneau of document.querySelectorAll(".slide-menu-panel")) {
      if (!panneau.hasAttribute("tabindex")) panneau.setAttribute("tabindex", "0");
    }
    return Boolean(bouton);
  };

  if (corriger()) return;
  // Le menu peut n'exister qu'après l'initialisation du plugin : on attend qu'il apparaisse.
  const observateur = new MutationObserver(() => {
    if (corriger()) observateur.disconnect();
  });
  observateur.observe(document.body, { childList: true, subtree: true });
})();
