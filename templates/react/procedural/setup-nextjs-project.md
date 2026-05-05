# Set Up a Next.js Project

## Prerequisites
- Node.js >= 18
- Package manager (pnpm recommended)

## Steps

1. Create project:
   ```bash
   pnpm create next-app@latest my-app --typescript --tailwind --eslint --app --src-dir
   cd my-app
   ```

2. Install common dependencies:
   ```bash
   pnpm add zustand @tanstack/react-query zod
   pnpm add -D @types/node prettier eslint-config-prettier
   ```

3. Configure path aliases in `tsconfig.json`:
   ```json
   {
     "compilerOptions": {
       "paths": {
         "@/*": ["./src/*"]
       }
     }
   }
   ```

4. Set up environment:
   ```bash
   cp .env.example .env.local
   # Add: NEXT_PUBLIC_API_URL=http://localhost:3000/api
   ```

5. Start development:
   ```bash
   pnpm dev
   ```

## Project Structure Convention

```
src/
├── app/           # Routes (Next.js App Router)
├── components/    # Shared UI components
│   ├── ui/        # Primitives (Button, Input, Modal)
│   └── features/  # Feature-specific (UserCard, OrderTable)
├── hooks/         # Custom hooks
├── lib/           # Utilities, clients, helpers
├── stores/        # State management
└── types/         # TypeScript type definitions
```
