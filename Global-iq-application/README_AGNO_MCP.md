# AGNO + MCP Integration - Quick Start

## 📁 Files Created

This setup includes the following new files:

### MCP Servers
- `services/mcp_prediction_server/compensation_server.py` - Compensation prediction MCP server
- `services/mcp_prediction_server/policy_server.py` - Policy analysis MCP server
- `services/mcp_prediction_server/requirements.txt` - MCP server dependencies

### AGNO Client
- `app/agno_mcp_client.py` - AGNO agent system that connects to MCP servers

### Utilities
- `test_installation.py` - Test script to verify installation
- `.env.example` - Environment variables template
- `START_MCP_SERVERS.bat` - Windows batch script to start both MCP servers
- `README_AGNO_MCP.md` - This file

---

## 🚀 Installation Steps

### Step 1: Install Required Packages

```bash
# Make sure you're in the virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
.\venv\Scripts\activate.bat   # Windows CMD

# Install AGNO and MCP packages
pip install agno
pip install mcp
pip install fastapi
pip install uvicorn

# Update requirements
pip freeze > requirements.txt
```

### Step 2: Verify Installation

```bash
python test_installation.py
```

You should see:
```
[SUCCESS] AGNO installed successfully
[SUCCESS] MCP installed successfully
[SUCCESS] FastAPI installed successfully
[SUCCESS] Uvicorn installed successfully
[SUCCESS] All packages installed correctly!
```

### Step 3: Set Up Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

---

## 🎮 Running the System

### Option 1: Use the Batch Script (Windows)

```bash
# Double-click or run:
START_MCP_SERVERS.bat
```

This will open two new command windows:
- One for Compensation MCP Server (port 8081)
- One for Policy MCP Server (port 8082)

### Option 2: Manual Start (Cross-platform)

**Terminal 1 - Compensation Server:**
```bash
python services/mcp_prediction_server/compensation_server.py
```

**Terminal 2 - Policy Server:**
```bash
python services/mcp_prediction_server/policy_server.py
```

**Terminal 3 - Chainlit App:**
```bash
chainlit run app/main.py
```

---

## 🧪 Testing the MCP Servers

### Test Compensation Server

```bash
curl -X POST http://localhost:8081/predict_compensation \
  -H "Content-Type: application/json" \
  -d "{\"origin_location\": \"New York, USA\", \"destination_location\": \"London, UK\", \"current_salary\": 100000}"
```

### Test Policy Server

```bash
curl -X POST http://localhost:8082/analyze_policy \
  -H "Content-Type: application/json" \
  -d "{\"origin_country\": \"USA\", \"destination_country\": \"UK\", \"assignment_type\": \"Long-term\"}"
```

---

## 📊 How It Works

### Current Flow (Before Integration)
```
User Input → Input Collector → GPT-4 → Text Response
```

### New Flow (With AGNO + MCP)
```
User Input → Input Collector → AGNO Agent → MCP Server → Prediction → Structured Response
                                     ↓ (if MCP fails)
                              GPT-4 Fallback
```

### What Each Component Does

1. **Input Collector** (existing)
   - Asks structured questions
   - Collects user responses
   - Validates data

2. **AGNO Agent** (`agno_mcp_client.py`)
   - Receives collected data
   - Connects to appropriate MCP server
   - Manages agent lifecycle
   - Handles errors and fallbacks

3. **MCP Server** (`compensation_server.py` or `policy_server.py`)
   - Receives prediction request
   - Runs calculation logic
   - Returns structured JSON response

4. **Response Formatter** (in `main.py`)
   - Takes structured JSON
   - Formats for user display
   - Shows breakdowns, confidence scores, recommendations

---

## 🔧 Next Steps

### To Complete Integration

You still need to modify `app/main.py` to use the AGNO client:

1. **Import the AGNO client:**
```python
from agno_mcp_client import GlobalIQAgentSystem
```

2. **Initialize the system:**
```python
agno_system = GlobalIQAgentSystem()
```

3. **Update calculation functions:**
   - Replace `_run_compensation_calculation()` to call `agno_system.predict_compensation()`
   - Replace `_run_policy_analysis()` to call `agno_system.analyze_policy()`

See the full implementation guide in `docs/AGNO_MCP_IMPLEMENTATION_GUIDE.md` for complete code examples.

---

## 📝 File Structure

```
Global-iq-application/
├── app/
│   ├── main.py                          # Main Chainlit app (needs modification)
│   ├── agno_mcp_client.py              # ✅ NEW: AGNO agent system
│   ├── enhanced_agent_router.py         # Existing router
│   └── input_collector.py               # Existing input collector
├── services/
│   └── mcp_prediction_server/
│       ├── compensation_server.py       # ✅ NEW: Compensation MCP server
│       ├── policy_server.py             # ✅ NEW: Policy MCP server
│       └── requirements.txt             # ✅ NEW: MCP dependencies
├── test_installation.py                 # ✅ NEW: Installation test
├── START_MCP_SERVERS.bat               # ✅ NEW: Server startup script
├── .env.example                         # ✅ NEW: Environment template
└── README_AGNO_MCP.md                  # ✅ NEW: This file
```

---

## 🐛 Troubleshooting

### MCP Server Won't Start

**Error:** `Port already in use`
```bash
# Check what's using the port
netstat -ano | findstr :8081

# Kill the process or use different port
```

**Error:** `Module not found: mcp`
```bash
# Make sure you installed in the correct environment
pip install mcp
```

### AGNO Agent Can't Connect

**Check server is running:**
```bash
curl http://localhost:8081/health
```

**Check environment variables:**
```bash
# Make sure .env has correct URLs
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082
```

### Import Errors

```bash
# Reinstall packages
pip uninstall agno mcp
pip install agno mcp
```

---

## 📚 Additional Resources

- **Full Implementation Guide:** `docs/AGNO_MCP_IMPLEMENTATION_GUIDE.md`
- **Quick Checklist:** `docs/AGNO_MCP_QUICK_CHECKLIST.md`
- **Current System Breakdown:** `docs/CURRENT_SYSTEM_BREAKDOWN.md`
- **AGNO Documentation:** https://docs.agno.com/
- **MCP Documentation:** https://modelcontextprotocol.io/

---

## ✅ Success Checklist

- [ ] Packages installed (run `test_installation.py`)
- [ ] Environment variables set (`.env` file created)
- [ ] MCP servers start without errors
- [ ] Can curl MCP endpoints successfully
- [ ] AGNO client imports without errors
- [ ] Ready to modify `main.py`

Once all items are checked, you're ready to integrate with the main application!

---

## 🎯 What You've Accomplished

✅ Created MCP servers for compensation and policy predictions  
✅ Built AGNO agent system to connect to MCP servers  
✅ Set up testing and startup scripts  
✅ Prepared environment configuration  

**Next:** Modify `main.py` to use AGNO agents instead of direct GPT-4 calls.

See the implementation guide for complete code to add to `main.py`!

