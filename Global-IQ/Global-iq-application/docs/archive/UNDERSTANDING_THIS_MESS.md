# Understanding This Vibe-Coded Project: The Complete Guide

**Status**: You inherited a "vibe coded" school project and need to understand WTF is going on.
**Goal**: Get you up to speed FAST so you can actually work with this thing.

## ⚠️ Critical: MCP Servers are Placeholders

**IMPORTANT**: The MCP prediction servers (`compensation_server.py` and `policy_server.py`) currently use **OpenAI GPT-4 API** as placeholders. They are NOT real ML models yet.

- **Current**: Both servers call GPT-4 for predictions
- **Design**: Clean API endpoints ready for real model integration
- **Target**: Data science team replaces OpenAI calls with trained models
- **Documentation**: See `MODEL_INTEGRATION_GUIDE.md` for integration instructions

**TL;DR**: Integration architecture is done. Prediction logic needs real models.

---

## Table of Contents
1. [What Is This Thing Actually Doing?](#what-is-this-thing-actually-doing)
2. [The Big Picture Flow](#the-big-picture-flow)
3. [How a User Query Actually Works (Step-by-Step)](#how-a-user-query-actually-works-step-by-step)
4. [The Components Breakdown](#the-components-breakdown)
5. [The Confusing Parts Explained](#the-confusing-parts-explained)
6. [How to Run It](#how-to-run-it)
7. [Common Issues & Debugging](#common-issues--debugging)
8. [What's Actually Happening Under the Hood](#whats-actually-happening-under-the-hood)

---

## What Is This Thing Actually Doing?

**In Plain English**: This is a chatbot that helps HR people figure out:
- How much to pay employees who are moving to other countries
- What visa/policy rules apply when relocating employees

**The Tech**: It's a web chat interface (Chainlit) that talks to OpenAI's GPT-4 to analyze HR questions.

**The "AI" Part**: There's NO actual machine learning model trained on real data. It's just GPT-4 making educated guesses based on prompts. When it says "compensation calculation", it's really just asking GPT-4 "hey, estimate this for me."

---

## The Big Picture Flow

```
1. User logs in (username/password)
   ↓
2. User asks a question like "How much should I pay an engineer moving to London?"
   ↓
3. The ROUTER decides what kind of question this is:
   - Policy question (visa, rules, compliance)
   - Compensation question (money, salary, allowances)
   - Both (complex strategic questions)
   - WTF question (user doesn't know what they want)
   ↓
4. The INPUT COLLECTOR gathers missing info:
   "Where are they moving from? Current salary? Job level?"
   ↓
5. Once all info is collected, it calls GPT-4 with a big prompt:
   "Calculate compensation for engineer moving NYC→London, $100k salary, etc."
   ↓
6. GPT-4 responds with an analysis
   ↓
7. User sees the response in the chat
```

**MCP Server Path** (NOW INTEGRATED):

- MCP servers (`compensation_server.py`, `policy_server.py`) are integrated with health checks and fallback
- Service Manager orchestrates calls to MCP servers
- **Currently**: MCP servers use GPT-4 (placeholders for real models)
- **Design**: When MCP servers have real ML models, they'll be used automatically
- **Fallback**: If MCP servers are down, system falls back to GPT-4 directly

---

## How a User Query Actually Works (Step-by-Step)

### Example Query: "How much will an engineer make moving from NYC to London?"

#### Step 1: Login
- User enters username (`employee`) and password (`employee123`)
- Password gets SHA-256 hashed
- System checks `USERS_DB` dictionary in [main.py:26-51](Global-IQ/Global-iq-application/app/main.py#L26-L51)
- If match found, user gets logged in with their role

#### Step 2: Message Received
- Chainlit triggers `@cl.on_message` handler at [main.py:379](Global-IQ/Global-iq-application/app/main.py#L379)
- Function `handle_message()` starts processing

#### Step 3: File Processing (if files attached)
- If user uploaded files (PDF, DOCX, XLSX, etc.), they get processed
- Text extracted and stored in `extracted_texts` list
- See [main.py:426-466](Global-IQ/Global-iq-application/app/main.py#L426-L466)

#### Step 4: Router Analysis
The **EnhancedAgentRouter** ([enhanced_agent_router.py](Global-IQ/Global-iq-application/app/enhanced_agent_router.py)) analyzes the query.

**It tries 3 routing methods in order**:

1. **Direct Match**: Checks if query is literally "compensation", "policy", etc.
   - See [enhanced_agent_router.py:151-159](Global-IQ/Global-iq-application/app/enhanced_agent_router.py#L151-L159)

2. **Keyword Matching**: Scans for keywords from [route_config.json](Global-IQ/Global-iq-application/app/route_config.json)
   - "salary", "pay", "allowance" → compensation route
   - "visa", "immigration", "compliance" → policy route
   - "cheapest", "optimal" → both route
   - See [enhanced_agent_router.py:94-123](Global-IQ/Global-iq-application/app/enhanced_agent_router.py#L94-L123)

3. **LLM Routing**: If keywords don't give clear answer, asks GPT-4 to decide
   - Uses LangChain's `LLMRouterChain`
   - See [enhanced_agent_router.py:169-183](Global-IQ/Global-iq-application/app/enhanced_agent_router.py#L169-L183)

**For our example**: "engineer", "make", "moving to London" → triggers **compensation** route via keyword matching.

#### Step 5: Conversational Data Collection
The **ConversationalCollector** ([conversational_collector.py](Global-IQ/Global-iq-application/app/conversational_collector.py)) starts gathering required info.

**Required fields for compensation**:
- Origin Location (found: "NYC" from original query)
- Destination Location (found: "London" from original query)
- Current Compensation (MISSING)
- Assignment Duration (MISSING)
- Job Level (found: "engineer")
- Family Size (MISSING)
- Housing Preference (MISSING)

It uses GPT-4 to extract what it can from the user's message, then asks follow-up questions:

> "Great! I can help calculate compensation for an engineer moving from NYC to London.
>
> I need a few more details:
> - What is their current annual salary?
> - How long will the assignment be?
> - Will they have family members accompanying them?
> - What are their housing preferences?"

**This happens at**: [main.py:684-726](Global-IQ/Global-iq-application/app/main.py#L684-L726)

#### Step 6: User Responds
User replies: "Current salary is $120,000, 2 year assignment, going alone, company housing"

The system:
1. Adds message to conversation history
2. Calls `conversational_collector.extract_information()` to parse the response
3. Updates `collected_data` with extracted values
4. Checks if all required fields are now complete

**This happens at**: [main.py:492-551](Global-IQ/Global-iq-application/app/main.py#L492-L551)

#### Step 7: Confirmation
Once all data collected, it shows a confirmation:

> "Let me confirm the details:
> - Origin: New York City, USA
> - Destination: London, UK
> - Current Salary: $120,000 USD
> - Assignment Duration: 2 years
> - Job Level: Engineer
> - Family Size: 1 (solo)
> - Housing: Company-provided
>
> Is this correct?"

#### Step 8: Calculation
When user confirms ("yes"), it calls `_run_compensation_calculation()` at [main.py:244-290](Global-IQ/Global-iq-application/app/main.py#L244-L290)

This function:
1. Formats all collected data
2. Adds any uploaded document context
3. Creates a big prompt for GPT-4:

```python
calc_prompt = f"""You are the Global IQ Compensation Calculator AI engine...

Based on the following employee data, calculate a comprehensive compensation package:

• Origin Location: New York City, USA
• Destination Location: London, UK
• Current Compensation: $120,000 USD
• Assignment Duration: 2 years
• Job Level: Engineer
• Family Size: 1
• Housing Preference: Company-provided

[Plus any context from uploaded documents]

Provide a detailed breakdown including:
1. Base salary adjustments
2. Cost of living adjustments
3. Housing allowances
4. Hardship pay (if applicable)
5. Tax implications
6. Total estimated package
7. Recommendations for optimization
"""
```

4. Sends to OpenAI API
5. Gets response back
6. Formats as "Compensation Calculation Results"

#### Step 9: Response Displayed
User sees something like:

> **Compensation Calculation Results**
>
> Based on your relocation from NYC to London, here's the recommended package:
>
> **Base Salary Adjustment**: $132,000 (10% increase for London market)
> **Cost of Living Allowance**: +15% ($19,800/year)
> **Housing Allowance**: Fully covered (£2,500/month apartment)
> **Tax Equalization**: Estimated $8,000/year
> **Total Package**: ~$159,800 + housing
>
> [Plus more GPT-generated analysis...]

---

## The Components Breakdown

### 1. main.py (821 lines) - THE BRAIN
**What it does**: Entry point for everything. Handles login, file uploads, message routing, and orchestrates all the other components.

**Key sections**:
- **Lines 26-51**: User database (hardcoded usernames/passwords)
- **Lines 54-75**: Authentication function
- **Lines 141-225**: File processing functions (PDF, DOCX, XLSX, CSV, JSON, TXT)
- **Lines 244-290**: Compensation calculation (calls GPT-4)
- **Lines 292-338**: Policy analysis (calls GPT-4)
- **Lines 342-377**: Chat start handler (welcome message)
- **Lines 379-822**: Message handler (THE MAIN EVENT - routes everything)

**Session state management**:
```python
cl.user_session.get("user_data", {})  # Stores:
  - conversational_mode: bool
  - current_route: "compensation" | "policy"
  - collected_data: dict of answers
  - conversation_history: list of messages
  - awaiting_both_choice: bool
  - intro_shown: bool
```

### 2. enhanced_agent_router.py (252 lines) - THE ROUTER
**What it does**: Decides which "specialist" should handle the user's question.

**Routes**:
- `policy` - Visa, immigration, compliance questions
- `compensation` - Money, salary, allowances
- `both_policy_and_compensation` - Complex strategic questions
- `guidance_fallback` - "WTF can you do?" questions

**How it decides**:
1. **Exact match** (lines 151-159): "compensation" → compensation route
2. **Keyword scoring** (lines 94-123): Counts keywords from route_config.json
3. **LLM routing** (lines 169-183): Asks GPT-4 to decide

**Why keyword matching matters**: LLM routing is slow and costs money. Keywords are instant and free.

### 3. conversational_collector.py (259 lines) - THE NEW WAY TO COLLECT DATA
**What it does**: Has a natural conversation with the user to gather required info.

**How it works**:
1. Defines required fields for each route (compensation vs policy)
2. Extracts info from user's message using GPT-4
3. Asks follow-up questions for missing fields
4. Confirms all data before processing

**Why it exists**: The old `input_collector.py` was too rigid (Q1, Q2, Q3...). This feels more natural.

**Required fields**:
- **Compensation**: origin_location, destination_location, current_compensation, assignment_duration, job_level, family_size, housing_preference
- **Policy**: origin_country, destination_country, assignment_type, duration, job_title

### 4. input_collector.py (374 lines) - THE OLD WAY TO COLLECT DATA (LEGACY)
**What it does**: Asks questions in a strict sequence from text files.

**Status**: Still in the code but mostly unused. Conversational collector is preferred.

**How it worked**:
- Loads questions from `app/agent_configs/compensation_questions.txt`
- Asks them one by one: "Question 1: What is your origin location?"
- Validates answers with AI spell-check
- Tracks progress with `current_question` index

**Why it's still here**: Fallback in case conversational mode breaks.

### 5. agno_mcp_client.py (283 lines) - MCP CLIENT (NOW INTEGRATED)

**What it does**: Bridge to connect to MCP "prediction servers" using AGNO framework.

**Status**: ✅ **NOW INTEGRATED** via service_manager.py

**What it does**:

- Connects to MCP servers on ports 8081 and 8082
- Sends prediction requests with structured parameters
- Returns JSON responses with predictions

**Important**: The MCP servers it connects to currently use GPT-4 as placeholders (not real models yet).

### 6. service_manager.py (418 lines) - MCP ORCHESTRATION (NEW)

**What it does**: Orchestrates MCP server calls with health checks and automatic fallback.

**Key features**:

- Health check monitoring (30s cache)
- Automatic fallback to GPT-4 if MCP servers are down
- Parameter mapping from conversational data to MCP API format
- Usage statistics tracking
- `/health` admin command for monitoring

**Integration points**:

- Used by main.py in compensation/policy calculation functions
- Calls agno_mcp_client.py to communicate with MCP servers
- Falls back to direct OpenAI calls if MCP unavailable

### 7. MCP Servers (services/mcp_prediction_server/)

**What they are**: FastAPI servers that expose prediction endpoints.

**⚠️ IMPORTANT**: These are **PLACEHOLDER IMPLEMENTATIONS** designed for easy model integration by the data science team.

**compensation_server.py**:

- POST `/predict` - Takes employee data, returns compensation breakdown
- GET `/health` - Health check endpoint
- **Current**: Uses OpenAI GPT-4 API (placeholder)
- **Target**: Replace with real ML models for compensation prediction
- **Location to modify**: Lines 146-150 (OpenAI call) and lines 182-240 (placeholder calculation functions)

**policy_server.py**:

- POST `/analyze` - Takes assignment data, returns policy analysis
- GET `/health` - Health check endpoint
- **Current**: Uses OpenAI GPT-4 API (placeholder)
- **Target**: Replace with real policy models/rule engines

**How to start them**: Run `START_MCP_SERVERS.bat` on Windows

**Integration status**: ✅ **NOW INTEGRATED** via service_manager.py with health checks and fallback

**For model integration**: See `MODEL_INTEGRATION_GUIDE.md` for step-by-step instructions on replacing OpenAI calls with real models.

### 8. route_config.json - THE ROUTING RULES
**What it is**: Configuration file that defines routing behavior.

**Structure**:
```json
{
  "route_messages": {
    "compensation": {
      "title": "Compensation Expert",
      "description": "Calculating salary packages...",
      "emoji": "💰"
    },
    // ... more routes
  },
  "routing_keywords": {
    "compensation": ["salary", "pay", "allowance", "housing", ...],
    "policy": ["visa", "immigration", "compliance", ...]
  }
}
```

**Why it matters**: Change keywords here to improve routing accuracy without touching code.

---

## The Confusing Parts Explained

### Why Are There TWO Input Collectors?

**Short answer**: Someone built a new one and didn't delete the old one.

- `input_collector.py` = Old rigid Q&A system (still works, just not preferred)
- `conversational_collector.py` = New natural conversation system (currently used)

**Which one runs?**: Check [main.py:489-551](Global-IQ/Global-iq-application/app/main.py#L489-L551) - if `conversational_mode` is True, it uses the new one.

### What's the Deal with MCP and AGNO?

**MCP** = Model Context Protocol (a way for AI apps to talk to external tools/servers)
**AGNO** = An agent framework that uses MCP to connect to services

**The plan was**:
1. User asks question
2. Chainlit routes to AGNO agent
3. AGNO agent calls MCP server
4. MCP server returns prediction
5. Chainlit shows result

**What actually happens**:
1. User asks question
2. Chainlit routes internally
3. Calls GPT-4 directly with a prompt
4. Shows result

**Why the disconnect?**: The MCP integration was started but never finished. The servers exist, the client code exists, but main.py doesn't use them.

**Where's the integration code?**: [agno_mcp_client.py](Global-IQ/Global-iq-application/app/agno_mcp_client.py) has all the methods ready to go, they're just not called from main.py.

### Why Does "Calculation" Just Call GPT-4?

**The honest truth**: There's no trained ML model. No real data. No statistical analysis.

When you see `_run_compensation_calculation()`, it:
1. Formats user data into a prompt
2. Sends to GPT-4
3. GPT-4 makes an educated guess
4. Returns the guess as "calculation results"

**This is not**: Machine learning, data science, or actual prediction
**This is**: Prompt engineering and LLM text generation

**Why?**: Building real ML models requires data, training, validation, deployment infrastructure. This is a school project that needed to demo quickly.

### What's with All the Documentation Files?

The project has like 12 markdown files because your team member was documenting different aspects as they built it:
- `KUBERNETES_DEPLOYMENT.md` - How to deploy to Kubernetes
- `DOCKER_DEPLOYMENT.md` - How to run with Docker
- `INSTALL_GUIDE.md` - How to install dependencies
- `README_AGNO_MCP.md` - The MCP integration plan
- etc.

**Which one matters?**: Start with `CLAUDE.md` (the main dev guide) and this file.

### Why Is Chat History Disabled?

See [main.py:90-102](Global-IQ/Global-iq-application/app/main.py#L90-L102):

```python
# @cl.data_layer
# def get_data_layer():
#     # ... SQLAlchemy setup
```

It's commented out because there were "user/thread integration issues" (see comment). The code for chat history exists in `chat_history.py` but it's not being used.

**Impact**: Conversations don't persist across sessions. Each login is a fresh start.

---

## How to Run It

### Option 1: Local Development (Simplest)

```bash
# Navigate to the app directory
cd Global-IQ/Global-iq-application

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (REQUIRED!)
# Windows:
set OPENAI_API_KEY=sk-your-key-here

# Mac/Linux:
export OPENAI_API_KEY=sk-your-key-here

# Run the app
chainlit run app/main.py

# Open browser to http://localhost:8000
```

**Login with**:
- Username: `employee`
- Password: `employee123`

### Option 2: With Docker

```bash
cd Global-IQ/Global-iq-application

# Make sure .env file has your API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start with docker-compose
docker-compose up

# Open browser to http://localhost:8000
```

### Option 3: With MCP Servers (Advanced)

```bash
# Terminal 1: Start MCP servers
cd Global-IQ/Global-iq-application
START_MCP_SERVERS.bat  # Windows
# Or manually:
# python services/mcp_prediction_server/compensation_server.py
# python services/mcp_prediction_server/policy_server.py

# Terminal 2: Start Chainlit
chainlit run app/main.py

# Servers will run on:
# - Compensation: http://localhost:8081
# - Policy: http://localhost:8082
# - Chainlit: http://localhost:8000
```

**Note**: Even with MCP servers running, main.py doesn't call them yet. You'd need to integrate agno_mcp_client.py.

---

## Common Issues & Debugging

### Issue 1: "OpenAI API Error"
**Cause**: Missing or invalid `OPENAI_API_KEY`

**Fix**:
```bash
# Check if key is set
echo $OPENAI_API_KEY  # Mac/Linux
echo %OPENAI_API_KEY%  # Windows

# Set it
export OPENAI_API_KEY=sk-...  # Mac/Linux
set OPENAI_API_KEY=sk-...     # Windows

# Or put in .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue 2: "Module not found"
**Cause**: Dependencies not installed

**Fix**:
```bash
pip install -r requirements.txt
```

### Issue 3: "Login fails"
**Cause**: Wrong username/password

**Fix**: Check [main.py:26-51](Global-IQ/Global-iq-application/app/main.py#L26-L51) for valid credentials:
- `admin` / `admin123`
- `hr_manager` / `hr2024`
- `employee` / `employee123`
- `demo` / `demo`

### Issue 4: "Routing always goes to fallback"
**Cause**: Keywords don't match, LLM routing failed

**Debug**:
1. Check console output - it prints routing decisions
2. Look at [route_config.json](Global-IQ/Global-iq-application/app/route_config.json) keywords
3. Add your query keywords to the appropriate route

**Example**: If "calculate pay" doesn't route to compensation, add "calculate" to compensation keywords.

### Issue 5: "File upload fails"
**Cause**: Unsupported file type

**Supported types**: PDF, DOCX, XLSX, CSV, JSON, TXT
**See**: [main.py:229-241](Global-IQ/Global-iq-application/app/main.py#L229-L241)

### Issue 6: "MCP servers won't start"
**Cause**: Port already in use, missing dependencies

**Fix**:
```bash
# Check if ports are free
netstat -ano | findstr :8081  # Windows
lsof -i :8081                 # Mac/Linux

# Install MCP dependencies
cd services/mcp_prediction_server
pip install -r requirements.txt

# Try starting manually
python compensation_server.py
```

---

## What's Actually Happening Under the Hood

### Authentication Flow
```python
# 1. User enters credentials
username = "employee"
password = "employee123"

# 2. Password gets hashed
password_hash = hashlib.sha256(password.encode()).hexdigest()
# Result: "9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05"

# 3. Lookup in database
if username in USERS_DB and USERS_DB[username]["password_hash"] == password_hash:
    # Create user session
    return cl.User(identifier="employee", metadata={...})
```

### Routing Decision Tree
```
User query: "How much for engineer to London?"

↓ Step 1: Direct match check
  - Is query literally "compensation", "policy", etc.? NO

↓ Step 2: Keyword scoring
  - Scan for "compensation" keywords: "much" (1), "engineer" (1), "london" (1) → Score: 3
  - Scan for "policy" keywords: None → Score: 0
  - Scan for "both" keywords: None → Score: 0
  - DECISION: compensation route (keyword-based)

↓ Step 3: LLM routing (SKIPPED because keywords matched)

↓ Result: Route to "compensation"
```

### Data Collection State Machine
```python
# Initial state
{
  "conversational_mode": True,
  "current_route": "compensation",
  "collected_data": {},
  "conversation_history": []
}

# After first message
{
  "conversational_mode": True,
  "current_route": "compensation",
  "collected_data": {
    "destination_location": "London",
    "job_level": "engineer"
  },
  "conversation_history": [
    {"role": "user", "content": "How much for engineer to London?"},
    {"role": "assistant", "content": "I need more details..."}
  ]
}

# After collecting all data
{
  "conversational_mode": True,  # Still true, waiting for confirmation
  "current_route": "compensation",
  "collected_data": {
    "origin_location": "NYC",
    "destination_location": "London",
    "current_compensation": "$120,000",
    "assignment_duration": "2 years",
    "job_level": "engineer",
    "family_size": "1",
    "housing_preference": "company-provided"
  },
  "conversation_history": [...]
}

# After confirmation
# conversational_mode set to False, calculation runs, state resets
```

### The GPT-4 Prompt That Actually Runs
```python
# System prompt (from main.py:107-136)
system_prompt = """You are the Global IQ Mobility Advisor,
an expert HR assistant helping Employee User (Role: Employee).

Your goal is to help plan employee relocations based on user requests.

User Role Context:
- You're assisting an Employee with personal relocation needs
- Focus on practical guidance and personal impact
- Explain policies in easy-to-understand terms

Instructions:
- First, check if context from attached documents is provided
- If documents are provided, prioritize that information
- If no specific document context is provided, state that you lack specific data
- Maintain conversation history context and be professional, concise, and helpful
- Always address the user as Employee User when appropriate"""

# User's file context (if files uploaded)
file_context = """Context from attached document(s):

--- Document: HR_Policy_2024.pdf ---
[First 3000 chars of PDF text...]

--- Document: Salary_Data.xlsx ---
[Spreadsheet data as CSV-like text...]
"""

# Conversation history
history = [
  {"role": "user", "content": "How much for engineer to London?"},
  {"role": "assistant", "content": "I need more details..."},
  {"role": "user", "content": "Current salary $120k, 2 years, solo, company housing"},
  {"role": "assistant", "content": "Let me confirm..."},
  {"role": "user", "content": "yes"}
]

# Final calculation prompt (from main.py:262-277)
calc_prompt = """You are the Global IQ Compensation Calculator AI engine
with years of mobility data and cost analysis experience.

Based on the following employee data, calculate a comprehensive compensation package:

• Origin Location: NYC
• Destination Location: London
• Current Compensation: $120,000
• Assignment Duration: 2 years
• Job Level: engineer
• Family Size: 1
• Housing Preference: company-provided

[File context if available]

Provide a detailed breakdown including:
1. Base salary adjustments
2. Cost of living adjustments
3. Housing allowances
4. Hardship pay (if applicable)
5. Tax implications
6. Total estimated package
7. Recommendations for optimization

Format your response professionally with clear financial breakdowns."""

# Final API call
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": calc_prompt}],
    temperature=0.3  # Lower = more consistent
)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                          │
│                    http://localhost:8000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                       CHAINLIT APP (main.py)                    │
│                                                                 │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │ Auth System  │  │ File Processor │  │  Message Handler   │ │
│  │ (SHA-256)    │  │ (PDF,DOCX,etc) │  │  (@cl.on_message)  │ │
│  └──────────────┘  └────────────────┘  └──────────┬─────────┘ │
│                                                     │           │
└─────────────────────────────────────────────────────┼───────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────┐
                    │                                 ↓                     │
                    │                    ┌────────────────────────┐         │
                    │                    │   Enhanced Router      │         │
                    │                    │  (Keyword + LLM)       │         │
                    │                    └────────┬───────────────┘         │
                    │                             │                         │
                    │        ┌────────────────────┼────────────────────┐    │
                    │        │                    │                    │    │
                    │        ↓                    ↓                    ↓    │
                    │   "policy"          "compensation"          "both"    │
                    │                             │                         │
                    │                             ↓                         │
                    │               ┌──────────────────────────┐            │
                    │               │ Conversational Collector │            │
                    │               │  (Gathers missing data)  │            │
                    │               └──────────┬───────────────┘            │
                    │                          │                            │
                    │                          ↓                            │
                    │          ┌──────────────────────────────┐             │
                    │          │  _run_compensation_calc()    │             │
                    │          │  or _run_policy_analysis()   │             │
                    │          └──────────┬───────────────────┘             │
                    │                     │                                 │
                    └─────────────────────┼─────────────────────────────────┘
                                          │
                                          ↓
                             ┌────────────────────────┐
                             │   OpenAI GPT-4 API     │
                             │  (The "AI" part)       │
                             └────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              OPTIONAL: MCP SERVERS (Not Integrated)             │
│                                                                 │
│  ┌──────────────────────┐        ┌──────────────────────┐      │
│  │ Compensation Server  │        │   Policy Server      │      │
│  │    (Port 8081)       │        │    (Port 8082)       │      │
│  │  FastAPI + GPT-4     │        │  FastAPI + GPT-4     │      │
│  └──────────────────────┘        └──────────────────────┘      │
│                                                                 │
│  Status: Coded but not called from main.py                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Importance Ranking

**Critical (Need to understand these)**:
1. `app/main.py` - Everything happens here
2. `app/enhanced_agent_router.py` - Routing logic
3. `app/route_config.json` - Routing rules
4. `app/conversational_collector.py` - Data collection

**Important (Should understand)**:
5. `requirements.txt` - Dependencies
6. `docker-compose.yml` - Local deployment
7. `.env` - Configuration

**Reference (Read if needed)**:
8. `app/input_collector.py` - Legacy collector
9. `app/agno_mcp_client.py` - MCP integration (future)
10. `services/mcp_prediction_server/*` - Microservices (not integrated)

**Documentation (For learning)**:
11. `CLAUDE.md` - Developer guide
12. `docs/*.md` - Various guides

---

## Quick Reference: Session State Variables

```python
# In cl.user_session
{
    # Core state
    "user": cl.User,  # Logged-in user object
    "history": [],    # Chat message history
    "user_data": {    # Main application state

        # Conversational mode (NEW)
        "conversational_mode": bool,           # Using new collector?
        "current_route": str,                  # "compensation" | "policy"
        "collected_data": dict,                # Extracted field values
        "conversation_history": list,          # Message log for extraction

        # Legacy mode (OLD)
        "compensation_collection": {
            "current_question": int,
            "answers": dict,
            "completed": bool,
            "awaiting_confirmation": bool
        },
        "policy_collection": {
            "current_question": int,
            "answers": dict,
            "completed": bool,
            "awaiting_confirmation": bool
        },

        # State flags
        "awaiting_both_choice": bool,          # Waiting for route selection
        "awaiting_compensation_confirmation": bool,
        "awaiting_policy_confirmation": bool,
        "intro_shown": bool                    # Showed intro message?
    }
}
```

---

## Next Steps: Actually Using This Project

### To Understand It Better:
1. Run it locally and watch the console output
2. Try different queries and see which route they hit
3. Add `print()` statements in key functions to trace flow
4. Read main.py from line 379 onwards (the message handler)

### To Modify It:
1. **Change routing**: Edit `route_config.json` keywords
2. **Change questions**: Edit `app/agent_configs/*.txt` files
3. **Change prompts**: Edit system prompts in main.py:105-136
4. **Add users**: Edit USERS_DB in main.py:26-51

### To Actually Finish MCP Integration:
1. Read [agno_mcp_client.py](Global-IQ/Global-iq-application/app/agno_mcp_client.py)
2. In main.py, import GlobalIQAgentSystem
3. Replace `_run_compensation_calculation()` with:
   ```python
   agent_system = GlobalIQAgentSystem()
   result = await agent_system.predict_compensation(...)
   ```
4. Start MCP servers before running Chainlit

### To Present This as a School Project:
1. Focus on the USER FLOW (login → query → routing → collection → response)
2. Demo the routing intelligence (show keyword vs LLM routing)
3. Demo file upload (upload a fake policy PDF, ask about it)
4. Explain the architecture (Chainlit + LangChain + OpenAI)
5. Be honest: "The calculations are GPT-4 estimates, not ML predictions"

---

## TL;DR

**What is it?**: Chatbot for HR mobility questions (salary & policy)
**How it works?**: Routes questions → Collects data → Asks GPT-4 → Shows response
**The "AI"?**: Just GPT-4 text generation, no real ML
**The confusing parts?**:
- Two input collectors (old rigid one + new conversational one)
- MCP servers exist but aren't used
- "Calculations" are just GPT-4 prompts
- Chat history disabled due to bugs

**To run it**: `pip install -r requirements.txt`, set `OPENAI_API_KEY`, run `chainlit run app/main.py`

**To understand it**: Start with main.py line 379 (`handle_message`) and trace from there.

**To modify it**: Change route_config.json for routing, main.py for logic, agent_configs/*.txt for questions.

---

**Good luck! You got this.**
