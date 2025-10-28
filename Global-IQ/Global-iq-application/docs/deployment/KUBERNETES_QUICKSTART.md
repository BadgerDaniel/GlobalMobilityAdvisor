# Kubernetes Quick Start Guide

This is a simplified guide to get your Global IQ application running on Kubernetes quickly.

## What Was Created

```
Global-IQ/Global-iq-application/
├── k8s/                              # Kubernetes manifests directory
│   ├── namespace.yaml                # Creates 'global-iq' namespace
│   ├── configmap.yaml                # Non-sensitive environment variables
│   ├── secret.yaml.template          # Template for secrets (copy to secret.yaml)
│   ├── persistent-volume.yaml        # Storage for uploads (5Gi) and logs (2Gi)
│   ├── deployment.yaml               # App deployment (2 replicas) + LoadBalancer service
│   ├── kustomization.yaml            # Optional: Kustomize deployment config
│   └── README.md                     # Detailed k8s documentation
├── deploy-k8s.sh                     # Automated deployment script (Linux/Mac)
├── deploy-k8s.bat                    # Automated deployment script (Windows)
├── KUBERNETES_DEPLOYMENT.md          # Comprehensive deployment guide
└── KUBERNETES_QUICKSTART.md          # This file
```

## Prerequisites

1. **Docker Desktop** with Kubernetes enabled
   - Windows/Mac: Enable in Docker Desktop Settings → Kubernetes → Enable Kubernetes
   - Or use any Kubernetes cluster (Minikube, kind, cloud provider)

2. **kubectl** installed
   ```bash
   # Check installation
   kubectl version --client
   ```

3. **Docker Hub account** (for pushing images)
   - Sign up at https://hub.docker.com

4. **OpenAI API Key**
   - Get from https://platform.openai.com/api-keys

## 5-Minute Deployment

### Option A: Automated Script (Recommended)

**Windows:**
```cmd
cd Global-IQ\Global-iq-application

REM Set your Docker Hub username
set DOCKER_USERNAME=your-dockerhub-username

REM Run deployment script
deploy-k8s.bat
```

**Linux/Mac:**
```bash
cd Global-IQ/Global-iq-application

# Set your Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username

# Make script executable and run
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

The script will:
1. ✅ Check prerequisites (Docker, kubectl)
2. ✅ Build Docker image
3. ✅ Optionally push to Docker Hub
4. ✅ Create `secret.yaml` from template (asks for API keys)
5. ✅ Update deployment with correct image
6. ✅ Deploy all Kubernetes resources
7. ✅ Wait for deployment to be ready
8. ✅ Optionally start port-forwarding

### Option B: Manual Deployment

**Step 1: Build and Push Docker Image**

```bash
cd Global-IQ/Global-iq-application

# Build image
docker build -t your-username/global-iq-app:v1 .

# Test locally (optional)
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... your-username/global-iq-app:v1

# Login to Docker Hub
docker login

# Push image
docker push your-username/global-iq-app:v1
```

**Step 2: Create Secrets**

```bash
cd k8s

# Copy template
cp secret.yaml.template secret.yaml

# Encode your OpenAI API key
echo -n "sk-your-actual-api-key" | base64
# Example output: c2stZm9vYmFy...

# Encode Chainlit secret (or use default "password")
echo -n "your-secret-password" | base64
# Example output: eW91ci1zZWNyZXQ=

# Edit secret.yaml and replace the base64 values
# Use your favorite editor (notepad, vim, nano, code)
notepad secret.yaml  # Windows
nano secret.yaml     # Linux/Mac
```

**Step 3: Update Deployment Image**

Edit `k8s/deployment.yaml` line ~20:

```yaml
containers:
- name: global-iq-app
  image: your-username/global-iq-app:v1  # ← Change this
```

**Step 4: Deploy to Kubernetes**

```bash
# From the k8s directory
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f persistent-volume.yaml
kubectl apply -f deployment.yaml

# Or deploy all at once
kubectl apply -f .
```

**Step 5: Verify Deployment**

```bash
# Check all resources
kubectl get all -n global-iq

# Check pods are running
kubectl get pods -n global-iq

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# global-iq-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# global-iq-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

**Step 6: Access Application**

```bash
# Port forward to localhost
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq

# Open browser to http://localhost:8000
# Login with credentials from LOGIN_CREDENTIALS.md
```

## Common Commands

### View Status
```bash
# All resources in namespace
kubectl get all -n global-iq

# Pods with details
kubectl get pods -n global-iq -o wide

# Services
kubectl get svc -n global-iq

# Storage
kubectl get pvc -n global-iq
```

### View Logs
```bash
# Follow logs from deployment
kubectl logs -f deployment/global-iq-deployment -n global-iq

# Logs from specific pod
kubectl logs <pod-name> -n global-iq

# Previous logs (if pod crashed)
kubectl logs --previous <pod-name> -n global-iq
```

