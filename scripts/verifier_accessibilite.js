#!/usr/bin/env node
// Échoue si le site rendu contient une violation d'accessibilité WCAG A ou AA (US-42).
//
//     node scripts/verifier_accessibilite.js            # analyse _site/
//     node scripts/verifier_accessibilite.js chemin/    # analyse un autre dossier
//
// Chaque page du site est auditée par axe-core dans les deux langues (toutes les pages rendues sont
// visitées), en mode clair et sombre, en largeur mobile (375 px) et desktop (1440 px).
//
// Les séances de cours sont des présentations revealjs : une seule slide est affichée à la fois, et axe
// ne voit donc que celle-là. Le deck est audité comme le voit un visiteur : une fois pour la page entière
// (titre, langue, zoom), puis slide par slide. Auditer le mode impression, où toutes les slides sont
// visibles d'un coup, remonterait des défauts de slides masquées et du menu replié, que personne ne
// rencontre. Les slides n'ont pas de mode sombre.
//
// Le navigateur est le Chrome déjà installé (« channel: chrome ») : aucun navigateur n'est téléchargé,
// ni en local ni en CI.

const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright-core");

const AXE = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const REGLES = { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } };
const LARGEURS = [[375, 812], [1440, 900]];
const MODES = ["clair", "sombre"];
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".woff2": "font/woff2", ".pdf": "application/pdf", ".xml": "application/xml", ".txt": "text/plain" };

// --------------------------------------------------------------------------------------------------
// Site rendu
// --------------------------------------------------------------------------------------------------

function servir(dossier) {
  const racine = path.resolve(dossier);
  const serveur = http.createServer((requete, reponse) => {
    const relatif = decodeURIComponent(requete.url.split("?")[0]).replace(/^\/+/, "");
    let fichier = path.resolve(racine, relatif);
    if (fs.existsSync(fichier) && fs.statSync(fichier).isDirectory()) fichier = path.join(fichier, "index.html");
    // Le préfixe interdit de sortir du dossier rendu par un chemin remontant.
    if (!fichier.startsWith(racine) || !fs.existsSync(fichier)) {
      reponse.writeHead(404).end("introuvable");
      return;
    }
    reponse.writeHead(200, { "Content-Type": TYPES[path.extname(fichier)] || "application/octet-stream" });
    fs.createReadStream(fichier).pipe(reponse);
  });
  return new Promise((resoudre) => {
    serveur.listen(0, "127.0.0.1", () => resoudre({
      adresse: `http://127.0.0.1:${serveur.address().port}`,
      fermer: () => new Promise((fin) => serveur.close(fin)),
    }));
  });
}

function pages(dossier) {
  const trouvees = [];
  (function parcourir(courant) {
    for (const entree of fs.readdirSync(courant, { withFileTypes: true })) {
      const complet = path.join(courant, entree.name);
      if (entree.isDirectory()) {
        if (entree.name !== "site_libs") parcourir(complet);
      } else if (entree.name.endsWith(".html")) {
        const contenu = fs.readFileSync(complet, "utf8");
        trouvees.push({
          adresse: "/" + path.relative(dossier, complet).split(path.sep).join("/"),
          slides: contenu.includes('class="reveal"'),
          langue: (contenu.match(/<html[^>]*\blang="([^"]{2})/) || [null, "??"])[1],
        });
      }
    }
  })(path.resolve(dossier));
  return trouvees.sort((a, b) => a.adresse.localeCompare(b.adresse));
}

// --------------------------------------------------------------------------------------------------
// Audit
// --------------------------------------------------------------------------------------------------

// « cible » vaut « document » pour une page entière, ou « slide » pour la seule slide affichée.
async function auditer(page, cible = "page") {
  if (cible === "page") await page.addScriptTag({ content: AXE });
  return page.evaluate(async ([regles, cible]) => {
    const racine = cible === "slide" ? window.Reveal.getCurrentSlide() : document;
    const resultat = await window.axe.run(racine, regles);
    return resultat.violations.map((violation) => ({
      regle: violation.id,
      gravite: violation.impact,
      noeuds: violation.nodes.slice(0, 3).map((noeud) =>
        `${noeud.target.join(" ")} :: ${(noeud.any[0] && noeud.any[0].message) || noeud.failureSummary || ""}`
          .replace(/\s+/g, " ").slice(0, 200)),
      total: violation.nodes.length,
    }));
  }, [REGLES, cible]);
}

