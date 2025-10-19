# Global IQ Current System - Complete Breakdown

## 🎯 System Overview

**Global IQ Mobility Advisor** is an AI-powered chatbot that helps HR professionals and employees plan international relocations. It provides guidance on:
- **Compensation packages** (salary, allowances, COLA)
- **Policy compliance** (visas, immigration, eligibility)
- **Document analysis** (upload and extract info from PDFs, Excel, etc.)

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                      (Chainlit Web UI)                          │
│  - Login Screen                                                 │
│  - Chat Interface                                               │
│  - File Upload                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                         │
│  - Password-based auth (SHA-256 hashing)                        │
│  - 4 User Roles: admin, hr_manager, employee, demo             │
│  - Session Management                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FILE PROCESSING LAYER                        │
│  - PDF (PyMuPDF)                                                │
│  - DOCX (python-docx)                                           │
│  - XLSX (openpyxl)                                              │
│  - CSV, JSON, TXT                                               │
│  → Extracts text for context                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ENHANCED AGENT ROUTER                          │
│                    (LangChain + GPT-4)                          │
│                                                                 │
│  Analyzes user query and routes to:                            │
│  1. Policy Route                                                │
│  2. Compensation Route                                          │
│  3. Both Policy & Compensation                                  │
│  4. Guidance Fallback                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────────┐
         │               │               │                 │
         ▼               ▼               ▼                 ▼
    ┌────────┐     ┌──────────┐    ┌────────┐      ┌──────────┐
    │ Policy │     │  Comp.   │    │  Both  │      │ Guidance │
    │ Route  │     │  Route   │    │ Routes │      │ Fallback │
    └───┬────┘     └────┬─────┘    └───┬────┘      └────┬─────┘
        │               │               │                │
        ▼               ▼               ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT COLLECTOR                              │
│  - Asks structured questions (loaded from config files)         │
│  - Collects user responses                                      │
│  - Validates and confirms data                                  │
│  - AI spell-check for inputs                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CALCULATION/ANALYSIS ENGINE                    │
│                        (GPT-4 Based)                            │
│                                                                 │
│  - _run_compensation_calculation()                              │
│  - _run_policy_analysis()                                       │
│  → Generates text-based "calculations" using LLM                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORMATTED RESPONSE                           │
│  - Markdown formatted                                           │
│  - Includes breakdowns, recommendations                         │
│  - Displayed in chat interface                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 1. Authentication System

### **Location:** `app/main.py` (lines 24-74)

### **How It Works:**

```python
USERS_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "name": "Administrator"
    },
    # ... other users
}

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS_DB and USERS_DB[username]["password_hash"] == password_hash:
        return cl.User(identifier=username, metadata={...})
    return None
```

### **User Roles:**

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| **Admin** | `admin` | `admin123` | Full access, user management, special commands (`/users`, `/help`, `/history`) |
| **HR Manager** | `hr_manager` | `hr2024` | Policy & compensation access |
| **Employee** | `employee` | `employee123` | Personal relocation queries |
| **Demo** | `demo` | `demo` | Exploration mode |

### **Security:**
- Passwords hashed with SHA-256
- User metadata stored in session
- Role-based prompts and access

---

## 📁 2. File Processing System

### **Location:** `app/main.py` (lines 135-237)

### **Supported Formats:**

```python
FILE_HANDLERS = {
    "application/pdf": process_pdf,                    # PyMuPDF
    "application/vnd...wordprocessingml.document": process_docx,  # python-docx
    "application/vnd...spreadsheetml.sheet": process_xlsx,        # openpyxl
    "text/csv": process_csv,                           # Built-in csv
    "application/json": process_json,                  # Built-in json
    "text/plain": process_txt                          # Built-in open()
}
```

### **Processing Flow:**

```
User uploads file → Chainlit receives file → Check MIME type
                                                    ↓
                                    Dispatch to appropriate handler
                                                    ↓
                                    Extract text content
                                                    ↓
                                    Add to prompt context
                                                    ↓
                                    Send to LLM with extracted text
```

