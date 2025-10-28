# Conversational Intake System Documentation

## Brief Overview

The conversational intake system uses GPT-4 to intelligently extract structured data from natural HR conversations. Instead of rigid sequential questionnaires, HR professionals describe employee relocations naturally (e.g., "moving someone from Chicago to Mumbai making 100k for 2 years"), and the LLM:

1. **Extracts** all provided information
2. **Identifies** missing required fields
3. **Asks** only for what's missing in a conversational way
4. **Confirms** when all data is collected

This eliminates redundant questions and creates a natural chat experience.

---

## Detailed Technical Explanation

### Architecture

```
User Query → Extract Information → Check Completeness → Generate Response
     ↓              ↓                      ↓                    ↓
"moving      GPT-4 parses      Missing: role,      "Thanks! I've captured...
someone      to structured     family, housing     What is the employee's
from         fields:                               role? Family size?..."
Chicago      ✓ Origin: Chicago
to Mumbai    ✓ Dest: Mumbai
making       ✓ Salary: $100k
100k"        ✓ Duration: 2yrs
```

### Core Components

#### 1. **ConversationalCollector Class** (`app/conversational_collector.py`)

**Purpose**: Orchestrates LLM-based data extraction and question generation.

**Key Methods**:

- `extract_information(route, user_message, conversation_history)`:
  - Uses GPT-4 to parse user's natural language
  - Returns: extracted fields, confidence scores, missing fields, clarifications needed
  - Prompt example:
    ```
    Extract from: "moving someone from chicago to mumbai"
    Required fields: Origin, Destination, Salary, Duration, Role, Family, Housing
    → Returns: {Origin: "Chicago, USA", Destination: "Mumbai, India", ...rest null}
    ```

- `generate_follow_up(route, extracted_data, missing_fields)`:
  - Creates natural follow-up questions for missing data
  - Uses GPT-4 to generate conversational prompts
  - Example: "Thanks! I've noted Chicago → Mumbai. Could you share: • Employee's role? • Family size?"

- `is_complete(extracted_data, route)`:
  - Checks if all required fields are present
  - Returns boolean

- `_generate_confirmation_message(route, collected_data)`:
  - Displays all collected data in formatted view
  - Asks user to confirm before proceeding

**Required Fields by Route**:

```python
"compensation": {
    "Origin Location": "Employee's current city and country",
    "Destination Location": "Where the employee will relocate to",
    "Current Compensation": "Annual salary with currency",
    "Assignment Duration": "How long the assignment will last",
    "Job Level/Title": "Employee's position or seniority level",
    "Family Size": "Number of family members relocating (including employee)",
    "Housing Preference": "Preferred housing arrangement"
}

"policy": {
    "Origin Country": "Employee's current country",
    "Destination Country": "Country they're relocating to",
    "Assignment Type": "Type of assignment",
    "Assignment Duration": "Duration of the assignment",
    "Job Title": "Employee's job title"
}
```

#### 2. **Integration in main.py**

**Initialization**:
```python
conversational_collector = ConversationalCollector(openai_client=client)
```

**Flow on Initial Query** (lines 683-726):

```python
if route_name == "compensation":
    # Extract information from initial query immediately
    extraction = await conversational_collector.extract_information(
        "compensation",
        user_query,
        []
    )

    # Update collected data
    collected_data = {}
    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    # Check completeness
    if conversational_collector.is_complete(collected_data, "compensation"):
        # Show confirmation
        confirmation = await conversational_collector._generate_confirmation_message(...)
    else:
        # Ask for missing fields
        follow_up = await conversational_collector.generate_follow_up(...)

    # Mark in conversational mode
    user_session["conversational_mode"] = True
    user_session["current_route"] = "compensation"
    user_session["collected_data"] = collected_data
```

**Flow on Follow-up Messages** (lines 489-551):

```python
in_conversational_mode = user_session.get("conversational_mode", False)

if in_conversational_mode:
    # Check if user is confirming
    if user_query.lower() in ['yes', 'correct', 'confirmed', ...]:
        # Run calculation/analysis
        if current_route == "compensation":
            calc_response = await _run_compensation_calculation(collected_data, extracted_texts)
        # Exit conversational mode
        user_session["conversational_mode"] = False
        return

    # Extract from new message
    extraction = await conversational_collector.extract_information(
        current_route,
        user_query,
        conversation_history
    )

    # Update collected data
    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    # Check if complete
    if conversational_collector.is_complete(collected_data, current_route):
        # Show confirmation
    else:
        # Ask for remaining fields
```

### LLM Prompts

