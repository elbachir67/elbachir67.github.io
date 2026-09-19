-- Fiche d'un cours (US-14) : remplace le bloc ::: {#fiche} ::: de cours/<slug>/index.qmd par les
-- métadonnées lues dans cours/<slug>/cours.yml. Les pages de cours sont monolingues (français).
--
-- Le titre de la page et le champ « titre » de cours.yml doivent coïncider : le premier sert à la
-- navigation et au référencement, le second au catalogue. Le rendu échoue s'ils divergent, pour que
-- les deux ne partent pas chacun de leur côté.

local INSECABLE = "\u{A0}"

-- Ressources d'une séance (US-49) : libellé par type et par langue. Un corrigé n'apparaît jamais —
-- il n'est pas écrit dans l'en-tête de la séance, et son fichier vit hors du site.
local RESSOURCES = {
  fr = { lab = "Lab", td = "TD", notebook = "Notebook" },
  en = { lab = "Lab", td = "Tutorial", notebook = "Notebook" },
}

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
  local langue = pandoc.utils.stringify(doc.meta.lang or "fr"):sub(1, 2)
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
      local formats = pandoc.Inlines({
        pandoc.Link(mots_pdf(), pdf, "", { class = "seance-pdf", download = "" }),
      })
      for _, ressource in ipairs(meta and meta.ressources or {}) do
        local type_ = pandoc.utils.stringify(ressource.type)
        local libelle = (RESSOURCES[langue] or RESSOURCES.fr)[type_]
        if libelle then
          formats:insert(pandoc.Str(" · "))
          formats:insert(pandoc.Link(pandoc.Inlines(libelle), pandoc.utils.stringify(ressource.chemin),
            pandoc.utils.stringify(ressource.titre), { class = "seance-ressource" }))
        end
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
      if div.identifier == "seances" then
        return seances(doc)
      end
    end,
  })
  return doc
end
