# 🏢 ERP System - Enterprise Resource Planning

![License](https://img.shields.io/badge/license-MIT-green)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

## Project Overview

A comprehensive **Employee Resource Planning (ERP) system** built with FastAPI and MongoDB. This system manages employee lifecycle, attendance tracking, leave management, and role-based access control for HR, Managers, and Employees.

---

## ✨ Key Features

### 🔐 **Authentication & Authorization**
- JWT-based token authentication
- Role-based access control (HR, Manager, Employee)
- Secure password hashing with bcrypt
- Separate login endpoints for different roles

### 👥 **Employee Management**
- Complete CRUD operations for employee records
- Comprehensive profile management (personal info, addresses, education, work experience)
- Advanced search functionality
- Employee activation/deactivation (soft delete)

### 📊 **Attendance System**
- Daily attendance marking with multiple status types
- Real-time attendance dashboard
- Historical attendance records with date filtering
- Email-based or ID-based attendance marking

### 🏖️ **Leave Management**
- Automated leave balance initialization
- Manager-based approval workflow
- Leave type support (Annual, Sick, Personal, Emergency)
- Auto-deduction of leave balance on approval
- Employee self-service for leave requests

### 🎯 **Self-Service Portal**
- Employees can view and update their profiles
- View personal attendance records
- Apply for leaves and track status
- Cancel pending leave requests

---

## 🏗️ System Architecture

### Technology Stack

**Backend:**
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **PyMongo** - MongoDB driver
- **Pydantic** - Data validation
- **JWT (jose)** - Token authentication
- **Bcrypt** - Password hashing

**Key Libraries:**
- `fastapi` - REST API framework
- `pymongo` - MongoDB operations
- `python-jose` - JWT handling
- `bcrypt` / `passlib` - Password security
- `pydantic` - Schema validation
- `python-dotenv` - Environment management

---

## 📁 Project Structure

```
ERP_PYTHON_B.../
├── app/
│   ├── Auth/                    # Authentication & Authorization
│   │   ├── router.py
│   │   ├── helper.py
│   │   ├── utils.py
│   │   ├── schemas.py
│   │   └── README.md
│   │
│   ├── HR/                      # HR Management
│   │   ├── router.py            # HR endpoints
│   │   ├── manager_router.py   # Manager endpoints
│   │   ├── crud.py
│   │   ├── helper.py
│   │   ├── schemas.py
│   │   └── README.md
│   │
│   ├── Employees/               # Employee Self-Service
│   │   ├── router.py
│   │   ├── crud.py
│   │   ├── schemas.py
│   │   └── README.md
│   │
│   ├── common/                  # Shared Utilities
│   │   ├── utils.py
│   │   └── README.md
│   │
│   ├── database.py              # MongoDB connection
│   ├── __init__.py
│   └── app.py
│
├── .env                         # Environment variables
├── .gitignore
├── requirements.txt
├── main.py
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- MongoDB 4.4+
- pip (Python package manager)

### Installation

**1. Clone the repository**
```bash
git clone <repository-url>
cd ERP_PYTHON_B...
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
# Create .env file in root directory
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=erp_system
```

**5. Run the application**
```bash
uvicorn main:app --reload
```

**6. Access the API**
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 Module Documentation

### 🔐 [Auth Module](./app/Auth/README.md)
**Authentication & Authorization System**
- JWT token-based authentication
- Role-based access control (RBAC)
- Password security (bcrypt hashing)
- Token generation and validation
- User authentication middleware

**Key Endpoints:**
- `POST /auth/login` - User login
- `POST /auth/create_hr_once` - Create HR account (one-time)
- `GET /auth/me` - Get current user details

---

### 👔 [HR Module](./app/HR/README.md)
**Human Resources Management**
- Complete employee lifecycle management
- Attendance tracking and reporting
- Leave request oversight
- Employee CRUD operations
- Advanced search and filtering

**Key Endpoints:**
- Employee Management: Register, update, search, activate/deactivate
- Attendance: Mark, view, update attendance records
- Leave Management: View all leave requests (Pending, Approved, Rejected)

---

### 👨‍💼 [Manager Module](./app/HR/manager_router.py)
**Team Leave Management**
- View team's pending leave requests
- Approve or reject leave requests
- View team's leave history
- Manager-specific authorization

**Key Endpoints:**
- `GET /hr/manager/leaves/pending` - View team's pending leaves
- `PUT /hr/manager/leave/{id}/approve` - Approve/reject leave
- `GET /hr/manager/leaves` - View all team leaves

---

### 👥 [Employee Module](./app/Employees/README.md)
**Employee Self-Service Portal**
- View and update personal profile
- View personal attendance records
- Apply for leaves with balance validation
- View leave status and history
- Cancel pending leave requests

**Key Endpoints:**
- `POST /employee/employee_login` - Employee login
- `GET /employee/profile` - View own profile
- `PUT /employee/profile/personal_info` - Update personal info
- `GET /employee/attendance` - View own attendance
- `POST /employee/leave-request` - Apply for leave
- `GET /employee/leaves` - View own leaves
- `DELETE /employee/leave/{id}` - Cancel pending leave

---

### 🔧 [Common Module](./app/common/README.md)
**Shared Utilities**
- Data serialization (MongoDB to JSON)
- Leave document enrichment
- Date/datetime conversions
- Cross-module helper functions

**Key Functions:**
- `serialize_leave()` - Convert leave docs to JSON-safe format with names
- `date_to_datetime()` - Convert date to datetime
- `get_leave_request_by_id()` - Fetch single leave with full details

---

## 🗄️ Database Schema

### Collections

**employee_db**
- Employee personal information
- Job details and salary
- Education and work experience
- Leave balance tracking
- Status (active/inactive)

**attendance_db**
- Daily attendance records
- Check-in/check-out times
- Attendance status (Present, Absent, Leave, Half-Day)

**leave_db**
- Leave requests
- Leave type and duration
- Approval status and history
- Manager assignment

---

## 🔑 User Roles & Permissions

### HR (Full Access)
- ✅ Manage all employees
- ✅ Mark and view all attendance
- ✅ View all leave requests
- ❌ Cannot approve/reject leaves (Manager only)

### Manager (Team Management)
- ✅ View team's leave requests
- ✅ Approve/reject team leaves
- ✅ View own profile and attendance
- ✅ Apply for own leaves
- ❌ Cannot manage employees or attendance

### Employee (Self-Service)
- ✅ View and update own profile
- ✅ View own attendance
- ✅ Apply for leaves
- ✅ Cancel pending leaves
- ❌ Cannot view others' data
- ❌ Cannot mark attendance

---

## 🔄 Key Workflows

### Employee Onboarding
1. HR creates employee account via `/hr/register_employee`
2. System auto-initializes leave balance (Annual: 12, Sick: 6, Personal: 3, Emergency: 2)
3. Employee receives login credentials
4. Employee logs in via `/employee/employee_login`
5. Employee views profile and updates personal info

### Leave Request Process
1. Employee applies for leave via `/employee/leave-request`
2. System validates leave balance availability
3. Leave auto-routed to assigned manager
4. Manager views pending leaves via `/hr/manager/leaves/pending`
5. Manager approves/rejects via `/hr/manager/leave/{id}/approve`
6. On approval, leave balance auto-deducted
7. Employee notified of status change

### Daily Attendance
1. HR marks attendance via `/hr/attendance/mark` (email or ID-based)
2. System records check-in/check-out times
3. Dashboard shows real-time summary
4. Employees view own attendance via `/employee/attendance`

---

## 🛡️ Security Features

### Authentication
- ✅ JWT tokens with configurable expiration
- ✅ Secure password hashing (bcrypt with salt)
- ✅ Token-based session management
- ✅ Email domain whitelisting

### Authorization
- ✅ Role-based access control (RBAC)
- ✅ Endpoint-level permission checks
- ✅ Manager-specific team validation
- ✅ Employee ownership verification

### Data Protection
- ✅ Passwords never stored in plain text
- ✅ Passwords excluded from all API responses
- ✅ MongoDB ObjectId sanitization
- ✅ Input validation with Pydantic

---

## 🧪 Testing

### API Testing with cURL
```bash
# HR Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "hr@sunfocus.com", "password": "HR@SecurePass123"}'

# Employee Login
curl -X POST "http://localhost:8000/employee/employee_login" \
  -H "Content-Type: application/json" \
  -d '{"email": "employee@sunfocus.com", "password": "Employee@2025"}'

# View Profile
curl -X GET "http://localhost:8000/employee/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.

---

## 📦 Dependencies

**Core:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pymongo` - MongoDB driver
- `pydantic[email]` - Data validation
- `python-jose[cryptography]` - JWT handling
- `bcrypt` / `passlib[bcrypt]` - Password hashing
- `python-dotenv` - Environment variables

**Install All:**
```bash
pip install fastapi uvicorn pymongo pydantic[email] python-jose[cryptography] passlib[bcrypt] python-dotenv bcrypt
```

---

## 🚧 Future Enhancements

### Planned Features
- [ ] Bulk employee import (CSV/Excel)
- [ ] Email notifications for leave approvals
- [ ] Biometric attendance integration
- [ ] Payroll management
- [ ] Performance review system
- [ ] Document management
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Audit logging

## ✅ Production Status

**Current Status:** Production Ready ✓

**Database:** MongoDB 4.4+  
**Server:** Uvicorn ASGI  
**Python:** 3.10+

---

## 🎯 Getting Started Checklist

- [ ] Install Python 3.10+
- [ ] Install MongoDB
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure .env file
- [ ] Run database migrations (if any)
- [ ] Create HR account via `/auth/create_hr_once`
- [ ] Start server with `uvicorn main:app --reload`
- [ ] Access API docs at `/docs`
- [ ] Register test employees
- [ ] Test all modules

## 📚 Module Documentation

- 🔐 **Auth Module** → [Auth README](./app/Auth/README.md)
- 👔 **HR Module** → [HR README](./app/HR/README.md)
- 👨‍💼 **Employees Module** → [Employees README](./app/Employees/README.md)
- 🛠 **Common Utilities** → [Common README](./app/common/README.md)
