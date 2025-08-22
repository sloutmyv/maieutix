# Style Guide - Implementation Reference

## Design Tokens

### Colors
```css
:root {
  /* Brand */
  --color-primary: #2D4B73;
  --color-primary-dark: #253C59;
  --color-accent: #D9BA23;
  --color-accent-dark: #BF8D30;
  
  /* Text */
  --color-text-primary: #253C59;
  --color-text-secondary: #2D4B73;
  --color-text-muted: #6B7C93;
  
  /* Backgrounds */
  --color-background: #FFFFFF;
  --color-background-light: #F8F9FA;
  --color-border: #99B4BF;
  
  /* Semantics */
  --color-success: #28A745;
  --color-danger: #DC3545;
  --color-warning: #BF8D30;
  --color-info: #99B4BF;
}
```

### Typography
```css
:root {
  --font-family: 'Lato', sans-serif;
  --font-size-h1: 28px;
  --font-size-h2: 22px;
  --font-size-h3: 18px;
  --font-size-body: 15px;
  --font-size-small: 13px;
  --line-height-tight: 1.2;
  --line-height-normal: 1.4;
  --line-height-relaxed: 1.6;
}
```

### Spacing
```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-xxl: 32px;
}
```

### Layout
```css
:root {
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --transition: 200ms ease-in-out;
}
```

## Component Patterns

### Buttons
```css
.btn-primary {
  background: var(--color-primary);
  color: white;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  transition: var(--transition);
}
.btn-primary:hover { background: var(--color-primary-dark); }

.btn-accent {
  background: var(--color-accent);
  color: var(--color-primary-dark);
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}
```

### Form Fields
```css
.input {
  padding: var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-body);
  transition: var(--transition);
}
.input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(45, 75, 115, 0.2);
}
.input.error { border-color: var(--color-danger); }
```

### Cards
```css
.card {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-xl);
  border: 1px solid var(--color-border);
}
```

### Tables
```css
.table th {
  background: var(--color-background-light);
  padding: var(--space-md);
  font-weight: 700;
  text-align: left;
}
.table td {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}
.table tr:hover { background: var(--color-background-light); }
```
### footer
```css
.footer {
  position: sticky;
  bottom: 0;
  width: 100%;
  padding: var(--space-md);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-small);
  background: var(--color-background);
  border-top: 1px solid var(--color-border);
}
```
### Alerts
```css
.alert {
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  border-left: 4px solid;
}
.alert-success { 
  background: #D4EDDA; 
  border-left-color: var(--color-success); 
}
.alert-danger { 
  background: #F8D7DA; 
  border-left-color: var(--color-danger); 
}
```

## Responsive Breakpoints
```css
/* Mobile: <768px */
/* Tablet: 768px-1024px */
/* Desktop: >1024px */
```

## Icon System
- **Library:** Lucide React
- **Default Size:** 20px
- **Stroke:** 2px
- **Color:** `currentColor`

## Accessibility
- Focus: `outline: 2px solid var(--color-primary)`
- Contrast: 4.5:1 minimum
- Motion: Respect `prefers-reduced-motion`

## Logo Usage
- **Location:** `/context/logo/`
- **Minimum:** 120px width (primary), 24px (icon)
- **Clearspace:** 25% of height around logo

## Implementation Notes
- Use CSS custom properties for all tokens
- Mobile-first responsive design
- Semantic HTML with ARIA labels
- Component-scoped styling
- Performance: <200ms interactions