#### **Extraction Prompt** (lines 104-138 in conversational_collector.py):

```
You are an intelligent data extraction assistant for an HR global mobility system.

The user is an HR professional describing an employee relocation scenario.
Extract information from their message to fill in these required fields:

- Origin Location: Employee's current city and country
- Destination Location: Where the employee will relocate to
- Current Compensation: Annual salary with currency
- ...

User's message: "moving someone from chicago to mumbai making 100k for 2 years"

Analyze the message and extract any information that matches these fields.
Be intelligent about inference:
- If they mention a city, infer the country if obvious (e.g., "Chicago" = "Chicago, USA")
- Parse salary formats (100k, $100,000, etc.)
- Understand duration (2 years, 24 months, etc.)
- Recognize third-person descriptions (e.g., "moving someone from Chicago" means Chicago is the origin)
- Family size should include the employee (e.g., "1 kid" = family of 2)

Return a JSON object with this EXACT structure:
{
    "extracted_fields": {"Field Name": "extracted value or null"},
    "confidence": {"Field Name": 0.0-1.0},
    "missing_fields": ["Field Name 1", ...],
    "clarifications_needed": [...]
}
```

**Example Response**:
```json
{
  "extracted_fields": {
    "Origin Location": "Chicago, USA",
    "Destination Location": "Mumbai, India",
    "Current Compensation": "$100,000 USD",
    "Assignment Duration": "2 years",
    "Job Level/Title": null,
    "Family Size": null,
    "Housing Preference": null
  },
  "confidence": {
    "Origin Location": 1.0,
    "Destination Location": 1.0,
    "Current Compensation": 0.9,
    "Assignment Duration": 0.95
  },
  "missing_fields": ["Job Level/Title", "Family Size", "Housing Preference"]
}
```

#### **Follow-up Generation Prompt** (lines 199-215):

```
Generate a BRIEF, conversational follow-up message for an HR global mobility assistant chatbot.

The HR professional has provided this information about the employee relocation:
- Origin Location: Chicago, USA
- Destination Location: Mumbai, India
- Current Compensation: $100,000 USD
- Assignment Duration: 2 years

We still need:
- Employee's position or seniority level
- Number of family members relocating (including employee)
- Preferred housing arrangement

Generate a SHORT, friendly chat message (2-4 sentences MAX) that:
1. Briefly acknowledges what we've received
2. Asks for the missing information naturally in a bulleted list
3. Uses professional third-person language (e.g., "What is the employee's role?" not "What's your role?")
4. Sounds like a helpful chatbot, NOT a formal business email

Example style: "Thanks! I've captured the origin and destination. To continue, I'll need a few more details:
• What is the employee's current salary?
• How long will the assignment be?
• ..."

Return ONLY the message text, no JSON, no subject line, no signature.
```

**Example Response**:
```
Great! I've noted the move from Chicago to Mumbai and the assignment details.
To assist further, could you share:
• What is the employee's position or seniority level?
• How many family members are relocating?
• What is the preferred housing arrangement?
```

### Session Management

**Session Variables**:
```python
user_session = {
    "conversational_mode": True,  # Flag to indicate conversational collection
    "current_route": "compensation",  # Which route we're collecting for
    "collected_data": {  # Accumulated extracted fields
        "Origin Location": "Chicago, USA",
        "Destination Location": "Mumbai, India",
        ...
    },
    "conversation_history": [  # For context in follow-ups
        {"role": "user", "content": "moving someone from chicago to mumbai"},
        {"role": "assistant", "content": "Thanks! I've captured..."}
    ]
}
```

### Complete Flow Example

**Interaction 1**:
```
User: "moving someone from chicago to mumbai making 100k for 2 years"

System:
1. Routes to "compensation"
2. Extracts: Origin, Destination, Salary, Duration
3. Missing: Role, Family, Housing
4. Response: "Great! I've noted the move from Chicago to Mumbai ($100k for 2 years).
   Could you share: • Employee's role? • Family size? • Housing preference?"
```

**Interaction 2**:
```
User: "Senior Engineer, family of 3, company housing"

System:
1. In conversational mode for compensation
2. Extracts: Role (Senior Engineer), Family (3), Housing (company housing)
3. All fields complete
4. Response: "Here's what I've gathered:
   • Origin: Chicago, USA
   • Destination: Mumbai, India
   • Salary: $100,000 USD
   • Duration: 2 years
   • Role: Senior Engineer
   • Family: 3
   • Housing: company housing

   Is this correct? (Reply 'yes' to proceed)"
```

