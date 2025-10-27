# 🚀 Your Next Steps - Kubernetes Deployment

**Last Updated**: October 21, 2025
**Status**: Ready for deployment testing
**Estimated Time to Deploy**: 10-15 minutes

---

## 📍 Where We Are Right Now

### ✅ **Completed Work**

You now have a **production-ready Kubernetes deployment setup** for your Global IQ Mobility Advisor application:

1. **Kubernetes Infrastructure** (7 manifest files in `k8s/` directory)
2. **Automated Deployment Scripts** (`deploy-k8s.bat` for Windows, `deploy-k8s.sh` for Linux/Mac)
3. **Comprehensive Documentation** (3 guides covering quick start to production)
4. **Security Setup** (Secrets management, .gitignore updates)

### 📦 **What You Already Had**

- ✅ Working Chainlit application
- ✅ Docker containerization (Dockerfile + docker-compose.yml)
- ✅ OpenAI integration
- ✅ User authentication system
- ✅ File processing (PDF, DOCX, XLSX, CSV)

### 🎯 **Current Architecture**

```
You Have:                           We Added:
┌──────────────────┐               ┌────────────────────────┐
│ Docker Compose   │──────────────>│ Kubernetes Cluster     │
│ - Single container│               │ - 2 replicas           │
│ - Port 8000      │               │ - LoadBalancer         │
│ - Local only     │               │ - Auto-scaling ready   │
└──────────────────┘               │ - Production-ready     │
                                   └────────────────────────┘
```

---

## 🎯 Your Next Steps (In Order)

### **Phase 1: Prerequisites Check** (5 minutes)

#### Step 1.1: Verify Docker Desktop Kubernetes

**Windows:**
```cmd
# Check Docker is running
docker --version
docker info

# Check Kubernetes is enabled
kubectl version --client
kubectl cluster-info

# If "connection refused", enable Kubernetes:
# Docker Desktop → Settings → Kubernetes → Enable Kubernetes → Apply & Restart
```

**Expected Output:**
```
Kubernetes control plane is running at https://kubernetes.docker.internal:6443
```

#### Step 1.2: Get a Docker Hub Account (if you don't have one)

1. Go to https://hub.docker.com
2. Sign up (free account is fine)
3. Remember your username - you'll need it!

**Or use a local registry** (advanced):
```bash
# Skip Docker Hub, use local images only
# We'll cover this option later if needed
```

#### Step 1.3: Login to Docker Hub

```cmd
docker login
# Enter your Docker Hub username and password
```

#### Step 1.4: Have Your OpenAI API Key Ready

- Get from: https://platform.openai.com/api-keys
- Keep it handy - you'll paste it during deployment
- Format: `sk-...` (starts with "sk-")

---

### **Phase 2: First Deployment (10 minutes)**

You have **two options**: Automated (recommended) or Manual

---

#### **Option A: Automated Deployment** ⭐ **RECOMMENDED**

This is the easiest and fastest way. The script does everything for you.

**Step 2.1: Open Command Prompt**

```cmd
# Navigate to the application directory
cd e:\SSD2_Projects\GIQ_Q2\Global-IQ\Global-iq-application
```

**Step 2.2: Set Your Docker Hub Username**

```cmd
# Replace "your-dockerhub-username" with your actual username
set DOCKER_USERNAME=your-dockerhub-username

# Example:
# set DOCKER_USERNAME=johndoe
```

**Step 2.3: Run the Deployment Script**

```cmd
deploy-k8s.bat
```

**Step 2.4: Follow the Prompts**

The script will ask you:

1. **"Push to Docker Hub? (y/n)"**
   - Type `y` if you have Docker Hub access
   - Type `n` to test locally only (skip if testing on single machine)

2. **"Enter your OpenAI API key:"**
   - Paste your API key: `sk-...`
   - Press Enter

3. **"Enter Chainlit auth secret (or press enter for 'password'):"**
   - Press Enter to use default "password"
   - Or type a custom secret

4. **"Would you like to start port-forwarding now? (y/n)"**
   - Type `y` to access the app immediately
   - The app will be available at http://localhost:8000

