# Global IQ Mobility Advisor - Authentication

## Login Credentials

The application now supports user authentication with role-based access control. Use the following credentials to test different user roles:

### 🔧 Administrator
- **Username:** `admin`
- **Password:** `admin123`
- **Features:** Full system access, user management, admin commands
- **Special Commands:** `/users`, `/help`

### 👥 HR Manager
- **Username:** `hr_manager`
- **Password:** `hr2024`
- **Features:** Policy information, compensation analysis, employee data access
- **Focus:** Policy compliance, cost management, detailed analysis

### 👤 Employee
- **Username:** `employee`
- **Password:** `employee123`
- **Features:** Personal relocation assistance, policy guidance
- **Focus:** Practical guidance, easy-to-understand explanations

### 🎯 Demo User
- **Username:** `demo`
- **Password:** `demo`
- **Features:** Full feature exploration with examples
- **Focus:** System demonstration, comprehensive examples

## Features by Role

### All Users
- Policy information and guidance
- Compensation analysis and calculations
- Document upload and analysis (PDF, DOCX, XLSX, CSV, JSON, TXT)
- Enhanced agent routing (Policy vs Compensation)
- Personalized welcome messages

### Admin Only
- User management commands
- System analytics access
- Technical information and insights
- Administrative recommendations

### HR Manager
- Detailed policy compliance information
- Employee welfare focus
- Cost management insights
- Comprehensive compensation analysis

### Employee
- Personal relocation guidance
- Simplified policy explanations
- Practical impact focus
- User-friendly interface

### Demo User
- Feature exploration
- Comprehensive examples
- System capability highlights
- Educational content

## Security Notes

- Passwords are hashed using SHA-256
- User sessions are managed by Chainlit
- Role-based access control implemented
- In production, replace with proper database and stronger authentication

## Next Steps

- Multi-chat functionality (conversation history)
- Data persistence for user preferences
- OAuth integration (Google, GitHub)
- Enhanced user management features
