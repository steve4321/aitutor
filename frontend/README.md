# AI Tutor — Frontend

Next.js 15 frontend for the AI Tutor platform (AMC Math / KET English / Chinese Composition & Poetry).

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v4
- **State**: Zustand + React Query
- **Animation**: Framer Motion
- **Math Rendering**: KaTeX
- **Testing**: Vitest + Testing Library

## Development

```bash
npm install
npm run dev
```

Open http://localhost:3000. Requires the backend running on port 8000.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm run lint` | ESLint check |
| `npm run test` | Run tests |
| `npm run test:watch` | Watch mode tests |
| `npm run test:coverage` | Coverage report |
| `npm run generate-types` | Generate API types from OpenAPI |

## Project Structure

```
src/
├── app/          # Pages (App Router)
├── components/   # React components by domain
├── hooks/        # Custom React hooks
├── lib/          # API client, utilities, renderers
├── stores/       # Zustand stores
└── types/        # TypeScript type definitions
```
