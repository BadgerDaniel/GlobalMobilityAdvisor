# Deployment Guide

Choose your deployment method based on your environment and requirements.

---

## Deployment Options

### 🐳 Docker Compose (Recommended for Development)
**Best for:** Local development, testing, quick demos

**Pros:**
- One command to start everything
- All services containerized
- Easy to tear down and rebuild

**Getting Started:** [Docker Deployment Guide](DOCKER.md)

---

### ☸️ Kubernetes (Recommended for Production)
**Best for:** Production deployments, cloud environments, scalability

**Pros:**
- High availability (2+ replicas)
- Auto-scaling and self-healing
- Load balancing built-in
- Cloud-native

**Getting Started:** 
- [Kubernetes Quick Start](KUBERNETES_QUICKSTART.md) - Deploy in 10 minutes
- [Kubernetes Full Guide](KUBERNETES.md) - Comprehensive deployment guide

---

### 🖥️ Local Development
**Best for:** Quick testing without containers

**Pros:**
- Fastest startup
- Easy debugging
- No Docker required

**Commands:**
```bash
# Run main app only
chainlit run app/main.py

# Run with MCP servers (3 terminals)
# Terminal 1:
python services/mcp_prediction_server/compensation_server.py
# Terminal 2:
python services/mcp_prediction_server/policy_server.py
# Terminal 3:
chainlit run app/main.py
```

**See:** [Quick Start Guide](../getting-started/README.md)

---

## Quick Comparison

| Feature | Local | Docker | Kubernetes |
|---------|-------|--------|------------|
| Setup Time | 1 min | 5 min | 15 min |
| Complexity | Simple | Medium | Advanced |
| Scalability | No | Limited | Excellent |
| HA | No | No | Yes |
| Production Ready | No | Partial | Yes |
| Cloud Native | No | Partial | Yes |

---

## Next Steps

1. **For Development**: Start with [Docker](DOCKER.md)
2. **For Production**: Use [Kubernetes](KUBERNETES.md)
3. **For Quick Test**: Use local development

---

## Support

- **Docker issues**: See [Docker Guide troubleshooting](DOCKER.md)
- **Kubernetes issues**: See [K8s Guide troubleshooting](KUBERNETES.md)
- **Application issues**: See [Architecture Guide](../architecture/README.md)
