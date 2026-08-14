# Winning Fellowship 3 Design System

## 1. Atmosphere

Quiet, determined, human. The page should feel like a well-edited invitation from people who have already explored difficult choices together, not an AI product launch. Its signature is a sequence of warm light and deep charcoal chapters connected by a single gold progress line. Copy is specific, conversational, and possibility-led: AI expands the field of view, peers add perspective, and repeated action turns possibility into evidence.

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
- Section pacing uses three named roles: `--section-space-compact: clamp(4rem, 7vw, 6rem)`, `--section-space-standard: clamp(5.5rem, 9vw, 8rem)`, and `--section-space-feature: clamp(7rem, 11vw, 9.5rem)`. Narrative chapters default to standard; quiet evidence uses compact; Core, pre-course emphasis, Schedule, and Final use feature selectively.
- Spacing primitives are `--space-1` through `--space-14` plus the named `--space-md`, `--space-lg`, `--space-xl`, and `--space-2xl`. Layout measures use `--measure-*`; recurring component geometry uses `--grid-*`, `--*-height`, `--dot-*`, and `--shell-gutter*` tokens.
- The 4px grid governs layout spacing and component geometry. One-pixel rules, the 2px timeline, optical letter spacing, fluid `clamp()` values, and the 44px accessibility target are intentional exceptions.
- Desktop uses asymmetric two-column layouts for explanations; mobile collapses to one column.
- Breakpoints: 1100px for the side guide, 900px for asymmetric layouts, 760px for main navigation, and 520px for compact CTA stacks.

## 5. Components

- Announcement bar: recruitment dates, pre-course review status, one direct CTA.
- Site navigation: fixed below announcement; desktop links, mobile disclosure menu, visible application CTA.
- Side guide: desktop-only `Folio Chapter Rail` with one hairline, eight transform-scaled chapter ticks, a compact `↑ TOP` anchor, and a progress fill. It has no shared capsule, card, or floating control background. The current chapter label (`01 / 소개`) remains visible; inactive labels appear only on hover or keyboard focus. Real hash anchors preserve destination semantics; JavaScript progressively controls the rail's scroll-gated visibility, `aria-current="location"`, tone, and progress. The redundant top/mobile anchor navigation remains the no-JavaScript fallback. The rail adapts its text, rule, and active accent to the current light, dark, or gold chapter. `origin` belongs to the schedule/selection narrative and `reviews` continues the history/evidence chapter, so those sections update the rail's macro-chapter state instead of adding more ticks.
- Hero: full-height editorial opening, two CTAs, a plain-language intake boundary, and four scannable facts. The 3-month core is the product and must be named first; the 2-week pre-course is its selection doorway and never the apparent destination. On mobile, the deadline row also carries a compact review, contact, selection, and non-guarantee summary before the detailed boundary. No photography.
- Origin story: the Fellowship's post-exam roots and `Ride Your Own Waves` philosophy, connected to the current late-college decision stage.
- Cohort journey: a text-only 1기 → 2기 → 3기 sequence. Historical activity descriptions stay at the format/rhythm level and verified anonymous quotes remain visually separate from operator narration.
- Audience fit: concrete self-selection scenes centered on strengths, options, and self-directed direction before operating details, plus a restrained long-horizon statement that promises no outcome.
- AI proficiency is never a sorting criterion. Public copy explicitly welcomes both first-time and experienced AI users, then selects for exploring a possibility with AI, testing it in a real-life scene, and revising direction from evidence.
- Chapter header: small gold label, large title, restrained lead copy.
- Numbered story row: editorial divider, large index, short human narrative; never a generic equal card grid.
- Pre-course dossier: the selected A2 layout presents the exact summary beside three flat ruled rows on wide screens and stacks them on narrow screens. The previous vertical line and dots remain in the DOM for contract stability but are visually hidden; the existing timeline observer may continue updating their state as a harmless no-op until shared markup is consolidated after recruitment.
- Story order: emotional recognition → possibility-and-direction reframe → 3-month exploration and validation rhythm → 2-week selection doorway → exact schedule → prior-cohort evidence. History supports the offer; it does not delay the current program explanation.
- Social share card: a text-only 1200×630 PNG using the same ink, paper, and gold tokens. The share promise names the 3-month core rather than the pre-course.
- Prior-cohort reviews: preserve the approved eight verified anonymous quotes, their attributions, and the original slow horizontal marquee. The repeated set is `aria-hidden`, hover and keyboard focus pause the track, and reduced-motion users see one horizontally scrollable set.
- Application support contact: a plain text line placed after the FAQ list and before the final application CTA, where it serves unresolved application questions rather than interrupting prior-cohort evidence. It directs additional questions to `irs8@finito.me` or Instagram DM at `@winning_fellowship`; it adds no portrait, title, response-time promise, or extra channel.
- FAQ: single-open accordion with explicit button state and accessible regions.
- Final CTA: direct invitation plus exact recruitment boundary.
- Application page: a dark editorial header followed by a flat paper process ledger, a preparation note, and one numbered form separated by thin rules instead of a floating rounded card. Labels name the requested information directly; examples show the expected level of specificity without implying a preferred life choice or AI skill level.
- Application preparation note: derives preparation prompts from the real form fields, states that answers are automatically saved only in the current device and browser, and tells applicants that activating the direct submit action sends the reviewed answers. It does not claim an average completion time.
- Application status ledger: `작성 → 접수 완료 → 2주 사전과정 안내 → 본과정 합류 결정`. It preserves the current policy that only selected applicants receive the next-course notice; it must not imply universal result notification, a receipt ID, or a receipt timestamp.
- Form controls: 44px+ targets, persistent labels, visible required markers, gold focus rings, inline validation, pending state, and a single unambiguous submit action.
- Form error recovery: one focusable error summary lists every invalid field in document order and links back to it. Each field keeps its value, exposes an adjacent error message, and sets `aria-invalid`; checkbox groups use the same pattern at group level.
- Draft and direct submission: every editable answer is restored from browser-local storage after reload, an explicit clear action erases that draft, and a successful submission clears it. One unambiguous submit action validates the numbered form and sends the application directly.
- Submission fallback: a persistent plain-text line immediately after the submit result directs applicants to email their completed application to `irs8@finito.me` if online submission is not working.
- Skip link: the landing and application page expose a keyboard-visible route to `main` without adding a persistent visual navigation element.
- Completion page: uses the same flat paper sheet, folio, thin rules, and status ledger as the application page. It confirms submission, states that only pre-course invitees are contacted by the response date, provides a route back to the 3기 introduction, and exposes the correction/withdrawal email. It does not expose internal receipt identifiers or timestamps.

