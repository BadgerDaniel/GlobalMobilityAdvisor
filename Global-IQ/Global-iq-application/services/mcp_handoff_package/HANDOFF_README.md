# MCP Server Handoff Package

**For:** Policy and Compensation Modeling Teams

---

## Team Assignments

This package contains two separate models for two separate teams:

### **Compensation Modeling Team**
- **Your Model:** Compensation calculations (salary, COLA, allowances)
- **Your File:** `compensation_server.py`
- **Your Port:** 8081
- **Your Endpoint:** `POST /predict`
- **Your Contract:** See "Compensation Server" section in [MCP_CONTRACT.md](MCP_CONTRACT.md)

### **Policy Modeling Team**
- **Your Model:** Mobility policy analysis (visa, compliance, eligibility)
- **Your File:** `policy_server.py`
- **Your Port:** 8082
- **Your Endpoint:** `POST /analyze`
- **Your Contract:** See "Policy Server" section in [MCP_CONTRACT.md](MCP_CONTRACT.md)

**Important:** You work independently! Each team implements their own model in their own file, running on their own port. Both can develop in parallel.

---

## What Is This?

This is a **containerized MCP (Model Context Protocol) server** that we need you to implement with your trained ML models.

**The Simple Version:**
- We give you: Docker containers with placeholder AI (using OpenAI)
- You give us: Docker containers with YOUR models
- We connect: If your API matches our contract, it just works

**Think of it like:** We're giving you an electrical outlet specification, you plug in whatever device you want, as long as it fits the outlet.

---

## Quick Start (5 Minutes)

### 1. Start the Placeholder Servers

```bash
# Set your OpenAI key (only for testing placeholder)
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start servers (Docker must be running!)
docker-compose up -d

# Wait 30 seconds for startup, then check they're running
curl http://localhost:8081/health
curl http://localhost:8082/health
# Should return: {"status":"healthy","service":"..."}
```

**Note:** If you get "connection refused", the servers haven't started yet. Wait a bit longer or check logs with `docker-compose logs`.

### 2. View Interactive API Docs

**After the servers are running** (step 1 above), open these in your browser:
- Compensation: http://localhost:8081/docs
- Policy: http://localhost:8082/docs

**This is the contract you need to match!**

The `/docs` endpoints only work while the Docker containers are running. You'll see interactive UI where you can test the API directly.

### 3. Test the Endpoints

```bash
# Linux/Mac
./test_examples.sh

# Windows
test_examples.bat
```

You should see successful responses. **Your job: Make the same responses come from YOUR models.**

---

## IMPORTANT: Input Requirements Discussion (Read This First)

Before you start coding, we need to align on inputs and outputs.

### Critical: We Only Provide User-Input Data

**What we will give you:**

- Data the user types into our LLM chat interface
- Answers to questions we ask the user conversationally
- Examples: origin city, destination city, current salary, job title, family size

**What we will NOT give you:**

- External API data (COLA databases, visa APIs, housing cost databases)
- Real-time exchange rates or tax data
- Industry benchmarks or historical trends
- Any data not directly provided by the user

**Your responsibility:** If your model needs external data (COLA indices, visa requirements, housing costs), you must fetch and integrate those data sources in your server code. We only pass through what users tell us directly.

---

### The API Contract is Negotiable!

The request/response input examples we provided are **starting points**, not final requirements. We can easily adjust what data we collect from users to match what your model needs.
The STRUCTURE is what is critical here!

### Let's Discuss (15 Minutes):

