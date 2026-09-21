-- Filtre du catalogue (US-11, US-14) : remplace le bloc ::: {#catalogue} ::: de index.qmd par les cartes
-- des cours, groupées par domaine.
--
-- Deux sources, sans recoupement :
--   * cours.yml, à côté de cette page : les cours qui n'ont pas encore de page sur le site ;
--   * cours/<slug>/cours.yml : les cours publiés, qui décrivent eux-mêmes leurs métadonnées (US-14).
-- Un cours publié ne doit donc plus figurer dans cours.yml ; le rendu échoue s'il y est encore.

local INSECABLE = "\u{A0}"
local STATUTS = { ["a-venir"] = true, ["en-ligne"] = true }

local LIBELLES = {
  fr = { niveau = "Niveau", niveaux = "Niveaux", a_venir = "Bientôt en ligne",
         en_ligne = "En ligne", seance = "séance", seances = "séances" },
  en = { niveau = "Level", niveaux = "Levels", a_venir = "Coming soon",
         en_ligne = "Online", seance = "session", seances = "sessions" },
}

-- cours.yml est lu comme un bloc de métadonnées : le Markdown en ligne des valeurs est interprété.
local function lire_donnees(doc)
  local dossier = pandoc.path.directory(quarto.doc.input_file)
  local chemin = doc.meta.donnees and pandoc.utils.stringify(doc.meta.donnees) or "cours.yml"
  local fichier = assert(io.open(pandoc.path.join({ dossier, chemin }), "r"))
  local texte = fichier:read("a")
  fichier:close()
  return pandoc.read("---\n" .. texte .. "\n---\n", "markdown").meta
end

-- Séances publiées d'un cours : le catalogue l'annonce sur la carte, pour qu'un étudiant sache ce
-- qui l'attend sans ouvrir la page (US-57).
local function nombre_de_seances(slug)
  local dossier = pandoc.path.join({ quarto.project.directory, "cours", slug, "chapitres" })
  local ok, entrees = pcall(pandoc.system.list_directory, dossier)
  if not ok then
    return 0
  end
  local compte = 0
  for _, nom in ipairs(entrees) do
    if nom:match("^%d%d%-.*%.qmd$") then
      compte = compte + 1
    end
  end
  return compte
end

-- Cours publiés : un dossier par cours sous cours/, avec son propre cours.yml (US-14).
local function cours_publies()
  local dossier = pandoc.path.join({ quarto.project.directory, "cours" })
  local ok, entrees = pcall(pandoc.system.list_directory, dossier)
  if not ok then
    return {}
  end
  table.sort(entrees)
  local publies = {}
  for _, slug in ipairs(entrees) do
    local fichier = io.open(pandoc.path.join({ dossier, slug, "cours.yml" }), "r")
    if fichier then
      local contenu = fichier:read("a")
      fichier:close()
      local cours = pandoc.read("---\n" .. contenu .. "\n---\n", "markdown").meta
      -- Lien depuis la racine du site : la même carte sert aux deux langues du catalogue.
      cours.lien = pandoc.Inlines("/cours/" .. slug .. "/")
      cours.seances = nombre_de_seances(slug)
      table.insert(publies, cours)
    end
  end
  return publies
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

local function carte(cours, mots)
  local statut = texte(cours.statut)
  if not STATUTS[statut] then
    error("cours.yml : statut inconnu « " .. statut .. " » pour « " .. texte(cours.titre) .. " »")
  end
  local en_ligne = statut == "en-ligne"

  local titre = pandoc.Strong(cours.titre)
  if en_ligne then
    if not cours.lien then
      error("cours.yml : « lien » manquant pour le cours en ligne « " .. texte(cours.titre) .. " »")
    end
    titre = pandoc.Link(titre, texte(cours.lien))
  end

  local niveaux = {}
  for _, niveau in ipairs(cours.niveaux) do
    table.insert(niveaux, texte(niveau))
  end
  local libelle_niveaux = #niveaux > 1 and mots.niveaux or mots.niveau

  -- Le domaine est **écrit** sur la carte : sa couleur ne fait que le redire, jamais le remplacer
  -- (US-57, WCAG 1.4.1).
  local domaine = texte(cours.domaine)
  local entete = pandoc.Para({ pandoc.Span(domaine, { class = "cours-domaine" }) })

  -- Le statut garde son libellé, et un cours en ligne annonce ce qui l'attend.
  local seances = en_ligne and math.floor(tonumber(texte(cours.seances)) or 0) or 0
  local libelle = en_ligne
    and (mots.en_ligne .. (seances > 0
      and (" " .. INSECABLE .. "· " .. seances .. INSECABLE .. (seances > 1 and mots.seances or mots.seance))
      or ""))
    or mots.a_venir
  local pastille = pandoc.Span(libelle,
    { class = "cours-statut " .. (en_ligne and "cours-statut-en-ligne" or "cours-statut-a-venir") })

  local blocs = {
    entete,
    pandoc.Para({ titre }),
    pandoc.Para(pandoc.Inlines(libelle_niveaux .. INSECABLE .. ": " .. table.concat(niveaux, ", "))),
    pandoc.Para({ pastille }),
  }

  -- Le champ skill de cours.yml n'est jamais affiché.
  local corps = pandoc.Div(blocs, { class = "card-body" })
  return pandoc.Div({ pandoc.Div({ corps },
      { class = "card h-100 cours-carte", ["data-domaine"] = identifiant(domaine) }) },
    { class = "g-col-12 g-col-md-6 g-col-lg-4" })
end

local function catalogue(donnees, mots)
  local publies = cours_publies()
  local titres_publies = {}
  for _, cours in ipairs(publies) do
    titres_publies[texte(cours.titre)] = true
  end
  local tous = {}
  for _, cours in ipairs(donnees.cours) do
    if titres_publies[texte(cours.titre)] then
      error("« " .. texte(cours.titre) .. " » est décrit dans cours/<slug>/cours.yml : "
        .. "retirer son entrée de enseignement/cours.yml.")
    end
    table.insert(tous, cours)
  end
  for _, cours in ipairs(publies) do
    table.insert(tous, cours)
  end

  -- Domaines dans l'ordre de première apparition : cours.yml d'abord, cours publiés ensuite.
  local domaines, cartes = {}, {}
  for _, cours in ipairs(tous) do
    local domaine = texte(cours.domaine)
    if not cartes[domaine] then
      table.insert(domaines, domaine)
      cartes[domaine] = {}
    end
    table.insert(cartes[domaine], carte(cours, mots))
  end

  local blocs = pandoc.Blocks({})
  for _, domaine in ipairs(domaines) do
    blocs:insert(pandoc.Header(2, domaine, { id = identifiant(domaine) }))
    blocs:insert(pandoc.Div(cartes[domaine], { class = "grid" }))
  end
  return blocs
end

function Pandoc(doc)
  local donnees = lire_donnees(doc)
  local langue = pandoc.utils.stringify(doc.meta.lang or "fr"):sub(1, 2)
  local mots = LIBELLES[langue] or LIBELLES.fr
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier == "catalogue" then
        return catalogue(donnees, mots)
      end
    end,
  })
  return doc
end