## 6. Motion

- Sources retained from the current build: shared-layout-bg for active navigation, bouncy-accordion for single-open disclosure, scroll-animation for progress feedback, and the approved slow review marquee.
- Motion tokens: fast 180ms, standard 280ms, reveal 650ms; ease `cubic-bezier(.22,1,.36,1)`.
- Purposeful motion only: hero word rise, active navigation, timeline progress, FAQ disclosure, button feedback, and explicit status changes. Editorial body copy and static evidence do not receive blanket reveal motion.
- Hover uses small translate/opacity/color changes. The restrained recruitment-status pulse and slow review marquee are the only repeating motion; the marquee pauses on hover or keyboard focus.
- `prefers-reduced-motion: reduce` disables smooth scrolling, transforms, progress interpolation, the recruitment-status pulse, and the review marquee while keeping one complete review set visible.

## 7. Depth

- Mostly tonal depth: chapter alternation and 1px translucent rules.
- Shadows are limited to fixed navigation and primary CTA hover. Application, review, and completion surfaces use paper tone and rules with no floating-card shadow.
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
- Validation never relies on the browser tooltip alone. The error summary receives focus after a failed attempt, field messages remain visible until corrected, and no application request is sent until required fields pass validation and the applicant activates the submit action.
- Accepted debt through the 3기 recruitment window: the static application and completion pages keep CSS and JavaScript inline and repeat the same documented tokens so they can deploy as self-contained pages. Consolidate shared assets after recruitment rather than changing asset loading during the live intake period.
- Accepted content debt: average application time, personal weekly execution time, universal result notification, receipt IDs, and receipt timestamps remain unpublished until measured or operationally approved. The current selected-only contact policy remains explicit.
- A2 accessibility translation: Core is a dark chapter, so its supporting copy, rules, indices, and boundary use the existing dark-surface roles (`--muted-light`, `--rule-light`, `--gold`). The light pre-course dossier uses `--muted-dark` and `--gold-deep`. This intentionally corrects the local comparison wrapper's inherited light/dark token mismatch without changing the selected structure.

## 9. Next Visual Iteration Boundary

- The next meaningful landing iteration is a second visual-rhythm pass, not a new content or product-definition pass. The approved hero thesis, broad chapter order, two-week summary, eight review quotes and marquee, support wording, factual dates/boundaries, application contract, and legal copy remain unchanged.
- Copy reduction may remove only repeated explanatory narration. It must not shorten or paraphrase the eight approved reviews, hero thesis, confirmed public facts, support line, selection boundaries, or legal text.
- Chapter pacing may vary, but spacing remains a documented single source of truth. If the global `--section-space` is replaced, introduce a named compact/standard/feature scale in `:root`; do not scatter per-section raw padding values.
- The approved direction is `Current-structure Trust & Editorial pass + Human-edited field journal`. Decision-brief compression and manifesto styling are reference-only unless hyun explicitly reopens information architecture.
- No Stitch creation/upload, public change, form change, commit/push, or production deployment follows from this design decision without its separate approval gate.

## 10. Selected A2 Translation — 2026-08-11

- hyun selected A2 `Stronger Evidence & Pacing` as one complete direction. A1 is not mixed into the implementation and the information architecture is not reopened.
- Hero, broad order, Folio Chapter Rail, exact reviews and marquee, support wording, facts, application contract, and legal copy remain unchanged.
- About, Fit, Origin, History, and FAQ use compact pacing. Core is the dominant ruled evidence spread; pre-course is a flat field-journal dossier; Schedule is an oversized tabular date ledger. Reviews keep all content and motion with quieter surrounding framing.
- Product CSS uses the three named spacing roles and A2-specific type/measure tokens declared in `:root`. Preview-only attributes, wrapper selectors, disabled links, countdown hiding, and capture motion overrides never enter product code.
- Required validation is 320/375/768/1280 responsive rendering, selected-reference comparison, CJK/overflow/contrast/target checks, keyboard and reduced-motion behavior, exact content and mirror contracts, application-flow regression with intercepted POST, fresh independent review, and World Model G4.