### **Example - PDF Processing:**

```python
def process_pdf(file_path: str) -> str:
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text += page_text + "\n\n"
    doc.close()
    return text.strip()
```

### **Key Features:**
- Handles multiple file types
- Extracts text for LLM context
- Error handling for corrupted files
- Truncates long documents (max 3000 chars per file)

---

## 🧭 3. Enhanced Agent Router

### **Location:** `app/enhanced_agent_router.py`

### **Purpose:**
Intelligently routes user queries to the appropriate specialist agent.

### **4 Route Destinations:**

#### **1. Policy Route**
- **Triggers:** visa, immigration, compliance, regulations, policy, rules
- **Handles:** 
  - Visa requirements
  - Immigration procedures
  - Assignment eligibility
  - Compliance guidelines
  - Policy documentation

#### **2. Compensation Route**
- **Triggers:** salary, pay, compensation, allowance, cost, money, calculate
- **Handles:**
  - Salary calculations
  - Cost of living adjustments (COLA)
  - Housing allowances
  - Hardship pay
  - Tax implications

#### **3. Both Policy & Compensation**
- **Triggers:** cheapest, best, optimal, recommend, compare
- **Handles:**
  - Complex scenarios needing both policy and financial analysis
  - Optimization questions
  - Strategic recommendations

#### **4. Guidance Fallback**
- **Triggers:** who are you, what can you do, help, hello
- **Handles:**
  - Unclear queries
  - System capability questions
  - General guidance

### **Routing Logic:**

```python
def route_query(self, user_input: str) -> dict:
    # Step 1: Direct keyword matching for obvious cases
    if user_input_lower in ['compensation', 'salary', 'pay']:
        return {"destination": "compensation"}
    
    # Step 2: LLM-based routing for complex queries
    routing_result = self.router_chain.invoke({"input": user_input})
    destination = routing_result["destination"]
    
    return {
        "destination": destination,
        "next_inputs": {"input": user_input},
        "routing_method": "llm"
    }
```

### **How LangChain Router Works:**

```
User Query → Router Prompt Template → GPT-4 Classification
                                            ↓
                        Selects best matching route based on descriptions
                                            ↓
                        Returns route name + confidence
```

### **Configuration:**
- Route descriptions in `route_config.json`
- Keywords for fast routing
- Display info (emoji, title, description)

---

## 📝 4. Input Collector System

### **Location:** `app/input_collector.py`

### **Purpose:**
Collects structured information from users through sequential Q&A.

### **How It Works:**

```
Route Selected → Load Questions from Config → Ask Question 1
                                                    ↓
                                            User Answers
                                                    ↓
                                            Store Answer
                                                    ↓
                                            Ask Question 2
                                                    ↓
                                            ... (repeat)
                                                    ↓
                                            All Questions Done
                                                    ↓
                                            Show Summary
                                                    ↓
                                            Ask for Confirmation
                                                    ↓
                                    Yes → Proceed    No → Edit Answers
```

### **Question Configuration Files:**

**`agent_configs/compensation_questions.txt`:**
```
1. **Origin Location**
   - Question: "What is the employee's current location?"
   - Format: City, Country

2. **Destination Location**
   - Question: "Where will the employee be relocating to?"
   - Format: City, Country

3. **Current Compensation**
   - Question: "What is the employee's current annual salary?"
   - Format: Amount and currency (e.g., "100,000 USD")

... (more questions)
```

**`agent_configs/policy_questions.txt`:**
```
1. **Origin Country**
   - Question: "What country is the employee currently in?"

2. **Destination Country**
   - Question: "What country will the employee relocate to?"

3. **Assignment Type**
   - Question: "What type of assignment is this?"
   - Options: Short-term, Long-term, Permanent Transfer

... (more questions)
```

### **Key Features:**

1. **Sequential Collection:**
   - One question at a time
   - Progress indicator (Question 3 of 7)
   - Stores answers in session

2. **AI Spell-Check:**
   ```python
   async def ai_spell_check_and_correct(self, user_input: str, question_title: str):
       # Uses GPT-4o-mini to correct spelling errors
       # Standardizes location names, currency formats
       # Returns corrected text + suggestions
   ```

