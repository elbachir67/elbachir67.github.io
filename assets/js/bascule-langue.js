// Sélecteur de langue (US-36) : mène à la page équivalente dans l'autre langue.
// Sans JavaScript, le lien garde la cible écrite dans la configuration : l'accueil de l'autre langue.
(() => {
  const lien = document.querySelector('#quarto-header a.nav-link[rel="alternate"]');
  if (!lien) return;
  const chemin = window.location.pathname;
  lien.href = chemin.startsWith("/en/") ? chemin.slice(3) : "/en" + chemin;
})();
