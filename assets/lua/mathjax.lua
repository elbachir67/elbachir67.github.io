-- MathJax dans les présentations : la version 4, celle des pages, et ses propres polices.
--
-- Quarto fixe MathJax **2.7.9** pour les présentations revealjs, là où les pages ont MathJax 4.
-- Deux défauts de rendu en sont venus : les accents mal placés (« ŷ » affiché « y^ »), parce que
-- MathJax 2 préfère une police installée sur la machine du lecteur ; et les matrices de mathtools
-- affichées en TeX brut dans un cadre, sans le dire. Le PO a demandé d'aligner les présentations
-- sur la version 4.
--
-- Comment. Quarto écrit `plugins: [… RevealMath …]` et charge `plugin/math/math.js`, qui assigne
-- `window.RevealMath` — le greffon **MathJax 2**. Rien dans Quarto ne permet d'en changer. Ce
-- script, posé dans l'en-tête, s'exécute **avant** `math.js` et avant `Reveal.initialize` : il
-- détourne la propriété globale pour rendre au lieu du greffon une coquille qui ne fait rien, puis
-- charge MathJax 4 lui-même et redemande la mise en page une fois les formules composées.
--
-- Ce que cela ne règle pas : MathJax 4 ne connaît pas mathtools non plus. `psmallmatrix` lui tire
-- un « Unknown environment » en rouge au lieu d'un cadre silencieux — plus lisible, mais fautif
-- tout de même. La réécriture des petites matrices à l'import reste donc nécessaire, et le
-- contrôle de `verifier_latex.py` avec elle.
--
-- Le réglage des polices de MathJax 2 est conservé : il ne coûte rien, et il protège si la
-- version venait à rebasculer.

-- Délimiteur long : le JavaScript contient « ]] », qui fermerait une chaîne ordinaire.
local CONFIGURATION = [==[
<script>
  window.MathJax = {
    // MathJax 2, si la version rebascule : ses propres polices TeX, et non celles du lecteur.
    "HTML-CSS": { availableFonts: [], preferredFont: null, webFont: "TeX" },
    // MathJax 4 : Quarto écrit les formules avec les délimiteurs de LaTeX.
    tex: { inlineMath: [["\\(", "\\)"]], displayMath: [["$$", "$$"], ["\\[", "\\]"]] },
    options: { skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"] },
    // MathJax 4 compose un peu plus grand que la version 2 : sans ce réglage, la slide
    // « Pourquoi 63 % ? le calcul détaillé » de la séance 8 dépassait le cadre de 32 unités.
    // C'est un réglage de taille, et non une décision de contenu.
    chtml: { scale: 0.95 },
    startup: {
      ready: function () {
        MathJax.startup.defaultReady();
        MathJax.startup.promise.then(function () {
          // Les formules composées changent la hauteur des slides : reveal doit les recentrer.
          if (window.Reveal && typeof Reveal.layout === "function") { Reveal.layout(); }
        });
      }
    }
  };

  // Le greffon de Quarto est neutralisé : on rend une coquille inerte à sa place. Sans cela,
  // MathJax 2 se chargerait par-dessus et écraserait `window.MathJax`.
  (function () {
    var garde;
    Object.defineProperty(window, "RevealMath", {
      configurable: true,
      get: function () { return { id: "mathjax-neutralise", init: function () {} }; },
      set: function (valeur) { garde = valeur; }
    });
  })();
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
]==]

function Pandoc(document)
  if quarto.doc.is_format("revealjs") then
    quarto.doc.include_text("in-header", CONFIGURATION)
  end
  return document
end
