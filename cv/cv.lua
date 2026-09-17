-- Filtre du CV (US-10, bilingue en US-36) : remplace le bloc ::: {#cv} ::: de la page par le contenu
-- de cv.yml. Le même filtre sert à la page HTML, au PDF Typst et aux deux langues : une seule source de
-- données, seuls les libellés sont traduits. La page peut donner le chemin des données (clé « donnees »).

local INSECABLE = "\u{A0}"

local LIBELLES = {
  fr = { parcours = "Parcours", formation = "Formation", mention = "Mention ",
         responsabilites = "Responsabilités scientifiques et associatives",
         distinctions = "Distinctions", langues = "Langues" },
  en = { parcours = "Positions", formation = "Education", mention = "Honours: ",
         responsabilites = "Scientific and professional responsibilities",
         distinctions = "Awards", langues = "Languages" },
}

local function libelles(doc)
  local langue = pandoc.utils.stringify(doc.meta.lang or "fr"):sub(1, 2)
  return LIBELLES[langue] or LIBELLES.fr
end

-- Valeur éventuellement traduite : une clé peut porter directement un texte, ou une table fr/en.
local function selon_langue(valeur, langue)
  if valeur == nil then return nil end
  if pandoc.utils.type(valeur) == "table" and valeur[langue] then return valeur[langue] end
  if pandoc.utils.type(valeur) == "table" and valeur.fr then return valeur.fr end
  return valeur
end

-- cv.yml est lu comme un bloc de métadonnées : le Markdown en ligne des valeurs est interprété.
local function lire_donnees(doc)
  local dossier = pandoc.path.directory(quarto.doc.input_file)
  local chemin = doc.meta.donnees and pandoc.utils.stringify(doc.meta.donnees) or "cv.yml"
  local fichier = assert(io.open(pandoc.path.join({ dossier, chemin }), "r"))
  local texte = fichier:read("a")
  fichier:close()
  return pandoc.read("---\n" .. texte .. "\n---\n", "markdown").meta
end

-- Concatène des chaînes et des Inlines en une seule liste d'Inlines.
local function en_ligne(...)
  local resultat = pandoc.Inlines({})
  for i = 1, select("#", ...) do -- select, et non ipairs : un morceau absent (nil) ne coupe pas la suite
    local morceau = select(i, ...)
    if type(morceau) == "string" then
      resultat:extend(pandoc.Inlines(morceau))
    elseif pandoc.utils.type(morceau) == "Inline" then
      resultat:insert(morceau)
    elseif morceau ~= nil then
      resultat:extend(morceau)
    end
  end
  return resultat
end

local function periode(entree)
  return en_ligne(entree.debut, " – ", entree.fin)
end

local function sous_liste(details)
  if not details then
    return {}
  end
  local items = {}
  for _, detail in ipairs(details) do
    table.insert(items, { pandoc.Plain(detail) })
  end
  return { pandoc.BulletList(items) }
end

local function section(titre, id, blocs)
  local contenu = pandoc.Blocks({ pandoc.Header(2, titre, { id = id }) })
  contenu:extend(blocs)
  return contenu
end

-- Une expérience ou un diplôme : intitulé en gras et lieu, puis dates, puis précisions éventuelles.
local function entree_cv(intitule, lieu, dates, details)
  local blocs = pandoc.Blocks({
    pandoc.Para(en_ligne(pandoc.Strong(intitule), " — ", lieu, pandoc.LineBreak(),
      pandoc.Span(dates, { class = "cv-dates" }))),
  })
  blocs:extend(sous_liste(details))
  return pandoc.Div(blocs, { class = "cv-entree" })
end

local function liste(elements, rendu)
  local items = {}
  for _, element in ipairs(elements) do
    table.insert(items, { pandoc.Plain(rendu(element)) })
  end
  return pandoc.BulletList(items)
end

local function contenu_cv(cv, mots)
  local blocs = pandoc.Blocks({})

  local parcours = {}
  for _, poste in ipairs(cv.parcours) do
    table.insert(parcours, entree_cv(poste.poste, poste.employeur, periode(poste), poste.details))
  end
  blocs:extend(section(mots.parcours, "parcours", parcours))

  local formation = {}
  for _, diplome in ipairs(cv.formation) do
    local dates = en_ligne(diplome.periode, " · " .. mots.mention, diplome.mention)
    table.insert(formation, entree_cv(diplome.diplome, diplome.etablissement, dates, diplome.details))
  end
  blocs:extend(section(mots.formation, "formation", formation))

  blocs:extend(section(mots.responsabilites, "responsabilites", {
    liste(cv.responsabilites, function(r)
      return en_ligne(pandoc.Strong(r.intitule), ", ", r.cadre, r.dates and en_ligne(" (", r.dates, ")"))
    end),
  }))

  blocs:extend(section(mots.distinctions, "distinctions", {
    liste(cv.distinctions, function(d)
      return en_ligne(d.intitule, " (", d.dates, ")")
    end),
  }))

  blocs:extend(section(mots.langues, "langues", {
    liste(cv.langues, function(l)
      return en_ligne(l.langue, INSECABLE .. ": ", l.niveau)
    end),
  }))

  return blocs
end

function Pandoc(doc)
  local cv = lire_donnees(doc)
  local mots = libelles(doc)
  local langue = pandoc.utils.stringify(doc.meta.lang or "fr"):sub(1, 2)
  local identite = cv.identite
  local titre = selon_langue(identite.titre, langue)
  if quarto.doc.is_format("typst") then
    -- PDF : le nom en titre.
    doc.meta.title = identite.nom
    doc.meta.subtitle = en_ligne(titre, ", ", identite.affiliation)
  else
    -- Page web : « CV » en titre, comme dans la navigation.
    doc.meta.subtitle = en_ligne(identite.nom, ", ", titre, ", ", identite.affiliation)
  end
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier == "cv" then
        return contenu_cv(cv, mots)
      end
    end,
  })
  return doc
end