**Expected Output:**
```
========================================
Global IQ Kubernetes Deployment
========================================

Step 1: Checking prerequisites...
[OK] Prerequisites check passed

Step 2: Building Docker image...
[OK] Docker image built successfully

Step 3: Push to Docker Hub? (y/n)
y
[OK] Image pushed successfully

Step 4: Checking Kubernetes secrets...
Enter your OpenAI API key: sk-***
[OK] secret.yaml created

Step 5: Updating deployment manifest...
[OK] Deployment manifest updated

Step 6: Deploying to Kubernetes...
[OK] Kubernetes resources deployed

Step 7: Waiting for deployment to be ready...
[OK] Deployment is ready

========================================
Deployment Complete!
========================================

Namespace: global-iq
Image: your-username/global-iq-app:v1

Would you like to start port-forwarding now? (y/n)
y

Starting port-forward on http://localhost:8000
Press Ctrl+C to stop
```

**Step 2.5: Test the Application**

1. Open browser to: **http://localhost:8000**
2. Login with credentials from [LOGIN_CREDENTIALS.md](LOGIN_CREDENTIALS.md):
   - Username: `admin`
   - Password: `admin123`
3. Test basic functionality:
   - Ask a policy question: "What visa do I need for UK?"
   - Upload a test document
   - Verify the response

**✅ If it works, you're done! Your app is running on Kubernetes!**

---

#### **Option B: Manual Deployment**

If you prefer to understand each step or troubleshoot issues:

See [KUBERNETES_QUICKSTART.md](KUBERNETES_QUICKSTART.md) → "Option B: Manual Deployment"

---

### **Phase 3: Verification & Monitoring** (5 minutes)

Once deployed, verify everything is working:

**Step 3.1: Check Pod Status**

Open a **new command prompt** (keep port-forward running in the first one):

```cmd
kubectl get pods -n global-iq
```

**Expected Output:**
```
NAME                                    READY   STATUS    RESTARTS   AGE
global-iq-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
global-iq-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

Both pods should be `Running` with `1/1` ready.

**Step 3.2: Check Service**

```cmd
kubectl get svc -n global-iq
```

**Expected Output:**
```
NAME                TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
global-iq-service   LoadBalancer   10.96.xxx.xxx   localhost     8000:xxxxx/TCP   2m
```

**Step 3.3: Check Storage**

```cmd
kubectl get pvc -n global-iq
```

**Expected Output:**
```
NAME                     STATUS   VOLUME                                     CAPACITY   AGE
global-iq-logs-pvc       Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   2Gi        2m
global-iq-uploads-pvc    Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   5Gi        2m
```

Both PVCs should be `Bound`.

**Step 3.4: View Logs**

```cmd
kubectl logs -f deployment/global-iq-deployment -n global-iq
```

You should see Chainlit startup logs. Press `Ctrl+C` to exit.

**Step 3.5: Check All Resources**

```cmd
kubectl get all -n global-iq
```

This shows everything at once: pods, services, deployments, replicasets.

---

### **Phase 4: Common Operations** (Reference)

#### **Scale the Application**

```cmd
# Scale to 3 replicas
kubectl scale deployment/global-iq-deployment --replicas=3 -n global-iq

# Verify
kubectl get pods -n global-iq

# Scale back to 2
kubectl scale deployment/global-iq-deployment --replicas=2 -n global-iq
```

#### **Update the Application**

After making code changes:

```cmd
# Build new version
docker build -t your-username/global-iq-app:v2 .

# Push to Docker Hub
docker push your-username/global-iq-app:v2

# Update Kubernetes deployment
kubectl set image deployment/global-iq-deployment ^
  global-iq-app=your-username/global-iq-app:v2 ^
  -n global-iq

# Watch the rollout
kubectl rollout status deployment/global-iq-deployment -n global-iq
```

#### **View Logs from Specific Pod**

```cmd
# Get pod name
kubectl get pods -n global-iq

# View logs
kubectl logs <pod-name> -n global-iq

# Follow logs
kubectl logs -f <pod-name> -n global-iq

# Previous logs (if pod crashed)
kubectl logs --previous <pod-name> -n global-iq
```

#### **Restart Deployment**

```cmd
kubectl rollout restart deployment/global-iq-deployment -n global-iq
```

#### **Access Pod Shell**

```cmd
# Get pod name
kubectl get pods -n global-iq

