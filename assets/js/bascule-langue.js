// Sélecteur de langue (US-36) : mène à la page équivalente dans l'autre langue.
// La cible est lue dans les balises hreflang de la page, posées par assets/lua/hreflang.lua : les
// correspondances d'adresses n'existent donc qu'à un seul endroit, et la CI les vérifie.
// Sans JavaScript, ou sur une page hors périmètre bilingue (les cours), le lien garde la cible écrite
// dans la configuration : l'accueil de l'autre langue.
(() => {
  const lien = document.querySelector('#quarto-header a.nav-link[rel="alternate"]');
  if (!lien) return;
  const autre = document.documentElement.lang.startsWith("fr") ? "en" : "fr";
  const equivalent = document.querySelector(`link[rel="alternate"][hreflang="${autre}"]`);
  // On ne garde que le chemin : le site se consulte aussi en local, sur un autre domaine.
  if (equivalent) lien.href = new URL(equivalent.href).pathname;
})();
