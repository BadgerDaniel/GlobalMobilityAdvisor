# Conversational Intake Implementation Guide

## 🎯 Goal

Replace rigid sequential questionnaires with intelligent conversational intake where:
1. User describes their situation naturally
2. LLM extracts information and identifies what's missing
3. LLM asks targeted follow-up questions
4. Process continues until all required data is collected

---

## 📋 Current vs New Flow

### **Current Flow (Rigid):**
```
Bot: "Question 1: What is your current location?"
User: "Chicago"
Bot: "Question 2: What is your destination?"
User: "Mumbai"
Bot: "Question 3: What is your current salary?"
User: "100k"
... (4 more questions)
```

### **New Flow (Conversational):**
```
Bot: "Tell me about your relocation situation"
User: "I'm making 100k in Chicago and thinking about moving to Mumbai for 2 years"

Bot: "Great! I've captured:
     ✓ Origin: Chicago, USA
     ✓ Destination: Mumbai, India
     ✓ Current Salary: $100,000
     ✓ Duration: 2 years

     Just a few more details:
     - Will family be relocating with you?
     - What's your role/position?
     - Any housing preferences?"

User: "I'm a senior engineer, family of 3, company housing"

Bot: "Perfect! Here's everything:
     ✓ Origin: Chicago, USA
     ✓ Destination: Mumbai, India
     ✓ Salary: $100,000
     ✓ Duration: 2 years
     ✓ Role: Senior Engineer
     ✓ Family Size: 3
     ✓ Housing: Company-provided

     Is this correct? (yes/no)"
```

---

## 🏗️ Architecture

### **Files Created:**
1. **`app/conversational_collector.py`** ✅
   - `Conversational Collector` class
   - `start_conversation()` - Initial prompt
   - `extract_information()` - LLM extracts data from natural language
   - `generate_follow_up()` - Creates smart follow-up questions
   - `is_complete()` - Checks if all required fields collected
   - `format_for_mcp()` - Formats data for MCP servers

### **Files to Modify:**
2. **`app/main.py`**
   - Import `ConversationalCollector`
   - Initialize it
   - Replace sequential input collection with conversational flow

---

## 🔧 Implementation Steps

### **Step 1: Initialize Conversational Collector** ✅ DONE

```python
# In app/main.py after line 84
conversational_collector = ConversationalCollector(openai_client=client)
```

### **Step 2: Modify Route Handling**

Replace the confirmation/sequential flow with conversational flow:

**Current code (around line 615):**
```python
if route_name == "compensation":
    # Show confirmation message before starting collection
    conf_message = input_collector.get_confirmation_message("compensation")
    await cl.Message(content=conf_message).send()
    user_session["awaiting_compensation_confirmation"] = True
    cl.user_session.set("user_data", user_session)
```

**New code:**
```python
if route_name == "compensation":
    # Start conversational intake
    intro_msg = await conversational_collector.start_conversation("compensation")
    await cl.Message(content=intro_msg).send()

    # Mark that we're in conversational collection mode
    user_session["conversational_mode"] = True
    user_session["current_route"] = "compensation"
    user_session["collected_data"] = {}
    user_session["conversation_history"] = []
    cl.user_session.set("user_data", user_session)
```

### **Step 3: Handle Conversational Responses**

Add new handler before sequential collection handlers (around line 486):

```python
# Check if we're in conversational mode
in_conversational_mode = user_session.get("conversational_mode", False)

if in_conversational_mode:
    current_route = user_session.get("current_route")
    collected_data = user_session.get("collected_data", {})
    conversation_history = user_session.get("conversation_history", [])

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_query})

    # Check if user is confirming final data
    if user_query.lower().strip() in ['yes', 'correct', 'looks good', 'confirmed']:
        # All data confirmed - proceed to calculation
        if current_route == "compensation":
            calc_response = await _run_compensation_calculation(collected_data, extracted_texts)
            await cl.Message(content=calc_response).send()
        elif current_route == "policy":
            policy_response = await _run_policy_analysis(collected_data, extracted_texts)
            await cl.Message(content=policy_response).send()

        # Reset conversational mode
        user_session["conversational_mode"] = False
        cl.user_session.set("user_data", user_session)
        return

    # Extract information from user's message
    extraction = await conversational_collector.extract_information(
        current_route,
        user_query,
        conversation_history
    )

    # Update collected data with extracted fields
    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    # Check if all required data is collected
    if conversational_collector.is_complete(collected_data, current_route):
        # Generate confirmation message
        confirmation = await conversational_collector._generate_confirmation_message(
            current_route,
            collected_data
        )
        await cl.Message(content=confirmation).send()
    else:
        # Generate follow-up questions for missing fields
        follow_up = await conversational_collector.generate_follow_up(
            current_route,
            collected_data,
            extraction["missing_fields"]
        )
        await cl.Message(content=follow_up).send()

        # Add bot message to history
        conversation_history.append({"role": "assistant", "content": follow_up})

    # Update session
    user_session["collected_data"] = collected_data
    user_session["conversation_history"] = conversation_history
    cl.user_session.set("user_data", user_session)
    return
```

