# Installation Guide

Complete installation instructions for Global IQ Mobility Advisor.

---

## System Requirements

- **Python:** 3.11 or higher
- **OS:** Windows, macOS, or Linux
- **Memory:** 2GB RAM minimum
- **Disk:** 500MB free space
- **OpenAI API Key:** Required ([Get one here](https://platform.openai.com/api-keys))

**Optional:**
- Docker Desktop (for containerized deployment)
- kubectl (for Kubernetes deployment)

---

## Installation Methods

### Method 1: Standard Installation (Recommended)

**Step 1: Clone Repository**
```bash
git clone <repository-url>
cd Global-IQ/Global-iq-application
```

**Step 2: Create Virtual Environment**
```bash
# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4: Configure Environment**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Or copy template
cp .env.example .env
# Then edit .env with your API key
```

**Step 5: Verify Installation**
```bash
# Quick test
python -c "import chainlit; print('✅ Chainlit installed')"
python -c "import openai; print('✅ OpenAI installed')"
python -c "import langchain; print('✅ LangChain installed')"
```

**Step 6: Run Application**
```bash
chainlit run app/main.py
```

Access at: **http://localhost:8000**

---

### Method 2: Docker Installation

**Prerequisites:**
- Docker Desktop installed and running

**Step 1: Clone Repository**
```bash
git clone <repository-url>
cd Global-IQ/Global-iq-application
```

**Step 2: Configure Environment**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Step 3: Build and Run**
```bash
# Start all services (app + MCP servers)
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access at: **http://localhost:8000**

See [Docker Deployment Guide](../deployment/DOCKER.md) for details.

---

### Method 3: Kubernetes Installation

For production deployment to Kubernetes cluster.

See [Kubernetes Deployment Guide](../deployment/KUBERNETES.md) for complete instructions.

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (auto-configured for Docker)
ENABLE_MCP=true
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082

# Chainlit settings
CHAINLIT_AUTH_SECRET=password
```

### Advanced Configuration

**Change Port:**
```bash
# Default: 8000
chainlit run app/main.py --port 8080
```

**Change Host:**
```bash
# Default: localhost
chainlit run app/main.py --host 0.0.0.0
```

**Disable MCP Integration:**
```bash
# In .env file
ENABLE_MCP=false
```

---

## Optional Components

### MCP Prediction Servers

The MCP servers are optional. The app works standalone with GPT-4 fallback.

**Install MCP Server Dependencies:**
```bash
cd services/mcp_prediction_server
pip install -r requirements.txt
```

**Run Servers:**
```bash
# Terminal 1: Compensation Server
python services/mcp_prediction_server/compensation_server.py

# Terminal 2: Policy Server
python services/mcp_prediction_server/policy_server.py
```

**Verify Servers:**
```bash
curl http://localhost:8081/health
curl http://localhost:8082/health
```

---

## Verification Steps

### 1. Check Python Version
```bash
python --version
# Should be 3.11 or higher
```

### 2. Check Dependencies
```bash
pip list | grep -E "(chainlit|openai|langchain)"
```

Expected output:
```
chainlit              X.X.X
openai                X.X.X
langchain             X.X.X
langchain-openai      X.X.X
```

### 3. Test OpenAI Connection
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print('✅ API Key found' if api_key else '❌ API Key missing')
"
```

### 4. Run Application
```bash
chainlit run app/main.py
```

Should see:
```
Your app is available at http://localhost:8000
```

### 5. Test Login
- Open http://localhost:8000
- Login with: `employee` / `employee123`
- Should see welcome message

---

## Troubleshooting

### "Command 'chainlit' not found"

**Solution:** Activate virtual environment
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### "No module named 'chainlit'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### "OpenAI API Error: Invalid API key"

**Solution:** Check API key
```bash
# Verify .env file exists
cat .env

# Check key is valid format (starts with sk-)
echo $OPENAI_API_KEY
```

### "Port 8000 already in use"

**Solution:** Use different port
```bash
chainlit run app/main.py --port 8080
```

Or find and kill process using port:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill <PID>
```

### "ModuleNotFoundError: No module named 'xxx'"

**Solution:** Install missing package
```bash
pip install <package-name>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

### "Permission denied" on Linux/Mac

**Solution:** Fix permissions
```bash
chmod +x deploy-k8s.sh
chmod +x START_MCP_SERVERS.bat
```

### Docker Build Fails

**Solution:** Check Docker is running
```bash
docker ps

# If error, start Docker Desktop
# Then try again:
docker-compose up --build -d
```

---

## Updating

### Update Application Code
```bash
git pull origin main
pip install -r requirements.txt --upgrade
chainlit run app/main.py
```

### Update Docker Images
```bash
docker-compose down
docker-compose pull
docker-compose up --build -d
```

---

## Uninstallation

### Standard Installation
```bash
# Deactivate venv
deactivate

# Remove virtual environment
rm -rf venv

# Remove application files
cd ..
rm -rf Global-IQ
```

### Docker Installation
```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi global-iq-application-global-iq-app
docker rmi global-iq-application-compensation-server
docker rmi global-iq-application-policy-server
```

---

## Next Steps

- **Quick Start:** [Quick Start Guide](README.md)
- **User Credentials:** [User Credentials & Roles](USER_CREDENTIALS.md)
- **Architecture:** [System Overview](../architecture/README.md)
- **Deployment:** [Deployment Guide](../deployment/README.md)

---

## Getting Help

- **Installation issues:** Check troubleshooting section above
- **Application issues:** See [Architecture Guide](../architecture/README.md)
- **Deployment issues:** See [Deployment Guide](../deployment/README.md)
- **Claude Code instructions:** See [CLAUDE.md](../../../CLAUDE.md)
