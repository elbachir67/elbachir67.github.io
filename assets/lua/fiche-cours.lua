-- Fiche d'un cours (US-14) : remplace le bloc ::: {#fiche} ::: de cours/<slug>/index.qmd par les
-- métadonnées lues dans cours/<slug>/cours.yml. Les pages de cours sont monolingues (français).
--
-- Le titre de la page et le champ « titre » de cours.yml doivent coïncider : le premier sert à la
-- navigation et au référencement, le second au catalogue. Le rendu échoue s'ils divergent, pour que
-- les deux ne partent pas chacun de leur côté.

local INSECABLE = "\u{A0}"

local function texte(valeur)
  return pandoc.utils.stringify(valeur)
end

-- cours.yml est lu comme un bloc de métadonnées : le Markdown en ligne des valeurs est interprété.
local function lire_cours(doc)
  local dossier = pandoc.path.directory(quarto.doc.input_file)
  local fichier = assert(io.open(pandoc.path.join({ dossier, "cours.yml" }), "r"),
    "cours.yml introuvable à côté de " .. quarto.doc.input_file)
  local contenu = fichier:read("a")
  fichier:close()
  return pandoc.read("---\n" .. contenu .. "\n---\n", "markdown").meta
end

local function liste(titre, elements)
  if not elements then
    return {}
  end
  local puces = {}
  for _, element in ipairs(elements) do
    table.insert(puces, pandoc.Blocks({ pandoc.Plain(element) }))
  end
  return { pandoc.Header(2, titre), pandoc.BulletList(puces) }
end

local function fiche(cours)
  local reperes = {}
  local niveaux = {}
  for _, niveau in ipairs(cours.niveaux or {}) do
    table.insert(niveaux, texte(niveau))
  end
  if #niveaux > 0 then
    table.insert(reperes, (#niveaux > 1 and "Niveaux" or "Niveau") .. INSECABLE .. ": " .. table.concat(niveaux, ", "))
  end
  if cours.semestre then
    table.insert(reperes, "Semestre" .. INSECABLE .. ": " .. texte(cours.semestre))
  end
  if cours.domaine then
    table.insert(reperes, "Domaine" .. INSECABLE .. ": " .. texte(cours.domaine))
  end

  local blocs = pandoc.Blocks({})
  if #reperes > 0 then
    blocs:insert(pandoc.Para(pandoc.Inlines(table.concat(reperes, " · "))))
  end
  blocs:extend(liste("Objectifs", cours.objectifs))
  blocs:extend(liste("Prérequis", cours.prerequis))
  return blocs
end

function Pandoc(doc)
  local cours = lire_cours(doc)
  local attendu, titre = texte(cours.titre), texte(doc.meta.title or "")
  if attendu ~= titre then
    error(string.format("cours.yml annonce « %s » et la page « %s » : mettre les deux d'accord.",
      attendu, titre))
  end
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier == "fiche" then
        return fiche(cours)
      end
    end,
  })
  return doc
end
