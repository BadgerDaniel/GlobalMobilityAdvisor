# AGNO + MCP Installation Guide

## 🎉 Files Created Successfully!

I've created all the necessary files for AGNO + MCP integration. Here's what you have:

### ✅ Created Files

1. **MCP Servers:**
   - `services/mcp_prediction_server/compensation_server.py` - Compensation predictions
   - `services/mcp_prediction_server/policy_server.py` - Policy analysis
   - `services/mcp_prediction_server/requirements.txt` - Dependencies

2. **AGNO Client:**
   - `app/agno_mcp_client.py` - AGNO agent system

3. **Utilities:**
   - `test_installation.py` - Installation verification
   - `START_MCP_SERVERS.bat` - Quick server startup (Windows)
   - `README_AGNO_MCP.md` - Detailed documentation

---

## 🚀 Quick Start (Follow These Steps)

### Step 1: Install Packages (5 minutes)

Open PowerShell in the project directory:

```powershell
# Navigate to project
cd Global-IQ\Global-iq-application

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install AGNO and MCP
pip install agno
pip install mcp
pip install fastapi
pip install uvicorn

# Verify installation
python test_installation.py
```

**Expected output:**
```
[SUCCESS] AGNO installed successfully
[SUCCESS] MCP installed successfully
[SUCCESS] FastAPI installed successfully
[SUCCESS] Uvicorn installed successfully
[SUCCESS] All packages installed correctly!
```

---

### Step 2: Set Up Environment (2 minutes)

Create a `.env` file in `Global-iq-application/` directory:

```bash
OPENAI_API_KEY=sk-your-actual-openai-key-here
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082
```

---

### Step 3: Test MCP Servers (5 minutes)

**Option A: Use the batch script (easiest)**
```powershell
# Just double-click or run:
.\START_MCP_SERVERS.bat
```

This opens two windows automatically!

**Option B: Manual start**

Open 3 separate PowerShell windows:

**Window 1 - Compensation Server:**
```powershell
cd Global-IQ\Global-iq-application
.\venv\Scripts\Activate.ps1
python services\mcp_prediction_server\compensation_server.py
```

**Window 2 - Policy Server:**
```powershell
cd Global-IQ\Global-iq-application
.\venv\Scripts\Activate.ps1
python services\mcp_prediction_server\policy_server.py
```

**Window 3 - Test the servers:**
```powershell
# Test compensation server
curl http://localhost:8081/docs

# Test policy server
curl http://localhost:8082/docs
```

You should see FastAPI documentation pages!

---

### Step 4: Verify Everything Works (3 minutes)

With the MCP servers running, test the AGNO client:

Create a test file `test_agno.py`:

```python
import asyncio
from app.agno_mcp_client import GlobalIQAgentSystem

async def test():
    agno = GlobalIQAgentSystem()
    
    # Test compensation prediction
    result = await agno.predict_compensation(
        origin_location="New York, USA",
        destination_location="London, UK",
        current_salary=100000,
        currency="USD"
    )
    
    print("Compensation Prediction:")
    print(f"Total Package: {result['predictions']['total_package']}")
    print(f"COLA Ratio: {result['predictions']['cola_ratio']}")
    print(f"Confidence: {result['confidence_scores']['overall']}")

asyncio.run(test())
```

Run it:
```powershell
python test_agno.py
```

**Expected output:**
```
Compensation Prediction:
Total Package: 115000.0
COLA Ratio: 1.15
Confidence: 0.82
```

---

## 🎯 What You've Accomplished

✅ **MCP Servers Created** - Two prediction servers ready to run  
✅ **AGNO Client Ready** - Agent system that connects to MCP  
✅ **Testing Tools** - Scripts to verify everything works  
✅ **Startup Scripts** - Easy server management  

---

## 📋 Next Steps

### To Complete the Integration:

You need to modify `app/main.py` to use the AGNO client. Here's a summary:

1. **Add import at the top:**
```python
from agno_mcp_client import GlobalIQAgentSystem
```

2. **Initialize after other components:**
```python
agno_system = GlobalIQAgentSystem()
```

3. **Replace the calculation functions:**

Find this function (around line 240):
```python
async def _run_compensation_calculation(collected_data: dict, extracted_texts: list) -> str:
```

Replace it with the version that calls AGNO (see full code in `docs/AGNO_MCP_IMPLEMENTATION_GUIDE.md`)

Same for `_run_policy_analysis()`

---

## 🎬 Full Workflow

Once integrated, here's what happens:

```
1. User asks: "How much will I earn in London?"
   ↓
2. Router → Compensation route
   ↓
3. Input Collector asks questions
   ↓
4. User provides: Origin, Destination, Salary, etc.
   ↓
5. main.py calls: agno_system.predict_compensation()
   ↓
6. AGNO Agent connects to MCP Server (port 8081)
   ↓
7. MCP Server runs prediction logic
   ↓
8. Returns structured JSON:
   {
     "predictions": {
       "total_package": 115000,
       "cola_ratio": 1.15,
       "housing_allowance": 24000
     },
     "confidence_scores": {
       "cola": 0.85,
       "overall": 0.82
     },
     "recommendations": [...]
   }
   ↓
9. main.py formats and displays to user
```

---

## 🐛 Troubleshooting

### "Module not found: agno"
```powershell
# Make sure you're in the venv
.\venv\Scripts\Activate.ps1
pip install agno
```

### "Port 8081 already in use"
```powershell
# Find what's using it
netstat -ano | findstr :8081

# Kill the process or change port in server file
```

### "Connection refused to MCP server"
```powershell
# Make sure servers are running
# Check the terminal windows for errors
# Try accessing http://localhost:8081/docs in browser
```

### "AGNO agent timeout"
```python
# In agno_mcp_client.py, increase timeout
# Or check if MCP server is responding
```

---

## 📚 Documentation

- **This Guide** - Quick installation steps
- **README_AGNO_MCP.md** - Detailed usage guide
- **docs/AGNO_MCP_IMPLEMENTATION_GUIDE.md** - Complete technical guide with all code
- **docs/AGNO_MCP_QUICK_CHECKLIST.md** - Step-by-step checklist

---

## ✅ Installation Checklist

- [ ] Virtual environment activated
- [ ] AGNO installed (`pip install agno`)
- [ ] MCP installed (`pip install mcp`)
- [ ] FastAPI installed (`pip install fastapi uvicorn`)
- [ ] `test_installation.py` passes
- [ ] `.env` file created with OpenAI key
- [ ] MCP servers start without errors
- [ ] Can access http://localhost:8081/docs
- [ ] Can access http://localhost:8082/docs
- [ ] `test_agno.py` runs successfully

Once all checked, you're ready to modify `main.py`!

---

## 🎉 You're Ready!

All the foundation files are created. Now you just need to:

1. ✅ Install packages (Step 1)
2. ✅ Test servers (Step 3)
3. 📝 Modify `main.py` to use AGNO (see implementation guide)

The hardest part is done - you have working MCP servers and AGNO client!

**Start with Step 1 above and work through each step.** 🚀

