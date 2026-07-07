# Loop X — Design System

Design system for **Loop X**, a machine-vision company building *all condition intelligence* — thermal perception that works with no tag, no map, and no light required. Its products serve the hardest, most dangerous environments: underground and surface mining, dust, glare, and total dark. Positioning: **"machine intelligence for uncontrolled environments."**

This system was reverse-engineered from the **"Loop X — Guidelines"** Figma brand book (34 guideline frames + 3 layout components; design by Spacecadet Studio®). Products/surfaces glimpsed in the book: the marketing website, product interfaces, presentation slides, and printed applications (business cards, roll-ups). Named products include the **Collision Avoidance System**, **Load Sight System**, and **LoopX SLAM**.

> Source of truth: the attached Figma file. Values here (colors, type sizes, geometry, the wordmark vectors) are transcribed verbatim from it.

---

## Content fundamentals — how Loop X writes

- **Voice:** intelligence-led authority. Confident, spare, declarative. "The most dangerous environments deserve the most intelligence." "Autonomy is won in the dark."
- **Two registers held together:** the *grounded* (precise, material, data-dense — the reality of the mine and proprietary thermal perception) and the *expansive* (ambitious, frontier-facing — the clarity of all-condition intelligence). Good Loop X work holds both.
- **Person:** collective **"we"** ("So we started where it's hardest"); addresses the reader plainly, no hype. Clarity is a value — "an operations lead gets it on the first scroll."
- **Casing:** display/headlines set **UPPERCASE** (e.g. ALL CONDITION INTELLIGENCE); body is **sentence case**; labels, eyebrows, links, technical detail set **UPPERCASE mono**.
- **Punctuation & tone:** em dashes for asides; short paragraphs; no exclamation. Technical specificity is welcome (LiDAR, RF, 360° detection, inertial fusion).
- **No emoji.** Never. The only non-alphabetic marks are the `>` link cue and the ® / © in credits.
- **Example lines:** "All condition intelligence" · "Machine intelligence for uncontrolled environments" · "> More info" · "Earned underground".

## Visual foundations

- **Palette:** relentlessly monochrome. Black `#000000` and white `#FFFFFF` as the high-contrast core (contrast drives brand recognition), off-white `#F7F7F7` for readable light surfaces and on-dark text, grey `#C4C4C4` for structure, deck grey `#383838` for backing. **Red `#FF0000` exists only as a rare technical stroke accent** — never a fill.
- **Type:** **Aeonik** (primary) for headlines, titles and body — uppercase headlines at ~90% leading, sentence-case body at 100–120%. **DM Mono** (secondary) for eyebrows, labels, links, UI and technical detail, uppercase. See the font substitution note below.
- **Signature geometry:** the **chamfered / cut-corner rectangle** (`.lx-chamfer`, default 7px) — echoing the notched LOOP X letterforms. It appears on buttons, nav items, label pills, cards and framed media. **Corners are cut, never rounded** (a 15px radius appears rarely on a few light panels only).
- **Layout:** a wide document grid — 50px page margins, a fixed label/sidebar column (471px) beside a large content column (1329px), separated by hairline rules. Everything is square-edged and orthogonal.
- **Backgrounds:** solid black or off-white; full-bleed photography on heroes; no gradients as decoration (only black protection gradients over hero imagery for legibility).
- **Photography:** black-and-white, high-contrast, grainy — terrain and rock, dust/particle clouds on black, cave/underground, thermal captures. Cool, austere, austere-industrial. Always desaturated (`grayscale(1)`), pushed contrast.
- **Borders & shadows:** hairline borders (0.5–1.3px) in black or off-white; essentially **no drop shadows** — depth comes from contrast and the cut-corner silhouette, not elevation.
- **Motion:** restrained. Short fades / opacity on hover (`a:hover` → 0.6; buttons/nav → ~0.62), standard easing (`cubic-bezier(.4,0,.2,1)`), 120–220ms. No bounces, no decorative loops.
- **Hover / press:** hover = reduced opacity; active/selected nav = solid ink fill (inverse). Selection highlight uses the signal red — a single spark.
- **Cards:** chamfered panels with a hairline border; flat fills (black, off-white or grey); no rounding, no shadow.

## Iconography

