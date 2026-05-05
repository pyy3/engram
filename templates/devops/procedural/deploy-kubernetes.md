# Deploy to Kubernetes

## Prerequisites
- kubectl configured with cluster access
- Container image built and pushed to registry
- Kubernetes manifests ready (or Helm chart)

## Steps

1. Build and push image:
   ```bash
   docker build -t registry.example.com/myapp:v1.2.3 .
   docker push registry.example.com/myapp:v1.2.3
   ```

2. Update deployment image:
   ```bash
   kubectl set image deployment/myapp myapp=registry.example.com/myapp:v1.2.3
   ```

3. Watch rollout:
   ```bash
   kubectl rollout status deployment/myapp
   ```

4. Verify:
   ```bash
   kubectl get pods -l app=myapp
   kubectl logs -l app=myapp --tail=50
   ```

## Rollback

If something goes wrong:
```bash
kubectl rollout undo deployment/myapp
# Or to specific revision:
kubectl rollout undo deployment/myapp --to-revision=3
```

## Blue-Green Deployment

1. Deploy new version as separate deployment
2. Run smoke tests against new deployment
3. Switch service selector to new deployment
4. Keep old deployment for quick rollback
5. Delete old deployment after confidence period

## Canary Deployment

1. Deploy new version with 1 replica
2. Route 10% traffic to new version (Istio/Nginx)
3. Monitor error rates and latency
4. Gradually increase traffic (25%, 50%, 100%)
5. Scale down old version

## Failure Recovery

| Symptom | Action |
|---------|--------|
| High error rate | Rollback immediately |
| OOMKilled | Increase memory limits |
| Slow startup | Increase initialDelaySeconds |
| Connection refused | Check service selector labels |
