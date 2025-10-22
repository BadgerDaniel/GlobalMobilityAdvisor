# Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the Global IQ Mobility Advisor application.

## Files Overview

| File | Description | Purpose |
|------|-------------|---------|
| `namespace.yaml` | Namespace definition | Creates isolated `global-iq` namespace |
| `configmap.yaml` | Non-sensitive config | Environment variables (Python settings, app config) |
| `secret.yaml.template` | Secret template | Template for API keys and auth secrets |
| `secret.yaml` | **Actual secrets** | **DO NOT COMMIT** - Created from template |
| `persistent-volume.yaml` | PersistentVolumeClaims | Storage for uploads (5Gi) and logs (2Gi) |
| `deployment.yaml` | Deployment + Service | App deployment (2 replicas) and LoadBalancer service |
| `kustomization.yaml` | Kustomize config | Optional: Deploy all resources with Kustomize |

## Quick Start

### 1. Create Secrets File

```bash
# Copy template
cp secret.yaml.template secret.yaml

# Encode your secrets
echo -n "sk-your-openai-key" | base64
echo -n "your-chainlit-secret" | base64

# Edit secret.yaml and paste the base64 values
# IMPORTANT: Never commit secret.yaml to git!
```

### 2. Update Docker Image

Edit `deployment.yaml` line 20:

```yaml
image: YOUR_DOCKERHUB_USERNAME/global-iq-app:v1
```

Replace with your actual Docker Hub username.

### 3. Deploy

```bash
# Deploy all resources in order
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f persistent-volume.yaml
kubectl apply -f deployment.yaml

# Or use Kustomize
kubectl apply -k .
```

### 4. Verify

```bash
kubectl get all -n global-iq
kubectl get pvc -n global-iq
kubectl logs -f deployment/global-iq-deployment -n global-iq
```

### 5. Access

```bash
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq
# Open http://localhost:8000
```

## Resource Details

### Namespace
- **Name**: `global-iq`
- **Purpose**: Isolate application resources from other workloads

### ConfigMap
- **Name**: `global-iq-config`
- **Data**: Python environment variables, app settings
- **Used by**: Deployment via `envFrom`

### Secret
- **Name**: `global-iq-secrets`
- **Type**: Opaque
- **Keys**:
  - `chainlit-auth-secret`: Chainlit authentication secret
  - `openai-api-key`: OpenAI API key
- **Used by**: Deployment via `valueFrom.secretKeyRef`

### PersistentVolumeClaims
1. **global-iq-uploads-pvc**
   - Storage: 5Gi
   - Access Mode: ReadWriteOnce
   - Mount: `/app/uploads`

2. **global-iq-logs-pvc**
   - Storage: 2Gi
   - Access Mode: ReadWriteOnce
   - Mount: `/app/logs`

### Deployment
- **Name**: `global-iq-deployment`
- **Replicas**: 2
- **Image**: Your Docker Hub image
- **Container Port**: 8000
- **Resources**:
  - Requests: 250m CPU, 512Mi RAM
  - Limits: 500m CPU, 1Gi RAM
- **Health Checks**:
  - Liveness: `/health` endpoint, 30s interval
  - Readiness: `/health` endpoint, 10s interval
- **Volumes**: uploads-storage, logs-storage

### Service
- **Name**: `global-iq-service`
- **Type**: LoadBalancer
- **Port**: 8000 → 8000
- **Selector**: `app: global-iq`

## Customization

### Change Replica Count

Edit `deployment.yaml`:

```yaml
spec:
  replicas: 3  # Change this value
```

Or use kubectl:

```bash
kubectl scale deployment/global-iq-deployment --replicas=3 -n global-iq
```

### Adjust Resources

Edit `deployment.yaml`:

```yaml
resources:
  requests:
    memory: "1Gi"     # Increase if needed
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Change Storage Size

Edit `persistent-volume.yaml` BEFORE first deployment:

```yaml
resources:
  requests:
    storage: 10Gi  # Increase size
```

**Note**: Cannot resize after creation without manual intervention.

### Use Different Service Type

Edit `deployment.yaml` Service section:

```yaml
spec:
  type: NodePort  # or ClusterIP
```

## Production Recommendations

### 1. Use Ingress Instead of LoadBalancer

Create `ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: global-iq-ingress
  namespace: global-iq
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - globaliq.yourdomain.com
    secretName: globaliq-tls
  rules:
  - host: globaliq.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: global-iq-service
            port:
              number: 8000
```

### 2. Use External Secrets Operator

Instead of storing secrets in YAML:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: global-iq-secrets
  namespace: global-iq
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: global-iq-secrets
  data:
  - secretKey: openai-api-key
    remoteRef:
      key: global-iq/openai-api-key
```

### 3. Add HorizontalPodAutoscaler

Create `hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: global-iq-hpa
  namespace: global-iq
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: global-iq-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 4. Add Network Policy

Create `networkpolicy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: global-iq-netpol
  namespace: global-iq
spec:
  podSelector:
    matchLabels:
      app: global-iq
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS for OpenAI API
```

### 5. Add Resource Quotas

Create `resourcequota.yaml`:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: global-iq-quota
  namespace: global-iq
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "5"
```

## Troubleshooting

### Pods Stuck in Pending

```bash
# Check events
kubectl get events -n global-iq --sort-by='.lastTimestamp'

# Check PVC status
kubectl get pvc -n global-iq

# Common causes:
# - PVC not bound (no storage class available)
# - Insufficient cluster resources
```

### ImagePullBackOff

```bash
# Describe pod
kubectl describe pod <pod-name> -n global-iq

# Common causes:
# - Wrong image name in deployment.yaml
# - Image not pushed to Docker Hub
# - Private registry without imagePullSecrets
```

### CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n global-iq

# Check previous logs if pod restarted
kubectl logs --previous <pod-name> -n global-iq

# Common causes:
# - Missing OPENAI_API_KEY secret
# - Application error at startup
# - Health check endpoint failing
```

### Secret Not Found

```bash
# Check if secret exists
kubectl get secret global-iq-secrets -n global-iq

# View secret keys (not values)
kubectl describe secret global-iq-secrets -n global-iq

# Create from template if missing
cp secret.yaml.template secret.yaml
# Edit and apply
kubectl apply -f secret.yaml
```

## Cleanup

```bash
# Delete entire namespace (all resources)
kubectl delete namespace global-iq

# Or delete individual resources
kubectl delete -f deployment.yaml
kubectl delete -f persistent-volume.yaml
kubectl delete -f secret.yaml
kubectl delete -f configmap.yaml
kubectl delete -f namespace.yaml
```

**Note**: Deleting PVCs will delete the stored data. Backup first if needed.

## Security Best Practices

1. **Never commit `secret.yaml`** - It's in `.gitignore`
2. **Use RBAC** - Limit who can access secrets
3. **Rotate secrets regularly** - Update OpenAI keys periodically
4. **Use Pod Security Standards** - Enforce security policies
5. **Scan images** - Use Trivy or Snyk to scan for vulnerabilities
6. **Limit network access** - Use NetworkPolicies
7. **Run as non-root** - Update Dockerfile to use non-root user

## Additional Resources

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
