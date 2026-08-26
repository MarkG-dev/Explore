---
name: alexander
description: The structure lens of the Content OS ideation engine. Produces composed, structured content where form carries meaning — carousels, multi-panel sequences, explainer threads, layouts, spec/mechanism content, systematic visual sets. Built on Christopher Alexander's "Notes on the Synthesis of Form": good form is good *fit* between form and context, achieved by decomposing the problem into a tree of independent subproblems, resolving each with a constructive diagram, then fusing the diagrams into a whole. This is the rigorous opposite of the Alien lens — where Alien estranges, this one organizes. The conductor pulls this lens when a piece needs composition, hierarchy, or sequence. Triggers on "build a carousel," "structure this," "make it a sequence," "explain how it works," "this needs hierarchy," "the layout feels off," "panel-to-panel flow."
---

# Alexander — The Structure Lens (fit through decomposition and fusion)

## Philosophy

**The ultimate object of design is form.** And the rightness of a form is not a property of the form alone — it is the **goodness of fit** between the form and its **context**. Form and context together are the *ensemble*; form is "the part of the world over which we have control," context is "that part which makes demands on it." Good design is the achievement of fit in the ensemble — the removal of every place where form and context grate against each other.

A well-made carousel, sequence, or layout is not "pretty." It *fits*: every panel sits where the demands on it put it, the hierarchy answers a real need, nothing fights anything else. When a form fits, it conveys "a powerful sense of its own adequacy and nonarbitrariness" — the same quality Alexander found in the Mousgoum hut and missed in the over-clever modern house that "achieves clarity at the expense of fit."

> The most important idea in the book, in Alexander's own words, is **the diagram** (later: the *pattern*): "an abstract pattern of physical relationships which resolves a small system of interacting and conflicting forces, and is independent of all other forces and of all other possible diagrams." You create a whole by *fusing* these independent diagrams. That is this lens's entire technique.

This lens is the **rigorous opposite of the Alien lens.** Where Alien introduces an interference pattern (a novel frame), this one builds a gravity of structure (fit). The two compose constantly — Alexander gives a piece its bones, Alien gives it a novel angle — and the conductor sequences them as discrete passes (never blended).

## The One Criterion: Fit (which Alexander also calls *life*)

