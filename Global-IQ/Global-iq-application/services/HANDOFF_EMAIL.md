# Email Template: MCP Server Handoff

---

**Subject:** MCP Server Integration Package - Ready for Model Implementation

---

Hi [Data Science Team],

Hope you're doing well! We're excited to share the MCP (Model Context Protocol) server package for integrating your ML models into our Global IQ Mobility Advisor application.

## What We're Sending You

**Attached:** `mcp_handoff_package.zip`

This package contains everything you need to integrate your trained models into our HR application with minimal coordination between our teams. We've designed this to be as straightforward as possible.

---

## 🎯 Team Assignments - TWO Separate Models

This package is for **TWO separate modeling teams** working independently:

### **Compensation Modeling Team**
- **Your Model:** Compensation package calculations (salary, COLA, housing allowances, tax gross-up)
- **Your File:** `compensation_server.py`
- **Your Port:** 8081
- **Your Endpoint:** `POST /predict`
- **Your Test:** http://localhost:8081/docs

### **Policy Modeling Team**
- **Your Model:** Mobility policy analysis (visa requirements, compliance, eligibility, documentation)
- **Your File:** `policy_server.py`
- **Your Port:** 8082
- **Your Endpoint:** `POST /analyze`
- **Your Test:** http://localhost:8082/docs

**Important:** Both teams can work in parallel! Each model runs independently in its own Docker container on its own port. You don't need to coordinate with each other - just match your respective API contract.

---

## The Simple Version

**We need:** Two prediction endpoints (compensation calculations and policy analysis)

**We're giving you:**
- Working containerized servers with placeholder AI (OpenAI)
- Clear API contract defining exact request/response formats
- Interactive API documentation (auto-generated)
- Test scripts to verify your implementation
- Complete integration guide

**You give us back:** The same Docker containers with YOUR implementation

**Integration:** If your API matches our contract, it plugs right in. No code changes on our end.

---

### 🎯 Important: Phased Delivery

**Phase 1 (Due ~November 8th):** Working containers with API contract met
- Can use OpenAI placeholder, simple rules, or basic model
- Goal: Integration working end-to-end

**Phase 2 (Due November 22nd):** Final production models deployed
- Swap in your trained ML models
- Must be complete 2 weeks before capstone presentation (December 6th)
- Updates can be done independently - just rebuild Docker image

This lets us unblock both teams quickly while giving you ~3 weeks total to deliver production-ready models!

## Quick Start (5 Minutes)

**To see what we need:**

1. **Unzip** the package
2. **Open terminal** in the `mcp_prediction_server` folder
3. **Set API key:** Create a `.env` file with `OPENAI_API_KEY=sk-your-key` (just for testing the placeholder)
4. **Start servers:** Run `docker-compose up -d`
   - This starts both MCP servers in Docker containers
   - Wait ~30 seconds for startup
5. **View interactive docs:**
   - Compensation API: http://localhost:8081/docs
   - Policy API: http://localhost:8082/docs
   - (These only work after step 4!)

The placeholder implementation uses OpenAI, so you can see exactly what the endpoints should do before you implement anything.

**Note:** The `localhost:8081` and `localhost:8082` URLs only work while the Docker containers are running. If you get "connection refused", run `docker-compose up -d` first.

## What You Need to Do

### 📋 IMPORTANT: Input Requirements Discussion (Step 0)

**Before you start coding, let's align on inputs/outputs!**

### Critical: We Only Provide User-Input Data!

**What we WILL give you:**
- Data users type into our LLM chat interface
- Answers to questions we ask users conversationally
- Examples: origin city, destination city, current salary, job title, family size

**What we will NOT give you:**
- External API data (COLA databases, visa APIs, housing cost databases)
- Real-time exchange rates or tax data
- Industry benchmarks or historical trends
- Any data not directly provided by the user

**Your responsibility:** If your model needs external data sources (COLA indices, visa requirements, housing costs), YOU must fetch/integrate those in YOUR server code. We only pass through what users tell us.

---

The API contract we provided is a **starting point for discussion**, not a rigid requirement. We can easily adjust what data we collect from users.

**Quick call needed to discuss:**

1. **What inputs does your model need from users?**
   - We can change what questions our LLM asks users
   - Just tell us what fields you need users to provide
   - Current fields (origin, destination, salary, etc.) are negotiable
   - Remember: We can ONLY collect what users can answer

2. **What can your model predict?**
   - We'll adjust how we display results based on what you provide
   - Don't worry if you can't predict everything - we'll adapt

