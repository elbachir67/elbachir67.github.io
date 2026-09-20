#!/usr/bin/env node
// Signale les slides qui dépassent la hauteur du cadre (US-43).
//
//     node scripts/verifier_debordement.js            # contrôle _site/
//     node scripts/verifier_debordement.js chemin/    # contrôle un autre dossier rendu
//
// Une slide trop chargée ne se voit pas au rendu : revealjs la laisse défiler (« scrollable »), et
// l'enseignant la découvre en amphi, quand la dernière ligne est sous le bord de l'écran. Le contrôle
// mesure chaque slide comme si elle était affichée, et échoue en nommant celles qui débordent.
//
// Le cadre fait 1050 × 700 unités (assets/css/slides.scss) : c'est la hauteur du conteneur .slides,
// et non celle de la fenêtre, qui fait foi — revealjs met l'ensemble à l'échelle.
//
// Aucune dépendance nouvelle : playwright-core pilote le Chrome déjà installé, comme l'audit
// d'accessibilité et l'impression des PDF.

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright-core");
const { servir } = require("./serveur_local.js");

// Quelques pixels de battement : une slide qui affleure le bord n'est pas un défaut, et les polices
// ne se posent pas au pixel près d'une machine à l'autre.
const BATTEMENT = 8;

function presentations(dossier) {
  const trouvees = [];
  (function parcourir(courant) {
    for (const entree of fs.readdirSync(courant, { withFileTypes: true })) {
      const complet = path.join(courant, entree.name);
      if (entree.isDirectory()) {
        if (entree.name !== "site_libs") parcourir(complet);
      } else if (entree.name.endsWith(".html")
                 && fs.readFileSync(complet, "utf8").includes('class="reveal"')) {
        trouvees.push(complet);
      }
    }
  })(path.resolve(dossier));
  return trouvees.sort();
}

// Mesure exécutée dans la page : chaque slide est affichée le temps d'être mesurée, puis remise
// comme elle était. Invisible pour qui regarde, et sans effet sur le fichier rendu.
function mesurer(battement) {
  const cadre = document.querySelector(".reveal .slides");
  const hauteur = cadre.offsetHeight;
  const trop = [];
  [...cadre.querySelectorAll(":scope > section")].forEach((section, index) => {
    const empilees = section.querySelectorAll(":scope > section");
    const cibles = empilees.length ? [...empilees] : [section];
    cibles.forEach((slide) => {
      const affichage = slide.style.display;
      const visibilite = slide.style.visibility;
      slide.style.display = "block";
      slide.style.visibility = "hidden";
      // Le contenu peut dépasser sans que la section grandisse : on regarde aussi ses enfants.
      const mesure = Math.max(slide.scrollHeight,
        ...[...slide.children].map((enfant) => enfant.scrollHeight || 0));
      slide.style.display = affichage;
      slide.style.visibility = visibilite;
      if (mesure > hauteur + battement) {
        const titre = slide.querySelector("h1, h2, h3");
        trop.push({
          numero: index + 1,
          titre: (titre ? titre.textContent : "(sans titre)").replace(/\s+/g, " ").trim(),
          mesure, hauteur,
        });
      }
    });
  });
  return { trop, hauteur, slides: cadre.querySelectorAll("section").length };
}

async function main() {
  const dossier = process.argv[2] || "_site";
  if (!fs.existsSync(dossier)) {
    console.error(`Dossier introuvable : ${dossier} (lancer scripts/rendre.py d'abord).`);
    return 1;
  }
  const decks = presentations(dossier);
  if (!decks.length) {
    console.log("Aucune présentation à contrôler.");
    return 0;
  }

  const site = await servir(dossier);
  const navigateur = await chromium.launch({ channel: "chrome" });
  const page = await navigateur.newPage({ viewport: { width: 1440, height: 900 } });
  let debordements = 0;
  let slides = 0;

  for (const fichier of decks) {
    const adresse = "/" + path.relative(path.resolve(dossier), fichier).split(path.sep).join("/");
    await page.goto(`${site.adresse}${adresse}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(700);
    const resultat = await page.evaluate(mesurer, BATTEMENT);
    slides += resultat.slides;
    for (const slide of resultat.trop) {
      console.log(`${adresse} slide ${slide.numero} « ${slide.titre} » : `
        + `${slide.mesure} px pour un cadre de ${slide.hauteur} px `
        + `(${slide.mesure - slide.hauteur} px de trop)`);
      debordements += 1;
    }
  }

  await navigateur.close();
  await site.fermer();

  if (debordements) {
    console.log(`\nÉCHEC : ${debordements} slide(s) dépassent le cadre. Alléger la slide dans le `
      + "`.tex` — c'est une décision pédagogique, pas un réglage — puis rejouer l'import.");
    return 1;
  }
  console.log(`OK : ${slides} slide(s) de ${decks.length} présentation(s) tiennent dans le cadre.`);
  return 0;
}

main().then((code) => process.exit(code)).catch((erreur) => {
  console.error(erreur);
  process.exit(1);
});
