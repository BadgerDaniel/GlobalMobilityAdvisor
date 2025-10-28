# Quick Start Guide

Get up and running with Global IQ Mobility Advisor in 5 minutes.

---

## Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Docker Desktop (optional, for containerized deployment)

---

## Installation

### Step 1: Install Dependencies

```bash
cd Global-IQ/Global-iq-application
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file:

```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

Or set environment variable:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows (CMD)
set OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run the Application

```bash
chainlit run app/main.py
```

The app will start on **http://localhost:8000**

---

## Login

Use these credentials to access the application:

| Role | Username | Password |
|------|----------|----------|
| Employee | `employee` | `employee123` |
| HR Manager | `hr_manager` | `hr2024` |
| Admin | `admin` | `admin123` |
| Demo | `demo` | `demo` |

See [User Credentials](USER_CREDENTIALS.md) for more details.

---

## Try It Out

### Ask a Compensation Question

```
"How much will an engineer make moving from NYC to London?"
```

The system will:
1. Route to compensation agent
2. Collect missing information (salary, job level, etc.)
3. Generate compensation analysis via MCP server or GPT-4 fallback

### Ask a Policy Question

```
"What visa do I need for a 2-year assignment to the UK?"
```

The system will:
1. Route to policy agent
2. Collect missing information (origin country, assignment type, etc.)
3. Generate policy analysis via MCP server or GPT-4 fallback

### Upload Documents

Click the upload button and attach:
- PDF documents (company policies, visa guides)
- Excel spreadsheets (salary data, cost of living)
- Word documents (assignment details)

The system will extract text and use it as context for responses.

---

## What's Running?

### Option 1: Standalone App (Default)

```bash
chainlit run app/main.py
```

- Main Chainlit application only
- MCP integration **disabled** or uses fallback to GPT-4
- Simplest setup for testing

### Option 2: With MCP Servers

```bash
# Terminal 1: Compensation Server
python services/mcp_prediction_server/compensation_server.py

# Terminal 2: Policy Server
python services/mcp_prediction_server/policy_server.py

# Terminal 3: Main App
chainlit run app/main.py
```

- All 3 services running
- MCP integration **enabled**
- Full architecture (though servers still use OpenAI placeholders)

### Option 3: Docker (Recommended)

```bash
docker-compose up -d
```

- All 3 services in containers
- Automatic startup and health checks
- Easiest for development

See [Docker Deployment](../deployment/DOCKER.md) for details.

---

## Verify MCP Integration

If running with MCP servers:

1. Login as `admin` / `admin123`
2. Type `/health` in chat
3. Check MCP server status:
   - ✅ Green = servers running
   - ❌ Red = servers down (using fallback)

---

## Next Steps

- **Learn the architecture**: [System Overview](../architecture/README.md)
- **Deploy to production**: [Deployment Guide](../deployment/README.md)
- **Integrate real models**: [Model Integration Guide](../development/MODEL_INTEGRATION.md)
- **Run tests**: [Testing Guide](../development/TESTING.md)

---

## Troubleshooting

### "OpenAI API Error"

Check your API key:
```bash
# Verify key is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### "Module not found"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"

Change the port:
```bash
chainlit run app/main.py --port 8080
```

### "Cannot connect to MCP servers"

The app will automatically fall back to GPT-4. To fix:

```bash
# Check if servers are running
curl http://localhost:8081/health
curl http://localhost:8082/health

# Restart servers
python services/mcp_prediction_server/compensation_server.py
python services/mcp_prediction_server/policy_server.py
```

---

## Common Issues

**Q: Do I need to run the MCP servers?**
A: No! The app works standalone with GPT-4 fallback. MCP servers are optional.

**Q: What's the difference between MCP servers and standalone?**
A: Currently, both use OpenAI GPT-4. MCP servers are placeholders for future real ML models.

**Q: Can I use this without Docker?**
A: Yes! Just run `chainlit run app/main.py` directly.

**Q: Where are uploaded files stored?**
A: In `./uploads/` directory (created automatically).

---

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).
