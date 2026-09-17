-- Shortcode {{< email >}} (US-12) : lien email reconstruit en JavaScript, pour limiter la collecte
-- automatique. L'adresse n'apparaît jamais en clair dans le HTML généré.
--
-- Adresse lue dans _quarto.yml (contact.email-utilisateur, contact.email-domaine).
-- Arguments facultatifs : texte="…" (libellé, « Email » par défaut) et icone="…" (icône Bootstrap
-- décorative placée avant le libellé, par exemple icone="envelope").
-- Placé dans un lien existant (bouton de l'accueil), le script en remplace la cible ; sinon il crée le lien.
-- Sans JavaScript, un repli lisible est affiché : « utilisateur [arobase] domaine ».

local function valeur(meta, cle)
  local contact = meta.contact
  local v = contact and contact[cle]
  if not v or pandoc.utils.stringify(v) == "" then
    error("_quarto.yml : contact." .. cle .. " manquant (shortcode email)")
  end
  return pandoc.utils.stringify(v)
end

local function echapper(texte)
  return (texte:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

return {
  email = function(args, kwargs, meta)
    if not quarto.doc.is_format("html:js") then
      return pandoc.Str("")
    end
    local utilisateur, domaine = valeur(meta, "email-utilisateur"), valeur(meta, "email-domaine")
    local texte = pandoc.utils.stringify(kwargs.texte or "")
    if texte == "" then
      texte = "Email"
    end

    quarto.doc.add_html_dependency({
      name = "email-protege",
      version = "1.0.0",
      scripts = { { path = "email-protege.js", afterBody = true } },
    })

    -- Adresse inversée puis encodée en base64 : aucune forme lisible dans la source HTML.
    local code = quarto.base64.encode((utilisateur .. "@" .. domaine):reverse())
    local icone = pandoc.utils.stringify(kwargs.icone or "")
    local prefixe = icone ~= "" and string.format('<i class="bi bi-%s" aria-hidden="true"></i> ', echapper(icone)) or ""
    return pandoc.RawInline("html", string.format(
      '%s<span class="email-protege" data-email="%s">%s</span><noscript> (%s [arobase] %s)</noscript>',
      prefixe, code, echapper(texte), echapper(utilisateur), echapper(domaine)))
  end,
}
