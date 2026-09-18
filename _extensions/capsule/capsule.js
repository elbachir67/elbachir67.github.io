// Chargement différé des capsules vidéo (US-19) : l'iframe n'est créée qu'au clic.
(() => {
  const lire = (bouton) => {
    const figure = bouton.closest(".capsule");
    const titre = bouton.querySelector(".capsule-titre")?.textContent?.trim() || "Capsule vidéo";
    const cadre = document.createElement("iframe");
    // youtube-nocookie.com : pas de cookie de suivi tant que la vidéo n'est pas lancée.
    cadre.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(bouton.dataset.video)}?autoplay=1&rel=0`;
    cadre.title = titre;
    cadre.loading = "lazy";
    cadre.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
    cadre.allowFullscreen = true;
    figure.replaceChild(cadre, bouton);
    cadre.focus();
  };

  document.addEventListener("click", (evenement) => {
    const bouton = evenement.target.closest(".capsule-declencheur");
    if (bouton) lire(bouton);
  });
})();
