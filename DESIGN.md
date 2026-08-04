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
- Display: `--font-display: clamp(3.15rem, 8.4vw, 7rem)`, 820 weight, tight tracking, compact line height.
- Section title: `--font-section: clamp(2.25rem, 5.6vw, 4.65rem)`, 790 weight.
- Body lead: `--font-lead: clamp(1.05rem, 2vw, 1.28rem)`, relaxed line height.
- Labels: 0.72–0.78rem, 800 weight, wide tracking.
- Korean copy uses `word-break: keep-all`; line length stays near 36–48 Korean characters for narrative sections.

## 4. Spacing and Layout

- Base spacing unit: 4px.
- Content width: `--content-max: 70rem` (1120px); narrative copy width: `--copy-max: 45rem` (720px).
- Section padding: `--section-space: clamp(92px, 12vw, 152px)`.
- Desktop uses asymmetric two-column layouts for explanations; mobile collapses to one column.
- Breakpoints: 1100px for the side guide, 900px for asymmetric layouts, 760px for main navigation, and 520px for compact CTA stacks.

## 5. Components

- Announcement bar: recruitment dates, beta-review status, one direct CTA.
- Site navigation: fixed below announcement; desktop links, mobile disclosure menu, visible application CTA.
- Side guide: desktop-only chapter dots with labels, active state, and back-to-top control.
- Hero: full-height editorial opening, two CTAs, factual footnote, four count-up facts. No photography.
- Chapter header: small gold label, large title, restrained lead copy.
- Numbered story row: editorial divider, large index, short human narrative; never a generic equal card grid.
- Program timeline: vertical gold progress line, numbered steps, factual boundaries.
- Review marquee: verified anonymous cohort-one quotes, duplicated track, pause on hover/focus.
- FAQ: single-open accordion with explicit button state and accessible regions.
- Final CTA: direct invitation plus exact recruitment boundary.

## 6. Motion

- Sources adapted from beui.dev patterns: shared-layout-bg for active navigation, marquee for social proof, bouncy-accordion for single-open disclosure, scroll-animation for progress feedback.
- Motion tokens: fast 180ms, standard 280ms, reveal 650ms; ease `cubic-bezier(.22,1,.36,1)`.
- Purposeful motion only: hero stagger, scroll reveal, count-up facts, active navigation, timeline progress, review marquee, FAQ disclosure.
- Hover uses small translate/opacity/color changes. No decorative continuous motion except the review marquee and a restrained recruitment-status pulse.
- `prefers-reduced-motion: reduce` disables smooth scrolling, transforms, counting, progress interpolation, and marquee animation while keeping all content visible.

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
- Debt: the static single-file architecture keeps CSS and JavaScript together; split only when the site gains more than one public landing template.
