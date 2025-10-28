# AGNO + MCP Implementation Checklist

## 🎯 Goal
Replace GPT-4 text generation with real predictions via AGNO agents calling MCP servers.

---

## ✅ Phase 1: Installation (30 minutes)

### Install Packages
```bash
cd Global-IQ/Global-iq-application
.\venv\Scripts\Activate.ps1  # Windows

pip install agno
pip install mcp
pip install starlette
pip install uvicorn
pip freeze > requirements.txt
```

### Verify Installation
```python
# test_install.py
from agno.agent import Agent
from agno.tools.mcp import MCPTools
print("✓ AGNO and MCP installed")
```

---

## ✅ Phase 2: Create MCP Servers (2-3 hours)

### Directory Structure
```bash
mkdir -p services/mcp_prediction_server
cd services/mcp_prediction_server
```

### Files to Create
- [ ] `compensation_server.py` (MCP server for compensation)
- [ ] `policy_server.py` (MCP server for policy)
- [ ] `requirements.txt` (dependencies)

### Test Servers
```bash
# Terminal 1
python compensation_server.py

# Terminal 2
python policy_server.py

# Terminal 3
curl http://localhost:8081/health
curl http://localhost:8082/health
```

---

## ✅ Phase 3: Create AGNO Client (1-2 hours)

### Files to Create
- [ ] `app/agno_mcp_client.py` (AGNO agent system)

### Key Components
```python
class GlobalIQAgentSystem:
    - compensation_tools (MCPTools)
    - policy_tools (MCPTools)
    - compensation_agent (Agent)
    - policy_agent (Agent)
    - agent_os (AgentOS)
```

---

## ✅ Phase 4: Modify main.py (1 hour)

### Changes Needed

1. **Import AGNO client**
```python
from agno_mcp_client import GlobalIQAgentSystem
```

2. **Initialize system**
```python
agno_system = GlobalIQAgentSystem()
```

3. **Replace calculation functions**
- [ ] Update `_run_compensation_calculation()` to call AGNO
- [ ] Update `_run_policy_analysis()` to call AGNO
- [ ] Keep original functions as `_llm()` fallbacks

4. **Add helper functions**
- [ ] `parse_salary()`
- [ ] `extract_currency()`

---

## ✅ Phase 5: Environment Setup (15 minutes)

### Update .env
```bash
OPENAI_API_KEY=sk-...
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082
```

---

## ✅ Phase 6: Testing (30 minutes)

### Start All Services
```bash
# Terminal 1: Compensation MCP Server
cd services/mcp_prediction_server
python compensation_server.py

# Terminal 2: Policy MCP Server
python policy_server.py

# Terminal 3: Chainlit App
cd ../..
chainlit run app/main.py
```

### Test Scenarios

#### Test 1: Compensation Calculation
1. Login as `demo` / `demo`
2. Ask: "How much will I earn in London?"
3. Route to compensation
4. Answer questions:
   - Origin: New York, USA
   - Destination: London, UK
   - Salary: 100,000 USD
   - Duration: 12 months
   - Job Level: Senior Engineer
   - Family Size: 2
   - Housing: Company-provided
5. Verify structured response with:
   - Total package
   - Breakdown (COLA, housing, hardship)
   - Confidence scores
   - Recommendations

#### Test 2: Policy Analysis
1. Ask: "What visa do I need for UK?"
2. Route to policy
3. Answer questions:
   - Origin: USA
   - Destination: UK
   - Assignment Type: Long-term
   - Duration: 24 months
   - Job Title: Software Engineer
4. Verify structured response with:
   - Visa requirements
   - Eligibility check
   - Compliance info
   - Timeline
   - Documentation list

#### Test 3: Fallback Mechanism
1. Stop MCP servers (Ctrl+C)
2. Try compensation calculation again
3. Verify fallback to LLM works
4. Check logs show "falling back to LLM"

---

## ✅ Phase 7: Verification Checklist

