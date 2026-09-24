#!/usr/bin/env node
// Quelles pages du site une PR touche-t-elle ? (US-63)
//
//     node scripts/pages_touchees.js origin/main       # liste les adresses, une par ligne
//
// L'audit d'accessibilité examine chaque page dans deux langues, deux thèmes et deux largeurs.
// À cinq cours, cela fait plus de deux mille combinaisons et vingt-quatre minutes — les trois
// quarts de la CI, et un job annulé au plafond. Sur une PR, il n'y a pas de raison d'auditer une
// page que la PR ne change pas.
//
// Encore faut-il savoir lesquelles elle change. Ce module fait la traduction : des fichiers
// modifiés vers les adresses du site rendu.
//
// **Le doute mène toujours au tout.** Une feuille de style, un filtre Lua, un profil Quarto
// touchent chaque page du site ; un fichier dont on ne sait rien aussi, par précaution. Un audit
// complet de trop coûte vingt minutes ; un audit manquant laisse passer un défaut d'accessibilité.
//
// Bibliothèques : aucune. `git` et le système de fichiers.

const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

// Ces fichiers changent le rendu de **tout** le site : il n'y a pas de sous-ensemble à auditer.
const GLOBAUX = [
  /^assets\//,                       // styles, scripts et filtres partagés
  /^_quarto.*\.ya?ml$/,              // configuration et profils de langue
  /^_extensions\//,                  // extensions Quarto
  /\.lua$/,                          // tout filtre Lua, où qu'il soit
  /^scripts\/verifier_accessibilite\.js$/,  // le contrôle lui-même
  /^scripts\/pages_touchees\.js$/,
  /^package(-lock)?\.json$/,
];
// Ces fichiers ne produisent aucune page : les ignorer n'affaiblit rien. Les sources d'un cours
// n'apparaissent pas sur le site, et le gel accompagne toujours un `.qmd` qui change avec lui.
const SANS_EFFET = [
  /^_specs\//, /^\.github\//, /^_import\//, /^cours\/[^/]+\/_sources\//,
  // Les contrôles ne produisent rien : ils lisent. Le reste de `scripts/` — l'import, le rendu —
  // peut changer une page, et tombe donc dans le cas « inconnu », qui audite tout.
  /^scripts\/verifier_[a-z_]+\.(py|js)$/, /^scripts\/serveur_local\.js$/,
  /^README/, /^CLAUDE\.md$/, /^\.gitignore$/, /^prompts\.txt$/, /^cv\/.*\.pdf$/,
];
// Le catalogue liste les cours : il change dès qu'un cours change.
const CATALOGUES = ["/enseignement/index.html", "/en/teaching/index.html"];

function fichiersModifies(base) {
  const sortie = execFileSync("git", ["diff", "--name-only", `${base}...HEAD`], { encoding: "utf8" });
  return sortie.split("\n").map((l) => l.trim()).filter(Boolean);
}

function pagesDuCours(slug, dossier) {
  const racine = path.join(dossier, "cours", slug);
  if (!fs.existsSync(racine)) return [];
  const trouvees = [];
  (function parcourir(courant) {
    for (const entree of fs.readdirSync(courant, { withFileTypes: true })) {
      const complet = path.join(courant, entree.name);
      if (entree.isDirectory()) parcourir(complet);
      else if (entree.name.endsWith(".html")) {
        trouvees.push("/" + path.relative(dossier, complet).split(path.sep).join("/"));
      }
    }
  })(racine);
  return trouvees;
}

// Un `.qmd` donne la page de même chemin ; « index.qmd » donne « index.html ».
function pageDuSource(fichier) {
  return "/" + fichier.replace(/\.qmd$/, ".html");
}

/**
 * Adresses à auditer, ou `null` quand l'audit doit être complet.
 */
function pagesTouchees(base, dossier = "_site") {
  return adressesPour(fichiersModifies(base), dossier);
}

/**
 * Traduction pure : des chemins modifiés vers les adresses du site, ou `null` pour « tout ».
 * Séparée de Git pour être éprouvable sans dépôt.
 */
function adressesPour(modifies, dossier = "_site") {
  if (modifies.length === 0) return [];

  const adresses = new Set();
  for (const fichier of modifies) {
    if (GLOBAUX.some((motif) => motif.test(fichier))) return null;
    if (SANS_EFFET.some((motif) => motif.test(fichier))) continue;

    // Le gel accompagne une page exécutée : il change ce qu'elle affiche.
    const gel = fichier.match(/^_freeze\/cours\/([^/]+)\//);
    if (gel) {
      pagesDuCours(gel[1], dossier).forEach((a) => adresses.add(a));
      continue;
    }
    if (/^_freeze\//.test(fichier)) return null;

    const cours = fichier.match(/^cours\/([^/]+)\//);
    if (cours) {
      // Une figure, une ressource ou la fiche d'un cours peuvent être citées par n'importe
      // laquelle de ses pages : on les prend toutes, et les catalogues qui l'annoncent.
      if (/\/(figures|ressources)\//.test(fichier) || fichier.endsWith("cours.yml")) {
        pagesDuCours(cours[1], dossier).forEach((a) => adresses.add(a));
        CATALOGUES.forEach((a) => adresses.add(a));
        continue;
      }
      if (fichier.endsWith(".qmd")) {
        adresses.add(pageDuSource(fichier));
        adresses.add(`/cours/${cours[1]}/index.html`);
        continue;
      }
      return null;  // fichier inconnu dans un cours : on n'invente pas
    }

    if (fichier.endsWith(".qmd")) {
      adresses.add(pageDuSource(fichier));
      continue;
    }
    if (fichier.endsWith(".bib")) {           // bibliographie : les pages de publications
      adresses.add("/publications/index.html");
      adresses.add("/en/publications/index.html");
      continue;
    }
    return null;  // tout le reste : on ne sait pas, donc on audite tout
  }

  // Une adresse dont la page n'existe pas (un `.qmd` supprimé) n'a rien à auditer.
  return [...adresses].filter((a) => fs.existsSync(path.join(dossier, a.slice(1)))).sort();
}

module.exports = { pagesTouchees, adressesPour };

if (require.main === module) {
  const base = process.argv[2] || "origin/main";
  const dossier = process.argv[3] || "_site";
  const adresses = pagesTouchees(base, dossier);
  if (adresses === null) {
    console.log("TOUTES");
  } else {
    adresses.forEach((a) => console.log(a));
  }
}
