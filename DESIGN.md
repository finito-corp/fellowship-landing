# Winning Fellowship 3 Design System

## 1. Atmosphere

Quiet, determined, human. The page should feel like a well-edited invitation from people who have already tried difficult things together, not an AI product launch. Its signature is a sequence of warm light and deep charcoal chapters connected by a single gold progress line. Copy is specific, conversational, and action-led.

## 2. Color

- `--ink: #171717` — dark chapter background and primary text on light sections
- `--paper: #f7f5ef` — warm light chapter background
- `--night-soft: #232323` — elevated dark surface
- `--gold: #f2bd3f` — one primary accent for progress, focus, dates, and CTAs
- `--gold-deep: #8f5f00` — AA-compliant accent text on light surfaces
- `--text-light: #faf8f2` — primary text on dark chapters
- `--muted-light: #aaa79f` — secondary text on dark chapters
- `--muted-dark: #68645d` — secondary text on light chapters
- Light and dark chapters alternate. Blue and purple gradients are not part of this system.

## 3. Typography

- Font stack: Pretendard Variable, system sans-serif fallback.
- Display: `--font-display: clamp(2.75rem, 5.2vw, 4.2rem)`, 820 weight, restrained Korean tracking, readable line height.
- Section title: `--font-section: clamp(1.95rem, 4.4vw, 3.65rem)`, 790 weight.
- Body lead: `--font-lead: clamp(1.05rem, 2vw, 1.28rem)`, relaxed line height.
- Labels: 0.72–0.78rem, 800 weight, wide tracking.
- Korean copy uses `word-break: keep-all`; line length stays near 36–48 Korean characters for narrative sections.
- Hero support copy is split into sentence-level blocks. A full sentence owns its line before the next thought begins.
- Type roles are centralized as `--font-display`, `--font-section`, `--font-heading`, `--font-lead`, `--font-hero-copy`, `--font-fact`, `--font-body*`, `--font-label`, `--font-meta`, `--font-small`, and `--font-micro`; components do not define their own type scale.

## 4. Spacing and Layout

- Base spacing unit: 4px.
- Content width: `--content-max: 70rem` (1120px); narrative copy width: `--copy-max: 45rem` (720px).
- Section padding: `--section-space: clamp(92px, 12vw, 152px)`.
- Spacing primitives are `--space-1` through `--space-14` plus the named `--space-md`, `--space-lg`, `--space-xl`, and `--space-2xl`. Layout measures use `--measure-*`; recurring component geometry uses `--grid-*`, `--*-height`, `--dot-*`, and `--shell-gutter*` tokens.
- The 4px grid governs layout spacing and component geometry. One-pixel rules, the 2px timeline, optical letter spacing, fluid `clamp()` values, and the 44px accessibility target are intentional exceptions.
- Desktop uses asymmetric two-column layouts for explanations; mobile collapses to one column.
- Breakpoints: 1100px for the side guide, 900px for asymmetric layouts, 760px for main navigation, and 520px for compact CTA stacks.

## 5. Components

- Announcement bar: recruitment dates, beta-review status, one direct CTA.
- Site navigation: fixed below announcement; desktop links, mobile disclosure menu, visible application CTA.
- Side guide: desktop-only chapter dots with labels, active state, and back-to-top control.
- Hero: full-height editorial opening, two CTAs, a plain-language intake boundary, and four scannable facts. The emotional time scale is `약 3개월`; detailed week counts belong to the operating chapter. No photography.
- Origin story: the Fellowship's post-exam roots and `Ride Your Own Waves` philosophy, connected to the current late-college decision stage.
- Cohort journey: a text-only 1기 → 2기 → 3기 sequence. Historical activity descriptions stay at the format/rhythm level and verified anonymous quotes remain visually separate from operator narration.
- Audience fit: concrete self-selection scenes before operating details, plus a restrained long-horizon statement that promises no outcome.
- AI proficiency is never a sorting criterion. Public copy explicitly welcomes both first-time and experienced AI users, then selects for applying AI to a real-life scene and iterating on the result.
- Chapter header: small gold label, large title, restrained lead copy.
- Numbered story row: editorial divider, large index, short human narrative; never a generic equal card grid.
- Program timeline: vertical gold progress line, numbered steps, factual boundaries.
- Review marquee: verified anonymous cohort-one quotes, duplicated track, pause on hover/focus, and explicit context that the quotes describe cohort-one team activities rather than cohort-three outcomes.
- FAQ: single-open accordion with explicit button state and accessible regions.
- Final CTA: direct invitation plus exact recruitment boundary.
- Application page: a dark editorial header followed by one process summary and one numbered form. Labels name the requested information directly; examples show the expected level of specificity without implying a preferred life choice or AI skill level.
- Form controls: 44px+ targets, persistent labels, visible required markers, gold focus rings, inline validation, pending state, and a single unambiguous submit action.
- Completion page: confirms submission, states that only successful applicants are contacted by the response date, and provides a route back to the 3기 introduction. It does not expose internal receipt identifiers.

## 6. Motion

- Sources adapted from beui.dev patterns: shared-layout-bg for active navigation, marquee for social proof, bouncy-accordion for single-open disclosure, scroll-animation for progress feedback.
- Motion tokens: fast 180ms, standard 280ms, reveal 650ms; ease `cubic-bezier(.22,1,.36,1)`.
- Purposeful motion only: hero stagger, scroll reveal, active navigation, timeline progress, review marquee, FAQ disclosure.
- Hover uses small translate/opacity/color changes. No decorative continuous motion except the review marquee and a restrained recruitment-status pulse.
- `prefers-reduced-motion: reduce` disables smooth scrolling, transforms, progress interpolation, and marquee animation while keeping all content visible.

## 7. Depth

- Mostly tonal depth: chapter alternation and 1px translucent rules.
- Shadows are limited to fixed navigation and primary CTA hover.
- Border radius is restrained: 0–8px for editorial content, full radius only for compact status/CTA controls.
- Avoid floating glass cards, collage surfaces, and repeated rounded feature tiles.

## 8. Accessibility and Design Debt

- Minimum interactive target: 44px.
- Gold is not used as small body text on light backgrounds; dark gold is used where contrast requires it.
- All interactive elements have visible `:focus-visible` states.
- Navigation and side-guide active state uses text/shape as well as color.
- The page contains no visible images; social proof is textual and attribution remains anonymous.
- Exact dates and selection boundaries remain text, not animation-dependent.
- Primary applicant: a late-college student or graduate completing the form on mobile, possibly under time pressure. The first screen must answer what this is, who can apply, what happens after submission, and the decision date.
- The application remains usable with keyboard-only navigation, browser zoom, reduced motion, and 320px-wide screens. Examples supplement labels but never replace them.
- Accepted debt through the 3기 recruitment window: the static application and completion pages keep CSS and JavaScript inline and repeat the same documented tokens so they can deploy as self-contained pages. Consolidate shared assets after recruitment rather than changing asset loading during the live intake period.