3. **Confirmation Workflow:**
   ```
   All Questions Answered → Show Summary
                                ↓
                    "Is this information correct?"
                                ↓
                    Yes → Proceed    No → Re-ask questions
   ```

4. **Session State Management:**
   ```python
   user_session = {
       "compensation_collection": {
           "current_question": 3,
           "answers": {
               "Origin Location": "New York, USA",
               "Destination Location": "London, UK",
               "Current Compensation": "100,000 USD"
           },
           "completed": False,
           "awaiting_confirmation": False
       }
   }
   ```

---

## 🧮 5. Calculation/Analysis Engines

### **Location:** `app/main.py` (lines 240-334)

### **Compensation Calculator**

```python
async def _run_compensation_calculation(collected_data: dict, extracted_texts: list):
    # Format collected data
    data_summary = "\n".join([f"• **{key}:** {value}" 
                              for key, value in collected_data.items()])
    
    # Add document context if files were uploaded
    context_info = ""
    if extracted_texts:
        for item in extracted_texts:
            context_info += f"\n--- {item['name']} ---\n{item['content'][:1000]}\n"
    
    # Create prompt for GPT-4
    calc_prompt = f"""You are the Global IQ Compensation Calculator AI engine.
    
Based on the following employee data, calculate a comprehensive compensation package:

{data_summary}{context_info}

Provide a detailed breakdown including:
1. Base salary adjustments
2. Cost of living adjustments
3. Housing allowances
4. Hardship pay (if applicable)
5. Tax implications
6. Total estimated package
7. Recommendations for optimization

Format your response professionally with clear financial breakdowns."""
    
    # Call OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": calc_prompt}],
        temperature=0.3
    )
    
    result = f"💰 **Compensation Calculation Results**\n\n{response.choices[0].message.content}"
    return result
```

### **Policy Analyzer**

```python
async def _run_policy_analysis(collected_data: dict, extracted_texts: list):
    # Similar structure to compensation calculator
    
    policy_prompt = f"""You are the Global IQ Policy Analyzer AI engine.
    
Based on the following assignment details, provide a comprehensive policy analysis:

{data_summary}{context_info}

Analyze and provide guidance on:
1. Eligibility requirements and compliance
2. Visa and immigration requirements
3. Assignment approval process
4. Policy constraints or limitations
5. Required documentation
6. Timeline and next steps
7. Risk factors and mitigation strategies

Format your response as a structured policy guidance document."""
    
    # Call OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": policy_prompt}],
        temperature=0.3
    )
    
    result = f"📋 **Policy Analysis Results**\n\n{response.choices[0].message.content}"
    return result
```

### **Key Characteristics:**

- ⚠️ **Not Real Calculations:** These are LLM text generations, not mathematical models
- ⚠️ **No Training Data:** GPT-4 uses general knowledge, not company-specific data
- ⚠️ **No Confidence Scores:** No way to measure accuracy
- ⚠️ **No External Data:** Doesn't pull live currency rates, COLA data, etc.

---

## 🔄 6. Complete User Flow Example

### **Scenario:** Employee asks "How much will I earn in London?"