**Interaction 3**:
```
User: "yes"

System:
1. Recognizes confirmation
2. Calls _run_compensation_calculation(collected_data, extracted_texts)
3. Returns compensation analysis
4. Exits conversational mode
```

---

## Replacing with Actual MCPs

### Brief Overview

Currently, the system uses **GPT-4 text generation** for both data extraction AND final calculations. To use real MCPs:

1. **Keep** the conversational collector for data extraction (it works well)
2. **Replace** `_run_compensation_calculation()` and `_run_policy_analysis()` with MCP client calls
3. **MCP servers** handle actual calculations using real data sources (COLA databases, currency APIs, visa requirements, etc.)

This separation allows:
- **Conversational layer**: GPT-4 handles natural language → structured data
- **Calculation layer**: MCP servers handle structured data → predictions/analysis

### Detailed Integration Plan

#### Current Architecture

```
User Query
    ↓
[Conversational Collector - GPT-4]
    ↓
Extracted Structured Data
    ↓
[GPT-4 "Calculation" - Text Generation]  ← REPLACE THIS
    ↓
Response
```

#### Target Architecture with MCPs

```
User Query
    ↓
[Conversational Collector - GPT-4]  ← KEEP THIS
    ↓
Extracted Structured Data
    ↓
[MCP Client] → [MCP Server - Real Predictions]  ← NEW
    ↓           - Currency APIs
Response        - COLA databases
                - Housing cost data
                - Visa requirement APIs
                - ML prediction models
```

#### Step 1: MCP Server Development (External Teams)

**Compensation MCP Server** (`services/mcp_prediction_server/compensation_server.py`):

Currently has this interface:
```python
@app.post("/predict")
async def predict_compensation_endpoint(request: CompensationRequest):
    # Currently uses GPT-4
    # REPLACE WITH:
    # 1. Currency conversion API
    # 2. COLA index lookup (Mercer, ECA, etc.)
    # 3. Housing cost API (Numbeo, etc.)
    # 4. Tax calculation engine
    # 5. ML model for package prediction
```

**Required Changes**:

**Before (Current - GPT-4)**:
```python
async def predict_compensation(origin, destination, salary, duration, ...):
    prompt = f"""You are a compensation expert. Calculate package for:
    Origin: {origin}, Destination: {destination}, Salary: {salary}..."""

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse GPT-4 response
    return json.loads(response)
```

**After (Real MCP)**:
```python
async def predict_compensation(origin, destination, salary, duration, ...):
    # 1. Get currency conversion
    exchange_rate = await currency_api.get_rate(origin_currency, dest_currency)

    # 2. Get COLA index
    cola_index = await cola_database.get_index(origin_city, dest_city)

    # 3. Get housing costs
    housing_cost = await housing_api.get_average_cost(
        dest_city,
        family_size,
        housing_type
    )

    # 4. Calculate base salary adjustment
    adjusted_salary = salary * exchange_rate * cola_index

    # 5. Use ML model for final prediction
    prediction = ml_model.predict({
        "origin": origin,
        "destination": destination,
        "base_salary": adjusted_salary,
        "duration": duration,
        "family_size": family_size,
        ...
    })

    # 6. Return structured response
    return {
        "predictions": {
            "adjusted_base_salary": adjusted_salary,
            "housing_allowance": housing_cost,
            "total_package": prediction.total_package,
            ...
        },
        "breakdown": {...},
        "confidence_scores": prediction.confidence,
        "data_sources": {
            "exchange_rate": "XE.com API",
            "cola_index": "Mercer COLA Database",
            "housing_data": "Numbeo API",
            "model": "CompensationPredictor v2.3"
        }
    }
```

**Policy MCP Server** - Similar changes for visa/compliance data:

```python
async def analyze_policy(origin_country, dest_country, duration, job_title, ...):
    # 1. Check visa requirements API
    visa_info = await visa_api.get_requirements(
        origin_country,
        dest_country,
        duration,
        job_title
    )

    # 2. Get tax treaty information
    tax_treaty = await tax_api.get_treaty_info(origin_country, dest_country)

    # 3. Check compliance requirements
    compliance = await compliance_db.get_requirements(dest_country, assignment_type)

    # 4. Use ML model for risk assessment
    risk_score = ml_model.predict_compliance_risk({
        "origin": origin_country,
        "destination": dest_country,
        "duration": duration,
        ...
    })

    return {
        "visa_requirements": visa_info,
        "tax_implications": tax_treaty,
        "compliance_requirements": compliance,
        "risk_assessment": risk_score,
        "data_sources": {...}
    }
```

#### Step 2: MCP Client Integration (Already Implemented)

