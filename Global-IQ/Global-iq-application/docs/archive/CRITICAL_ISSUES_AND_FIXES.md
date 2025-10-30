# Critical Issues & Recommended Fixes
**Global IQ Mobility Advisor - MCP Integration**

---

## ISSUE SUMMARY

The application is **production-ready** but has 2 non-critical issues that should be addressed before full deployment:

1. **AGNO Library Missing** (Missing Dependencies)
2. **MCP Client Subprocess Logic** (Inefficient Design)

Both issues are handled gracefully by the fallback mechanism, but they create confusion and inefficiency.

---

## ISSUE #1: Missing AGNO Library

### Severity: MEDIUM
### Impact: MCP servers won't be used; falls back to GPT-4 silently

### Root Cause

**File:** app/agno_mcp_client.py (lines 1-18)

```python
from agno.agent import Agent                    # NOT IN REQUIREMENTS
from agno.models.openai import OpenAIChat       # NOT IN REQUIREMENTS
from agno.tools.mcp import MCPTools             # NOT IN REQUIREMENTS
from mcp import StdioServerParameters           # NOT IN REQUIREMENTS
```

**Current requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
openai==1.3.7
python-dotenv==1.0.0
httpx==0.25.2
```

These imports are MISSING from requirements.

### What Happens

1. App starts up
2. service_manager.py tries to initialize GlobalIQAgentSystem
3. agno_mcp_client imports fail (ModuleNotFoundError)
4. Exception caught at lines 105-108 of service_manager.py:
   ```python
   except Exception as e:
       logger.error(f"Failed to initialize AGNO Agent System: {str(e)}")
       self.agent_system = None
       self.enable_mcp = False
   ```
5. MCP is silently disabled
6. All requests fall back to GPT-4
7. No errors in UI, but teams' models are never used

### Evidence

**Log Output (if libraries were missing):**
```
ERROR:service_manager:Failed to initialize AGNO Agent System: No module named 'agno'
```

### Fix

**Option A: Add Missing Libraries to requirements.txt** (5 minutes)

```bash
# Get the correct versions
pip install agno
pip freeze | grep agno

# Add to requirements.txt:
agno>=0.x.x
mcp>=0.x.x
```

**However**, this creates a new problem: See Issue #2 below.

**Option B: Simplify agno_mcp_client.py** (Recommended)

The AGNO approach is overcomplicated. The servers are already running as Docker containers. The client should just make HTTP requests.

**Replace agno_mcp_client.py with:**

```python
"""
Simplified MCP Client for Global IQ
Makes HTTP requests to already-running MCP servers
"""

import logging
from typing import Dict, Any
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalIQAgentSystem:
    """
    Simplified HTTP client for MCP servers
    Makes direct HTTP calls to compensation and policy servers
    """

    def __init__(
        self,
        compensation_server_url: str = "http://localhost:8081",
        policy_server_url: str = "http://localhost:8082"
    ):
        self.compensation_server_url = compensation_server_url
        self.policy_server_url = policy_server_url
        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info(f"Global IQ Agent System initialized")
        logger.info(f"  Compensation: {compensation_server_url}")
        logger.info(f"  Policy: {policy_server_url}")

    async def predict_compensation(
        self,
        origin_location: str,
        destination_location: str,
        current_salary: float,
        currency: str = "USD",
        assignment_duration: str = "12 months",
        job_level: str = "Manager",
        family_size: int = 1,
        housing_preference: str = "Company-provided"
    ) -> Dict[str, Any]:
        """
        Call compensation prediction endpoint
        """
        try:
            logger.info(f"Requesting compensation: {origin_location} -> {destination_location}")

            payload = {
                "origin_location": origin_location,
                "destination_location": destination_location,
                "current_salary": current_salary,
                "currency": currency,
                "assignment_duration": assignment_duration,
                "job_level": job_level,
                "family_size": family_size,
                "housing_preference": housing_preference
            }

            response = await self.client.post(
                f"{self.compensation_server_url}/predict",
                json=payload
            )

            if response.status_code == 200:
                logger.info("Compensation prediction successful")
                return response.json()
            else:
                logger.error(f"Compensation server returned {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "message": "Compensation server error"
                }

        except Exception as e:
            logger.error(f"Compensation prediction failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get compensation prediction"
            }

    async def analyze_policy(
        self,
        origin_country: str,
        destination_country: str,
        assignment_type: str,
        duration: str,
        job_title: str
    ) -> Dict[str, Any]:
        """
        Call policy analysis endpoint
        """
        try:
            logger.info(f"Requesting policy analysis: {origin_country} -> {destination_country}")

            payload = {
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_type": assignment_type,
                "duration": duration,
                "job_title": job_title
            }

            response = await self.client.post(
                f"{self.policy_server_url}/analyze",
                json=payload
            )

            if response.status_code == 200:
                logger.info("Policy analysis successful")
                return response.json()
            else:
                logger.error(f"Policy server returned {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "message": "Policy server error"
                }

        except Exception as e:
            logger.error(f"Policy analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get policy analysis"
            }

    def health_check(self) -> Dict[str, bool]:
        """Check health of MCP servers"""
        import requests  # Use sync requests for health check

        health = {
            "compensation_server": False,
            "policy_server": False
        }

        try:
            resp = requests.get(
                f"{self.compensation_server_url}/health",
                timeout=2
            )
            health["compensation_server"] = resp.status_code == 200
        except:
            pass

        try:
            resp = requests.get(
                f"{self.policy_server_url}/health",
                timeout=2
            )
            health["policy_server"] = resp.status_code == 200
        except:
            pass

        return health
