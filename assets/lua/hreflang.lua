-- Balises hreflang réciproques (US-36, ADR-0003).
-- Les pages françaises sont à la racine, les anglaises sous en/ : le chemin de l'une se déduit de l'autre.
-- Les pages hors périmètre bilingue (les cours) ne reçoivent pas de balise.

local HORS_PERIMETRE = { cours = true }

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
    en, fr = chemin, chemin:sub(4)
  else
    fr, en = chemin, "en/" .. chemin
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
