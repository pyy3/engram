# Docker Patterns

## Multi-Stage Builds

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

Benefits: smaller images, no dev dependencies in production, cached layers.

## Layer Caching

- Copy dependency files first (`package.json`), install, THEN copy source
- Least-changing layers at top, most-changing at bottom
- Use `.dockerignore` to exclude node_modules, .git, tests

## Common Gotchas

- **PID 1 problem**: Use `tini` or `dumb-init` for signal handling
- **Non-root user**: Always `USER nonroot` in production
- **Health checks**: `HEALTHCHECK CMD curl -f http://localhost:3000/health`
- **Cache busting**: `ARG CACHEBUST=1` before `RUN git clone`
- **Secrets**: Never COPY secrets — use build secrets (`--mount=type=secret`)

## Docker Compose Patterns

- `depends_on` with `condition: service_healthy` for ordering
- Named volumes for persistence, tmpfs for ephemeral data
- Environment files: `env_file: .env` (never commit .env)
- Networks: isolate frontend/backend services