### Functionality
- [ ] MCP servers start without errors
- [ ] AGNO agents connect to MCP servers
- [ ] Compensation predictions return structured data
- [ ] Policy analysis returns structured data
- [ ] Confidence scores are included
- [ ] Recommendations are generated
- [ ] Fallback to LLM works when MCP unavailable
- [ ] Error handling works properly

### Response Quality
- [ ] Total package calculation is reasonable
- [ ] COLA ratio makes sense for city pair
- [ ] Housing allowance scales with family size
- [ ] Visa requirements match destination country
- [ ] Timeline is realistic
- [ ] Recommendations are actionable

### Performance
- [ ] Response time < 3 seconds
- [ ] No timeout errors
- [ ] Logs show successful predictions
- [ ] Health checks pass

---

## 🎯 Success Criteria

You've successfully implemented AGNO + MCP when:

✅ **Input Collection** → Works as before  
✅ **AGNO Agent** → Receives collected data  
✅ **MCP Server** → Processes prediction request  
✅ **Structured Response** → Returns JSON with predictions  
✅ **Formatted Display** → Shows breakdown to user  
✅ **Fallback** → Uses LLM if MCP fails  

---

## 📊 What You've Achieved

### Before
```
Input → GPT-4 → Text Response
```

### After
```
Input → AGNO Agent → MCP Server → Prediction Model → Structured Response
                ↓ (if MCP fails)
              GPT-4 Fallback
```

### Key Improvements
1. **Structured Data** - JSON instead of text
2. **Confidence Scores** - Know prediction reliability
3. **Methodology Tracking** - Know which model/version used
4. **Scalability** - MCP servers scale independently
5. **Extensibility** - Easy to add new models

---

## 🚀 Next Steps (Future Enhancements)

### Week 2-3: Add External Data
- [ ] Integrate Numbeo API for real COLA data
- [ ] Add currency exchange API
- [ ] Connect visa requirement database
- [ ] Add housing cost API

### Week 4-6: Train ML Models
- [ ] Collect historical compensation data
- [ ] Train COLA prediction model (scikit-learn)
- [ ] Train housing allowance model
- [ ] Replace rule-based logic with ML

### Month 2+: Production Features
- [ ] Add model versioning (MLflow)
- [ ] Implement A/B testing
- [ ] Add monitoring dashboard (Grafana)
- [ ] Setup auto-retraining pipeline
- [ ] Add caching layer (Redis)

---

## 🆘 Troubleshooting

### Issue: MCP server won't start
```bash
# Check port availability
netstat -ano | findstr :8081
netstat -ano | findstr :8082

# Try different ports
python compensation_server.py --port 8091
```

### Issue: AGNO can't connect to MCP
```bash
# Verify server is running
curl http://localhost:8081/health

# Check firewall settings
# Check URL in .env matches server port
```

### Issue: Predictions return errors
```bash
# Check server logs
# Verify input data format
# Test with curl directly
```

### Issue: Fallback always triggers
```bash
# Check health_check() function
# Verify server URLs are correct
# Check network connectivity
```

---

## 📚 Reference Documents

- **Full Implementation Guide:** `AGNO_MCP_IMPLEMENTATION_GUIDE.md`
- **Current System Breakdown:** `CURRENT_SYSTEM_BREAKDOWN.md`
- **Code Examples:** See implementation guide for complete code

---

## ⏱️ Time Estimate

| Phase | Time | Difficulty |
|-------|------|------------|
| Installation | 30 min | Easy |
| MCP Servers | 2-3 hours | Medium |
| AGNO Client | 1-2 hours | Medium |
| Modify main.py | 1 hour | Easy |
| Testing | 30 min | Easy |
| **Total** | **5-7 hours** | **Medium** |

---

## 🎉 You're Ready!

Follow this checklist step-by-step, and you'll have AGNO + MCP working with your Global IQ system in about half a day!

**Start with:** Phase 1 (Installation) and work your way through each phase sequentially.

Good luck! 🚀


