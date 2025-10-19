# 🚀 Getting Started with Global IQ + AGNO/MCP

## ✅ Prerequisites Complete!

You've successfully installed all required packages. Here's what to do next:

---

## 📝 Step 1: Configure Your OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```bash
# Location: Global-IQ/Global-iq-application/.env

OPENAI_API_KEY=sk-your-actual-key-here  # ← Replace this
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082
```

---

## 🚀 Step 2: Start the MCP Servers

### Option A: Easy Way (Windows Batch File)

Simply run:
```bash
cd Global-IQ/Global-iq-application
START_MCP_SERVERS.bat
```

This will open 2 terminal windows automatically:
- **Window 1**: Compensation Server (port 8081)
- **Window 2**: Policy Server (port 8082)

### Option B: Manual Start

**Terminal 1 - Compensation Server:**
```bash
cd Global-IQ/Global-iq-application
python services/mcp_prediction_server/compensation_server.py
```

**Terminal 2 - Policy Server:**
```bash
cd Global-IQ/Global-iq-application
python services/mcp_prediction_server/policy_server.py
```

### ✅ Verify Servers Are Running

Open your browser and check:
- Compensation Server: http://localhost:8081/docs
- Policy Server: http://localhost:8082/docs

You should see FastAPI Swagger documentation pages.

---

## 🧪 Step 3: Test the Integration

Create a test file to verify everything works:

**File: `test_quick.py`**
```python
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple test without AGNO first
async def test_basic():
    print("Testing basic setup...")

    # Check environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ Please set your OPENAI_API_KEY in .env file")
        return False

    print("✅ OpenAI API key found")

    # Test MCP server connection
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8081/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Compensation server is running")
            else:
                print("❌ Compensation server returned error")
                return False

            response = await client.get("http://localhost:8082/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Policy server is running")
            else:
                print("❌ Policy server returned error")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to MCP servers: {e}")
        print("   Make sure the servers are running!")
        return False

    print("\n✅ All checks passed! You're ready to go!")
    return True

if __name__ == "__main__":
    asyncio.run(test_basic())
```

Run it:
```bash
cd Global-IQ/Global-iq-application
python test_quick.py
```

---

## 🎯 Step 4: Run the Full Application

### Option A: Run Chainlit App Only (Without MCP Integration)

```bash
cd Global-IQ/Global-iq-application
chainlit run app/main.py
```

Then open: http://localhost:8000

Login with:
- **Username:** demo
- **Password:** demo

### Option B: Run with MCP Integration (Advanced)

This requires modifying `app/main.py` to use the AGNO client. See the implementation guide in `docs/` folder.

---

## 📊 What Each Component Does

### **Chainlit App** (port 8000)
- Web UI for chat interface
- User authentication
- File upload handling
- Conversation management

### **Compensation Server** (port 8081)
- Handles compensation calculations
- COLA adjustments
- Salary recommendations
- Housing allowances

### **Policy Server** (port 8082)
- Visa requirement analysis
- Policy compliance checks
- Immigration guidance
- Timeline recommendations

---

## 🐛 Troubleshooting

### Problem: "Module 'agno' not found"
**Solution:**
```bash
pip install agno
```

### Problem: "Port already in use"
**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8081

# Kill the process or change the port in the server file
```

### Problem: "Cannot connect to MCP servers"
**Solution:**
- Make sure both servers are running
- Check terminal windows for error messages
- Verify ports 8081 and 8082 are not blocked by firewall

### Problem: "OpenAI API Error"
**Solution:**
- Verify your API key in `.env` file
- Check you have credits in your OpenAI account
- Ensure no extra spaces in the API key

---

## 📚 Next Steps

### 1. **Test the Basic App First**
Run the Chainlit app without MCP to understand the flow:
```bash
chainlit run app/main.py
```

### 2. **Start MCP Servers**
Get the prediction servers running and test them via Swagger UI

### 3. **Integrate AGNO** (Advanced)
Follow the detailed guide in:
- `INSTALL_GUIDE.md` - Step-by-step installation
- `README_AGNO_MCP.md` - Usage documentation
- `docs/AGNO_MCP_INTEGRATION_PLAN.md` - Full technical details

### 4. **Customize for Your Needs**
- Modify questions in `app/agent_configs/*.txt`
- Add new routes in `app/route_config.json`
- Update prediction logic in MCP servers

---

## ✅ Quick Checklist

- [x] All packages installed (test_installation.py passed)
- [ ] `.env` file created with valid OpenAI API key
- [ ] MCP servers can start without errors
- [ ] Can access http://localhost:8081/docs
- [ ] Can access http://localhost:8082/docs
- [ ] `test_quick.py` passes all checks
- [ ] Chainlit app runs successfully
- [ ] Can login and chat with the app

---

## 🎉 You're All Set!

Once you complete Steps 1-3 above, you'll have:
- ✅ A working Global IQ Mobility Advisor
- ✅ MCP prediction servers running
- ✅ AGNO agent system ready to use
- ✅ Full test coverage

**Start with Step 1 (configure API key) and work through each step!**

---

## 📞 Need Help?

Check these resources:
- `CLAUDE.md` - Repository guide for Claude Code
- `INSTALL_GUIDE.md` - Detailed installation steps
- `README_AGNO_MCP.md` - AGNO/MCP usage guide
- `docs/PROJECT_OVERVIEW.md` - System architecture
- `docs/QUICK_START.md` - MCP integration quick start

Good luck! 🚀
