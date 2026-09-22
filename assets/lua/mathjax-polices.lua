-- MathJax : imposer aux présentations les polices TeX de MathJax, et non celles du lecteur.
--
-- Quarto fixe MathJax **2.7.9** pour les présentations revealjs ; les pages, elles, ont MathJax 4,
-- qui n'a pas ce défaut. MathJax 2 préfère une police mathématique **installée sur la machine du
-- lecteur** — STIX est livrée avec macOS — et place mal les composés qu'il en tire : « ŷ » s'affiche
-- « y^ », « X̃ » devient « X~ », « ⊤ » un T barré, « 𝜹 » perd son gras, et les accolades
-- horizontales de `\underbrace` sortent brisées. Le défaut dépend donc de la machine qui lit, ce qui
-- le rendait invisible : les cours de C et de Python comptent deux accents à eux deux, celui
-- d'Introduction au ML en compte plus de deux cents.
--
-- `window.MathJax` est lu par MathJax à son démarrage. Le greffon de reveal appelle ensuite
-- `MathJax.Hub.Config(options)` avec ses propres réglages, qui **complètent** celui-ci sans
-- l'effacer : il ne touche pas à la clé `HTML-CSS`.
--
-- Pourquoi un filtre et non `format: revealjs:` dans `_quarto.yml` : déclarer ce format au niveau du
-- projet demanderait à Quarto de rendre **chaque** page du site en présentation, en plus du HTML.
-- Le rendu s'interrompait sur le premier notebook.

local CONFIGURATION = [[
<script>
  window.MathJax = window.MathJax || {};
  window.MathJax["HTML-CSS"] = { availableFonts: [], preferredFont: null, webFont: "TeX" };
</script>
]]

function Pandoc(document)
  if quarto.doc.is_format("revealjs") then
    quarto.doc.include_text("in-header", CONFIGURATION)
  end
  return document
end