- **Approach:** minimal and drawn from the geometry, not a decorative icon set. The one recurring "icon" is the **directional arrow** paired with mono link/CTA text (`> More info`, the arrow inside the chamfered button — see `assets/icons/button-frame.svg`).
- **Brand marks:** the **LOOP X wordmark** (custom cut-corner letterforms) and its **symbol** (the standalone X) are the primary graphic devices — both recreated as vector in `Logo.jsx` and paint in `currentColor`. Never redraw, recolour internally, stretch or decorate them.
- **No icon font, no emoji, no Unicode-glyph icons.** If a functional UI icon set is ever needed, add a thin (~1.3px) monoline set and record it here as an intentional addition; the source does not define one.

## Components

Reusable primitives (React, styled via CSS custom properties), bundled to `window.DesignSystem_d0e166`:

- **Logo** (`components/brand/`) — official wordmark + standalone symbol; `currentColor` SVG.
- **Button** (`components/controls/`) — chamfered DM Mono control; outline / solid / ghost, dark/light tone, optional arrow.
- **Eyebrow** (`components/content/`) — mono uppercase label, optionally in a chamfered hairline frame.
- **ProductCard** (`components/content/`) — chamfered, hairline-framed product/feature tile with a "more info" action.
- **Navbar** (`components/navigation/`) — wordmark + chamfered mono nav items with a solid active pill.
- **Panel** (`components/layout/`) — the signature chamfered surface / card (light, dark, muted, grey tones).
- **PageHeader** (`components/layout/`) — document header bar (mono labels over hairline rules + index marker).

### Intentional additions
The Figma file is a brand book, not a component library — it defines only three generic layout-helper symbols (`Component 1` a header bar, `Component 2` a sidebar title block, `Frame 316129128` a title+body column). It contains **no standard-named UI component families**. Therefore **all seven components in this system are intentional additions**, and each is confirmed below as derived from the source (not invented):

- **Logo** — the LOOP X wordmark + symbol, transcribed vector-for-vector from the brand file's logotype artwork.
- **PageHeader** — folds in `Component 1` (the "LOOP X / BRAND GUIDELINES / page no." header bar).
- **Button** — the chamfered "MORE INFO" / "> Know More" control used across the site and slides.
- **Eyebrow** — the mono label / framed "EYEBROW TEXT" pill above headlines.
- **ProductCard** — the chamfered product tile (Collision Avoidance System, etc.) from the website/deck.
- **Navbar** — the wordmark + chamfered nav-pill bar from the website hero.
- **Panel** — the chamfered surface underlying the framed media and content blocks throughout.

None is a primitive a design system "usually has" bolted on speculatively — each mirrors an applied pattern in the source.

## Font substitution ⚠︎

**Aeonik** is a licensed typeface (CoType Foundry) and is **not** bundled. **Hanken Grotesk** (Google Fonts) is loaded as the nearest free grotesque substitute so specimens render sensibly. **DM Mono** is exact. To go to production, add licensed Aeonik web files and swap `--font-primary` in `tokens/typography.css`. *Please supply Aeonik web fonts if you have a license.*

## Index / manifest

- **styles.css** — global entry point (imports only). Consumers link this.
- **tokens/** — `fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `base.css`.
- **components/** — `brand/Logo`, `controls/Button`, `content/Eyebrow` + `content/ProductCard`, `navigation/Navbar`, `layout/Panel` + `layout/PageHeader`. Each has `.jsx` + `.d.ts` + `.prompt.md` + a `@dsCard` HTML.
- **guidelines/** — foundation specimen cards (Colors, Neutrals, Signal; Aeonik display/body, DM Mono; spacing scale, chamfer geometry; photography, logotype on grounds).
- **ui_kits/website/** — interactive marketing-site recreation (`index.html` + `screens.jsx`).
- **ui_kits/slides/** — presentation slide layouts (title, content, agenda, chapter, three-up).
- **templates/** — starter artifacts consuming projects can seed from: `website/` (dark hero site) and `deck/` (title + content slides), each composing the components.
- **assets/img/** — monochrome photography. **assets/icons/** — button frame SVG.
- **SKILL.md** — Agent Skill wrapper.

> **No standalone logo file was provided in the source**; the wordmark and symbol are recreated as vector paths in `Logo.jsx` (transcribed from the Figma artwork). There is no separate logo image asset to copy.