---

## 💡 How It Works

### **1. User Describes Situation**
```
User: "I'm making 100k in Chicago and want to move to Mumbai"
```

### **2. LLM Extracts Information**
The `extract_information()` function sends this prompt to GPT-4:
```
Extract these fields from the user's message:
- Origin Location
- Destination Location
- Current Compensation
- Assignment Duration
- Job Level/Title
- Family Size
- Housing Preference

User said: "I'm making 100k in Chicago and want to move to Mumbai"

Return JSON with:
- extracted_fields: {field: value or null}
- confidence: {field: 0-1 score}
- missing_fields: [list of missing fields]
```

**GPT-4 Returns:**
```json
{
  "extracted_fields": {
    "Origin Location": "Chicago, USA",
    "Destination Location": "Mumbai, India",
    "Current Compensation": "$100,000",
    "Assignment Duration": null,
    "Job Level/Title": null,
    "Family Size": null,
    "Housing Preference": null
  },
  "confidence": {
    "Origin Location": 0.95,
    "Destination Location": 0.95,
    "Current Compensation": 0.90
  },
  "missing_fields": ["Assignment Duration", "Job Level/Title", "Family Size", "Housing Preference"]
}
```

### **3. Generate Follow-Up**
The `generate_follow_up()` function creates a natural message:
```
Great! I've captured:
✓ Origin: Chicago, USA
✓ Destination: Mumbai, India
✓ Current Salary: $100,000

To complete the analysis, I need a few more details:
- How long will the assignment be?
- What's your role or position?
- Will family be relocating with you?
- Any preferences for housing?
```

### **4. Repeat Until Complete**
User answers → Extract → Follow-up → Until all fields collected → Confirmation

---

## 🧪 Testing Scenarios

### **Scenario 1: Full Details in First Message**
```
User: "I'm a Senior Engineer making $120k in New York moving to London for 18 months with my family of 4, prefer company housing"

Bot extracts ALL fields → Shows confirmation immediately
```

### **Scenario 2: Partial Details**
```
User: "Moving from Chicago to Mumbai"

Bot: "I've captured origin and destination. What else can you tell me about the move?"

User: "100k salary, 2 years, senior engineer"

Bot: "Great! Just need to know about family and housing preferences"

User: "Family of 3, company housing"

Bot: "Perfect! Here's everything I have: ..." (confirmation)
```

### **Scenario 3: Corrections**
```
Bot: "Is this correct? Origin: Chicago..."

User: "No, it's San Francisco not Chicago"

Bot extracts correction → Updates data → Shows new confirmation
```

---

## 📦 Benefits

### **User Experience:**
- ✅ Natural conversation (not rigid Q&A)
- ✅ Can provide all info at once
- ✅ Can provide info gradually
- ✅ Fewer total messages needed
- ✅ More flexible and forgiving

### **Technical:**
- ✅ LLM handles parsing and inference
- ✅ Smart about context (knows "Chicago" = "Chicago, USA")
- ✅ Handles various formats ("100k", "$100,000", "100000 USD")
- ✅ Can correct/update extracted data
- ✅ Easy to add new fields

---

## 🚀 Next Steps

1. **Add initialization in main.py** ← Currently here
2. **Replace route handling** with conversational flow
3. **Add conversational mode handler**
4. **Test with various input patterns**
5. **Fine-tune prompts based on results**

---

## 📝 Notes

- The conversational collector is **independent** of the old sequential collector
- You can keep both and let users choose (or use conversational by default)
- The collected data format is **the same** - works with existing calculation functions
- Works with both compensation and policy routes
- Can be extended to other routes easily

---

## ✅ Current Status

- ✅ `conversational_collector.py` created
- ✅ Import added to `main.py`
- ⏳ Need to add initialization
- ⏳ Need to modify route handlers
- ⏳ Need to add conversational mode handler
- ⏳ Need to test

**Ready to implement the next steps!** 🚀
