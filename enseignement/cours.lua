-- Filtre du catalogue (US-11) : remplace le bloc ::: {#catalogue} ::: de index.qmd par les cartes des
-- cours de cours.yml, groupées par domaine. Ajouter un cours = ajouter une entrée dans cours.yml.

local INSECABLE = "\u{A0}"
local STATUTS = { ["a-venir"] = true, ["en-ligne"] = true }

-- cours.yml est lu comme un bloc de métadonnées : le Markdown en ligne des valeurs est interprété.
local function lire_donnees()
  local dossier = pandoc.path.directory(quarto.doc.input_file)
  local fichier = assert(io.open(pandoc.path.join({ dossier, "cours.yml" }), "r"))
  local texte = fichier:read("a")
  fichier:close()
  return pandoc.read("---\n" .. texte .. "\n---\n", "markdown").meta
end

-- Identifiant d'ancre stable pour un domaine : « IA & Data » -> « ia-data ».
local ACCENTS = { ["à"] = "a", ["â"] = "a", ["ç"] = "c", ["é"] = "e", ["è"] = "e", ["ê"] = "e", ["ë"] = "e",
  ["î"] = "i", ["ï"] = "i", ["ô"] = "o", ["ù"] = "u", ["û"] = "u", ["ü"] = "u" }
local function identifiant(texte)
  local id = pandoc.text.lower(texte)
  for accent, lettre in pairs(ACCENTS) do
    id = id:gsub(accent, lettre)
  end
  return (id:gsub("[^%w]+", "-"):gsub("^%-+", ""):gsub("%-+$", ""))
end

local function texte(valeur)
  return pandoc.utils.stringify(valeur)
end

local function carte(cours)
  local statut = texte(cours.statut)
  if not STATUTS[statut] then
    error("cours.yml : statut inconnu « " .. statut .. " » pour « " .. texte(cours.titre) .. " »")
  end

  local titre = pandoc.Strong(cours.titre)
  if statut == "en-ligne" then
    if not cours.lien then
      error("cours.yml : « lien » manquant pour le cours en ligne « " .. texte(cours.titre) .. " »")
    end
    titre = pandoc.Link(titre, texte(cours.lien))
  end

  local niveaux = {}
  for _, niveau in ipairs(cours.niveaux) do
    table.insert(niveaux, texte(niveau))
  end
  local libelle_niveaux = #niveaux > 1 and "Niveaux" or "Niveau"

  local details = pandoc.Inlines(libelle_niveaux .. INSECABLE .. ": " .. table.concat(niveaux, ", "))
  details:insert(pandoc.LineBreak())
  details:extend(pandoc.Inlines("Établissement" .. INSECABLE .. ": "))
  details:extend(cours.etablissement)

  local blocs = { pandoc.Para({ titre }), pandoc.Para(details) }
  if statut == "a-venir" then
    -- Pas de lien tant que le cours natif n'est pas publié.
    table.insert(blocs, pandoc.Para({ pandoc.Span("Bientôt en ligne", { class = "badge text-bg-secondary" }) }))
  end

  local corps = pandoc.Div(blocs, { class = "card-body" })
  return pandoc.Div({ pandoc.Div({ corps }, { class = "card h-100 cours-carte" }) },
    { class = "g-col-12 g-col-md-6 g-col-lg-4" })
end

local function catalogue(donnees)
  -- Domaines dans l'ordre de première apparition dans cours.yml.
  local domaines, cartes = {}, {}
  for _, cours in ipairs(donnees.cours) do
    local domaine = texte(cours.domaine)
    if not cartes[domaine] then
      table.insert(domaines, domaine)
      cartes[domaine] = {}
    end
    table.insert(cartes[domaine], carte(cours))
  end

  local blocs = pandoc.Blocks({})
  for _, domaine in ipairs(domaines) do
    blocs:insert(pandoc.Header(2, domaine, { id = identifiant(domaine) }))
    blocs:insert(pandoc.Div(cartes[domaine], { class = "grid" }))
  end
  return blocs
end

function Pandoc(doc)
  local donnees = lire_donnees()
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier == "catalogue" then
        return catalogue(donnees)
      end
    end,
  })
  return doc
end