```
Step 1: Authentication
├─ User logs in as "employee" with password "employee123"
├─ System validates credentials (SHA-256 hash match)
└─ Creates user session with role metadata

Step 2: Query Input
├─ User types: "How much will I earn in London?"
├─ Message stored in session history
└─ Optional: User uploads salary document (PDF)

Step 3: File Processing (if applicable)
├─ System detects PDF MIME type
├─ Calls process_pdf() → extracts text
├─ Truncates to 3000 chars
└─ Adds to context

Step 4: Agent Routing
├─ Router analyzes query: "How much will I earn in London?"
├─ Keyword match: "earn" → compensation route
├─ LLM confirms: destination = "compensation"
└─ Displays: "💰 Routed to: Compensation Expert"

Step 5: Confirmation
├─ System: "I detected you need compensation analysis. Start questionnaire?"
├─ User: "Yes"
└─ Proceeds to input collection

Step 6: Input Collection
├─ Q1: "What is your current location?" → User: "New York, USA"
├─ Q2: "Where will you relocate to?" → User: "London, UK"
├─ Q3: "What is your current salary?" → User: "100k USD"
├─ Q4: "Assignment duration?" → User: "12 months"
├─ Q5: "Job level?" → User: "Senior Engineer"
├─ Q6: "Family size?" → User: "2"
└─ Q7: "Housing preference?" → User: "Company-provided"

Step 7: Confirmation
├─ System shows summary of all answers
├─ User confirms: "Yes, this is correct"
└─ System: "✅ Processing confirmed!"

Step 8: Calculation
├─ Calls _run_compensation_calculation()
├─ Formats collected data into prompt
├─ Adds uploaded document context
├─ Sends to GPT-4 with temperature=0.3
└─ GPT-4 generates text-based "calculation"

Step 9: Response
├─ System formats GPT-4 response with markdown
├─ Displays breakdown:
│   ├─ Base salary adjustments
│   ├─ COLA (Cost of Living Adjustment)
│   ├─ Housing allowance
│   ├─ Tax implications
│   └─ Total estimated package
└─ User sees formatted response in chat

Step 10: Follow-up
├─ User can ask clarifying questions
├─ System maintains conversation context
└─ Can start new calculation or policy analysis
```

---

## 📊 7. Session Management

### **What's Stored in Session:**

```python
cl.user_session = {
    "user": {
        "identifier": "employee",
        "metadata": {
            "role": "employee",
            "name": "Employee User",
            "email": "employee@globaliq.com"
        }
    },
    "history": [
        {"role": "user", "content": "How much will I earn in London?"},
        {"role": "assistant", "content": "I detected you need..."}
    ],
    "user_data": {
        "compensation_collection": {
            "current_question": 7,
            "answers": {
                "Origin Location": "New York, USA",
                "Destination Location": "London, UK",
                "Current Compensation": "100,000 USD",
                "Assignment Duration": "12 months",
                "Job Level": "Senior Engineer",
                "Family Size": "2",
                "Housing Preference": "Company-provided"
            },
            "completed": True,
            "awaiting_confirmation": False
        },
        "awaiting_compensation_confirmation": False,
        "intro_shown": True
    }
}
```

### **Session Lifecycle:**

```
User Login → Session Created → Chat History Initialized
                                        ↓
                            User Interactions Stored
                                        ↓
                            Collection State Tracked
                                        ↓
                            Session Persists Until Logout
```

---

## 🎨 8. User Interface (Chainlit)

### **Configuration:** `chainlit.toml`

```toml
[UI]
name = "Global IQ Mobility Advisor"
default_theme = "light"

[UI.theme]
primary_color = "#02afdc"
```

### **Custom Branding:**
- Logo: `public/logo_light.png`, `public/logo_dark.png`
- Favicon: `public/favicon.png`
- Theme: `public/theme.json`

### **Chat Features:**
- Markdown rendering
- File upload widget
- Message history
- Typing indicators
- Error messages

---

## 🔧 9. Admin Commands

### **Available to Admin Role Only:**

```python
if msg.content.lower() == '/users':
    # Display all registered users
    user_list = "👥 **Current Users:**\n\n"
    for username, data in USERS_DB.items():
        user_list += f"• **{username}** - {data['name']} ({data['role']})\n"

if msg.content.lower() == '/help':
    # Show admin help message
    help_msg = "🔧 **Admin Commands:**\n\n"
    help_msg += "• `/users` - List all registered users\n"
    help_msg += "• `/help` - Show this help message\n"
    help_msg += "• `/history` - View current session chat history\n"

if msg.content.lower() == '/history':
    # Show last 10 messages from session
    history = cl.user_session.get("history", [])
    for i, item in enumerate(history[-10:], 1):
        history_msg += f"{i}. {item['role']}: {item['content'][:100]}...\n"
```

---

## ⚙️ 10. System Initialization

### **Startup Sequence:**

