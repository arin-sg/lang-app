# Frontend - Language Learning App

React 19.2.0 application with Vite build tool.

## Design System: Cheerful Nanobanana

A warm, friendly UI theme designed for an enjoyable language learning experience.

### Colors (HSL)
- `--color-background: 45 100% 99%` - Creamy off-white
- `--color-primary: 47 100% 50%` - Banana yellow
- `--color-secondary: 50 100% 91%` - Pale yellow
- `--color-muted: 45 100% 96%` - Warm backgrounds
- `--color-accent: 200 90% 94%` - Pale sky blue
- `--color-destructive: 0 85% 60%` - Warm red

### Typography
- **Font**: Nunito (weights 400, 600, 700, 800)
- **Headings**: font-extrabold (800 weight) with tight tracking
- **Body**: Regular weight (400-600)

### Component Library
- **shadcn/ui**: Pre-built, accessible React components
- **Installation**: `npx shadcn@latest add [component-name]`
- **Location**: `src/components/ui/`
- **Import**: `import { Button } from '@/components/ui/button'`

### Styling
- **Tailwind CSS v4** with CSS variables
- **Border Radius**: 1.25rem default (bubbly aesthetic)
- **No CSS files**: All styling via Tailwind utility classes
- **Theme defined in**: `src/index.css` using `@theme` block

## Development

```bash
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
```

## Adding New Components

```bash
# Install a shadcn/ui component
npx shadcn@latest add button

# Available components: button, card, input, textarea, badge, alert, dialog, progress, etc.
```

## Path Aliasing

Import from `src/` using `@/` alias:
```javascript
import { Button } from '@/components/ui/button'
import { api } from '@/api/client'
```

Configuration in `jsconfig.json` and `vite.config.js`.

## Architecture

- **Router**: React Router v7 (client-side routing)
- **State**: Local component state (useState) + API calls
- **API Client**: Axios-based client in `src/api/client.js`
- **Pages**: Ingest, Library, Review, Coach

### Pages Overview

1. **IngestPage** - Text input with extraction results display
   - Textarea for German text input
   - Submit button triggers extraction API
   - Results show extracted items with stats
   - Error handling with Alert component

2. **LibraryPage** - Browse and manage learned items
   - Filter tabs (All / Words / Phrases / Patterns)
   - Multi-select with checkboxes
   - Item cards with metadata and stats
   - Dialog modals for item details and delete confirmation

3. **ReviewPage** - Spaced repetition practice
   - Progress bar showing deck completion
   - Two modes: Flip Card (default) and Type Answer
   - Flip Card: Recognition-based learning with self-grading
   - Type Answer: Input-based practice with automatic grading
   - Results recorded via API

4. **CoachPage** - Placeholder for Iteration 2
   - Coming soon message with feature list

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   └── Layout.jsx    # Navigation wrapper
│   ├── pages/
│   │   ├── IngestPage.jsx
│   │   ├── LibraryPage.jsx
│   │   ├── ReviewPage.jsx
│   │   └── CoachPage.jsx
│   ├── api/
│   │   └── client.js     # Axios API client
│   ├── lib/
│   │   └── utils.js      # cn() utility
│   ├── App.jsx           # Root component with router
│   ├── main.jsx          # Entry point
│   └── index.css         # Theme CSS variables
├── components.json       # shadcn/ui config
├── jsconfig.json         # Path aliases
├── tailwind.config.js    # Tailwind config
├── vite.config.js        # Vite config
└── package.json
```

## API Integration

Backend API base URL configured in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

API client in `src/api/client.js` provides:
- `ingestText(text)` - POST to `/sources`
- `getLibraryItems(type)` - GET from `/library`
- `getItemDetail(itemId)` - GET from `/library/{itemId}`
- `deleteItems(itemIds)` - DELETE to `/library`
- `getReviewDeck()` - GET from `/review/today`
- `submitReviewResult(result)` - POST to `/review/result`

## Troubleshooting

**Dev server won't start:**
- Check that `npm install` completed successfully
- Verify `.env` has correct API URL
- Try deleting `node_modules` and running `npm install` again

**Components not found:**
- Ensure path alias is working (`@/` should resolve to `src/`)
- Check that `jsconfig.json` and `vite.config.js` have correct configuration
- Restart VS Code to refresh path alias

**Styles not applying:**
- Verify Tailwind CSS is processing correctly
- Check that `src/index.css` is imported in `main.jsx`
- Ensure `tailwind.config.js` content paths include your files

**Build errors:**
- Run `npm run build` to check for TypeScript/import errors
- Fix any import paths or missing dependencies
- Check console for specific error messages
