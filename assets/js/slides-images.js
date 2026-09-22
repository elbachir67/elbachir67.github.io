// Une image matricielle chargée après coup laisse reveal mal centrer sa slide.
//
// Reveal ne charge une image qu'au moment où sa slide paraît (`data-src`), et il calcule la
// position verticale de la slide **avant** que les pixels arrivent. La slide grandit ensuite sans
// que la position soit refaite : sur la séance 6 du cours d'Introduction au ML, la slide restait
// posée à 156 unités du haut alors que son contenu en mesurait 539, et son bas sortait du cadre
// de 700. Le lecteur voyait la dernière phrase coupée.
//
// Deux gestes, dans cet ordre : charger les images tout de suite, puis redemander la mise en page
// à chaque image qui arrive. `Reveal.layout()` recentre les slides ; l'appeler plusieurs fois est
// sans effet de bord.

(function () {
  function remettreEnPage() {
    if (window.Reveal && typeof Reveal.layout === "function") {
      Reveal.layout();
    }
  }

  function preparer() {
    document.querySelectorAll("img[data-src]").forEach(function (image) {
      image.src = image.getAttribute("data-src");
      image.removeAttribute("data-src");
    });
    document.querySelectorAll("img").forEach(function (image) {
      if (image.complete) return;
      image.addEventListener("load", remettreEnPage, { once: true });
      image.addEventListener("error", remettreEnPage, { once: true });
    });
    remettreEnPage();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", preparer);
  } else {
    preparer();
  }
})();