```python
# 1. Load environment variables
load_dotenv()

# 2. Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. Initialize router
router = EnhancedAgentRouter(api_key=os.getenv("OPENAI_API_KEY"))

# 4. Initialize input collector
input_collector = InputCollector(openai_client=client)

# 5. Start Chainlit app
@cl.on_chat_start
async def start_chat():
    # Initialize session history
    cl.user_session.set("history", [])
    
    # Get authenticated user
    user = cl.user_session.get("user")
    
    # Send welcome message
    await cl.Message(content=welcome_msg).send()

# 6. Handle incoming messages
@cl.on_message
async def handle_message(msg: cl.Message):
    # Process files, route query, collect input, generate response
```

---

## 📦 11. Dependencies

### **From `requirements.txt`:**

```
chainlit              # Web UI framework
openai                # GPT-4 API
python-dotenv         # Environment variables
PyMuPDF               # PDF processing
python-docx           # Word document processing
openpyxl              # Excel processing
langchain             # LLM routing framework
langchain-openai      # OpenAI integration for LangChain
pandas                # Data manipulation
SQLAlchemy            # Database ORM (for chat history)
aiosqlite             # Async SQLite
```

---

## 🚀 12. Deployment

### **Docker Setup:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["chainlit", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose:**

```yaml
version: '3.8'

services:
  global-iq-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./app:/app/app
```

### **Running Locally:**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="sk-..."

# Run application
chainlit run app/main.py
```

---

## 🔍 13. Key Limitations (Why MCP Integration Needed)

### **1. No Real ML Models**
- Everything is LLM text generation
- No trained models on historical data
- Can't measure accuracy

### **2. No External Data**
- No live currency exchange rates
- No real-time cost-of-living data
- No visa requirement databases
- No housing cost APIs

### **3. No Confidence Scores**
- Can't quantify uncertainty
- No way to know if "calculation" is reliable
- Users must trust blindly

### **4. Limited Scalability**
- All processing in-line (synchronous)
- Single OpenAI API dependency
- No caching or optimization

### **5. No Model Versioning**
- Can't track improvements
- Can't A/B test different approaches
- No rollback capability

### **6. No Monitoring**
- No prediction accuracy tracking
- No performance metrics
- No user satisfaction feedback

---

## 📈 14. Data Flow Summary

```
┌──────────┐
│   User   │
└────┬─────┘
     │ 1. Login
     ▼
┌──────────────┐
│  Auth Layer  │ ← Validates credentials
└────┬─────────┘
     │ 2. Upload file (optional)
     ▼
┌──────────────┐
│ File Process │ ← Extracts text
└────┬─────────┘
     │ 3. Ask question
     ▼
┌──────────────┐
│    Router    │ ← Routes to agent
└────┬─────────┘
     │ 4. Route selected
     ▼
┌──────────────┐
│Input Collect │ ← Asks questions
└────┬─────────┘
     │ 5. Data collected
     ▼
┌──────────────┐
│  GPT-4 Call  │ ← Generates response
└────┬─────────┘
     │ 6. Format response
     ▼
┌──────────────┐
│  Display UI  │ ← Shows to user
└──────────────┘
```

---

## 🎯 Summary

The current Global IQ system is a **well-structured LLM-powered chatbot** with:

✅ **Strengths:**
- Clean architecture with separated concerns
- Intelligent routing system
- Structured data collection
- Multiple file format support
- Role-based access control
- Good user experience

❌ **Limitations:**
- No real ML predictions (just LLM text)
- No external data integration
- No confidence scores
- Limited scalability
- No model versioning or monitoring

**This is why AGNO MCP integration is valuable** - it transforms the system from LLM-only to a hybrid architecture with real ML models, external data sources, and production-grade infrastructure.

---

## 📚 Related Documents

- **[AGNO_MCP_INTEGRATION_PLAN.md](./AGNO_MCP_INTEGRATION_PLAN.md)** - How to add MCP
- **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)** - High-level overview
- **[QUICK_START.md](./QUICK_START.md)** - Implementation guide