```

### Advantages of Simplified Version

1. **No AGNO dependency** - Just uses httpx (already in requirements)
2. **Clear HTTP semantics** - Easy to understand what's happening
3. **Works with Docker containers** - Calls already-running services
4. **Easier to debug** - Simple requests/responses, no subprocess complexity
5. **Better error handling** - Clear HTTP status codes

### Implementation Steps

1. Replace `app/agno_mcp_client.py` with simplified version above
2. Update `app/service_manager.py` lines 99-108:
   ```python
   try:
       self.agent_system = GlobalIQAgentSystem(
           compensation_server_url=compensation_server_url,
           policy_server_url=policy_server_url
       )
       logger.info("MCP Agent System initialized successfully")
   except Exception as e:
       logger.error(f"Failed to initialize MCP Agent System: {str(e)}")
       self.agent_system = None
       self.enable_mcp = False
   ```
3. No changes to requirements.txt needed (httpx already there)
4. Test: `docker-compose up -d && curl http://localhost:8081/health`

---

## ISSUE #2: MCP Client Tries to Spawn Servers

### Severity: LOW
### Impact: Confusing behavior; potential subprocess errors

### Root Cause

**File:** app/agno_mcp_client.py (lines 40-52, 75-87)

```python
async def _get_compensation_agent(self) -> Agent:
    """Lazy initialization of compensation agent"""
    if self._compensation_agent is None:
        # THIS IS THE PROBLEM: Tries to spawn server as subprocess
        server_params = StdioServerParameters(
            command="python",
            args=[
                os.path.join(
                    os.path.dirname(__file__),
                    "../services/mcp_prediction_server/compensation_server.py"
                )
            ],
        )

        mcp_tools = MCPTools(server_params=server_params)

        self._compensation_agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[mcp_tools],
            # ...
        )
```

### What's Actually Happening

1. **docker-compose.yml starts the servers as containers** on ports 8081 & 8082
2. **agno_mcp_client tries to start them AGAIN as local Python processes**
3. Result: **Duplicate server instances or port conflicts**

### Why This Is Wrong

```
Expected Behavior:
docker-compose up -d
  ├─ compensation-server (port 8081)
  ├─ policy-server (port 8082)
  └─ global-iq-app
      └─ calls http://localhost:8081/predict
      └─ calls http://localhost:8082/analyze

Actual Behavior:
docker-compose up -d
  ├─ compensation-server (port 8081) ← Started by docker-compose
  │   └─ also tries to start python subprocess? ← Duplicate!
  ├─ policy-server (port 8082)
  └─ global-iq-app
      └─ tries to spawn MORE subprocesses
          └─ port conflicts / errors
```

### Why Fallback Works

Even with this inefficiency, the fallback still works because:
1. If the subprocess approach fails (exception), it's caught
2. service_manager disables MCP
3. Application falls back to GPT-4
4. User still gets an answer

### Fix

Use simplified version from Issue #1 above. This removes the subprocess spawning entirely and just makes HTTP calls to the already-running containers.

---

## RECOMMENDED ACTION PLAN

### Immediate (For Production Readiness)

**Priority 1: Fix agno_mcp_client.py** (20 minutes)
- Replace with simplified HTTP version
- No external dependencies needed
- Test with: `docker-compose up -d && docker-compose logs -f`

**Priority 2: Verify requirements.txt** (5 minutes)
- Current requirements.txt is correct for simplified version
- httpx is already included

