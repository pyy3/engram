# Set Up GitHub Actions CI/CD

## Prerequisites
- GitHub repository
- Docker Hub or GHCR for container images (optional)

## Steps

1. Create workflow directory:
   ```bash
   mkdir -p .github/workflows
   ```

2. Create CI workflow (`.github/workflows/ci.yml`):
   ```yaml
   name: CI
   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with:
             node-version: 20
             cache: 'pnpm'
         - run: pnpm install
         - run: pnpm test
         - run: pnpm build
   ```

3. Add deployment workflow:
   ```yaml
   deploy:
     needs: test
     if: github.ref == 'refs/heads/main'
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v4
       - name: Deploy
         run: ./scripts/deploy.sh
         env:
           DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
   ```

4. Configure secrets:
   - Go to: Settings > Secrets and Variables > Actions
   - Add required secrets (API keys, deploy keys)

## Best Practices

- Cache dependencies (actions/cache or built-in cache)
- Matrix for multi-version testing
- Reusable workflows for shared CI logic
- Branch protection: require status checks before merge
- Use environment deployments for staging/production gates
