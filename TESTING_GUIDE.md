# 🧪 Testing Guide - MCP Integration

## ✅ All Services Running!

- ✅ **Compensation Server** (8081) - Healthy
- ✅ **Policy Server** (8082) - Healthy
- ✅ **Chainlit App** (8000) - Running

---

## 🚀 **How to Test**

### **Step 1: Open the Application**

Open your browser and go to:
```
http://localhost:8000
```

### **Step 2: Login**

Use these credentials:
- **Username:** `demo`
- **Password:** `demo`

---

## 🧪 **Test Case 1: Compensation Calculation**

### **Query to Test:**
```
calculate salary for someone making 100k in chicago moving to mumbai
```

### **Expected Behavior:**

1. **Routing:**
   - Should show: **"💰 Routed to: Compensation Expert"**
   - ✅ Should NOT route to "Guidance Fallback"

2. **Questions Asked (Sequential):**
   - Question 1: "What is the employee's current location?"
   - Question 2: "Where will the employee be relocating to?"
   - Question 3: "What is the employee's current annual salary?"
   - Question 4: "What is the expected duration of the assignment?"
   - Question 5: "What is the employee's job level or title?"
   - Question 6: "How many family members will be relocating?"
   - Question 7: "What is the employee's housing preference?"

3. **Sample Answers:**
   - Current Location: `Chicago, USA`
   - Destination: `Mumbai, India`
   - Current Salary: `100,000 USD`
   - Duration: `24 months`
   - Job Level: `Senior Engineer`
   - Family Size: `2`
   - Housing: `Company-provided`

4. **Confirmation:**
   - Shows summary of all answers
   - Asks: "Is this information correct? (yes/no)"
   - Type: `yes`

5. **Final Output:**
   - Shows: **"💰 Compensation Calculation Results"**
   - Includes:
     - Summary (Origin, Destination, Current Salary)
     - Base Salary
     - COLA Ratio
     - Adjusted Salary
     - Housing Allowance
     - Hardship Pay
     - **Total Package**
     - Confidence Scores (COLA, Housing, Overall)
     - Recommendations
     - Methodology: `openai_gpt4o (v2.0.0)`

---

## 🧪 **Test Case 2: Policy Analysis**

### **Query to Test:**
```
what visa requirements do I need to move to UK from USA
```

### **Expected Behavior:**

1. **Routing:**
   - Should show: **"📋 Routed to: Policy Specialist"**

2. **Questions Asked:**
   - Origin country
   - Destination country
   - Assignment type
   - Duration
   - Job title

3. **Sample Answers:**
   - Origin: `USA`
   - Destination: `United Kingdom`
   - Type: `Long-term`
   - Duration: `24 months`
   - Job Title: `Manager`

4. **Final Output:**
   - Shows: **"📋 Policy Analysis Results"**
   - Includes:
     - Visa Requirements (Type, Processing Time, Cost)
     - Eligibility
     - Timeline
     - Required Documentation
     - Compliance Considerations
     - Recommendations
     - Confidence Score
     - Data Source: `openai_gpt4o`

---

## 🧪 **Test Case 3: Both Routes**

### **Query to Test:**
```
what's the cheapest way to relocate a manager to london
```

### **Expected Behavior:**

1. **Routing:**
   - Should show: **"🎯 Routed to: Strategic Advisor"**
   - Should ask if you want compensation, policy, or both

---

## 🧪 **Test Case 4: Fallback**

### **Query to Test:**
```
what can you do?
```

### **Expected Behavior:**

1. **Routing:**
   - Should show: **"🤝 Routed to: General Assistant"**
   - Provides guidance on system capabilities

---

## 🔍 **What to Look For**

### ✅ **Success Indicators:**

1. **Routing Works:**
   - "calculate salary" → Routes to Compensation ✅
   - "visa requirements" → Routes to Policy ✅
   - "cheapest way" → Routes to Both/Strategic ✅

2. **MCP Integration Working:**
   - Results show **Methodology: openai_gpt4o (v2.0.0)**
   - Results include **Confidence Scores**
   - Results are **structured and formatted** (not raw text)

3. **Server Communication:**
   - No error messages about "connection refused"
   - No "MCP server not running" warnings
   - Responses appear within 5-10 seconds

### ❌ **Failure Indicators:**

1. **Routing Issues:**
   - Routes to "Guidance Fallback" for compensation queries
   - Shows "I'm here to help" instead of asking questions

2. **MCP Connection Issues:**
   - Error: "Connection refused to MCP servers"
   - Error: "MCP compensation service error"
   - Shows old methodology (not `openai_gpt4o`)

3. **OpenAI Issues:**
   - Error: "OpenAI API key not set"
   - Error: "Rate limit exceeded"
   - JSON parse errors

---

## 🐛 **If Something Goes Wrong**

### **Check Server Status:**
```bash
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### **Check Logs:**
- Look at the terminal windows where servers are running
- Check for OpenAI API errors
- Check for JSON parsing errors

### **Restart Services:**
```bash
# Kill servers
# Then restart:
cd Global-IQ/Global-iq-application
python services/mcp_prediction_server/compensation_server.py  # Terminal 1
python services/mcp_prediction_server/policy_server.py        # Terminal 2
chainlit run app/main.py                                       # Terminal 3
```

---

## 📊 **Expected vs Previous Behavior**

| Aspect | Previous (Direct OpenAI) | New (MCP) |
|--------|-------------------------|-----------|
| **Routing** | Sometimes went to Fallback | Routes correctly ✅ |
| **Output** | Plain text | Structured with scores ✅ |
| **Methodology** | Not shown | `openai_gpt4o v2.0.0` ✅ |
| **Confidence** | Not shown | COLA: 85%, Overall: 82% ✅ |
| **Format** | Inconsistent | Predictable structure ✅ |

---

## ✅ **Test Checklist**

- [ ] Open http://localhost:8000
- [ ] Login with demo/demo
- [ ] Test compensation query
- [ ] Verify routing to "Compensation Expert"
- [ ] Answer all questions
- [ ] Check results show methodology and confidence
- [ ] Test policy query
- [ ] Verify structured policy output
- [ ] Test "both" route query
- [ ] Test fallback query
- [ ] Verify no MCP connection errors

---

## 🎉 **Success Criteria**

Your integration is working if:
1. ✅ Queries route to correct specialists (not Fallback)
2. ✅ MCP servers respond (no connection errors)
3. ✅ Results show `openai_gpt4o` methodology
4. ✅ Confidence scores are displayed
5. ✅ Output is structured and formatted

---

**Ready to test! Open http://localhost:8000 and try the test cases above!** 🚀
