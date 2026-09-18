// US-12 : reconstruit les liens email protégés produits par le shortcode {{< email >}}.
document.querySelectorAll(".email-protege[data-email]").forEach((element) => {
  const adresse = atob(element.dataset.email).split("").reverse().join("");
  let lien = element.closest("a");
  if (!lien) {
    lien = document.createElement("a");
    element.replaceWith(lien);
    lien.append(element);
  }
  lien.href = "mailto:" + adresse;
  lien.title = adresse;
});
