-- Ressources d'une séance (US-49), partagées par deux filtres : celui de la séance
-- (`ressources.lua`) et celui de la page du cours (`fiche-cours.lua`).
--
-- Deux données ne peuvent être connues qu'au rendu, et non à l'import :
--   * le **poids** du fichier, qui change dès que le PO remplace son énoncé ;
--   * le fait qu'un **corrigé** ait atteint sa date de publication.
-- C'est pourquoi la liste est construite ici, et non écrite dans la page.

local M = {}

-- Libellé par type et par langue. `corrige` n'apparaît qu'à partir de sa date.
local LIBELLES = {
  fr = { lab = "Lab", td = "TD", notebook = "Notebook", corrige = "Corrigé" },
  en = { lab = "Lab", td = "Tutorial", notebook = "Notebook", corrige = "Solution" },
}

local UNITES = {
  fr = { "o", "Ko", "Mo", separateur = "," },
  en = { "B", "KB", "MB", separateur = "." },
}

function M.langue(doc)
  local lang = doc.meta and doc.meta.lang
  local code = lang and pandoc.utils.stringify(lang):sub(1, 2) or "fr"
  return LIBELLES[code] and code or "fr"
end

--- Poids lisible d'un fichier, ou nil s'il est absent (le filtre n'invente pas de chiffre).
function M.poids(chemin, langue)
  local fichier = io.open(chemin, "rb")
  if not fichier then
    return nil
  end
  local octets = fichier:seek("end")
  fichier:close()
  local unites = UNITES[langue] or UNITES.fr
  if octets < 1024 then
    return string.format("%d %s", octets, unites[1])
  end
  if octets < 1024 * 1024 then
    return string.format("%d %s", math.floor(octets / 1024 + 0.5), unites[2])
  end
  local mega = string.format("%.1f", octets / (1024 * 1024))
  return mega:gsub("%.", unites.separateur) .. " " .. unites[3]
end

--- Aujourd'hui, en AAAA-MM-JJ : les dates ISO se comparent comme des chaînes.
function M.aujourdhui()
  return os.date("%Y-%m-%d")
end

--- Ressources visibles aujourd'hui : un corrigé sans date, ou dont la date n'est pas atteinte, est
--- absent — pas de lien, pas de mention, rien. C'est la règle impérative d'US-49.
function M.publiables(ressources)
  local visibles = {}
  local maintenant = M.aujourdhui()
  for _, ressource in ipairs(ressources or {}) do
    local type_ = pandoc.utils.stringify(ressource.type or "")
    local date = ressource.date and pandoc.utils.stringify(ressource.date) or ""
    local attendue = type_ == "corrige" and (date == "" or date > maintenant)
    if LIBELLES.fr[type_] and not attendue then
      table.insert(visibles, {
        type = type_,
        titre = pandoc.utils.stringify(ressource.titre or ""),
        fichier = pandoc.utils.stringify(ressource.fichier or ""),
        chemin = pandoc.utils.stringify(ressource.chemin or ""),
      })
    end
  end
  return visibles
end

--- Lien d'une ressource, avec son type et son poids : « **Lab** · Lab 1 — … (235 Ko) ».
--- `court` ne garde que le type : c'est la forme de la table des séances, où la place manque.
--- Attributs du lien : tout ce qui n'est pas un PDF se télécharge.
--- Le navigateur affiche correctement un PDF ; il afficherait un notebook en JSON brut, ce qui
--- n'aide personne. L'attribut `download` lui dit d'enregistrer le fichier au lieu de l'ouvrir.
local function attributs(ressource)
  local extension = (ressource.chemin:match("%.(%w+)$") or ""):lower()
  if extension == "pdf" then
    return { class = "seance-ressource" }
  end
  return { class = "seance-ressource", download = "" }
end

function M.lien(ressource, langue, cours, court)
  local libelle = LIBELLES[langue][ressource.type]
  local inlines = pandoc.Inlines({})
  local attr = attributs(ressource)
  if court then
    inlines:insert(pandoc.Link(pandoc.Inlines(libelle), ressource.chemin, ressource.titre, attr))
  else
    inlines:insert(pandoc.Strong(pandoc.Inlines(libelle)))
    inlines:insert(pandoc.Str(" · "))
    inlines:insert(pandoc.Link(pandoc.Inlines(ressource.titre), ressource.chemin, ressource.titre,
      attr))
  end
  local poids = M.poids(pandoc.path.join({ cours, ressource.fichier }), langue)
  if poids then
    inlines:insert(pandoc.Space())
    inlines:insert(pandoc.Span(pandoc.Inlines("(" .. poids .. ")"), { class = "ressource-poids" }))
  end
  return inlines
end

return M
