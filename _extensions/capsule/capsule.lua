-- Shortcode « capsule » (US-19) : une vidéo YouTube, chargée seulement au clic.
--
--     {{< capsule dQw4w9WgXcQ titre="Séance 1 — l'architecture en couches" >}}
--
-- Tant que le lecteur n'a pas cliqué, **aucune requête ne part vers Google** : la vignette est dessinée
-- par le site, sans appel à img.youtube.com, et l'iframe n'existe pas. Au clic, elle est créée sur
-- youtube-nocookie.com, qui ne dépose pas de cookie de suivi avant lecture.
--
-- Accessibilité : le bouton porte un nom explicite, et l'iframe reçoit le même titre.

local function echapper(texte)
  return (texte:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

return {
  ["capsule"] = function(args, kwargs)
    local identifiant = pandoc.utils.stringify(args[1] or "")
    local titre = pandoc.utils.stringify(kwargs["titre"] or "")
    if identifiant == "" then
      error("shortcode capsule : identifiant de la vidéo manquant.")
    end
    if titre == "" then
      error("shortcode capsule : attribut « titre » obligatoire, il nomme la vidéo pour tous les lecteurs.")
    end
    if not identifiant:match("^[%w_-]+$") then
      error("shortcode capsule : identifiant inattendu « " .. identifiant .. " ».")
    end

    quarto.doc.add_html_dependency({ name = "capsule", scripts = { "capsule.js" },
                                     stylesheets = { "capsule.css" } })

    return pandoc.RawBlock("html", string.format([[
<figure class="capsule">
  <button type="button" class="capsule-declencheur" data-video="%s" aria-label="Lire la vidéo : %s">
    <span class="capsule-icone" aria-hidden="true"></span>
    <span class="capsule-titre">%s</span>
    <span class="capsule-note">La vidéo est hébergée par YouTube : rien n'est chargé avant le clic.</span>
  </button>
  <noscript>
    <a href="https://www.youtube.com/watch?v=%s">Voir la vidéo sur YouTube : %s</a>
  </noscript>
</figure>]], echapper(identifiant), echapper(titre), echapper(titre),
               echapper(identifiant), echapper(titre)))
  end,
}