// Le mode suit le bouton du site, comme pour un visiteur ; il est mémorisé pour les pages suivantes.
async function regler_mode(page, mode) {
  const sombre = await page.evaluate(() => document.body.classList.contains("quarto-dark"));
  if (sombre === (mode === "sombre")) return;
  const bouton = page.locator(".quarto-color-scheme-toggle:visible").first();
  if (await bouton.count()) {
    await bouton.click();
    await page.waitForTimeout(250);
  }
}

async function main() {
  const dossier = process.argv[2] || "_site";
  if (!fs.existsSync(dossier)) {
    console.error(`Dossier introuvable : ${dossier} (lancer scripts/rendre.py d'abord).`);
    return 1;
  }
  const depart = Date.now();
  const site = await servir(dossier);
  const toutes = pages(dossier);
  const ordinaires = toutes.filter((p) => !p.slides);
  const presentations = toutes.filter((p) => p.slides);
  const navigateur = await chromium.launch({ channel: "chrome" });
  const problemes = [];
  let combinaisons = 0;

  for (const [largeur, hauteur] of LARGEURS) {
    for (const mode of MODES) {
      const contexte = await navigateur.newContext({ viewport: { width: largeur, height: hauteur } });
      const page = await contexte.newPage();
      for (const { adresse } of ordinaires) {
        await page.goto(site.adresse + adresse, { waitUntil: "networkidle" });
        await regler_mode(page, mode);
        await page.evaluate(() => document.fonts.ready);
        for (const violation of await auditer(page)) {
          problemes.push({ adresse, mode, largeur, ...violation });
        }
        combinaisons += 1;
      }
      await contexte.close();
    }
    // Les slides n'ont qu'un mode : chaque deck est audité une fois en entier, puis slide par slide.
    const contexte = await navigateur.newContext({ viewport: { width: largeur, height: hauteur } });
    const page = await contexte.newPage();
    for (const { adresse } of presentations) {
      await page.goto(site.adresse + adresse, { waitUntil: "networkidle" });
      await page.waitForTimeout(600);
      await page.addScriptTag({ content: AXE });
      for (const violation of await auditer(page, "document")) {
        problemes.push({ adresse, mode: "clair", largeur, ...violation });
      }
      const total = await page.evaluate(() => window.Reveal.getTotalSlides());
      for (let numero = 0; numero < total; numero += 1) {
        for (const violation of await auditer(page, "slide")) {
          problemes.push({ adresse: `${adresse} slide ${numero + 1}`, mode: "clair", largeur, ...violation });
        }
        await page.evaluate(() => window.Reveal.next());
        await page.waitForTimeout(90);
      }
      combinaisons += total + 1;
    }
    await contexte.close();
  }

  await navigateur.close();
  await site.fermer();
  const duree = Math.round((Date.now() - depart) / 1000);

  for (const probleme of problemes) {
    const entete = `${probleme.adresse} [${probleme.mode}, ${probleme.largeur}px] ${probleme.regle}`
      + ` (${probleme.gravite}, ${probleme.total} élément(s))`;
    if (process.env.GITHUB_ACTIONS) console.log(`::error title=Accessibilité::${entete}`);
    console.log(entete);
    for (const noeud of probleme.noeuds) console.log(`    ${noeud}`);
  }

  const langues = [...new Set(toutes.map((p) => p.langue))].sort().join(", ");
  if (problemes.length) {
    console.log(`ÉCHEC : ${problemes.length} violation(s) d'accessibilité dans ${dossier}/ `
      + `(${combinaisons} combinaisons, ${duree} s).`);
    return 1;
  }
  console.log(`OK : aucune violation WCAG A ou AA sur ${ordinaires.length} page(s) et `
    + `${presentations.length} présentation(s), en ${langues}, clair et sombre, 375 et 1440 px `
    + `(${combinaisons} combinaisons, ${duree} s).`);
  return 0;
}

main().then((code) => process.exit(code)).catch((erreur) => {
  console.error(erreur);
  process.exit(1);
});
