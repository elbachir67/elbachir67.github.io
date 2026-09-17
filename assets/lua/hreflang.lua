-- Balises hreflang réciproques (US-36, ADR-0003).
-- Les pages françaises sont à la racine, les anglaises sous en/ : le chemin de l'une se déduit de l'autre.
-- Les pages hors périmètre bilingue (les cours) ne reçoivent pas de balise.

local HORS_PERIMETRE = { cours = true }

-- Dossiers dont le nom change d'une langue à l'autre (décision PO : /en/research/, /en/teaching/).
-- La même table figure dans scripts/verifier_bilingue.py, qui échoue si les deux divergent.
-- Le sélecteur de langue, lui, lit les balises posées ici : il n'a pas de table à tenir à jour.
local FR_VERS_EN = { recherche = "research", enseignement = "teaching" }
local EN_VERS_FR = {}
for fr, en in pairs(FR_VERS_EN) do
  EN_VERS_FR[en] = fr
end

local function traduire(chemin, correspondances)
  local premier, reste = chemin:match("^([^/]+)(/.*)$")
  if premier and correspondances[premier] then
    return correspondances[premier] .. reste
  end
  return chemin
end

local function chemin_relatif()
  local racine = quarto.project.directory
  local fichier = quarto.doc.input_file
  if racine and fichier:sub(1, #racine) == racine then
    return (fichier:sub(#racine + 2))
  end
  return fichier
end

function Pandoc(doc)
  if not quarto.doc.is_format("html:js") then
    return doc
  end
  local site = doc.meta["site-url"] or (doc.meta.website and doc.meta.website["site-url"])
  if not site then
    return doc
  end
  site = pandoc.utils.stringify(site):gsub("/$", "")

  local chemin = chemin_relatif():gsub("%.qmd$", ".html"):gsub("index%.html$", "")
  local fr, en
  if chemin:sub(1, 3) == "en/" then
    en = chemin
    fr = traduire(chemin:sub(4), EN_VERS_FR)
  else
    fr = chemin
    en = "en/" .. traduire(chemin, FR_VERS_EN)
  end
  if HORS_PERIMETRE[fr:match("^([^/]+)/") or ""] then
    return doc
  end

  quarto.doc.include_text("in-header", table.concat({
    string.format('<link rel="alternate" hreflang="fr" href="%s/%s">', site, fr),
    string.format('<link rel="alternate" hreflang="en" href="%s/%s">', site, en),
    string.format('<link rel="alternate" hreflang="x-default" href="%s/%s">', site, fr),
  }, "\n"))
  return doc
end
