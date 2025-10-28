# Kubernetes Deployment Guide

This guide explains how to deploy the Global IQ Mobility Advisor to Kubernetes, following the containerization patterns from the [fastapi-k8s-template](https://github.com/alexacheui/fastapi-k8s-template).

## Prerequisites

- **Docker Desktop** with Kubernetes enabled (or any Kubernetes cluster)
- **kubectl** command-line tool installed
- **Docker Hub account** (for pushing images to a registry)
- **OpenAI API key**

## Quick Start

### 1. Build and Push Docker Image

```bash
# Set your Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username
export VERSION=v1

# Build the image
docker build -t ${DOCKER_USERNAME}/global-iq-app:${VERSION} .

# Test locally (optional)
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... ${DOCKER_USERNAME}/global-iq-app:${VERSION}

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push ${DOCKER_USERNAME}/global-iq-app:${VERSION}
```

### 2. Configure Secrets

Create `k8s/secret.yaml` from the template:

```bash
# Create base64 encoded values
echo -n "sk-your-openai-api-key" | base64
echo -n "your-chainlit-secret" | base64

# Copy template and edit with your values
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml and replace the base64 values
```

**IMPORTANT**: Add `k8s/secret.yaml` to `.gitignore` to avoid committing secrets!

### 3. Update Deployment Image

Edit `k8s/deployment.yaml` and update the image reference:

```yaml
spec:
  containers:
  - name: global-iq-app
    image: YOUR_DOCKERHUB_USERNAME/global-iq-app:v1  # <-- Update this line
```

### 4. Deploy to Kubernetes

```bash
# Deploy everything
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/deployment.yaml

# Or use the automated script
./deploy-k8s.sh
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n global-iq

# Check services
kubectl get svc -n global-iq

# View logs
kubectl logs -f deployment/global-iq-deployment -n global-iq

# Describe pod for troubleshooting
kubectl describe pod <pod-name> -n global-iq
```

### 6. Access the Application

```bash
# Port forward to access locally
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq

# Then open http://localhost:8000 in your browser
```

## Architecture Overview

### Kubernetes Resources

The deployment consists of:

1. **Namespace** (`namespace.yaml`): Isolated environment `global-iq`
2. **ConfigMap** (`configmap.yaml`): Non-sensitive configuration
3. **Secret** (`secret.yaml`): Sensitive data (API keys, auth secrets)
4. **PersistentVolumeClaims** (`persistent-volume.yaml`): Storage for uploads and logs
5. **Deployment** (`deployment.yaml`): Application pods (2 replicas)
6. **Service** (`deployment.yaml`): LoadBalancer exposing port 8000

### Resource Specifications

**CPU/Memory Limits:**
- Requests: 250m CPU, 512Mi RAM
- Limits: 500m CPU, 1Gi RAM

**Storage:**
- Uploads: 5Gi persistent volume
- Logs: 2Gi persistent volume

**Health Checks:**
- Liveness probe: `/health` endpoint, 30s interval
- Readiness probe: `/health` endpoint, 10s interval

## File Structure

```
Global-IQ/Global-iq-application/
├── k8s/
│   ├── namespace.yaml           # Namespace definition
│   ├── configmap.yaml           # Environment variables
│   ├── secret.yaml.template     # Secret template (DO NOT commit secret.yaml)
│   ├── persistent-volume.yaml   # PVCs for storage
│   ├── deployment.yaml          # Deployment + Service
│   └── kustomization.yaml       # Kustomize config (optional)
├── deploy-k8s.sh                # Automated deployment script
├── Dockerfile                   # Container build instructions
├── docker-compose.yml           # Docker Compose config
└── KUBERNETES_DEPLOYMENT.md     # This file
```

## Deployment Script

The `deploy-k8s.sh` script automates the entire deployment process:

```bash
# Basic usage
./deploy-k8s.sh

# With custom Docker Hub username and version
DOCKER_USERNAME=myname VERSION=v2 ./deploy-k8s.sh
```

**Script features:**
- Validates prerequisites (Docker, kubectl)
- Builds Docker image
- Optionally pushes to Docker Hub
- Creates `secret.yaml` interactively if missing
- Updates deployment manifest with correct image
- Deploys all Kubernetes resources
- Waits for deployment readiness
- Offers to start port-forwarding

## Common Operations

### Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment/global-iq-deployment --replicas=3 -n global-iq

# Or edit deployment.yaml and reapply
```

### Updating the Application

```bash
# Build new version
docker build -t ${DOCKER_USERNAME}/global-iq-app:v2 .
docker push ${DOCKER_USERNAME}/global-iq-app:v2

# Update deployment
kubectl set image deployment/global-iq-deployment \
  global-iq-app=${DOCKER_USERNAME}/global-iq-app:v2 \
  -n global-iq

# Or edit deployment.yaml and reapply
kubectl apply -f k8s/deployment.yaml
```

### Viewing Logs

```bash
# Follow logs from all pods
kubectl logs -f deployment/global-iq-deployment -n global-iq

# Logs from specific pod
kubectl logs -f <pod-name> -n global-iq

# Previous pod logs (if crashed)
kubectl logs --previous <pod-name> -n global-iq
```

### Debugging

```bash
# Get pod details
kubectl describe pod <pod-name> -n global-iq

# Execute commands in pod
kubectl exec -it <pod-name> -n global-iq -- /bin/bash

# Check events
kubectl get events -n global-iq --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n global-iq
```

### Cleanup

```bash
# Delete entire namespace (all resources)
kubectl delete namespace global-iq

# Or delete individual resources
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/persistent-volume.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
```

## Environment Variables

### ConfigMap (non-sensitive)

Defined in `k8s/configmap.yaml`:
- `PYTHONDONTWRITEBYTECODE=1`
- `PYTHONUNBUFFERED=1`
- `APP_PORT=8000`
- `APP_HOST=0.0.0.0`

### Secret (sensitive)

Defined in `k8s/secret.yaml` (base64 encoded):
- `chainlit-auth-secret`: Chainlit authentication secret
- `openai-api-key`: OpenAI API key

## Production Considerations

### 1. Use a Managed Kubernetes Service

Instead of Docker Desktop Kubernetes, consider:
- **AWS EKS** (Elastic Kubernetes Service)
- **Google GKE** (Google Kubernetes Engine)
- **Azure AKS** (Azure Kubernetes Service)
- **DigitalOcean Kubernetes**

### 2. Ingress Controller

For production, use an Ingress instead of LoadBalancer:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: global-iq-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
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

### 3. Use Secrets Management

Instead of storing secrets in YAML files:
- **AWS Secrets Manager** + External Secrets Operator
- **HashiCorp Vault**
- **Sealed Secrets** (Bitnami)

### 4. Persistent Volume Considerations

For production:
- Use cloud provider storage classes (AWS EBS, GCP Persistent Disk, Azure Disk)
- Set up backup/restore procedures
- Consider `ReadWriteMany` access mode if scaling beyond single-node

### 5. Monitoring and Logging

Add observability:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** or **Loki** for log aggregation
- **Jaeger** or **OpenTelemetry** for tracing

### 6. Security Hardening

- Run as non-root user in Dockerfile
- Use Network Policies to restrict traffic
- Enable Pod Security Standards
- Scan images for vulnerabilities (Trivy, Snyk)
- Use read-only root filesystem where possible

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n global-iq

# Describe pod for events
kubectl describe pod <pod-name> -n global-iq

# Common issues:
# - ImagePullBackOff: Wrong image name or not pushed to registry
# - CrashLoopBackOff: Application crashing, check logs
# - Pending: Insufficient resources or PVC not bound
```

### Health Check Failures

If liveness/readiness probes fail:

```bash
# Check if /health endpoint exists
kubectl exec -it <pod-name> -n global-iq -- curl localhost:8000/health

# Adjust probe timing in deployment.yaml if needed
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n global-iq

# Describe PVC
kubectl describe pvc global-iq-uploads-pvc -n global-iq

# If Pending, check storage class availability
kubectl get storageclass
```

## Comparison: Docker Compose vs Kubernetes

| Feature | Docker Compose | Kubernetes |
|---------|----------------|------------|
| **Orchestration** | Single host | Multi-node cluster |
| **Scaling** | Manual | Automatic (HPA) |
| **Load Balancing** | Limited | Built-in |
| **Health Checks** | Basic | Advanced probes |
| **Storage** | Volume mounts | PersistentVolumes |
| **Secrets** | Environment files | Encrypted Secrets |
| **Updates** | Manual restart | Rolling updates |
| **High Availability** | No | Yes |
| **Best For** | Development | Production |

## Next Steps

1. **Set up CI/CD**: Automate builds and deployments (GitHub Actions, GitLab CI)
2. **Configure Ingress**: Set up domain name and SSL certificates
3. **Enable Monitoring**: Deploy Prometheus and Grafana
4. **Implement Autoscaling**: Add HorizontalPodAutoscaler
5. **Backup Strategy**: Automate PVC backups with Velero
6. **Security Audit**: Implement Pod Security Standards and Network Policies

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [fastapi-k8s-template](https://github.com/alexacheui/fastapi-k8s-template)
- [Chainlit Documentation](https://docs.chainlit.io/)

## Support

For issues specific to:
- **Kubernetes deployment**: Check this guide and Kubernetes docs
- **Application functionality**: See `CLAUDE.md` in project root
- **Docker issues**: See `DOCKER_DEPLOYMENT.md`
