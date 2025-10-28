# User Credentials & Roles

The application supports role-based access control with different capabilities for each user type.

---

## Login Credentials

### 🔧 Administrator
- **Username:** `admin`
- **Password:** `admin123`

**Capabilities:**
- Full system access
- User management
- Special commands: `/users`, `/help`, `/health`, `/history`
- System analytics and monitoring
- Technical insights

### 👥 HR Manager
- **Username:** `hr_manager`
- **Password:** `hr2024`

**Capabilities:**
- Policy information and analysis
- Compensation calculations
- Employee data access
- Cost management insights
- Detailed policy compliance information

### 👤 Employee
- **Username:** `employee`
- **Password:** `employee123`

**Capabilities:**
- Personal relocation guidance
- Simplified policy explanations
- Compensation estimates
- Document uploads
- Practical impact focus

### 🎯 Demo User
- **Username:** `demo`
- **Password:** `demo`

**Capabilities:**
- Full feature exploration
- System demonstration mode
- Comprehensive examples
- Educational content

---

## Features by Role

### All Users Can:
- Ask policy questions (visa requirements, compliance)
- Request compensation calculations
- Upload documents (PDF, DOCX, XLSX, CSV, JSON, TXT)
- Get personalized responses based on role
- View chat history during session

### Admin Only:
- `/users` - View all registered users
- `/help` - View admin help
- `/health` - Check MCP server health and statistics
- `/history` - View session chat history
- Access to system analytics

### HR Manager Focus:
- Detailed policy compliance information
- Employee welfare considerations
- Cost management and budget analysis
- Comprehensive compensation breakdowns

### Employee Focus:
- User-friendly explanations
- Practical guidance
- Personal impact analysis
- Step-by-step instructions

---

## Admin Commands

Only available to users with `admin` role:

### `/users`
Lists all registered users with their roles.

**Example output:**
```
Registered Users:
1. admin (admin) - admin@globaliq.com
2. hr_manager (hr_manager) - hr@globaliq.com
3. employee (employee) - employee@globaliq.com
4. demo (demo) - demo@globaliq.com
```

### `/health`
Shows MCP server health status and usage statistics.

**Example output:**
```
MCP Service Status

MCP Integration: Enabled
Compensation Server: ✅ Healthy
Policy Server: ✅ Healthy

Usage Statistics:
- MCP Calls: 45
- Fallback Calls: 3
- Errors: 0
```

### `/help`
Shows admin-specific help and available commands.

### `/history`
Displays the current session's chat history.

---

## Security Notes

**Authentication:**
- Passwords are hashed using SHA-256
- User sessions managed by Chainlit
- Role-based access control (RBAC) implemented

**For Production:**
- Replace hardcoded users with database
- Use stronger authentication (OAuth, SAML)
- Implement password complexity requirements
- Add rate limiting
- Enable audit logging

---

## Adding New Users

Currently, users are defined in `app/main.py` (lines 26-51):

```python
USERS_DB = {
    "username": {
        "password_hash": hashlib.sha256("password".encode()).hexdigest(),
        "role": "employee",
        "name": "Display Name",
        "email": "email@example.com"
    }
}
```

**To add a user:**
1. Open `app/main.py`
2. Add entry to `USERS_DB` dictionary
3. Hash password: `hashlib.sha256("password".encode()).hexdigest()`
4. Restart application

**Future Enhancement:** Move to database-backed user management.

---

## Role Comparison

| Feature | Employee | HR Manager | Admin | Demo |
|---------|----------|------------|-------|------|
| Policy Questions | ✅ | ✅ | ✅ | ✅ |
| Compensation Calc | ✅ | ✅ | ✅ | ✅ |
| Document Upload | ✅ | ✅ | ✅ | ✅ |
| Detailed Analysis | ❌ | ✅ | ✅ | ✅ |
| Admin Commands | ❌ | ❌ | ✅ | ❌ |
| User Management | ❌ | ❌ | ✅ | ❌ |
| System Monitoring | ❌ | ❌ | ✅ | ❌ |

---

## Testing Different Roles

To see how responses differ by role:

1. **Login as Employee**
   - Ask: "What visa do I need for UK?"
   - Notice: Simplified, practical explanation

2. **Login as HR Manager**
   - Ask: "What visa do I need for UK?"
   - Notice: Detailed compliance info, cost considerations

3. **Login as Admin**
   - Ask: "What visa do I need for UK?"
   - Use `/health` to check system status
   - Use `/users` to see all users

---

For more information, see:
- [Quick Start Guide](README.md)
- [Installation Guide](INSTALLATION.md)
- [Architecture Overview](../architecture/README.md)
