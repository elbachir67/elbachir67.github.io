-- Fiche d'un cours (US-14) : remplace le bloc ::: {#fiche} ::: de cours/<slug>/index.qmd par les
-- métadonnées lues dans cours/<slug>/cours.yml. Les pages de cours sont monolingues (français).
--
-- Le titre de la page et le champ « titre » de cours.yml doivent coïncider : le premier sert à la
-- navigation et au référencement, le second au catalogue. Le rendu échoue s'ils divergent, pour que
-- les deux ne partent pas chacun de leur côté.

local INSECABLE = "\u{A0}"

-- Ressources des séances (US-49) : le poids des fichiers et la date des corrigés sont lus au rendu.
package.path = package.path .. ";" .. pandoc.path.directory(PANDOC_SCRIPT_FILE) .. "/?.lua"
local R = require("ressources-communes")

-- Libellé du lien de téléchargement, avec l'icône du thème.
local function mots_pdf()
  return pandoc.Inlines({
    pandoc.RawInline("html", '<i class="bi bi-file-earmark-pdf" aria-hidden="true"></i> '),
    pandoc.Str("PDF"),
  })
end

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

-- Ressources du cours entier, et non d'un chapitre (US-59) : un corrigé de devoir surveillé ne
-- relève d'aucun chapitre, mais de tout le cours. Elles se déclarent dans `cours.yml`, sous la même
-- forme que celles d'une séance, et suivent les mêmes règles — un corrigé n'apparaît qu'à partir de
-- sa date de publication.
local function ressources_du_cours(cours, dossier)
  local publiables = R.publiables(cours.ressources)
  if #publiables == 0 then
    return pandoc.Blocks({})
  end
  -- Une ressource de séance porte son adresse publique, calculée à l'import ; celle-ci est déclarée
  -- à la main dans cours.yml, et n'a que son chemin relatif au cours. On la complète ici, de la même
  -- façon, pour que le lien et l'attribut de téléchargement se décident comme ailleurs.
  -- `publiables` renvoie une chaîne vide, et non nil, quand le champ manque : en Lua, « or » ne
  -- l'aurait pas vue, puisque seule nil est fausse.
  local slug = pandoc.path.filename(dossier)
  local puces = {}
  for _, ressource in ipairs(publiables) do
    if ressource.chemin == "" then
      ressource.chemin = "/cours/" .. slug .. "/" .. ressource.fichier
    end
    table.insert(puces, pandoc.Blocks({ pandoc.Plain(R.lien(ressource, "fr", dossier, false)) }))
  end
  return pandoc.Blocks({ pandoc.Header(2, "Ressources du cours"), pandoc.BulletList(puces) })
end


-- En-tête YAML d'un chapitre : son titre et sa description, pour la table des séances.
local function entete_chapitre(chemin)
  local fichier = io.open(chemin, "r")
  if not fichier then
    return nil
  end
  local contenu = fichier:read("a")
  fichier:close()
  local yaml = contenu:match("^%-%-%-\n(.-)\n%-%-%-")
  if not yaml then
    return nil
  end
  return pandoc.read("---\n" .. yaml .. "\n---\n", "markdown").meta
end

-- Table des séances : chacune mène à ses slides et à leur PDF (US-17). Le PDF est produit au rendu par
-- scripts/generer_pdf.js, à côté de la page : le lien est donc le même chemin, en .pdf.
local function seances(doc)
  local langue = R.langue(doc)
  local cours = pandoc.path.directory(quarto.doc.input_file)
  local dossier = pandoc.path.join({ pandoc.path.directory(quarto.doc.input_file), "chapitres" })
  local ok, fichiers = pcall(pandoc.system.list_directory, dossier)
  if not ok then
    return pandoc.Blocks({})
  end
  table.sort(fichiers)

  local lignes = {}
  for _, nom in ipairs(fichiers) do
    if nom:match("%.qmd$") then
      local meta = entete_chapitre(pandoc.path.join({ dossier, nom }))
      local page = "chapitres/" .. nom:gsub("%.qmd$", ".html")
      local pdf = "chapitres/" .. nom:gsub("%.qmd$", ".pdf")
      local titre = meta and meta.title or pandoc.Inlines(nom)
      local description = meta and meta.description or pandoc.Inlines("")
      -- Une séance en slides est imprimée en PDF au rendu ; une page rédigée, non : son PDF est
      -- celui que LaTeX a compilé, attaché en ressource (US-40).
      local page_redigee = meta and meta.cible and pandoc.utils.stringify(meta.cible) == "page"
      local formats = pandoc.Inlines({})
      if not page_redigee then
        formats:insert(pandoc.Link(mots_pdf(), pdf, "", { class = "seance-pdf" }))
      end
      for _, ressource in ipairs(R.publiables(meta and meta.ressources)) do
        if #formats > 0 then
          formats:insert(pandoc.Str(" · "))
        end
        formats:extend(R.lien(ressource, langue, cours, true))
      end
      table.insert(lignes, {
        { pandoc.Plain(pandoc.Link(titre, page)) },
        { pandoc.Plain(description) },
        { pandoc.Plain(formats) },
      })
    end
  end
  if #lignes == 0 then
    return pandoc.Blocks({})
  end

  local entete = { { pandoc.Plain("Séance") }, { pandoc.Plain("Contenu") }, { pandoc.Plain("Format") } }
  return pandoc.Blocks({ pandoc.utils.from_simple_table(
    pandoc.SimpleTable(pandoc.Inlines(""), { "AlignLeft", "AlignLeft", "AlignLeft" },
      { 0.3, 0.55, 0.15 }, entete, lignes)) })
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
      -- « seances » pour un cours en slides, « chapitres » pour un cours rédigé : le même tableau,
      -- sous le mot qui convient au cours.
      if div.identifier == "seances" or div.identifier == "chapitres" then
        return seances(doc)
      end
      if div.identifier == "ressources-cours" then
        return ressources_du_cours(cours, pandoc.path.directory(quarto.doc.input_file))
      end
    end,
  })
  return doc
end
