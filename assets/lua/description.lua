-- Balise <meta name="description"> des slides (US-15).
--
-- Le format HTML du site écrit cette balise à partir de « description » ; revealjs, lui, ne pose que les
-- métadonnées de partage (og:description, twitter:description). Le contrôle de référencement d'US-13
-- exige la balise sur chaque page : ce filtre l'ajoute, et seulement pour les slides.

local function echapper(texte)
  return (texte:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

function Pandoc(doc)
  if not quarto.doc.is_format("revealjs") or not doc.meta.description then
    return doc
  end
  local description = pandoc.utils.stringify(doc.meta.description)
  quarto.doc.include_text("in-header",
    string.format('<meta name="description" content="%s">', echapper(description)))
  return doc
end
