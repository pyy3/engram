# Testing React Applications

## Prerequisites
- Vitest or Jest
- @testing-library/react
- @testing-library/user-event

## Setup

```bash
pnpm add -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
```

## Unit Tests (Components)

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

test('calls onClick when clicked', async () => {
  const user = userEvent.setup()
  const onClick = vi.fn()
  render(<Button onClick={onClick}>Click me</Button>)

  await user.click(screen.getByRole('button', { name: /click me/i }))
  expect(onClick).toHaveBeenCalledOnce()
})
```

## Hook Tests

```tsx
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './useCounter'

test('increments counter', () => {
  const { result } = renderHook(() => useCounter())
  act(() => result.current.increment())
  expect(result.current.count).toBe(1)
})
```

## Integration Tests (API Routes)

```ts
import { GET } from '@/app/api/users/route'

test('returns users list', async () => {
  const response = await GET()
  const data = await response.json()
  expect(response.status).toBe(200)
  expect(data).toHaveLength(3)
})
```

## Best Practices

- Query by role > text > testId (accessibility-first)
- Use `userEvent` over `fireEvent` (more realistic)
- Test behavior, not implementation
- Mock at network boundary (MSW), not internal functions
- Snapshot tests only for stable, visual components
