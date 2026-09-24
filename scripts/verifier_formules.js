#!/usr/bin/env node
// Échoue si une page rendue annonce des formules et n'en compose aucune.
//
//     node scripts/verifier_formules.js            # contrôle _site/
//     node scripts/verifier_formules.js chemin/    # contrôle un autre dossier rendu
//
// Pourquoi ce contrôle existe. Quarto fixe MathJax 2.7.9 pour les présentations, et rien chez lui
// ne permet d'en changer : `assets/lua/mathjax.lua` détourne la variable globale `RevealMath` pour
// charger MathJax 4 à la place. Ce détournement dépend de ce que Quarto expose cette variable et la
// lise dans son appel d'initialisation. **Si Quarto passait aux modules ES, les présentations
// perdraient leurs formules sans un mot** : le HTML resterait juste — Pandoc y écrit bien
// `<span class="math">\(…\)</span>` —, aucun contrôle de texte ne verrait rien, et le lecteur
// trouverait du LaTeX en clair sur ses slides.
//
// Aucun contrôle statique ne peut voir cela : la composition n'existe qu'après l'exécution de
// MathJax dans un navigateur. Le contrôle ouvre donc chaque page, attend, et compare deux nombres :
// ce que la **source** annonce (`span.math`, écrits par Pandoc) et ce que le **navigateur** affiche
// (`mjx-container` pour MathJax 3 et 4, `.MathJax` pour la version 2). Une page qui annonce des
// formules et n'en compose aucune est en panne.
//
// Le contrôle ne compte pas une par une : MathJax fusionne parfois plusieurs spans, et une égalité
// stricte serait un piège. C'est l'effondrement à zéro qui signe la panne.
//
// Aucune dépendance nouvelle : playwright-core pilote le Chrome déjà installé, comme l'audit
// d'accessibilité et le contrôle de débordement.

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright-core");
const { servir } = require("./serveur_local.js");

// MathJax a besoin de charger ses polices depuis le CDN avant de composer.
const ATTENTE = 6000;

function pagesAvecFormules(dossier) {
  const trouvees = [];
  (function parcourir(courant) {
    for (const entree of fs.readdirSync(courant, { withFileTypes: true })) {
      const complet = path.join(courant, entree.name);
      if (entree.isDirectory()) {
        if (entree.name !== "site_libs") parcourir(complet);
      } else if (entree.name.endsWith(".html")) {
        const html = fs.readFileSync(complet, "utf8");
        const annoncees = (html.match(/class="math (?:inline|display)"/g) || []).length;
        if (annoncees > 0) trouvees.push({ fichier: complet, annoncees });
      }
    }
  })(path.resolve(dossier));
  return trouvees.sort((a, b) => a.fichier.localeCompare(b.fichier));
}

// Exécuté dans la page : ce que le navigateur a réellement composé.
function composees() {
  return {
    mathjax4: document.querySelectorAll("mjx-container").length,
    mathjax2: document.querySelectorAll(".MathJax, .MathJax_Display").length,
    // Le TeX laissé en clair : MathJax n'est pas passé, ou il a échoué.
    restantes: document.querySelectorAll("span.math").length,
  };
}

async function main() {
  const dossier = process.argv[2] || "_site";
  if (!fs.existsSync(dossier)) {
    console.log(`Dossier introuvable : ${dossier} (lancer python3 scripts/rendre.py d'abord).`);
    return 1;
  }

  const pages = pagesAvecFormules(dossier);
  if (pages.length === 0) {
    console.log("Aucune page ne porte de formule : rien à vérifier.");
    return 0;
  }

  const site = await servir(dossier);
  const navigateur = await chromium.launch({ channel: "chrome" });
  const page = await navigateur.newPage({ viewport: { width: 1440, height: 900 } });
  let pannes = 0;
  let total = 0;

  for (const { fichier, annoncees } of pages) {
    const adresse = "/" + path.relative(path.resolve(dossier), fichier).split(path.sep).join("/");
    await page.goto(`${site.adresse}${adresse}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(ATTENTE);
    const vu = await page.evaluate(composees);
    const rendues = vu.mathjax4 + vu.mathjax2;
    total += rendues;
    if (rendues === 0) {
      console.log(`${adresse} : ${annoncees} formule(s) annoncée(s) par la source, `
        + `**aucune composée** — MathJax n'a pas tourné, et le lecteur voit du LaTeX en clair`);
      pannes += 1;
    }
  }

  await navigateur.close();
  await site.fermer();

  if (pannes) {
    console.log(`\nÉCHEC : ${pannes} page(s) annoncent des formules sans en composer aucune. `
      + "Vérifier `assets/lua/mathjax.lua` : Quarto a probablement changé la façon dont il "
      + "enregistre son greffon de mathématiques.");
    return 1;
  }
  console.log(`OK : ${total} formule(s) composée(s) sur ${pages.length} page(s) qui en annoncent.`);
  return 0;
}

main().then((code) => process.exit(code)).catch((erreur) => {
  console.error(erreur);
  process.exit(1);
});