3. **What external data sources will you integrate?**
   - COLA databases? Visa APIs? Housing cost data?
   - These are YOUR responsibility to fetch and integrate
   - We only provide the user input as the trigger

**Why this matters:** Changing our input collection is trivial (just a config file), but we should align on this BEFORE you build your model to avoid rework.

**Action:** Reply to this email with your model's input requirements, or let's schedule 15 minutes to discuss.

---

### Step 1: Understand the Contract (After We Align)
Read `MCP_CONTRACT.md` - this defines the exact request/response format we need. As long as your API matches this contract, we're integrated.

### Step 2: Replace the Placeholder
Open `compensation_server.py` and `policy_server.py`. Find the OpenAI API calls (clearly marked around line 146-150) and replace them with your model inference code.

### Step 3: Test It
Run the test scripts (`test_examples.sh` or `test_examples.bat`) to verify your responses match the contract.

### Step 4: Hand Back to Us
Give us your Docker containers (or Docker images we can pull). We'll deploy them and test integration.

## Key Points

**Ports:**
- Compensation server: 8081
- Policy server: 8082
(These are fixed - our app expects these)

**Endpoints:**
- `GET /health` - Health check
- `POST /predict` (compensation) or `POST /analyze` (policy)

**Response Format:**
Must match the schemas exactly (see MCP_CONTRACT.md). You can implement however you want internally, but the JSON output must match.