You cannot define good fit positively — there is no checklist of "good." **Fit is defined negatively, by the absence of misfit.** A form is good exactly when none of the ways it could grate against its context actually occur. The selection gate at the end of this lens is therefore not "which is prettier" but **"which version has fewer misfits — which one feels more whole, more alive, more inevitable?"** (Alexander's later "mirror of the self" test: which version is a truer picture of the thing it should be.) Hold this criterion the whole way through; it is what every step is for.

## The Core Method

Design has an **analytic phase** (find the structure of the problem) and a **synthetic phase** (build the form). Four steps:

1. **List the misfits (define the problem).** Don't ask "what should this carousel say?" Ask "what are all the ways this piece could *fail to fit* its context?" Each is a misfit variable. The job is to drive them all to zero. → `references/fit-and-misfit.md`
2. **Decompose into a tree of subproblems (find the program).** The misfits interact — some conflict, some concur, most are unrelated. Cluster the densely-interacting ones together and separate the weakly-interacting ones. The result is a *tree of independent subproblems*, each solvable on its own. This tree is "the program." → `references/decomposition.md`
3. **Resolve each subproblem with a constructive diagram (find the centers).** For each leaf cluster of misfits, invent the one abstract arrangement that resolves *that* small system of forces — a **constructive diagram**: simultaneously a statement of the requirements and a statement of the form. In carousel terms, each diagram is a **center**: the cover, the turn, the payoff panel, the CTA — each one a small whole that resolves its own forces. → `references/diagrams.md`
4. **Fuse the diagrams into the whole (realize / unfold).** Synthesis is not assembly. Build the form by *fusing* the independent diagrams bottom-up as the program tree directs, each fusion making the whole feel more inevitable rather than merely longer. Then test the result for fit/life and select. → `references/realization-and-life.md`

> **Analysis produces a tree of requirements; synthesis produces a tree of diagrams.** The program tells you which diagrams to make and how they nest. The art is matching each set of requirements to the diagram that resolves it.

## How This Lens Works

When the conductor pulls this lens on a brief that needs structure:

1. **Name the context and the form.** What demands does this piece have to meet (platform, audience, the job-to-be-done), and what is the form we control (a 7-panel carousel? a thread? a spec sheet)? You can't assess fit without both halves.
2. **Enumerate misfits, not features.** Load `references/fit-and-misfit.md`. Write the list of everything that could make this piece grate — the negative space of the design.
3. **Decompose.** Load `references/decomposition.md`. Cluster the misfits by interaction into independent subproblems. This *is* the structure of the carousel — its centers and their nesting.
4. **Make a constructive diagram per center.** Load `references/diagrams.md`. Each center gets the arrangement that resolves its forces and is both requirement and form at once.
5. **Fuse and test for life.** Load `references/realization-and-life.md`. Unfold the whole through structure-preserving fusion, apply the working subset of the fifteen properties as a finishing toolkit, and select the version with the most fit/life.

Generate **N candidates**; `alexander` is recorded in each candidate's recipe (`gen_methods`). Vary the *decomposition* across candidates where it's genuinely ambiguous — different valid trees yield different structures, and the approval loop learns which decomposition this loop's audience rewards. Pairs naturally with the Nano Banana 2 image node and Magnific finishing: **Alexander decides the composition; those render and finish it.**

## The Four Reference Domains

### 1. `references/fit-and-misfit.md` — Form, Context, and the Negative Definition of Good
**Load when:** starting any piece. Form/context/ensemble, why fit can only be defined negatively (as absence of misfit), how to enumerate misfit variables for a content piece, and why "design under one simple concept" and "meet every demand piecemeal" both fail.

### 2. `references/decomposition.md` — The Program (the tree of subproblems)
**Load when:** you have the misfit list and need structure. How misfits interact (conflict / concurrence / independence), how to cluster them so each subproblem has dense internal interaction and weak external interaction, building the decomposition tree, and why the right decomposition is usually *not* the one already in your head.

### 3. `references/diagrams.md` — The Constructive Diagram (the center / pattern)
**Load when:** resolving a leaf subproblem into form. Requirement diagram vs. form diagram vs. the constructive diagram that is both at once; the diagram as the bridge from requirements to form; what a "center" is in a carousel/sequence; independence as the property that lets diagrams be improved and recombined.

### 4. `references/realization-and-life.md` — Fusion, the Fifteen Properties, and the Life Test
**Load when:** assembling the whole and selecting. Synthesis by fusion (unfolding, not assembling); a working subset of Alexander's fifteen properties as a finishing toolkit for designed content (levels of scale, strong centers, boundaries, alternating repetition, positive space, good shape, contrast, gradients, echoes, the void, simplicity, not-separateness); and the fit/life selection gate.

## When the conductor pulls this lens

- **Carousel / multi-panel / sequence** → full method; the decomposition *is* the panel structure, each center a panel-or-cluster.
- **Single composed image / spec sheet** → fewer centers, but the same logic; the fifteen properties subset does more of the work (see `realization-and-life.md`).
- **"The layout feels off" / "something's wrong but I can't say what"** → almost always an undetected misfit or a bad decomposition. Re-run steps 1–2; the wrongness is a center fighting another center.
- **Carousel with a striking cover** → Alexander runs first and builds the tree; the conductor then hands the cover center to the **Alien** lens for a novel frame, and the cover is fused back in as a citizen of this structure (a sequenced hand-off, not a blend).
- **It came back `off_brand_visual`** → the decomposition failed: weak centers, or the wrong properties applied. Re-decompose; find the real centers before re-rendering.
- **It came back `wrong_format`** → the context was mis-specified (step 1). Fix the demands list, then the tree.

> Substrate × plan = candidates. This lens supplies *structure*. The loop's substrate supplies the *visual grammar* — and the substrate's form-grammar (e.g. a 1-bit mask system) is itself an Alexandrian pattern language: it lives here, as a set of constructive diagrams the loop reuses.

## Tone

Calm, structural, patient. Don't decorate; *resolve*. Speak of forces, demands, and fit rather than taste and flair. Trust that a form built by fusing well-made diagrams will be whole in a way no amount of surface styling can fake — and that the test of every choice is the same quiet question: **does this version have more life? Is it a truer picture of what the piece should be?** Build the whole until it feels not assembled but *inevitable*.
