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

// Adresse du site, déclarée une seule fois dans _quarto.yml : la page de garde en tire l'URL de la
// séance, pour qu'un PDF reçu par messagerie ramène au cours en ligne (US-48).
function adresseDuSite() {
  const configuration = fs.readFileSync(path.join(__dirname, "..", "_quarto.yml"), "utf8");
  const trouve = configuration.match(/^site-url:\s*&site-url\s*"([^"]+)"/m);
  return trouve ? trouve[1].replace(/\/$/, "") : "";
}

// Page de garde, ajoutée au seul PDF : elle n'existe ni dans le deck ni dans la page (US-48).
// Le sceau de l'UCAD est en haut à droite, comme sur les decks Beamer du PO.
async function poserLaPageDeGarde(page, adresse, site) {
  const url = site ? site + adresse.replace(/\.html$/, ".html") : "";
  const numero = (adresse.match(/\/(\d+)-[^/]*\.html$/) || [, ""])[1];
  const dossierDuCours = adresse.replace(/\/chapitres\/[^/]*$/, "/");

  return page.evaluate(async ({ url, numero, dossierDuCours }) => {
    const texte = (selecteur) => {
      const element = document.querySelector(selecteur);
      return element ? element.textContent.replace(/\s+/g, " ").trim() : "";
    };

    // Le titre du cours vient de sa page, seule source de cette donnée.
    let cours = "";
    try {
      const reponse = await fetch(dossierDuCours);
      const html = await reponse.text();
      const arbre = new DOMParser().parseFromString(html, "text/html");
      cours = (arbre.querySelector("h1.title") || {}).textContent || "";
      cours = cours.replace(/\s+/g, " ").trim();
    } catch (erreur) { /* sans elle, la garde se passe du nom du cours */ }

    const seance = texte("#title-slide .subtitle");
    const auteur = texte("#title-slide .quarto-title-author-name");
    const affiliation = texte("#title-slide .quarto-title-affiliation");
    const date = new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });

    const premiere = document.querySelector(".reveal .slides .pdf-page");
    if (!premiere) return false;
    const style = getComputedStyle(premiere);

    const garde = document.createElement("div");
    garde.className = "pdf-page page-de-garde";
    // La garde vit hors du cadre que revealjs met à l'échelle : sans taille de base explicite, elle
    // hérite d'un corps démesuré et déborde. Elle se règle donc sur la hauteur de la page.
    const base = Math.round(parseFloat(style.height) * 0.030);
    garde.style.cssText = `width:${style.width};height:${style.height};overflow:hidden;`
      + `font-size:${base}px;`
      + "position:relative;background:#fff;box-sizing:border-box;padding:8% 9%;"
      + "display:flex;flex-direction:column;justify-content:center;"
      + "font-family:'Source Sans 3',system-ui,sans-serif;color:#1c2a33;";
    garde.innerHTML = `
      <img src="/assets/img/ucad-sceau.png" alt=""
           style="position:absolute;top:7%;right:8%;width:10%;height:auto">
      <p style="margin:0 0 .5em;font-size:1.35em;font-weight:600;color:#1F6FB5">${cours}</p>
      <h1 style="margin:0 0 .9em;font-size:2.2em;line-height:1.15;font-weight:700;max-width:78%">
        ${numero ? `Séance&nbsp;${Number(numero)}` : ""}${numero && seance ? " — " : ""}${seance}
      </h1>
      <p style="margin:0;font-size:1.25em;font-weight:600">${auteur}</p>
      <p style="margin:.2em 0 0;font-size:1em;color:#5a6b75;max-width:34em">${affiliation}</p>
      <div style="margin-top:auto;padding-top:1.4em;border-top:2px solid #1F6FB5;font-size:.95em">
        <p style="margin:0;color:#1F6FB5">${url}</p>
        <p style="margin:.15em 0 0;color:#5a6b75">Version du ${date}</p>
      </div>`;
    premiere.parentElement.insertBefore(garde, premiere);

    // Pied de page sur chaque page imprimée, la garde exceptée : de qui et de quoi parle ce PDF, et
    // où l'on en est. Le numéro de revealjs, qui ne compte que les slides, laisse la place au nôtre,
    // aligné sur la pagination du PDF — c'est celle que voit le lecteur dans sa visionneuse.
    const pages = [...document.querySelectorAll(".reveal .slides .pdf-page")];
    const rappel = [cours, numero ? `Séance\u00a0${Number(numero)}` : ""].filter(Boolean).join(" — ");
    pages.forEach((feuille, index) => {
      feuille.querySelectorAll(".slide-number, .slide-number-pdf").forEach((n) => n.remove());
      if (index === 0) return;                       // la page de garde n'en porte pas
      const pied = document.createElement("div");
      pied.className = "pied-de-page";
      pied.style.cssText = `position:absolute;left:3%;right:3%;bottom:1.6%;`
        + `font-size:${Math.round(base * 0.52)}px;`
        + "font-family:'Source Sans 3',system-ui,sans-serif;color:#5a6b75;"
        + "display:flex;justify-content:space-between;align-items:baseline;"
        + "border-top:1px solid #d8dee3;padding-top:.5em;";
      pied.innerHTML = `<span>${rappel}</span><span>${index + 1}&nbsp;/&nbsp;${pages.length}</span>`;
      feuille.appendChild(pied);
    });
    return true;
  }, { url, numero, dossierDuCours });
}

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
  const adresseSite = adresseDuSite();
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
    const posee = await poserLaPageDeGarde(page, adresse, adresseSite);
    if (!posee) {
      console.log(`   page de garde non posée pour ${adresse} : aucune page d'impression trouvée.`);
    }
    // En mode impression, revealjs dispose une .pdf-page par page du PDF : c'est le compte qui parle au
    // lecteur, et non le nombre de <section>, qui inclut les piles de section. La garde s'y ajoute.
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
