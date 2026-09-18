// Lien de téléchargement du PDF, sur la slide de titre (US-17).
//
// Le PDF de la séance est imprimé au rendu, à côté de sa page : son adresse est celle de la page, en
// « .pdf ». Le lien n'est ajouté que si le fichier existe — une séance rendue sans les outils Node n'a pas
// son PDF — et jamais en mode impression, où il n'aurait aucun sens.
(() => {
  if (window.location.search.includes("print-pdf")) return;

  const titre = document.querySelector(".reveal .slides section#title-slide");
  if (!titre) return;
  const pdf = window.location.pathname.replace(/\.html$/, ".pdf");

  fetch(pdf, { method: "HEAD" }).then((reponse) => {
    if (!reponse.ok) return;
    const lien = document.createElement("a");
    lien.className = "telecharger-pdf";
    lien.href = pdf;
    lien.setAttribute("download", "");
    // Pas d'icône : la police d'icônes du site n'est pas chargée dans les présentations.
    lien.textContent = "Télécharger le PDF";
    titre.appendChild(lien);
  }).catch(() => {});
})();
