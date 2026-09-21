# Correspondance LaTeX → Quarto (US-15)

Ce que `scripts/importer_chapitre.py` fait d'un deck Beamer de cours, et pourquoi. La référence est le
chapitre 1 du cours pilote (`cours/architectures-logicielles-modernes/_sources/cm1_archi_seance1.tex`,
20 frames) et le style `beamerucad.sty` qui l'accompagne.

Règle générale : **ce que le script ne sait pas convertir n'est jamais supprimé**. Il reste dans la page
en commentaire `<!-- NON CONVERTI: … -->` et figure dans le rapport de conversion.

## Structure

| LaTeX | Quarto | Remarque |
|---|---|---|
| `\documentclass[aspectratio=169]{beamer}` | `format: revealjs` | 16:9, comme le deck d'origine |
| `\title`, `\subtitle`, `\author`, `\institute` | en-tête YAML | la slide de titre est produite par Quarto |
| `\begin{frame}[plain]…\titlepage…\end{frame}` | *(supprimée)* | l'en-tête YAML la remplace |
| `\section{X}` | `# X` | slide de section (pile verticale, navigation linéaire) |
| `\begin{frame}{Titre}` | `## Titre` | une frame donne une slide |
| `[fragile]` et autres options de frame | *(ignorées)* | sans objet en HTML |

## Encadrés sémantiques

Les sept environnements de `beamerucad.sty` deviennent des callouts Quarto, avec une classe qui porte la
couleur d'origine (`assets/css/slides.scss`). Le titre optionnel — `\begin{ucaddef}[Dette architecturale]` —
devient le titre du callout ; sans lui, le titre par défaut de l'environnement est repris.

| Environnement | Titre par défaut | Callout | Classe | Couleur (filet et fond) |
|---|---|---|---|---|
| `ucaddef` | L'essentiel | `.callout-note` | `.ucad-def` | `#3b6fb0` |
| `ucadform` | Formellement | `.callout-note` | `.ucad-form` | `#7d3c98` |
| `ucadex` | Exemple | `.callout-tip` | `.ucad-ex` | `#2e8b57` |
| `ucadpiege` | Piège | `.callout-warning` | `.ucad-piege` | `#b1621c` |
| `ucadret` | À retenir | `.callout-important` | `.ucad-ret` | `#8a7008` |
| `ucadrec` | En pratique | `.callout-tip` | `.ucad-rec` | `#1f776c` |
| `ucadfront` | Pour aller plus loin | `.callout-note` | `.ucad-front` | `#1d7382` |

Le type de callout (`note`, `tip`, `warning`, `important`) porte le sens pour les lecteurs d'écran et les
technologies d'assistance ; la classe porte la couleur. Le titre est écrit dans une version assombrie de la
couleur (au moins 5,9:1 sur le fond teinté) : la teinte vive du filet plafonnait à 3,9:1.

## Contenu

| LaTeX | Quarto | Remarque |
|---|---|---|
| `\begin{itemize}` / `\begin{enumerate}` | liste à puces / numérotée | `\item` par élément |
| `\textbf{…}`, `\alert{…}` | `**…**` | |
| `\emph{…}`, `\textit{…}` | `*…*` | |
| `\texttt{…}` | `` `…` `` | |
| `\begin{lstlisting}` | bloc de code | langage déduit : `java`, ou `bash` pour une commande |
| `\begin{tabular}` + `booktabs` | tableau Markdown | `\newline` dans une cellule devient `<br>` |
| `$…$`, `$$…$$`, `\[…\]` | inchangés | rendus par MathJax |
| `{\small …}`, `{\scriptsize …}` | *(retirés)* | la taille est affaire de style |
| `\vskip`, `\centering`, `\par`, `\vfill` | *(retirés)* | idem |
| `\\`, `\\[2pt]`, `\\*` | `<br>` | saut de ligne ; l'espacement en plus est affaire de style |
| `\vspace{3pt}`, `\vskip 2ex`, `\vspace*{1cm}` | *(retirés)* | avec ou sans accolades, et quelle que soit l'unité |
| `\smallskip`, `\medskip`, `\bigskip` | *(retirés)* | idem |
| `\quad` | espace | sépare des éléments sur une même ligne |
| `\figslide{l}{fichier}{légende}` | figure + légende | macro de `beamerucad.sty` ; la légende sert de texte alternatif |
| `\resultat` | **Résultat →** | annonce la sortie du programme qui suit |
| `lstlisting[style=out]`, `[style=err]` | bloc sans langage | une sortie de programme n'est pas du code |
| `lstlisting[style=sh]` | ```` ```bash ```` | |
| `\oe` | `œ` | |
| `~` | espace insécable | sauf dans un code en ligne, où « ~ » désigne un dossier personnel |
| `\{`, `\}`, `\[`, `\]`, `\$`, `\%`, `\&`, `\_`, `\#`, `\~`, `\^{}` | le caractère lui-même | dans un **code en ligne**, la barre oblique disparaît — sinon elle s'affiche. Dans le **texte courant**, elle reste devant les caractères que Markdown interprète (`{}[]$_#~^`) : c'est alors une échappe Markdown, et non un reste de LaTeX |
| toute autre commande ou environnement | `<!-- NON CONVERTI: … -->` | et une ligne dans le rapport |