# Execute bash in pod
kubectl exec -it <pod-name> -n global-iq -- /bin/bash

# Inside pod, you can run:
ls -la /app
cat /app/requirements.txt
exit
```

---

### **Phase 5: Troubleshooting** (If Needed)

#### **Issue: Pods Stuck in "Pending"**

```cmd
# Check what's wrong
kubectl describe pod <pod-name> -n global-iq

# Common causes:
# - PVC not bound → Check: kubectl get pvc -n global-iq
# - Insufficient resources → Enable more resources in Docker Desktop
```

**Fix for PVC issues:**
```cmd
# Check storage class exists
kubectl get storageclass

# If none, Docker Desktop should provide one automatically
# Restart Docker Desktop if needed
```

#### **Issue: Pods Stuck in "ImagePullBackOff"**

```cmd
# Check the error
kubectl describe pod <pod-name> -n global-iq

# Common causes:
# - Wrong image name in deployment.yaml
# - Image not pushed to Docker Hub
# - Docker Hub authentication failed
```

**Fix:**
```cmd
# Check deployment image
kubectl get deployment global-iq-deployment -n global-iq -o yaml | findstr image:

# Should match: your-username/global-iq-app:v1

# Update if wrong
kubectl edit deployment global-iq-deployment -n global-iq
# Change the image line, save, exit
```

#### **Issue: Pods in "CrashLoopBackOff"**

```cmd
# Check logs
kubectl logs <pod-name> -n global-iq

# Common causes:
# - Missing OpenAI API key
# - Invalid secret.yaml
# - Application error
```

**Fix for missing secrets:**
```cmd
# Check secret exists
kubectl get secret global-iq-secrets -n global-iq

# Recreate secret
cd k8s
copy secret.yaml.template secret.yaml
# Edit secret.yaml with your base64-encoded API key

# Apply
kubectl delete secret global-iq-secrets -n global-iq
kubectl apply -f secret.yaml

# Restart deployment
kubectl rollout restart deployment/global-iq-deployment -n global-iq
```

#### **Issue: Can't Access Application**

```cmd
# Make sure port-forward is running
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq

# If port 8000 is already in use
kubectl port-forward svc/global-iq-service 8080:8000 -n global-iq
# Then access at http://localhost:8080
```

#### **Issue: "Connection Refused" to Kubernetes**

```cmd
# Check Kubernetes is enabled in Docker Desktop
kubectl cluster-info

# If error, go to:
# Docker Desktop → Settings → Kubernetes → Enable Kubernetes → Apply & Restart
# Wait 2-3 minutes for Kubernetes to start
```

---

### **Phase 6: Cleanup** (When Done Testing)

#### **Option A: Delete Everything**

```cmd
# Delete entire namespace (removes all resources)
kubectl delete namespace global-iq

# This removes:
# - Pods
# - Services
# - PVCs (and data!)
# - ConfigMaps
# - Secrets
```

#### **Option B: Keep Infrastructure, Delete Pods Only**

```cmd
# Delete deployment (keeps storage and config)
kubectl delete deployment global-iq-deployment -n global-iq
kubectl delete service global-iq-service -n global-iq

# Storage and secrets remain
```

#### **Option C: Stop Kubernetes, Keep Config**

```cmd
# Just stop Docker Desktop Kubernetes
# Docker Desktop → Settings → Kubernetes → Uncheck "Enable Kubernetes"