### Debugging
```bash
# Describe pod (shows events and errors)
kubectl describe pod <pod-name> -n global-iq

# Execute shell in pod
kubectl exec -it <pod-name> -n global-iq -- /bin/bash

# Check events
kubectl get events -n global-iq --sort-by='.lastTimestamp'
```

### Scaling
```bash
# Scale to 3 replicas
kubectl scale deployment/global-iq-deployment --replicas=3 -n global-iq

# Check status
kubectl get pods -n global-iq
```

### Update Application
```bash
# Build new version
docker build -t your-username/global-iq-app:v2 .
docker push your-username/global-iq-app:v2

# Update deployment
kubectl set image deployment/global-iq-deployment \
  global-iq-app=your-username/global-iq-app:v2 \
  -n global-iq

# Watch rollout
kubectl rollout status deployment/global-iq-deployment -n global-iq
```

### Cleanup
```bash
# Delete everything (including data!)
kubectl delete namespace global-iq

# Or delete individual resources
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/persistent-volume.yaml
kubectl delete -f k8s/secret.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/namespace.yaml
```

## Troubleshooting

### Pods not starting?

```bash
# Check pod status
kubectl get pods -n global-iq

# If status is "ImagePullBackOff":
#   → Wrong image name or not pushed to Docker Hub
#   → Edit k8s/deployment.yaml with correct image

# If status is "CrashLoopBackOff":
#   → Check logs: kubectl logs <pod-name> -n global-iq
#   → Usually missing OPENAI_API_KEY in secret.yaml

# If status is "Pending":
#   → Check events: kubectl describe pod <pod-name> -n global-iq
#   → Usually PVC not bound or insufficient resources
```

### Can't access application?

```bash
# Check service
kubectl get svc -n global-iq

# Make sure port-forward is running
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq

# Try accessing: http://localhost:8000
```

### Secret not working?

```bash
# Check secret exists
kubectl get secret global-iq-secrets -n global-iq

# Recreate secret
kubectl delete secret global-iq-secrets -n global-iq
kubectl apply -f k8s/secret.yaml

# Restart pods to pick up new secret
kubectl rollout restart deployment/global-iq-deployment -n global-iq
```

## Architecture Summary

```
┌─────────────────────────────────────────────────┐
│  Kubernetes Cluster (global-iq namespace)       │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  Service (LoadBalancer)                 │    │
│  │  Port: 8000                             │    │
│  └──────────────┬─────────────────────────┘    │
│                 │                               │
│  ┌──────────────▼──────────────┐                │
│  │  Deployment (2 replicas)    │                │
│  │  ┌────────────────────────┐ │                │
│  │  │  Pod 1                 │ │                │
│  │  │  - global-iq-app:v1    │ │                │
│  │  │  - Port: 8000          │ │                │
│  │  │  - CPU: 250m-500m      │ │                │
│  │  │  - RAM: 512Mi-1Gi      │ │                │
│  │  └────────────────────────┘ │                │
│  │  ┌────────────────────────┐ │                │
│  │  │  Pod 2                 │ │                │
│  │  │  - global-iq-app:v1    │ │                │
│  │  │  - Port: 8000          │ │                │
│  │  │  - CPU: 250m-500m      │ │                │
│  │  │  - RAM: 512Mi-1Gi      │ │                │
│  │  └────────────────────────┘ │                │
│  └─────────────────────────────┘                │
│                 │                               │
│  ┌──────────────▼──────────────┐                │
│  │  PersistentVolumeClaims     │                │
│  │  - uploads: 5Gi             │                │
│  │  - logs: 2Gi                │                │
│  └─────────────────────────────┘                │
│                                                  │
│  ┌─────────────────────────────┐                │
│  │  ConfigMap                  │                │
│  │  - PYTHONUNBUFFERED=1       │                │
│  │  - APP_PORT=8000            │                │
│  └─────────────────────────────┘                │
│                                                  │
│  ┌─────────────────────────────┐                │
│  │  Secret                     │                │
│  │  - openai-api-key           │                │
│  │  - chainlit-auth-secret     │                │
│  └─────────────────────────────┘                │
└─────────────────────────────────────────────────┘
```

## Next Steps

1. **Review Full Documentation**: See [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
2. **Production Setup**: Review production recommendations in `k8s/README.md`
3. **Set up Monitoring**: Add Prometheus and Grafana
4. **Configure Ingress**: Set up domain name and SSL
5. **Enable Autoscaling**: Add HorizontalPodAutoscaler
6. **CI/CD Pipeline**: Automate deployments with GitHub Actions

## Learn More

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **kubectl Cheatsheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Template Reference**: https://github.com/alexacheui/fastapi-k8s-template
- **Chainlit Docs**: https://docs.chainlit.io/

## Support

- Check logs: `kubectl logs -f deployment/global-iq-deployment -n global-iq`
- Describe resources: `kubectl describe pod <pod-name> -n global-iq`
- View events: `kubectl get events -n global-iq`
- Full documentation: `KUBERNETES_DEPLOYMENT.md`