**Performance Targets:**
- Response time: < 2 seconds (95th percentile)
- Concurrent requests: Handle 10+
- Uptime: 99%+ (we have automatic fallback if you're down)

## What You DON'T Need to Worry About

Our user interface (Chainlit)
Query routing logic
Authentication/authorization
File uploads or document processing
Session management
Deployment infrastructure (we can help with this)

You ONLY need to match the API contract and return valid predictions.

## Architecture Overview

```
User → Our App → Your MCP Server → Your Model → Response
           ↓
    (If your server is down)
           ↓
    Fallback to OpenAI
```

We've built automatic health checks and fallback, so if your servers are temporarily unavailable, the system keeps working with OpenAI.

## What's in the Package

| File | Purpose |
|------|---------|
| **HANDOFF_README.md** | Complete walkthrough (START HERE) |
| **MCP_CONTRACT.md** | API specification with examples |
| **compensation_server.py** | Compensation endpoint code |
| **policy_server.py** | Policy endpoint code |
| **docker-compose.yml** | Run both servers standalone |
| **test_examples.sh/.bat** | Test scripts |
| **Dockerfile.*** | Container definitions |

## Example: What You'll Replace

**Current (placeholder):**
```python
# compensation_server.py line 146-150
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1
)
```

**After your implementation:**
```python
# Your model code here
features = preprocess_inputs(origin, destination, salary, ...)
predictions = your_trained_model.predict(features)
response = format_to_contract(predictions)
```

Keep the FastAPI endpoint structure, Pydantic models, and response format - just replace the prediction logic.

## Timeline & Phased Delivery

### Two-Phase Approach

We're splitting this into two phases to make it manageable:

**Phase 1: Integration (Due: November 8th - ~10 days)**

**What we need:**
- Working Docker containers on ports 8081 & 8082
- API contract met (correct request/response format)
- **Any** working implementation that returns valid predictions

**What you can deliver:**
- Option A: Keep the OpenAI placeholder (just containerized)
- Option B: Simple rule-based model
- Option C: Basic trained model
- **Your choice** - as long as the API works!

**Goal:** Get the integration working end-to-end so our teams are unblocked.

---

**Phase 2: Production Models (Due: November 22nd - 2 weeks before capstone)**

**What you do:**
- 🔄 Swap in your trained ML models
- 🔄 Add external data sources (COLA databases, visa APIs)
- 🔄 Optimize predictions for production quality
- 🔄 Final testing and validation

**Key benefit:** Once your containers are integrated in Phase 1, you can improve models **without coordination** with us. Just rebuild your Docker image, we redeploy, done.

**Hard deadline:** Must be complete by November 22nd (2 weeks before December 6th capstone presentation)

---

### Suggested Schedule

**Days 1-3 (Oct 29 - Oct 31):** Understand package, test placeholder
**Days 4-7 (Nov 1 - Nov 4):** Get YOUR containers running with basic implementation
**Day 10 (Nov 8):** Hand us working containers (Phase 1 complete ✓)
**Nov 8-22:** Final model development and deployment (Phase 2)
**Nov 22:** Production models complete and deployed ✅
**Dec 6:** Capstone presentation 🎓

**Timeline summary:** 3 weeks total - 10 days for integration, 14 days for final models.

## Questions?

**Technical questions about the API contract:**
- Check MCP_CONTRACT.md first
- Email me if anything is unclear

**Questions about your model implementation:**
- Coordinate with your team lead
- We're happy to provide sample queries if helpful

**Integration testing:**
- Once you have working containers, we'll coordinate testing
- We can schedule a sync to walk through any issues

## What Happens After Handoff

### Phase 1 Delivery (~November 8th)
1. You give us Docker containers (or images to pull)
2. We deploy to our test environment
3. We run integration tests with real user queries
4. If everything works (responses match contract), we deploy to production
5. **Integration complete!** Both teams unblocked.

### Phase 2 (Production Model Deployment - Due November 22nd)
1. You develop/train your production ML models (Nov 8-22)
2. You rebuild your Docker image with trained models
3. You tell us "production version ready"
4. We pull and redeploy (takes 5 minutes)
5. Final testing and validation
6. **Production ready for capstone!**

**The beauty of this approach:**
- Phase 1: Get integration done fast (~10 days) - unblocks both teams
- Phase 2: You have 2 weeks to deploy production models independently
- Updates are trivial - just rebuild Docker image
- **Final deadline: November 22nd** (2 weeks cushion before December 6th capstone)

## Testing Strategy

**Your side:**
- Use the test scripts to verify responses
- Check interactive docs at `/docs`
- Test with realistic inputs

**Our side:**
- Integration tests with our full app
- Real user query testing
- Load testing with realistic traffic

**Success criteria:**
Health checks pass
Response times < 2s
JSON format matches exactly
Containers start reliably
Error handling works

## Support

We're here to help! If you run into issues:
- Technical questions: [Your email/Slack]
- Deployment questions: [DevOps contact]
- Model questions: Your team lead

We've tried to make this as self-explanatory as possible, but don't hesitate to reach out if something isn't clear.

## Why We Built It This Way

We wanted to create a clean integration that:
- Lets you focus on models, not our application code
- Allows independent testing without our infrastructure
- Makes deployment straightforward
- Provides clear success criteria
- Enables you to iterate on models without coordinating with us

Think of it like an electrical outlet - we defined the shape, you build whatever device you want, as long as it plugs in correctly.

## Next Steps

### Phase 1 (October 29 - November 8)

1. **Day 1-2 (Oct 29-30):** Unzip, read HANDOFF_README.md, run `docker-compose up -d`
2. **Day 3-4 (Oct 31 - Nov 1):** Understand API contract, explore interactive docs at /docs
3. **Day 5-7 (Nov 2-4):** Get YOUR containers running with basic implementation
4. **Day 8-9 (Nov 5-6):** Test with test_examples.sh, verify contract compliance
5. **Day 10 (Nov 8):** Hand us Docker containers → Integration complete! ✅

**For November 8th delivery, you can:**
- Keep OpenAI placeholder (easiest)
- Use simple rule-based logic
- Use basic trained model
- **Whatever works!** Model quality improves in Phase 2.

### Phase 2 (November 8-22) - HARD DEADLINE


Production model development and deployment:
1. **Nov 8-18:** Develop/train your production ML models
2. **Nov 19-20:** Final testing and validation
3. **Nov 21:** Rebuild: `docker-compose build`
4. **Nov 21:** Tell us: "Production version ready"
5. **Nov 22:** We deploy, final checks → **Production ready!** ✅
6. **Dec 6:** Capstone presentation 🎓

**Critical:** November 22nd is a hard deadline - must be complete 2 weeks before capstone.

Let us know ASAP if this timeline won't work!

## Excited to Integrate!

We're really looking forward to seeing your ML models in action! We've built the integration layer to make this as smooth as possible for everyone.

The placeholder implementation (using OpenAI) gives you a working baseline - you'll probably outperform it significantly with trained models on real data.

Feel free to reach out with any questions, and let's schedule a quick kickoff call if that would be helpful.

Thanks,
[Your Name]

---

**P.S.** After running `docker-compose up -d`, the interactive API documentation at http://localhost:8081/docs and http://localhost:8082/docs is your best friend for understanding what the endpoints do. You can test them directly from the browser!

---

**Attachments:**
- mcp_handoff_package.zip (contains everything above)