# All manifests remain in k8s/ directory
# Can re-enable and re-deploy anytime
```

---

## 🎓 What Happens Next?

### **Immediate Next Steps**

1. ✅ **Test Local Deployment** (follow Phase 2 above)
2. ✅ **Verify All Features Work** (login, file upload, queries)
3. ✅ **Try Scaling** (Phase 4 - scale to 3 replicas)
4. ✅ **Review Logs** (Phase 3.4 - understand what's happening)

### **After Successful Local Testing**

Once working locally, you can:

#### **Option 1: Deploy to Cloud Kubernetes**

Move from Docker Desktop to production cloud:

- **AWS EKS** (Elastic Kubernetes Service)
  - Same `k8s/` manifests work
  - Just change kubectl context
  - Guide: https://docs.aws.amazon.com/eks/

- **Google GKE** (Google Kubernetes Engine)
  - Same manifests
  - Guide: https://cloud.google.com/kubernetes-engine/docs

- **Azure AKS** (Azure Kubernetes Service)
  - Same manifests
  - Guide: https://docs.microsoft.com/azure/aks/

- **DigitalOcean Kubernetes**
  - Easiest and cheapest for testing
  - Guide: https://docs.digitalocean.com/products/kubernetes/

#### **Option 2: Set Up Production Features**

Enhance your deployment:

1. **Ingress Controller** (instead of LoadBalancer)
   - Get a domain name
   - Set up SSL certificates (Let's Encrypt)
   - Configure NGINX Ingress

2. **Autoscaling** (HorizontalPodAutoscaler)
   - Automatically scale based on CPU/memory
   - Handle traffic spikes

3. **Monitoring** (Prometheus + Grafana)
   - Track performance metrics
   - Set up alerts
   - View dashboards

4. **Logging** (ELK Stack or Loki)
   - Centralized log management
   - Search and analyze logs
   - Debugging production issues

5. **CI/CD Pipeline** (GitHub Actions)
   - Automate builds on git push
   - Run tests automatically
   - Deploy to staging/production

#### **Option 3: Integrate with AGNO MCP**

You have plans for this in `README_AGNO_MCP.md`:

- Add real ML prediction models
- External API integration
- Model versioning
- Confidence scores

---

## 📚 Documentation Quick Reference

| When You Need... | Read This... |
|------------------|--------------|
| **Quick deployment** | [KUBERNETES_QUICKSTART.md](KUBERNETES_QUICKSTART.md) |
| **Detailed setup** | [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) |
| **Customize manifests** | [k8s/README.md](k8s/README.md) |
| **Current status** | [CONTAINERIZATION_STATUS.md](CONTAINERIZATION_STATUS.md) |
| **Next steps** | [NEXT_STEPS.md](NEXT_STEPS.md) (this file) |
| **Docker Compose** | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) |
| **Application details** | [../../CLAUDE.md](../../CLAUDE.md) |
| **Login credentials** | [LOGIN_CREDENTIALS.md](LOGIN_CREDENTIALS.md) |

---

## ✅ Quick Command Reference

### **Deploy**
```cmd
set DOCKER_USERNAME=your-username
deploy-k8s.bat
```

### **Check Status**
```cmd
kubectl get all -n global-iq
kubectl get pods -n global-iq
kubectl get svc -n global-iq
kubectl get pvc -n global-iq
```

### **View Logs**
```cmd
kubectl logs -f deployment/global-iq-deployment -n global-iq
```

### **Access Application**
```cmd
kubectl port-forward svc/global-iq-service 8000:8000 -n global-iq
# Then: http://localhost:8000
```

### **Scale**
```cmd
kubectl scale deployment/global-iq-deployment --replicas=3 -n global-iq
```

### **Update**
```cmd
docker build -t username/global-iq-app:v2 .
docker push username/global-iq-app:v2
kubectl set image deployment/global-iq-deployment global-iq-app=username/global-iq-app:v2 -n global-iq
```

### **Cleanup**
```cmd
kubectl delete namespace global-iq
```

---

## 🎯 Success Criteria

You'll know everything is working when:

- ✅ `kubectl get pods -n global-iq` shows 2 pods in "Running" status
- ✅ `kubectl get svc -n global-iq` shows LoadBalancer service
- ✅ http://localhost:8000 loads the Chainlit interface
- ✅ You can login with admin credentials
- ✅ You can ask a question and get a response
- ✅ You can upload a file and it processes correctly

---

## 🚀 Your Immediate Action

**Right now, run this:**

```cmd
cd e:\SSD2_Projects\GIQ_Q2\Global-IQ\Global-iq-application
set DOCKER_USERNAME=your-dockerhub-username
deploy-k8s.bat
```

That's it! The script will guide you through the rest.

---

**Need Help?**
- Check [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) troubleshooting section
- Review logs: `kubectl logs -f deployment/global-iq-deployment -n global-iq`
- Check events: `kubectl get events -n global-iq --sort-by='.lastTimestamp'`

**Good luck! 🚀**
