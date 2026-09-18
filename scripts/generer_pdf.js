#!/usr/bin/env node
// Produit le PDF de chaque séance de cours, à côté de sa page (US-17).
//
//     node scripts/generer_pdf.js            # traite _site/
//     node scripts/generer_pdf.js chemin/    # traite un autre dossier rendu
//
// Le PDF est imprimé par le navigateur depuis la page elle-même, en mode « ?print-pdf » de revealjs :
// même source, même style, mêmes figures, et le texte reste sélectionnable. C'est ce que fait un lecteur
// qui imprime la présentation à la main, en une commande et sans intervention.
//
// Aucune dépendance nouvelle : playwright-core pilote le Chrome déjà installé, tous deux déjà là pour le
// contrôle d'accessibilité (US-42). decktape, l'outil habituel pour revealjs, aurait téléchargé son
// propre Chromium.
//
// Les PDF vivent dans le site rendu, pas dans le dépôt : ils sont refaits à chaque rendu, comme les pages.

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright-core");
const { servir } = require("./serveur_local.js");

// Le cadre d'une slide, en points : 960 × 540 pt, soit le 16:9 des decks.
const PAGE = { width: "960px", height: "540px" };
const LIMITE_MO = 5;

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

async function main() {
  const dossier = process.argv[2] || "_site";
  if (!fs.existsSync(dossier)) {
    console.error(`Dossier introuvable : ${dossier} (lancer scripts/rendre.py d'abord).`);
    return 1;
  }
  const decks = presentations(dossier);
  if (!decks.length) {
    console.log("Aucune présentation à imprimer.");
    return 0;
  }

  const site = await servir(dossier);
  const navigateur = await chromium.launch({ channel: "chrome" });
  const page = await navigateur.newPage({ viewport: { width: 1280, height: 720 } });
  let lourds = 0;

  for (const fichier of decks) {
    const adresse = "/" + path.relative(path.resolve(dossier), fichier).split(path.sep).join("/");
    await page.goto(`${site.adresse}${adresse}?print-pdf`, { waitUntil: "networkidle" });
    // Les figures et les formules finissent de se poser après le chargement.
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1200);
    // En mode impression, revealjs dispose une .pdf-page par page du PDF : c'est le compte qui parle au
    // lecteur, et non le nombre de <section>, qui inclut les piles de section.
    const feuilles = await page.evaluate(() => document.querySelectorAll(".reveal .pdf-page").length);

    const pdf = fichier.replace(/\.html$/, ".pdf");
    await page.pdf({ path: pdf, printBackground: true, preferCSSPageSize: false, ...PAGE,
                     margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    const mo = fs.statSync(pdf).size / 1024 / 1024;
    if (mo > LIMITE_MO) lourds += 1;
    console.log(`-> ${path.relative(process.cwd(), pdf)} (${feuilles} pages, ${mo.toFixed(1)} Mo)`);
  }

  await navigateur.close();
  await site.fermer();
  if (lourds) {
    console.log(`Attention : ${lourds} PDF dépasse(nt) ${LIMITE_MO} Mo.`);
  }
  console.log(`OK : ${decks.length} présentation(s) imprimée(s).`);
  return 0;
}

main().then((code) => process.exit(code)).catch((erreur) => {
  console.error(erreur);
  process.exit(1);
});