**1. What inputs does your model need from users?**
Tell us what's optional and what's required. Simple Python code can fill in optional items we don't provide with an average or assumed value.
   - Current fields: origin_location, destination_location, current_salary, job_level, family_size, housing_preference, assignment_duration
   - **These are flexible!** Tell us what you actually need users to provide
   - **Remember:** We can ONLY collect what users can answer (we can't fetch COLA data, visa databases, etc.)

**2. What can your model predict?**
   - Total compensation? Breakdown by component? Confidence scores?
   - We'll adjust our UI to display whatever you can provide
   - If you need external data sources, you integrate them on your side


### Why This Matters

On our side, changing what questions our LLM asks users is trivial:
```python
# app/agent_configs/compensation_questions.txt
1. What is your current location?
2. Where are you relocating to?
3. What is your current salary?



### Action Required

**Before starting Step 1 below, email us with:**
- What inputs your model needs 
- What outputs your model can provide
- Any questions about the integration

Or let's schedule 15 minutes to align. 
---

## What You Need to Do

### Step 1: Understand the Contract (After We Align)

Read [MCP_CONTRACT.md](MCP_CONTRACT.md) - this defines:
- Exact request format we'll send
- Exact response format you must return
- Port numbers (8081, 8082)
- HTTP endpoints (`/health`, `/predict`, `/analyze`)

**Golden Rule:** Match the contract exactly, implement however you want.

### Step 2: Replace the AI (Team-Specific)

#### **For Compensation Modeling Team:**

Open `compensation_server.py` and find lines 146-150:

```python
# LINE 146-150: This is what you replace
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": calc_prompt}],
    temperature=0.1
)
```

**Replace with YOUR compensation model:**
```python
# Your compensation model code here
features = preprocess_inputs(...)
predictions = your_model.predict(features)
result = format_response(predictions)
return result
```

**Keep everything else** (FastAPI endpoints, Pydantic models, port numbers).

### Step 3: Maintain the Response Format

Your response MUST match this structure:

```json
{
  "status": "success",
  "predictions": {
    "total_package": 145000.00,
    "base_salary": 100000.00,
    "currency": "USD",
    "cola_ratio": 1.15
  },
  "breakdown": {
    "cola_adjustment": 15000.00,
    "housing": 24000.00,
    "hardship": 0.00,
    "tax_gross_up": 6000.00
  },
  "confidence_scores": {
    "overall": 0.85,
    "cola": 0.90,
    "housing": 0.80
  },
  "recommendations": ["...", "..."],
  "metadata": {
    "model_version": "your-model-v1.0",
    "timestamp": "2025-10-27T12:00:00Z",
    "methodology": "Your ML approach"
  }
}
```

**Copy the structure, fill with your predictions.**

### Step 4: Test Your Implementation

```bash
# Rebuild with your changes
docker-compose up --build -d

# Test it works
./test_examples.sh  # or test_examples.bat on Windows

# Verify interactive docs still work
open http://localhost:8081/docs
```

### Step 5: Hand Back to Us

Give us:
1. Your Docker images (or Dockerfiles)
2. Updated `requirements.txt` if you added dependencies
3. Brief doc explaining your model approach

We'll plug it in and test integration.

---

#### **For Policy Modeling Team:**

Open `policy_server.py` and find lines 146-150:

```python
# LINE 146-150: This is what you replace
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": analysis_prompt}],
    temperature=0.1
)
```

**Replace with YOUR policy model:**
```python
# Your policy model code here
features = preprocess_policy_inputs(...)
analysis = your_policy_model.analyze(features)
result = format_policy_response(analysis)
return result
```

**Keep everything else** (FastAPI endpoints, Pydantic models, port numbers).

### Step 3: Maintain the Response Format (Team-Specific)

#### **Compensation Team Response:**
```json
{
  "status": "success",
  "predictions": {
    "total_package": 145000.00,
    "base_salary": 100000.00,
    ...
  },
  "breakdown": {...},
  "confidence_scores": {...}
}
```

#### **Policy Team Response:**
```json
{
  "status": "success",
  "analysis": {
    "visa_required": true,
    "visa_type": "Tier 2 General",
    ...
  },
  "compliance": {...},
  "requirements": {...}
}
```

See [MCP_CONTRACT.md](MCP_CONTRACT.md) for complete schemas.

### Step 4: Test Your Implementation

```bash
# Rebuild with your changes
docker-compose up --build -d

# Test it works
./test_examples.sh  # or test_examples.bat on Windows

