# Talk outline

Source of truth for the talk's structure. `slides.qmd` follows this; keep them in sync.

## Frame

- **Title:** Industry Skills I Learnt and Didn't Learn in B Math
- **Audience:** _(reunion crowd — TBD)_
- **Length:** ~25 min talk + ~5 min Q&A
- **One-sentence goal:** _(TBD)_

## Time budget (~25 min)

| Part | Time | Notes |
|------|------|-------|
| Intro + photos | ~3 min | |
| § 1 · Taught + Useful | ~4–5 min | shortest |
| § 2 · Not taught + Useful | ~6–7 min | longest, most points |
| § 3 · Taught + Harmful | few points, but slow | take my time; must land hard |
| Takeaway | ~1 min | single slide |

## Style rules (non-negotiable)

- **Laconic slides.** Few words. Each word earns its place. Anything spoken live is NOT on the slide.
- **Deliberate reveals.** Some points are hidden / reworded / re-revealed for effect. Never pre-empt a reveal. When in doubt, ask.

## The organizing device: a 2×2

Grid axes shown to the audience: **Taught in B Math** vs **Not taught** × **Useful in industry** vs **Not useful**.

|                    | Useful in industry | Not useful |
|--------------------|--------------------|------------|
| **Taught in B Math**   | § 1  Taught + Useful   | § 3  quadrant = "Taught + Not useful" |
| **Not taught in B Math** | § 2  quadrant = "Not taught + Useful" | — (irrelevant, skip) |

The **section names** deliberately diverge from the grid labels:

1. **"Taught + Useful"** — matches the grid
2. **"Not taught + Needed"** — grid says *useful*, section is named **needed** *(switch)*
3. **"Taught + Harmful"** — grid says *not useful*, section is named **harmful** *(switch)*

> The fourth quadrant (not taught + not useful) is irrelevant and dropped.

> Names are internal placeholders. Final on-slide wording is tweaked later, point by point.

## Structure

### Intro (~3 min)
1. **Disclaimer slide** _(content TBD — user will dictate)_
2. **Batch photo** slide
3. **In-memoriam** slide — a friend who is no more
4. **2×2 matrix** slide — show the grid, then jump into the sections

### Core — § 1 · Taught + Useful  (~4–5 min, shortest)
High-level points (each may span multiple slides):
- **[1a · rigour]** modular problem solving, precise thought, rigour — all broadly similar
- **[1b · detach]** ability to change your mind; don't tie your person to your argument — you're okay to be proven wrong

### Core — § 2 · Not taught + Needed  (~6–7 min, longest)
- **[2a · communication]** communication, sales *(cover quickly)*
- **[2b · good-enough]** don't let perfection be the enemy of the good — "decent + quick" ≫ "perfect + slow" (not always) *(cover quickly)*
- **[2c · politics]** politics — getting people with different agendas to agree and do what you need; collaboration

### Core — § 3 · Taught + Harmful  (few points, slow, must land hard)
- **[3a · do-it-yourself]** do everything yourself
- **[3b · math-logic]** mathematical logic

### Takeaway (1 slide)
- Three columns, one per section; each section's points restated precisely underneath.
- A quick single-slide overview of the whole talk.

## Reveal plan

- **Grid shown upfront, fully labeled** — axes read **Useful** vs **Not useful**. Walk it later.
- **Two relabels (don't telegraph):**
  - § 2 quadrant reads "Not taught + Useful"; the section is *named* **"Not taught + Needed"** (useful → needed).
  - § 3 quadrant reads "Taught + Not useful"; the section is *named* **"Taught + Harmful"** (not useful → harmful). This is the payoff.

## Visual system (built in `slides.qmd` / `theme.scss`)

- **Quadrant colours:** §1 green `#2e8b6b` · §2 blue `#0b6e99` · §3 red `#c1452b` · Q4 grey (irrelevant).
- **Intro matrix slide:** full 2×2, grid labels (Useful / Not useful).
- **Section headers:** section-colour background + mini 2×2 with the active quadrant highlighted (callback); the highlighted cell shows the *relabel* (Needed / Harmful).
- **Content slides:** light tint of the section colour + a corner label pill naming the section.
- **Takeaway:** three colour-topped columns, one per section.
- Flat horizontal deck (dividers are `##` with `.sechead`, not `#`, to avoid vertical nesting).

## Open questions

- ...
