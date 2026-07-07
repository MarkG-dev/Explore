---
name: loopx-design
description: Use this skill to generate well-branded interfaces and assets for Loop X, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.
If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.
If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Quick orientation:
- Loop X = machine vision / thermal perception for uncontrolled environments (mining). Monochrome, high-contrast, austere-industrial.
- Palette: black #000000, white #FFFFFF, off-white #F7F7F7, grey #C4C4C4; red #FF0000 rare stroke accent only.
- Type: Aeonik (headlines uppercase / body sentence case) + DM Mono (labels, links, technical). Aeonik is substituted with Hanken Grotesk — see README.
- Signature shape: the chamfered / cut-corner rectangle (`.lx-chamfer`), echoing the LOOP X letterforms. Corners cut, never rounded. No shadows, no gradients (except hero legibility), no emoji.
- Link `styles.css` for tokens; components load from the compiled bundle on `window.DesignSystem_d0e166`.
