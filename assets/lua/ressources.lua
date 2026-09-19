-- Slide « Ressources de la séance » (US-49).
--
-- L'import laisse un emplacement vide — `::: {#ressources-seance} :::` — et ce filtre le remplit au
-- rendu, avec le poids de chaque fichier et les seuls corrigés dont la date est atteinte. Si rien
-- n'est à montrer aujourd'hui, l'emplacement disparaît : pas de slide vide en fin de deck.

package.path = package.path .. ";" .. pandoc.path.directory(PANDOC_SCRIPT_FILE) .. "/?.lua"
local R = require("ressources-communes")

local TITRES = { fr = "Ressources de la séance", en = "Session resources" }

local langue, cours

function Pandoc(doc)
  langue = R.langue(doc)
  -- Le dossier du cours est le parent de `chapitres/`, où vit la séance.
  cours = pandoc.path.directory(pandoc.path.directory(quarto.doc.input_file))
  local visibles = R.publiables(doc.meta.ressources)

  local blocs = pandoc.Blocks({})
  for _, bloc in ipairs(doc.blocks) do
    if bloc.t == "Div" and bloc.identifier == "ressources-seance" then
      if #visibles > 0 then
        local items = {}
        for _, ressource in ipairs(visibles) do
          table.insert(items, pandoc.Plain(R.lien(ressource, langue, cours, false)))
        end
        blocs:insert(pandoc.Header(2, pandoc.Inlines(TITRES[langue])))
        blocs:insert(pandoc.BulletList(items))
      end
    else
      blocs:insert(bloc)
    end
  end
  doc.blocks = blocs
  return doc
end
