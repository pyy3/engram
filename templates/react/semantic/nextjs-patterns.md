# Next.js Patterns

## App Router (Next.js 13+)

- `app/` directory with file-based routing
- `page.tsx` = route, `layout.tsx` = shared wrapper, `loading.tsx` = Suspense fallback
- Server Components by default — add `'use client'` only when needed
- Route groups `(group)` for organization without affecting URL
- Parallel routes `@slot` for complex layouts

## Data Fetching

- **Server Components**: fetch directly in component (no useEffect needed)
- **Server Actions**: `'use server'` for mutations (forms, API calls)
- **Route Handlers**: `app/api/route.ts` for REST endpoints
- **Revalidation**: `revalidatePath()`, `revalidateTag()`, or time-based ISR

## File Conventions

```
app/
├── layout.tsx          # Root layout (html, body)
├── page.tsx            # Home page
├── globals.css         # Global styles
├── (auth)/             # Route group
│   ├── login/page.tsx
│   └── signup/page.tsx
├── dashboard/
│   ├── layout.tsx      # Dashboard layout
│   ├── page.tsx        # /dashboard
│   └── [id]/page.tsx   # /dashboard/:id
└── api/
    └── webhook/route.ts
```

## Common Gotchas

- Client components can't be async — use useEffect or React Query
- Metadata must be in Server Components (`export const metadata`)
- Environment variables: `NEXT_PUBLIC_` prefix for client-side access
- Middleware runs on Edge — limited API (no fs, no Node.js APIs)
- `redirect()` throws — don't wrap in try/catch
