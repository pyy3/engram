# Kubernetes Patterns

## Resource Structure

```
k8s/
├── base/                 # Kustomize base
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── production/
└── charts/               # Helm charts (alternative)
```

## Pod Design Patterns

- **Sidecar**: logging, proxy, config reload (e.g., envoy, fluentd)
- **Init Container**: migrations, dependency checks, secret fetch
- **Ambassador**: proxy for external services (connection pooling)

## Resource Limits

Always set requests AND limits:
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

Rule of thumb: request = average usage, limit = peak * 1.5.

## Health Probes

```yaml
livenessProbe:    # Restarts pod if fails
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:   # Removes from service if fails
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Common Gotchas

- **OOMKilled**: Memory limit too low — check actual usage with metrics
- **CrashLoopBackOff**: Check logs, init containers, config
- **ImagePullBackOff**: Wrong image name, missing registry auth
- **Pending pods**: No node with enough resources — scale or adjust requests
- **DNS resolution**: Services are at `<name>.<namespace>.svc.cluster.local`
