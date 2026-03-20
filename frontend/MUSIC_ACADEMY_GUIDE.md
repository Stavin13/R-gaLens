# Music Academy Journal Explorer

A premium, high-contrast RAG-based AI search engine for 90 years of historical journals (1930-2023), built with Next.js, Tailwind CSS, and Framer Motion.

## Design Features

### Premium Aesthetic
- **Color Scheme**: Pure black (#000) background with gold/amber (#f59e0b) accent colors and zinc grays (#27272a) for borders
- **Typography**: 
  - Primary: Playfair Display (serif) for headings and drop-caps - premium, historical feel
  - Secondary: Geist (sans-serif) for body text and UI - clean, modern
- **Glass Effect**: Frosted glass search bar with backdrop blur for modern sophistication

### Accessibility (Elderly Users)
- **Large Typography**: Answer text 24-32px (from `text-lg` to `text-3xl` with responsive scaling)
- **High Contrast**: White text (#f5f5f5) on pure black background (WCAG AAA compliant)
- **Clear Buttons**: Large touch targets (48px+ minimum), high visibility with amber highlighting
- **Semantic HTML**: Proper ARIA labels, screen reader support
- **Responsive**: Mobile-first design with graceful scaling to larger screens

## Component Architecture

### `JournalExplorer` (Main Container)
- Orchestrates all child components
- Manages overall page flow and animations
- Provides ambient background elements
- Handles loading, error, and result states

### `SearchHeader`
- Floating glass search bar with Consult button
- Responsive input with placeholder guidance
- Loading state with spinner animation
- Form submission handling

### `QuickStartCards` (6 Cards)
- Pre-populated important terms: Raagas, Marga, Taala, Desi, Gharana, Hindustani
- Hover effects with scale and background glow
- Staggered entrance animation
- Disabled state during search

### `ResultsDisplay`
- **Drop-cap Typography**: Giant first letter (6-8xl) in gold with serif font
- Historical journal aesthetic through CSS styling
- Responsive text sizing (24-32px for accessibility)
- Divider line with gradient effect

### `ScholarlyEvidence`
- Citation cards with publication year badges
- Detailed metadata: Author, Volume, Pages
- Hover glow effects with color transitions
- Archive note footer

### `SkeletonLoader`
- Shimmer animation using Framer Motion
- Matches result layout structure
- Staggered animation delays for visual flow
- Uses gradient backgrounds with animated position shifts

### `useJournalSearch` Hook
- State management: `isSearching`, `result`, `error`
- POST requests to `http://localhost:8000/query`
- Error handling with user-friendly messages
- TypeScript interfaces for `SearchResult` and `Citation`

## Animations (Framer Motion)

### Page-Level
- Fade-in on mount (opacity 0→1, duration 0.4s)
- Ambient background blur elements for depth

### Component Reveals
- Staggered children animations with 0.1s delays
- Smooth Y-axis translations (y: 20→0)
- Easing functions for natural motion

### Interactive Elements
- Button scale on hover (1→1.05) and tap (1→0.98)
- Card background color transitions on hover
- Glow blur layers that fade in on hover
- Input focus animation with box shadow

### Loading States
- Continuous shimmer loop (2s duration, infinite repeat)
- Spinning loader icon in Consult button
- Staggered skeleton elements

## Color System

- **Background**: `#000000` (pure black)
- **Foreground/Text**: `#f5f5f5` (near white)
- **Primary Accent**: `#f59e0b` (amber-500)
- **Secondary Accent**: `#fbbf24` (amber-400)
- **Cards/Borders**: `#0a0a0a`, `#18181b`, `#27272a` (zinc variants)
- **Borders**: `border-zinc-800` with `/50` opacity for subtle lines

## Responsive Design

- Mobile-first approach with breakpoints: `sm:`, `md:`, `lg:`
- Text scaling: 
  - Headings: `text-3xl → text-5xl → text-6xl`
  - Answers: `text-lg → text-2xl → text-3xl`
- Spacing scaling: Proportional padding and gaps
- Grid layouts: 1 column (mobile) → 2 columns (tablet) → 3 columns (desktop)

## State Flow

```
User Input (Search Header)
    ↓
handleSearch() (useJournalSearch hook)
    ↓
POST to http://localhost:8000/query
    ↓
Loading: Show SkeletonLoader
    ↓
Success: Show ResultsDisplay + ScholarlyEvidence
    ↓
Error: Show error message in alert box
```

## Dependencies

- **Next.js 16.2.0**: Framework
- **React 19.2.4**: UI library
- **Tailwind CSS 4.2.0**: Styling with design tokens
- **Framer Motion 11.0.0**: Animations
- **TypeScript 5.7.3**: Type safety

## API Integration

The component expects a backend endpoint at `http://localhost:8000/query` that:
- Accepts POST requests with JSON body: `{ query: string }`
- Returns JSON response:
  ```json
  {
    "answer": "string",
    "citations": [
      {
        "source": "string",
        "publicationYear": number,
        "author": "string (optional)",
        "volume": "string (optional)",
        "pages": "string (optional)"
      }
    ]
  }
  ```

## Getting Started

1. Install dependencies: `pnpm install`
2. Start dev server: `pnpm dev`
3. Ensure backend is running on `http://localhost:8000`
4. Open `http://localhost:3000` in browser
5. Try searching for terms or click Quick Start cards

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 15+
- Mobile browsers with CSS backdrop-filter support

## Accessibility Checklist

- ✅ WCAG AAA contrast ratios (black/white)
- ✅ Large touch targets (48px minimum)
- ✅ Keyboard navigation (Tab, Enter)
- ✅ ARIA labels on buttons
- ✅ Semantic HTML structure
- ✅ Screen reader friendly
- ✅ Focus indicators visible
- ✅ Motion respects `prefers-reduced-motion` (via Framer Motion defaults)
