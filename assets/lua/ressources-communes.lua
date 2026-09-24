-- Ressources d'une séance (US-49), partagées par deux filtres : celui de la séance
-- (`ressources.lua`) et celui de la page du cours (`fiche-cours.lua`).
--
-- Une donnée ne peut être connue qu'au rendu, et non à l'import : le **poids** du fichier, qui
-- change dès que le PO remplace son énoncé. C'est pourquoi la liste est construite ici, et non
-- écrite dans la page.

local M = {}

-- Libellé par type et par langue. `corrige` n'y figure pas : aucun corrigé, aucune piste, aucune
-- indication de correction ne paraît sur le site (décision du PO). Un type inconnu est ignoré, ce
-- qui fait de cette table le dernier filet du rendu.
local LIBELLES = {
  fr = { lab = "Lab", tp = "TP", td = "TD", notebook = "Notebook", pdf = "PDF du cours" },
  en = { lab = "Lab", tp = "Lab", td = "Tutorial", notebook = "Notebook", pdf = "Course PDF" },
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

--- Ressources publiables : celles dont le type porte un libellé. Un corrigé, une piste ou une
--- correction n'en a pas, et n'apparaît donc nulle part — pas de lien, pas de mention, rien.
function M.publiables(ressources)
  local visibles = {}
  for _, ressource in ipairs(ressources or {}) do
    local type_ = pandoc.utils.stringify(ressource.type or "")
    if LIBELLES.fr[type_] then
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
  -- Un PDF s'ouvre dans la visionneuse ; un notebook a maintenant sa page lisible (US-50), où
  -- deux boutons proposent le téléchargement et Colab. Le reste s'enregistre.
  if extension == "pdf" or extension == "ipynb" then
    return { class = "seance-ressource" }
  end
  return { class = "seance-ressource", download = "" }
end

--- Adresse publique d'une ressource : un notebook mène à sa page, les autres à leur fichier.
local function adresse(ressource)
  if ressource.chemin:lower():match("%.ipynb$") then
    return (ressource.chemin:gsub("%.ipynb$", ".html"))
  end
  return ressource.chemin
end

function M.lien(ressource, langue, cours, court)
  local libelle = LIBELLES[langue][ressource.type]
  local inlines = pandoc.Inlines({})
  local attr = attributs(ressource)
  if court then
    inlines:insert(pandoc.Link(pandoc.Inlines(libelle), adresse(ressource), ressource.titre, attr))
  else
    inlines:insert(pandoc.Strong(pandoc.Inlines(libelle)))
    inlines:insert(pandoc.Str(" · "))
    inlines:insert(pandoc.Link(pandoc.Inlines(ressource.titre), adresse(ressource), ressource.titre,
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