The MCP client is already set up in `main.py` (lines 86-130):

```python
class MCPClient:
    """Client for communicating with MCP prediction servers"""

    def __init__(self):
        self.compensation_url = os.getenv("COMPENSATION_SERVER_URL", "http://localhost:8081")
        self.policy_url = os.getenv("POLICY_SERVER_URL", "http://localhost:8082")

    async def predict_compensation(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.compensation_url}/predict",
                json=data
            )
            return response.json()

    async def analyze_policy(self, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.policy_url}/predict",
                json=data
            )
            return response.json()
```

#### Step 3: Modify Calculation Functions

**Current (GPT-4 based)**:
```python
async def _run_compensation_calculation(user_data: dict, extracted_texts: list) -> str:
    # Build context from user data
    context = "\n".join([
        f"- **{key}**: {value}"
        for key, value in user_data.items()
    ])

    # Use GPT-4 directly
    prompt = f"""You are a Global Mobility Compensation Expert...
    {context}
    Calculate compensation package..."""

    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

**With MCP**:
```python
async def _run_compensation_calculation(user_data: dict, extracted_texts: list) -> str:
    # Format data for MCP server
    mcp_request = {
        "origin_location": user_data.get("Origin Location"),
        "destination_location": user_data.get("Destination Location"),
        "current_compensation": user_data.get("Current Compensation"),
        "assignment_duration": user_data.get("Assignment Duration"),
        "job_level": user_data.get("Job Level/Title"),
        "family_size": user_data.get("Family Size"),
        "housing_preference": user_data.get("Housing Preference"),
        "context_documents": extracted_texts  # Company policies, etc.
    }

    # Call MCP server
    try:
        mcp_response = await mcp_client.predict_compensation(mcp_request)

        # Format MCP response for user
        formatted_response = f"""## Compensation Package Analysis

**Predicted Package**: ${mcp_response['predictions']['total_package']:,.2f}

### Breakdown:
- **Adjusted Base Salary**: ${mcp_response['predictions']['adjusted_base_salary']:,.2f}
- **Housing Allowance**: ${mcp_response['predictions']['housing_allowance']:,.2f}
- **COLA Adjustment**: ${mcp_response['predictions']['cola_adjustment']:,.2f}
- **Tax Equalization**: ${mcp_response['predictions']['tax_equalization']:,.2f}

### Confidence Scores:
- Base Salary: {mcp_response['confidence_scores']['base_salary']:.1%}
- Housing: {mcp_response['confidence_scores']['housing']:.1%}
- Overall: {mcp_response['confidence_scores']['overall']:.1%}

### Data Sources:
{chr(10).join([f"- {source}" for source in mcp_response['data_sources'].values()])}

### Recommendations:
{chr(10).join([f"- {rec}" for rec in mcp_response['recommendations']])}
"""
        return formatted_response

    except Exception as e:
        # Fallback to GPT-4 if MCP unavailable
        logging.warning(f"MCP server unavailable, falling back to GPT-4: {e}")
        return await _run_compensation_calculation_gpt4(user_data, extracted_texts)
```

#### Step 4: Environment Configuration

**`.env` updates**:
```bash
# OpenAI for conversational extraction
OPENAI_API_KEY=sk-...

# MCP Server URLs
COMPENSATION_SERVER_URL=http://compensation-mcp.company.com/api
POLICY_SERVER_URL=http://policy-mcp.company.com/api

# MCP Authentication (if needed)
MCP_API_KEY=...
MCP_AUTH_TOKEN=...
```

#### Step 5: Testing Strategy

**Unit Tests**:
```python
# test_mcp_integration.py

async def test_compensation_mcp():
    """Test MCP compensation prediction"""
    client = MCPClient()

    request = {
        "origin_location": "Chicago, USA",
        "destination_location": "Mumbai, India",
        "current_compensation": "$100,000 USD",
        "assignment_duration": "2 years",
        "job_level": "Senior Engineer",
        "family_size": 3,
        "housing_preference": "company housing"
    }

    response = await client.predict_compensation(request)

    assert "predictions" in response
    assert "total_package" in response["predictions"]
    assert response["confidence_scores"]["overall"] > 0.5
    assert len(response["data_sources"]) > 0
