# 🔐 Authentication Module

## 📋 Overview

The Auth module handles **secure authentication and authorization** for the ERP system. It provides JWT-based token authentication with role-based access control (RBAC), ensuring only authorized users can access protected resources.

---

## ✨ Key Features

### 🛡️ Security Features
- **JWT Token-based Authentication** - Secure, stateless authentication
- **Password Hashing** - Bcrypt encryption for password security
- **Token Expiration** - Configurable token lifetime (default: 30 minutes)
- **Role-Based Access Control (RBAC)** - HR, Admin, Employee roles
- **Email Domain Validation** - Whitelist-based domain verification

### 🔑 Password Security
- **Minimum 8 characters, Maximum 30 characters**
- **Must contain:**
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 number (0-9)
  - At least 1 special character (!@#$%^&*(),.?\":{}|<>)

### ✅ Email Domain Whitelist
```
sunfocus.com | erp.com | gmail.com | outlook.com | yahoo.com | hotmail.com | test.com
```

---

## 🏗️ Architecture

### Technology Stack
- **FastAPI** - Web framework
- **JWT (Jose)** - Token generation & validation
- **Bcrypt** - Password hashing
- **Pydantic** - Data validation
- **MongoDB** - User data storage

### Module Structure
```
Auth/
├── router.py          # API endpoints
├── schemas.py         # Pydantic models & validation
├── helper.py          # Authentication logic
├── utils.py           # Token & password utilities
└── README.md          # This file
```

---

## 🔄 Authentication Flow

### 1️⃣ **Login Process**
```
User sends credentials → Validate email domain → Check password strength 
→ Verify user in DB → Verify password hash → Generate JWT token 
→ Return token with role
```

### 2️⃣ **Protected Route Access**
```
User sends request with token → Extract token from header 
→ Decode & validate token → Fetch user from DB → Attach role to user 
→ Grant access
```

---

## 🚀 API Endpoints

### 1. **POST** `/auth/login`
**Login user and receive JWT token**

**Request Body:**
```json
{
  "email": "user@sunfocus.com",
  "password": "SecurePass@123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "HR"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid email or password
- `422 Validation Error` - Email domain not allowed or weak password

---

### 2. **POST** `/auth/create_hr_once`
**One-time HR account creation (Admin only)**

⚠️ **Security Note:** This route is disabled after first HR is created.

**Request Body:**
```json
{
  "email": "hr@sunfocus.com",
  "password": "HRSecure@2025"
}
```

**Success Response (200):**
```json
{
  "msg": "HR account created successfully"
}
```

**Error Response:**
- `400 Bad Request` - HR already exists

---

### 3. **GET** `/auth/me`
**Get current authenticated user details**

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Success Response (200):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "user@sunfocus.com",
  "role": "HR",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token
- `401 Unauthorized` - User not found

---

## 🔐 Security Implementation

### Password Hashing (Bcrypt)
```python
# Hash password during registration
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify password during login
bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### JWT Token Structure
```json
{
  "sub": "user@sunfocus.com",    // User email (subject)
  "role": "HR",                   // User role
  "exp": 1737540000               // Expiration timestamp
}
```

### Token Generation
```python
# Create token with 30-minute expiry
token = create_access_token(
    data={"sub": email, "role": role},
    expires_delta=timedelta(minutes=30)
)
```

---

## 🎯 Role-Based Access Control (RBAC)

### Available Roles
| Role | Access Level | Permissions |
|------|-------------|-------------|
| **HR** | Full Admin | Manage employees, departments, leave requests |
| **Admin** | System Admin | System configuration, user management |
| **Employee** | Standard User | View own data, submit requests |

### Middleware Protection
```python
from fastapi import Depends
from .helper import get_current_user

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    # Only authenticated users can access
    return current_user
```

---

## 📝 Data Models (Pydantic Schemas)

### UserLogin
```python
class UserLogin(BaseModel):
    email: EmailStr          # Validated email with domain check
    password: str            # Password with strength validation
```

### Token Response
```python
class Token(BaseModel):
    access_token: str        # JWT token
    token_type: str          # Always "bearer"
    role: str | None         # User role (HR/Admin/Employee)
```

### Email & Password Validation
```python
class EmailPasswordValidator(BaseModel):
    email: EmailStr          # Auto-validates email format
    password: str            # Must meet complexity requirements
    
    # Custom validators check:
    # - Email domain whitelist
    # - Password length (8-30 chars)
    # - Password complexity (uppercase, lowercase, number, special char)
```

---

## 🛠️ Utility Functions

### `utils.py` Functions

| Function | Purpose |
|----------|---------|
| `hash_password(password)` | Hash plain password using bcrypt |
| `verify_password(plain, hashed)` | Verify password against hash |
| `create_access_token(data, expires_delta)` | Generate JWT token |
| `decode_access_token(token)` | Decode and validate JWT |
| `get_user_by_email(email)` | Fetch user from MongoDB |

### `helper.py` Functions

| Function | Purpose |
|----------|---------|
| `authenticate_user(email, password)` | Verify user credentials |
| `get_current_user(authorization)`    | Middleware for token validation |

---

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-super-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ **Security Warning:** Never commit `.env` file to version control!

---

## 🧪 Testing

### Manual Testing with cURL

**1. Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@sunfocus.com",
    "password": "SecurePass@123"
  }'
```

**2. Access Protected Route:**
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Expected Behaviors

✅ **Valid Login:**
- Returns token with 200 status
- Token expires after configured time

❌ **Invalid Email Domain:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Email domain 'invalid.com' is not allowed",
      "type": "value_error"
    }
  ]
}
```

❌ **Weak Password:**
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

❌ **Invalid Token:**
```json
{
  "detail": "Invalid or expired token"
}
```

---

## 🔒 Security Best Practices

### ✅ Implemented
- ✔️ **Password hashing** with bcrypt (salt rounds: auto)
- ✔️ **JWT tokens** with expiration
- ✔️ **Email domain whitelisting**
- ✔️ **Password complexity requirements**
- ✔️ **Token validation** on every protected request
- ✔️ **Role-based authorization**

## 📚 Dependencies

### Required Packages
```txt
fastapi>=0.104.0
python-jose[cryptography]>=3.3.0
bcrypt>=4.0.1
passlib>=1.7.4
pydantic[email]>=2.0.0
python-dotenv>=1.0.0
pymongo>=4.5.0
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔗 Integration with Other Modules

### Database Connection
```python
from app.database import get_db

# Auth module uses "employee_db" collection
db = get_db()
users = db["employee_db"]
```

### Usage in Other Modules
```python
from app.Auth.helper import get_current_user
from fastapi import Depends

@router.get("/hr/dashboard")
def hr_dashboard(current_user: dict = Depends(get_current_user)):
    # Verify HR role
    if current_user["role"] != "HR":
        raise HTTPException(status_code=403, detail="HR access required")
    return {"msg": "HR Dashboard"}
```

---

## 🎓 Code Examples

### Complete Login Flow
```python
# 1. User submits credentials
credentials = UserLogin(
    email="hr@sunfocus.com",
    password="HRSecure@2025"
)

# 2. Authenticate user
user = authenticate_user(credentials.email, credentials.password)

# 3. Generate token
token = create_access_token(
    data={"sub": user["email"], "role": user["role"]},
    expires_delta=timedelta(minutes=30)
)

# 4. Return token to user
return {
    "access_token": token,
    "token_type": "bearer",
    "role": user["role"]
}
```

### Protected Route with Role Check
```python
@router.get("/admin-only")
def admin_route(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["Admin", "HR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return {"msg": "Welcome Admin!"}
```

---