# Verify interactive docs still work
# Compensation Team: http://localhost:8081/docs
# Policy Team: http://localhost:8082/docs
```

### Step 5: Hand Back to Us

Give us:
1. Your Docker images (or Dockerfiles)
2. Updated `requirements.txt` if you added dependencies
3. Brief doc explaining your model approach

We'll plug it in and test integration.

---

## File Structure

```
services/mcp_prediction_server/
├── README.md                     # Overview
├── HANDOFF_README.md             # This file
├── MCP_CONTRACT.md               # API contract (READ THIS!)
│
├── compensation_server.py        # Compensation endpoint (modify this)
├── policy_server.py              # Policy endpoint (modify this)
├── requirements.txt              # Python dependencies (add yours)
│
├── Dockerfile.compensation       # Compensation container
├── Dockerfile.policy             # Policy container
├── docker-compose.yml            # Run both servers
│
├── test_examples.sh              # Test script (Linux/Mac)
└── test_examples.bat             # Test script (Windows)
```

---

## Common Questions

### Q: Do I need to understand the whole HR application?
**A:** No! You only care about:
- Input: JSON requests we send you
- Output: JSON responses matching our format
- Everything else is our problem

### Q: Can I use TensorFlow / PyTorch / scikit-learn / whatever?
**A:** Yes! As long as:
- Your Docker container runs
- Your API matches the contract
- You return JSON in the right format

### Q: What if I need external data (COLA databases, visa APIs, etc.)?
**A:** Perfect! Add it to your implementation. Just:
- Keep your data sources/APIs inside your container
- Document them in your handoff notes
- Maintain the same response format

### Q: Can I change the ports?
**A:** No. Ports must be 8081 and 8082. Our app expects these.

### Q: Can I change the request/response format?
**A:** No. The contract is the contract. But you can add OPTIONAL fields if needed.

### Q: What about performance?
**A:** Target:
- < 2 seconds response time (95th percentile)
- Handle 10 concurrent requests
- 99% uptime (we have fallback if you're down)

### Q: What if my model can't predict something?
**A:** Return:
```json
{
  "status": "error",
  "error": "Unable to predict for this scenario",
  "error_code": "INSUFFICIENT_DATA"
}
```

We'll fall back to GPT-4.

---

## Testing Strategy

### Local Testing (You)
1. Run your Docker container
2. Hit it with curl/Postman
3. Verify response matches contract
4. Check interactive docs at `/docs`

### Integration Testing (Us)
1. Point our app at your endpoints
2. Send real user queries
3. Verify responses work in UI
4. Load test with realistic traffic

### Success Criteria
- Health checks pass
- Response time < 2s
- JSON format matches exactly
- Confidence scores present
- Error handling works
- Container starts reliably

---

## Deployment

### Development
```bash
# Your local machine
docker-compose up -d
```

### Production (We'll Handle)
We'll deploy your containers to:
- AWS ECS / Azure Container Instances / GKE
- With proper health checks and monitoring
- Auto-scaling based on load
- Your job: Just give us working containers

---

## Example Workflow

### Current (Placeholder)
```
User Query → Our App → OpenAI API → Response
                  ↓
            (Works but not optimal)
```

### After Your Integration
```
User Query → Our App → Your MCP Server → Your Model → Response
                  ↓
            (Production-ready ML!)
```

### If Your Server Is Down
```
User Query → Our App → Your MCP Server (timeout)
                  ↓
            Health Check Fails
                  ↓
            Fallback to OpenAI
                  ↓
            (Still works!)
```

---

## What We Handle

**You DON'T need to worry about:**
- User interface (Chainlit)
- Authentication (we handle login)
- Query routing (we route to right endpoint)
- File uploads (we process PDFs/docs)
- Session management
- Load balancing
- Monitoring / alerting
- Deployment infrastructure

**You ONLY need:**
- Docker container
- FastAPI endpoints matching contract
- Your ML model
- Response format

---

## Debugging

### Container won't start
```bash
docker-compose logs compensation-server
docker-compose logs policy-server
```

### Port already in use
```bash
# Check what's using the port
netstat -ano | findstr :8081  # Windows
lsof -i :8081                 # Linux/Mac

# Change port in docker-compose.yml if needed (but tell us!)
```

### Endpoint returns 404
- Check URL: Should be `/predict` or `/analyze` (not `/prediction`)
- Check method: Should be POST (not GET)
- Check server is running: `docker-compose ps`

### Response format rejected
- Compare your JSON to examples in MCP_CONTRACT.md
- Use online JSON validator
- Check field names match exactly (case-sensitive!)

---

## Contact

**Technical Questions:**
- API Contract: See MCP_CONTRACT.md
- Implementation Help: [Ask Daniel Sa]

---


---

## Summary

**What we're giving you:**

- Docker containers with working placeholder implementation
- Clear API contract defining request/response formats
- Interactive documentation at `/docs` endpoints
- Test scripts to verify your implementation
- Reference code showing the structure

**What we need back:**

- Your Docker containers with your ML models
- Same ports (8081 for compensation, 8082 for policy)
- Same endpoints (`/health`, `/predict`, `/analyze`)
- Same response format as specified in the contract
- Your trained models replacing the OpenAI placeholder

That's it. Match the contract, and we can plug your containers directly into our application.

---

## Ready to Start?

1. Read [MCP_CONTRACT.md](MCP_CONTRACT.md)
2. Run `docker-compose up -d`
3. Test with `./test_examples.sh`
4. View docs at http://localhost:8081/docs
5. Replace OpenAI with your model
6. Test again
7. Hand back to us

