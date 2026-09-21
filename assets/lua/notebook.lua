-- Notebooks de TP rendus en page (US-50).
--
-- Un notebook déclaré comme ressource est rendu en page lisible : code coloré, sorties, figures —
-- telles que le PO les a enregistrées, puisque rien n'est réexécuté. La page porte deux boutons :
-- télécharger le fichier, et l'ouvrir dans Google Colab.
--
-- Le filtre est global mais ne fait rien ailleurs : il ne s'applique qu'aux pages issues d'un
-- `.ipynb`.

local DEPOT = "elbachir67/elbachir67.github.io"
local BRANCHE = "main"

local MOTS = {
  fr = { telecharger = "Télécharger le notebook", colab = "Ouvrir dans Colab",
         note = "Les sorties sont celles enregistrées dans le notebook : rien n'est réexécuté.",
         sortie = "Figure produite par le code de la cellule précédente." },
  en = { telecharger = "Download the notebook", colab = "Open in Colab",
         note = "Outputs are those stored in the notebook: nothing is re-executed.",
         sortie = "Figure produced by the code in the preceding cell." },
}

function Pandoc(doc)
  local entree = quarto.doc.input_file
  if not entree:match("%.ipynb$") then
    return doc
  end

  local langue = pandoc.utils.stringify(doc.meta.lang or "fr"):sub(1, 2)
  local mots = MOTS[langue] or MOTS.fr
  local racine = quarto.project.directory
  -- Chemin du notebook dans le dépôt : Colab lit le fichier depuis GitHub, pas depuis le site.
  local relatif = entree:sub(#racine + 2)
  local fichier = pandoc.path.filename(entree)

  local boutons = pandoc.Div({
    pandoc.Plain({
      -- Le téléchargement vise le notebook copié à côté de la page, et force l'enregistrement :
      -- ouvert dans le navigateur, un .ipynb ne serait que du JSON.
      pandoc.Link(pandoc.Inlines(mots.telecharger), fichier, mots.telecharger,
        { class = "btn btn-primary btn-sm", download = "" }),
      pandoc.Space(),
      pandoc.Link(pandoc.Inlines(mots.colab),
        "https://colab.research.google.com/github/" .. DEPOT .. "/blob/" .. BRANCHE .. "/" .. relatif,
        mots.colab, { class = "btn btn-outline-primary btn-sm" }),
    }),
    pandoc.Plain({ pandoc.Emph(pandoc.Inlines(mots.note)) }),
  }, { class = "notebook-boutons" })

  -- Le référencement exige une description par page. Celle-ci vient du notebook : sa première
  -- phrase, écrite par le PO — jamais une phrase inventée ici.
  if not doc.meta.description then
    for _, bloc in ipairs(doc.blocks) do
      if bloc.t == "Para" then
        local phrase = pandoc.utils.stringify(bloc):gsub("%s+", " ")
        local point = phrase:find("%. ")
        phrase = point and phrase:sub(1, point) or phrase
        if #phrase > 40 then
          doc.meta.description = pandoc.MetaString(phrase)
          break
        end
      end
    end
  end

  -- Les figures produites par le code n'ont pas de texte alternatif : personne ne les a écrites,
  -- elles sortent d'une exécution. On ne décrit pas ce qu'elles montrent — ce serait inventer —,
  -- mais on dit **d'où elles viennent**, ce qu'un lecteur d'écran a besoin de savoir pour
  -- comprendre qu'il peut lire le code juste au-dessus.
  doc.blocks = doc.blocks:walk({
    Image = function(image)
      if #image.caption == 0 and not image.attributes.alt then
        image.caption = pandoc.Inlines(mots.sortie)
        image.attributes.alt = mots.sortie
        return image
      end
    end,
  })

  quarto.doc.include_text("after-body", '<script src="/assets/js/notebook-defilement.js"></script>')
  doc.blocks:insert(1, boutons)
  return doc
end
