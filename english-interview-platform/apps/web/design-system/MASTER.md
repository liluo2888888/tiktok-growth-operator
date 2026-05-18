# Quest English — Design System (Master)

Source: `E:\前端\skills` — frontend-design, ui-ux-pro-max, teach-impeccable.

## Product

Editorial interview coach for non-native English speakers preparing for job interviews.

## Style

- **Tone**: Warm parchment, ink typography, copper/brass accents (passport metaphor)
- **Not**: Purple gradients, Inter-only stacks, emoji icons, gamified candy UI

## Typography

- Display: **Fraunces** (editorial serif)
- Body: **IBM Plex Sans** (clarity for ESL readers)

## Color (OKLCH tokens)

See `src/styles/global.css` — semantic tokens only in components.

## UX priorities (ui-ux-pro-max)

1. Accessibility: 4.5:1 contrast, focus rings, labels, skip link
2. Touch: 44px targets, loading feedback on submit
3. Motion: 150–300ms micro; stagger on page enter; `prefers-reduced-motion`
4. Icons: SVG only (Lucide-style strokes), no emoji as UI chrome

## Page notes

- **Interview**: Dark question panel + light answer — focus mode
- **Passport**: Stamp cards with perforation motif
- **Feedback**: Readiness as editorial hero, not dashboard widget
