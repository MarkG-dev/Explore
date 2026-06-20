# Decomposition — The Program (the tree of subproblems)

*The analytic heart of the method. You have a list of misfits; this stage finds the hidden structure that turns an unmanageable problem into a set of small, independent, solvable ones. From "Notes on the Synthesis of Form," chapters 6–8 and Appendix 2.*

## The problem with the misfit list

A real design problem has too many misfits to hold in the mind at once. Alexander's worked example — a village — had **141** misfit requirements. You cannot solve 141 things simultaneously, and you cannot solve them one at a time either, because they *interact*: fixing one breaks another. The list alone is overwhelming. What rescues it is **structure**.

## Misfits interact in three ways

Between any two misfits, exactly one of three relationships holds:

- **Conflict** (negative link) — solving one makes the other harder. (A bold full-bleed cover image vs. the need for a legible headline: the more dramatic the image, the harder the text is to read.)
- **Concurrence** (positive link) — solving one helps solve the other; they have common physical implications. (A strong reading-order and a clear visual hierarchy reinforce each other.)
- **Independence** — they don't interact at all. (The cover's stopping power and the CTA's wording barely touch.)

Links can also be **weighted** by strength of interaction. The misfits plus their links form a graph Alexander calls **G(M, L)** — "a picture of the designer's view of the problem." Its single most important feature is its **articulation**: how the misfits clump.

## The goal: clusters of dense internal interaction, weak external interaction

> Find a grouping of the misfits such that **interaction *within* each group is dense, and interaction *between* groups is weak.**

This is the whole game. A cluster whose members interact tightly with each other but barely with anything outside is a **subproblem with its own integrity** — it can be solved on its own without disturbing the rest. Alexander's analogy: a system of lights where flipping one flips others; if it decomposes into independent subsystems, you can settle each subsystem separately and the whole reaches order far faster than if everything is tangled.

> "Each subproblem will have its own integrity, and be independent of the other subproblems, so that it can be solved independently."

For a carousel, the clusters *are* the natural units of the piece: the misfits about stopping the scroll cluster into "the cover problem"; the misfits about earning each swipe cluster into "the flow problem"; the misfits about landing the insight cluster into "the payoff problem"; the misfits about converting cluster into "the CTA problem." Each is a **center** (see `diagrams.md`).

## Building the decomposition tree

The decomposition is a **tree (hierarchy of nested sets)**:

- The top is the whole problem M (all misfits).
- It splits into a few major subproblems (the densely-interacting clusters).
- Each splits again, down to leaves that are small enough to resolve with a single diagram.
- Rule: subproblems at the same level don't overlap, and a parent is exactly the union of its children.

> "A decomposition of a set of misfits M is a tree of sets... Each subset which appears in the tree defines a subproblem, each with its own integrity, solvable independently."

This tree is what Alexander calls **the program**: not a list of requirements, but a *reorganization of the way you think about the problem* — directions telling you which clusters are the significant pieces and the order to address them.

## The right decomposition is usually NOT the one in your head

> "For every problem there is one decomposition which is especially proper to it, and this is usually different from the one in the designer's head."

The decomposition you arrive at by habit ("cover, then three value props, then CTA") is a *conventional* tree, not necessarily the one the actual interactions favor. The discipline is to let the **links decide the clusters**, not the template. Two misfits you'd never group by convention may interact so densely that they belong in the same center; two you'd habitually pair may be independent and belong apart. When a designed piece feels subtly wrong, the cause is usually a decomposition that follows the template instead of the forces.

**This is also where candidate variance comes from.** Where the decomposition is genuinely ambiguous — more than one valid clustering of the misfits — generate a candidate per tree. Different valid decompositions yield structurally different carousels, and the approval loop learns which structure this loop's audience actually rewards. (Tag each `gen_method = alexander`; the structural difference is the training signal.)

## How to do it in practice (the fast version)

Alexander's formal method uses graph partitioning; in practice, for a single content piece, run the lightweight version:

1. **Write each misfit on its own.** (From `fit-and-misfit.md`.)
2. **Draw the strong links.** For each pair, mark conflict / concurrence / nothing, weighting the strong ones. You're looking only for the *dense* interactions; ignore the faint ones.
3. **Let clusters fall out.** Misfits that link densely to each other and weakly to everything else form a cluster. Name each cluster by the job it does ("the cover problem").
4. **Nest the clusters into a tree.** Group related clusters under larger ones until you reach a clean hierarchy whose leaves are each small enough to resolve with one diagram.
5. **Check independence.** If two clusters still interact strongly, the decomposition is wrong — either merge them or find the misfit that actually bridges them and reassign it. Subproblems must be genuinely separable, or fusion (`realization-and-life.md`) will fail later.

## The handoff

Output of this stage: a **program** — a tree of independent subproblems (centers), each a small cluster of densely-interacting misfits, each solvable on its own. Carry the leaves into `diagrams.md`, where each becomes a constructive diagram. Carry the tree itself into `realization-and-life.md`, where it directs the order of fusion.
