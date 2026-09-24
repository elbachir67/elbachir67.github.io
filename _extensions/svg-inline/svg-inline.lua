-- Shortcode « svg » (US-15) : insère un SVG dans la page plutôt que de le lier.
--
--     {{< svg figures/fig2_couches.svg alt="Les trois couches…" largeur="60%" >}}
--
-- Pourquoi inliner : les figures des cours utilisent « currentColor » pour suivre la couleur du texte
-- (mode sombre, projection). Dans un <img>, currentColor se résout dans le document SVG lui-même, donc
-- en noir ; il ne prend la couleur de la page que si le SVG fait partie de la page.
--
-- Accessibilité : role="img" et aria-label donnent à la figure le nom accessible que porterait l'attribut
-- alt d'une image. Sans texte alternatif, le shortcode échoue : une figure sans description n'est pas
-- publiable (règle du projet).

local function lire(chemin)
  local fichier = io.open(chemin, "r")
  if not fichier then
    return nil
  end
  local contenu = fichier:read("a")
  fichier:close()
  return contenu
end

-- Chemin relatif au fichier source de la page, comme le ferait un lien Markdown.
local function resoudre(chemin)
  if chemin:sub(1, 1) == "/" then
    return pandoc.path.join({ quarto.project.directory or ".", chemin:sub(2) })
  end
  return pandoc.path.join({ pandoc.path.directory(quarto.doc.input_file), chemin })
end

local function echapper(texte)
  return (texte:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

return {
  ["svg"] = function(args, kwargs)
    local chemin = pandoc.utils.stringify(args[1] or "")
    local alt = pandoc.utils.stringify(kwargs["alt"] or "")
    local largeur = pandoc.utils.stringify(kwargs["largeur"] or "")
    if chemin == "" then
      error("shortcode svg : chemin du fichier manquant.")
    end
    if alt == "" then
      error("shortcode svg : attribut « alt » obligatoire pour « " .. chemin .. " ».")
    end

    local svg = lire(resoudre(chemin))
    if not svg then
      error("shortcode svg : fichier introuvable « " .. chemin .. " ».")
    end
    -- Déclaration XML et commentaires de tête : inutiles dans une page HTML.
    svg = svg:gsub("^%s*<%?xml.-%?>%s*", ""):gsub("^%s*<!%-%-.-%-%->%s*", "")
    -- Le nom accessible et le rôle remplacent l'attribut alt d'une image.
    --
    -- Le remplacement passe par une **fonction** : dans une chaîne de remplacement, Lua donne un
    -- sens particulier au « % », et un texte alternatif qui en contient — « part de zéros
    -- impossibles (%) », au cours d'Introduction au ML — faisait échouer le rendu de la page
    -- entière sur « invalid use of "%" in replacement string ».
    local entete = string.format('<svg role="img" aria-label="%s"', echapper(alt))
    svg = svg:gsub("<svg", function() return entete end, 1)

    local style = largeur ~= "" and string.format(' style="width: %s"', echapper(largeur)) or ""
    return pandoc.RawInline("html",
      string.format('<span class="figure-cours"%s>%s</span>', style, svg))
  end,
}
