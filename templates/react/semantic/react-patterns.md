# React Patterns & Best Practices

## Component Architecture

- **Prefer function components** with hooks over class components
- **Custom hooks** for reusable logic (prefix with `use`)
- **Composition over inheritance** — use children/render props
- **Single responsibility** — each component does one thing well

## State Management

- **Local state** (useState) for component-scoped data
- **Context** for cross-cutting concerns (theme, auth, locale)
- **External stores** (Zustand, Redux, XState) for complex shared state
- **Server state** (React Query/SWR) for API data — separate from UI state

## Performance

- `React.memo()` for expensive pure components
- `useMemo` for expensive computations, `useCallback` for stable function refs
- Virtual lists for large datasets (react-window, tanstack-virtual)
- Code splitting with `React.lazy()` + `Suspense`
- Image optimization: next/image, srcset, lazy loading

## Common Gotchas

- Stale closures in useEffect — always include deps
- Object/array in deps cause infinite loops — memoize or use refs
- `key` must be stable and unique (never use array index for mutable lists)
- useEffect cleanup runs on unmount AND before re-run
- setState is async — use functional form for sequential updates
