-- Fiche d'un cours (US-14) : remplace le bloc ::: {#fiche} ::: de cours/<slug>/index.qmd par les
-- métadonnées lues dans cours/<slug>/cours.yml. Les pages de cours sont monolingues (français).
--
-- Le titre de la page et le champ « titre » de cours.yml doivent coïncider : le premier sert à la
-- navigation et au référencement, le second au catalogue. Le rendu échoue s'ils divergent, pour que
-- les deux ne partent pas chacun de leur côté.

local INSECABLE = "\u{A0}"

-- Ressources des séances (US-49) : le poids des fichiers est lu au rendu.
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

-- Graphe des cours (US-67) : qui vient avant qui. Les deux sources du catalogue sont lues, parce
-- qu'un prérequis peut désigner un cours qui n'est pas encore en ligne — il s'affiche alors sans
-- lien, en texte simple.
--
-- La relation inverse — « Ce cours prépare à » — n'est **jamais saisie** : elle se calcule en
-- parcourant les prérequis de tous les autres cours. Saisir les deux sens, c'est accepter qu'ils
-- divergent.
local function tous_les_cours()
  local liste = {}

  -- Cours publiés : un dossier par cours, son slug est le nom du dossier.
  local dossier = pandoc.path.join({ quarto.project.directory, "cours" })
  local ok, entrees = pcall(pandoc.system.list_directory, dossier)
  if ok then
    table.sort(entrees)
    for _, slug in ipairs(entrees) do
      local fichier = io.open(pandoc.path.join({ dossier, slug, "cours.yml" }), "r")
      if fichier then
        local contenu = fichier:read("a")
        fichier:close()
        local meta = pandoc.read("---\n" .. contenu .. "\n---\n", "markdown").meta
        table.insert(liste, { slug = slug, titre = meta.titre, en_ligne = true,
                              prerequis = meta["prerequis-cours"] })
      end
    end
  end

  -- Cours à venir : une entrée de enseignement/cours.yml, avec son champ slug.
  local catalogue = io.open(pandoc.path.join({ quarto.project.directory, "enseignement", "cours.yml" }), "r")
  if catalogue then
    local contenu = catalogue:read("a")
    catalogue:close()
    local meta = pandoc.read("---\n" .. contenu .. "\n---\n", "markdown").meta
    for _, entree in ipairs(meta.cours or {}) do
      if entree.slug then
        table.insert(liste, { slug = texte(entree.slug), titre = entree.titre, en_ligne = false,
                              prerequis = entree["prerequis-cours"] })
      end
    end
  end
  return liste
end

-- Un cours désigné par son slug : lien s'il est en ligne, texte simple sinon (US-67).
local function lien_vers(slug, catalogue)
  for _, autre in ipairs(catalogue) do
    if autre.slug == slug then
      local titre = autre.titre or pandoc.Inlines(slug)
      if autre.en_ligne then
        return pandoc.Inlines({ pandoc.Link(titre, "/cours/" .. slug .. "/") })
      end
      -- Le cours existe au catalogue mais n'a pas de page : le nommer sans promettre un lien.
      return pandoc.Inlines(titre) ..
        pandoc.Inlines({ pandoc.Space(), pandoc.Emph(pandoc.Inlines("(bientôt en ligne)")) })
    end
  end
  -- Slug inconnu : la CI l'interdit (scripts/verifier_catalogue.py), et le rendu ne l'invente pas.
  return pandoc.Inlines({ pandoc.Code(slug) })
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

  -- Prérequis (US-67) : les cours du site d'abord, en liens, puis les prérequis en texte libre.
  -- Un étudiant lit une seule liste — ce qu'il doit avoir fait avant —, et la distinction entre
  -- les deux champs reste dans les données, où elle sert.
  local catalogue = tous_les_cours()
  local prerequis = pandoc.List({})
  for _, slug in ipairs(cours["prerequis-cours"] or {}) do
    prerequis:insert(lien_vers(texte(slug), catalogue))
  end
  for _, libre in ipairs(cours.prerequis or {}) do
    prerequis:insert(libre)
  end
  blocs:extend(liste("Prérequis", #prerequis > 0 and prerequis or nil))

  -- « Ce cours prépare à » : la relation inverse, calculée et jamais saisie.
  local moi = pandoc.path.filename(pandoc.path.directory(quarto.doc.input_file))
  local suites = pandoc.List({})
  for _, autre in ipairs(catalogue) do
    for _, slug in ipairs(autre.prerequis or {}) do
      if texte(slug) == moi then
        suites:insert(lien_vers(autre.slug, catalogue))
      end
    end
  end
  blocs:extend(liste("Ce cours prépare à", #suites > 0 and suites or nil))

  return blocs
end

-- Ressources du cours entier, et non d'un chapitre (US-59) : un sujet d'examen, par exemple, ne
-- relève d'aucun chapitre mais de tout le cours. Elles se déclarent dans `cours.yml`, sous la même
-- forme que celles d'une séance, et suivent les mêmes règles.
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

-- La colonne « Contenu » d'une séance montre sa description. Celle-ci commence par nommer le cours
-- et le numéro de la séance — « Séance 3 d'Introduction au Machine Learning : … », « Programmation
-- Python — Séance 3 — … » —, ce que la colonne « Séance » dit déjà, juste à côté. Cette part est
-- retirée **à l'affichage seulement** : la description de la page, elle, garde son contexte, parce
-- que c'est elle que lisent un moteur de recherche et un aperçu de lien (US-13).
local function contenu_seul(description)
  local texte = pandoc.utils.stringify(description)
  -- « Programmation Python — Séance 3 — Contrôle du flux » (tiret cadratin, sans deux-points).
  -- Les motifs Lua travaillent sur des octets : « [ée] » serait une classe des octets de « é »,
  -- qui en occupe deux en UTF-8, et ne reconnaîtrait donc pas « Séance ». Le mot est écrit en
  -- toutes lettres, ce qui est aussi bien plus clair.
  local apres_tiret = texte:match("^.*—%s*Séance%s+%d+%s*—%s*(.+)$")
    or texte:match("^.*—%s*Chapitre%s+%d+%s*—%s*(.+)$")
  if apres_tiret then
    return pandoc.read(apres_tiret, "markdown").blocks[1].content
  end
  -- « Séance 1 du cours Architectures Logicielles Modernes : dette architecturale… » et
  -- « Chapitre d'introduction du cours de Programmation C avancée : pourquoi le C… ».
  local apres_deux_points = texte:match("^Séance[^:]*:%s*(.+)$")
    or texte:match("^Chapitre[^:]*:%s*(.+)$")
  if apres_deux_points then
    return pandoc.read(apres_deux_points, "markdown").blocks[1].content
  end
  return description
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
      description = contenu_seul(description)
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
