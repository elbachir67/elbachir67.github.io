// Petit serveur de fichiers pour les contrôles et l'impression du site rendu (US-17, US-42).
//
// Les pages du site utilisent des chemins absolus (« /assets/… ») : les ouvrir depuis le disque ne
// suffirait pas. Ce serveur tient dans la bibliothèque standard de Node, sans dépendance.

const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");

const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".woff2": "font/woff2", ".pdf": "application/pdf", ".xml": "application/xml", ".txt": "text/plain" };

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

module.exports = { servir };