**Priority 3: Test Integration** (10 minutes)
```bash
docker-compose up -d
sleep 5
curl http://localhost:8081/health
curl http://localhost:8082/health
curl -X POST http://localhost:8081/predict -H "Content-Type: application/json" -d '{...}'
```

### Timeline

- **Total fix time: 35 minutes**
- **Risk level: LOW** (error handling covers us)
- **Testing required: 10 minutes**

---

## FILES TO MODIFY

### File 1: app/agno_mcp_client.py
**Action:** Replace entire file with simplified version (shown above)
**Lines affected:** All lines (1-284)
**Backup:** Current version has AGNO dependencies; new version uses only httpx

### File 2: app/service_manager.py
**Action:** No changes needed
**Reason:** Error handling already in place (lines 105-108)

### File 3: requirements.txt
**Action:** No changes needed
**Reason:** httpx already included

### File 4: docker-compose.yml
**Action:** No changes needed
**Reason:** Already correctly structured

---

## TESTING THE FIX

### Test 1: Containers Start Cleanly
```bash
docker-compose up -d
sleep 10
docker-compose ps
# Expected: All containers running, no errors
```

### Test 2: Health Checks Pass
```bash
curl http://localhost:8081/health
curl http://localhost:8082/health
# Expected: {"status":"healthy","service":"..."}
```

### Test 3: API Endpoints Respond
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin_location": "New York, USA",
    "destination_location": "London, UK",
    "current_salary": 100000,
    "currency": "USD",
    "assignment_duration": "12 months",
    "job_level": "Manager",
    "family_size": 1,
    "housing_preference": "Company-provided"
  }'
# Expected: Valid JSON response with predictions
```

### Test 4: Logs Are Clean
```bash
docker-compose logs app
# Expected: No errors about AGNO or subprocess issues
```

### Test 5: Fallback Still Works
```bash
docker-compose down compensation-server
docker-compose logs -f app
# Ask a compensation question in UI
# Expected: Still works, uses GPT-4 fallback
```

---

## SUMMARY

| Issue | Severity | Fix Time | Action |
|-------|----------|----------|--------|
| AGNO library missing | MEDIUM | 20 min | Replace agno_mcp_client.py with simplified version |
| MCP client subprocess logic | LOW | 0 min | Removed by simplified version |
| **Total** | **MEDIUM** | **20 min** | **Replace 1 file** |

**Current Status:** Application works due to fallback mechanism
**After Fix:** Application works AND uses MCP servers correctly

---

## IMPLEMENTATION: BEFORE & AFTER

### BEFORE

```
User Question
    ↓
Router → Compensation
    ↓
Input Collector → Questions
    ↓
Data: {origin, destination, salary, ...}
    ↓
service_manager.predict_compensation()
    ↓
GlobalIQAgentSystem (tries AGNO)
    ↓
AGNO Import Error ❌
    ↓
Exception caught → MCP disabled
    ↓
Fall back to GPT-4 ✓
    ↓
User gets answer (via GPT-4)
```

### AFTER

```
User Question
    ↓
Router → Compensation
    ↓
Input Collector → Questions
    ↓
Data: {origin, destination, salary, ...}
    ↓
service_manager.predict_compensation()
    ↓
GlobalIQAgentSystem (simplified HTTP)
    ↓
HTTP POST to http://localhost:8081/predict ✓
    ↓
Docker container responds (YOUR MODEL)
    ↓
User gets answer (via your ML model)
    ↓
If server down → Fall back to GPT-4 ✓
```

---

## NEXT STEPS FOR TEAMS

After this fix is applied:

1. **Compensation Team**
   - Receives compensation_server.py
   - Replaces OpenAI with their model (lines 192-272)
   - Sends back Docker image + requirements.txt

2. **Policy Team**
   - Receives policy_server.py
   - Replaces OpenAI with their model (lines 79-156)
   - Sends back Docker image + requirements.txt

3. **Integration**
   - Both docker images tested independently
   - docker-compose.yml points to their images
   - Full integration test with UI

---

## VERIFICATION CHECKLIST

Before considering the fix complete:

- [ ] agno_mcp_client.py replaced with simplified version
- [ ] No AGNO imports in codebase
- [ ] docker-compose up -d succeeds
- [ ] Both /health endpoints return 200
- [ ] HTTP requests to /predict and /analyze succeed
- [ ] Logs show no errors about missing modules
- [ ] Fallback still works when server is down
- [ ] Response format matches expected schema
- [ ] Teams receive updated files

---