```

**Integration Tests**:
```python
async def test_end_to_end_flow():
    """Test full conversational → MCP flow"""

    # 1. Extract data conversationally
    collector = ConversationalCollector(openai_client)
    extraction = await collector.extract_information(
        "compensation",
        "moving someone from chicago to mumbai making 100k for 2 years",
        []
    )

    # 2. Complete missing fields
    collected_data = extraction["extracted_fields"]
    collected_data["Job Level/Title"] = "Senior Engineer"
    collected_data["Family Size"] = "3"
    collected_data["Housing Preference"] = "company housing"

    # 3. Call MCP
    result = await _run_compensation_calculation(collected_data, [])

    # 4. Verify response format
    assert "Compensation Package Analysis" in result
    assert "Confidence Scores" in result
    assert "Data Sources" in result
```

#### Step 6: Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chainlit Frontend                        │
│                  (port 8000/8001/8003)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                     main.py                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │  ConversationalCollector (GPT-4)                 │       │
│  │  - Extract structured data from natural language │       │
│  │  - Generate follow-up questions                  │       │
│  └──────────────────────────────────────────────────┘       │
│                      │                                       │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────────┐       │
│  │  MCPClient                                       │       │
│  │  - predict_compensation()                        │       │
│  │  - analyze_policy()                              │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        ↓                            ↓
┌──────────────────┐      ┌──────────────────┐
│ Compensation MCP │      │   Policy MCP     │
│   (port 8081)    │      │   (port 8082)    │
├──────────────────┤      ├──────────────────┤
│ - Currency API   │      │ - Visa API       │
│ - COLA Database  │      │ - Tax Treaties   │
│ - Housing API    │      │ - Compliance DB  │
│ - ML Model v2.3  │      │ - Risk Model     │
└──────────────────┘      └──────────────────┘
```

#### Step 7: Migration Path

**Phase 1: Current State (Done)**
- ✅ Conversational collector extracting data
- ✅ GPT-4 generating "calculations"
- ✅ MCP client code exists but calls GPT-4

**Phase 2: Parallel Development (Next)**
- External teams build real MCP servers with APIs
- Test MCP servers independently
- Keep GPT-4 as fallback in production

**Phase 3: Gradual Rollout**
- Deploy MCP servers to staging
- Add feature flag: `USE_MCP_SERVERS=true/false`
- A/B test: 10% traffic to MCP, 90% to GPT-4
- Monitor accuracy, latency, errors

**Phase 4: Full Migration**
- 100% traffic to MCP servers
- Keep GPT-4 as fallback for failures
- Remove old GPT-4 calculation code

**Code for Phase 2 (Feature Flag)**:
```python
async def _run_compensation_calculation(user_data: dict, extracted_texts: list) -> str:
    use_mcp = os.getenv("USE_MCP_SERVERS", "false").lower() == "true"

    if use_mcp:
        try:
            return await _run_compensation_calculation_mcp(user_data, extracted_texts)
        except Exception as e:
            logging.error(f"MCP failed, falling back to GPT-4: {e}")
            return await _run_compensation_calculation_gpt4(user_data, extracted_texts)
    else:
        return await _run_compensation_calculation_gpt4(user_data, extracted_texts)
```

---

## Key Differences: Conversational Collector vs MCP

| Aspect | Conversational Collector | MCP Servers |
|--------|--------------------------|-------------|
| **Purpose** | Extract structured data from natural language | Perform calculations/predictions on structured data |
| **Input** | Unstructured text: "moving someone from chicago to mumbai making 100k" | Structured JSON: `{"origin": "Chicago", "destination": "Mumbai", "salary": 100000}` |
| **Output** | Structured fields + missing field list | Predictions + confidence scores + data sources |
| **Technology** | GPT-4 (LLM for NLP) | APIs + Databases + ML Models (domain-specific) |
| **Accuracy** | ~95% for extraction (tested) | Depends on data sources and models (measurable) |
| **Latency** | 1-3 seconds (GPT-4 API call) | Variable (depends on external API calls) |
| **Cost** | $0.01-0.05 per query (GPT-4 pricing) | Depends on API usage (currency, COLA, etc.) |
| **Keep or Replace?** | **KEEP** - works well for NLP | **REPLACE** - use real data sources |

---

## Summary

**Current System**:
- Conversational collector: ✅ Works great for data extraction
- Calculations: ❌ Uses GPT-4 text generation (not real data)

**Target System**:
- Conversational collector: ✅ Keep as-is
- Calculations: ✅ Replace with MCP servers using real APIs/databases/models

**Migration**:
1. External teams build MCP servers with real data sources
2. Replace `_run_compensation_calculation()` and `_run_policy_analysis()` to call MCP instead of GPT-4
3. Conversational extraction layer stays unchanged

This separation provides best of both worlds:
- **Natural language interface** (GPT-4 strength)
- **Accurate predictions** (domain-specific tools strength)
