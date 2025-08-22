# SaaS Dashboard Design Principles

## Core Philosophy
- **Users First:** Prioritize workflows and ease of use
- **Meticulous Craft:** Precision and polish in every element
- **Speed & Performance:** Fast, responsive interactions
- **Simplicity & Clarity:** Clean, unambiguous interface
- **Consistency:** Uniform design language across app
- **Accessibility:** WCAG AA+ compliance
- **Opinionated Defaults:** Reduce decision fatigue

## Design System Foundation

### Colors (Reference: style-guide.md)
- **Primary:** `#2D4B73` (Dark Blue), Dark: `#253C59`
- **Accent:** `#D9BA23` (Golden Yellow), Dark: `#BF8D30`
- **Semantics:** Success `#28a745`, Error `#dc3545`, Warning `#BF8D30`, Info `#99B4BF`

### Typography
- **Font:** Lato (400, 700)
- **Scale:** H1(28px), H2(22px), H3(18px), Body(15px), Small(13px)
- **Line Heights:** 1.2(headings), 1.4(UI), 1.6(body)

### Spacing & Layout
- **Base:** 4px system (xs:4px, sm:8px, md:12px, lg:16px, xl:24px, xxl:32px)
- **Breakpoints:** Mobile <768px, Tablet 768-1024px, Desktop >1024px
- **Grid:** 12-column, 24px gutters
- **Sidebar:** 280px (desktop), collapsible to 64px

### Component Standards
- **Border Radius:** sm:4px, md:6px, lg:8px, xl:12px
- **Shadows:** xs-xl scale for depth hierarchy
- **States:** Default, Hover, Active, Focus, Disabled
- **Transitions:** 200ms ease-in-out

## Module-Specific Patterns

### Multimedia Moderation
- Large preview + metadata sidebar
- Color-coded status badges
- Keyboard shortcuts (A/R/F)
- Bulk operations with progress indicators
- Auto-advance workflow

### Data Tables
- Virtual scrolling for 1000+ rows
- Sticky headers, resizable columns
- Mobile: card layout transformation
- Smart alignment: text-left, numbers-right
- Zebra striping for dense data

### Configuration Panels
- Progressive disclosure (accordions)
- Auto-save with visual confirmation
- Real-time validation and preview
- Contextual help tooltips
- Reset to defaults option

## Layout Structure
[Fixed Top Navbar: Logo, User Menu, Administration]
├─────────────────────────────────────────────────────────────────
│ Navigation      │ [Content with max-width constraints]       │
│ Menu            │ [Scrollable content area]                  │
│                 │ [Footer/Status Bar]                        │
Layout Specifications

Top Navbar: Fixed position, full width, 64px height
Content Area: Offset by navbar height + sidebar width

## Implementation Notes
- Use utility-first CSS (Tailwind recommended)
- Design tokens via CSS custom properties
- Component-scoped styles
- Semantic HTML with ARIA support
- Mobile-first responsive approach
- Performance budget: <200ms interactions