Les lignes de code ne sont pas numérotées : le deck d'origine ne les numérote pas, et les ancres que Quarto
ajoute pour cela portent un `aria-label` interdit sur un lien sans cible (relevé par axe-core).

## Figures

| LaTeX | Quarto | Remarque |
|---|---|---|
| `\includegraphics[width=0.6\linewidth]{nom}` | `{{< svg ../figures/nom.svg alt="…" largeur="60%" >}}` | shortcode de `_extensions/svg-inline` |
| `{\scriptsize …}` suivant l'image | `::: {.legende} … :::` | la légende reste visible sous la figure |

- **Texte alternatif** : la légende du `.tex` quand il y en a une ; sinon la phrase fournie par le PO dans
  `_sources/textes-alternatifs.toml` ; sinon un `TODO(PO)` visible, signalé dans le rapport. Le script
  n'invente jamais de description.
- **SVG incorporé, et non lié** : les figures utilisent `currentColor` pour suivre la couleur du texte. Dans
  une balise `<img>`, `currentColor` se résout dans le fichier SVG lui-même, donc en noir ; la figure doit
  faire partie de la page pour s'adapter au mode sombre et à la projection.
- **Nettoyage** (local, jamais en CI) : les encres et les gris (`#000`, `#1a3a5c`, `#1c2a33`, `#5a5a5a`,
  `#5a6b75`…) deviennent `currentColor` ; les fonds clairs des **formes** (`#fff`, `#f8f9fb`…) deviennent
  transparents ; `font-family` devient `inherit`. Le blanc est conservé sur les `<text>` : il y sert à écrire
  dans un bloc de couleur. Les couleurs d'accent (orange, vert, violet, jaune) sont conservées telles quelles.
- **Figure calculée** : `figA_cout_changement` n'est pas importée. Avec `--figure-python`, le script
  matplotlib du PO devient un **bloc Python exécuté** (US-18), dont Quarto gèle le résultat : la slide
  montre la figure, la légende du `.tex` la suit, et le code est repris juste en dessous dans un repli
  `<details>` — en revealjs, ni `code-fold` ni un callout `collapse` ne replient quoi que ce soit. Les
  lignes d'export du script (`matplotlib.use`, `savefig`, `print`) sont retirées et comptées dans le
  rapport : dans un bloc exécuté, la figure est affichée par Quarto. Sans `--figure-python`, le script
  laisse à la place un commentaire `<!-- FIGURE CALCULÉE (US-18) : … -->`.

## Ce que la conversion ne fait pas

- Elle ne relit pas le texte : les coquilles du `.tex` se retrouvent dans les slides.
- Elle ne découpe pas une slide trop chargée : c'est un choix pédagogique, pas un choix de conversion.
- Elle ne produit pas de PDF. Un deck s'imprime depuis le navigateur (`?print-pdf`) ; la génération
  automatisée est prévue en US-17.

## Un CM rédigé vers une page (US-40)

Le document est un `article`, et non un deck : `--cible page` produit une **page** de cours, avec sa
table des matières latérale, là où la cible par défaut produit des slides.

| LaTeX | Quarto | Remarque |
|---|---|---|
| `\section{…}` | `## …` | le niveau 1 est le titre de la page |
| `\subsection{…}` | `### …` | et `\subsubsection` un niveau de plus |
| `\maketitle` | *(retiré)* | l'en-tête YAML porte le titre |
| `\title{…}` | `title:` | souvent une **couverture** LaTeX, avec le sous-titre et la promotion : `--titre` le remplace par le titre de la page |
| `\begin{monencadre}{Titre}` | `::: {.callout-… title="Titre"}` | déclaré par `--encadre nom=genre\|titre` : le sens d'un encadré est une décision du PO, jamais une déduction. Le titre est ici entre **accolades**, là où Beamer le met entre crochets |
| `\begin{tikzpicture}` | *(non converti)* | US-55 |

Le **numéro affiché** d'un chapitre est une donnée à part (`--numero`) : un cours peut commencer à
`-1` ou à `0` — le chapitre d'introduction de *Programmation C avancée* est le « -1 » —, et le nom du
fichier ne sert qu'à ordonner. Sans numéro, la page porte son seul titre.
