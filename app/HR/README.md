# 👔 HR Module

## 📋 Overview

The HR Module is the **central management system** for employee lifecycle, attendance tracking, and leave management in the ERP system. It provides comprehensive tools for HR personnel to manage employee records, track attendance, and oversee leave requests with manager-based approval workflows.

---

## ✨ Key Features

### 👥 Employee Management
- **Complete CRUD Operations** - Create, Read, Update employee records
- **Comprehensive Employee Profiles** - Personal info, addresses, job details, education, work experience
- **Advanced Search** - Multi-field search by name, department, designation, job title
- **Status Management** - Activate/Deactivate employees (soft delete)
- **Flexible Lookup** - Find employees by ID or email

### 📊 Attendance System
- **Daily Attendance Marking** - Track Present, Absent, Leave, Half-Day status
- **Email-based Marking** - Mark attendance using employee ID or email
- **Real-time Dashboard** - Today's attendance summary with live counts
- **Historical Records** - Filter attendance by employee, date, or status
- **Update Support** - Modify attendance records when needed

### 🏖️ Leave Management
- **Automated Leave Balance** - Auto-assigned on employee creation
  - Annual: 12 days
  - Sick: 6 days
  - Personal: 3 days
  - Emergency: 2 days
- **Manager-based Approval** - Leaves routed to assigned managers
- **Status Tracking** - Pending, Approved, Rejected leaves
- **Auto-deduction** - Leave balance updated on approval
- **Team Management** - Managers see only their team's leaves

---

## 🏗️ Architecture

### Technology Stack
- **FastAPI** - REST API framework
- **MongoDB** - NoSQL database with 3 collections:
  - `employee_db` - Employee records
  - `attendance_db` - Attendance records
  - `leave_db` - Leave requests
- **Pydantic** - Data validation & serialization
- **BSON ObjectId** - MongoDB document identifiers

### Module Structure
```
HR/
├── router.py          # Main HR endpoints
├── manager_router.py  # Manager-specific endpoints
├── crud.py            # Database operations
├── helper.py          # Authorization helpers
├── schemas.py         # Pydantic models
└── README.md          # This file
```

---

## 🔐 Role-Based Access Control

### HR Role
- **Full Access** to all employee, attendance, and leave operations
- Can register, update, search employees
- Can mark and view all attendance records
- Can view all leave requests (but cannot approve/reject)

### Manager Role
- **Team-specific Access** to leave management
- Can view pending leaves for their team
- Can approve/reject leaves assigned to them
- Cannot modify other managers' team leaves

### Authorization Flow
```python
# HR endpoints protected by
@Depends(require_hr_role)

# Manager endpoints protected by
@Depends(require_manager_role)
```

---

## 🚀 API Endpoints

## 👥 Employee Management APIs

### 1. **POST** `/hr/register_employee`
**Register a new employee (HR only)**

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@sunfocus.com",
  "password": "SecurePass@123",
  "phone": "+91-9876543210",
  "date_of_birth": "1995-05-15",
  "gender": "Male",
  "role": "employee",
  "current_address": {
    "street": "123 Main St",
    "city": "Ludhiana",
    "state": "Punjab",
    "postal_code": "141001",
    "country": "India"
  },
  "job_info": {
    "department": "Engineering",
    "designation": "Software Developer",
    "job_title": "Senior Developer",
    "employee_type": "Full-time",
    "joining_date": "2025-01-20",
    "manager_email": "manager@sunfocus.com"
  }
}
```

**Success Response (201):**
```json
{
  "message": "Employee registered successfully",
  "employee": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@sunfocus.com",
    "leave_balance": {
      "annual": 12,
      "sick": 6,
      "personal": 3,
      "emergency": 2,
      "annual_used": 0,
      "sick_used": 0,
      "personal_used": 0,
      "emergency_used": 0
    },
    "status": "active"
  }
}
```

**Auto-created Features:**
- ✅ Password hashed using bcrypt
- ✅ Status set to "active"
- ✅ Leave balance initialized
- ✅ Password excluded from response

---

### 2. **GET** `/hr/employees`
**Get list of all employees and managers (HR only)**

**Success Response (200):**
```json
{
  "message": "Employees data fetched successfully",
  "employees": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@sunfocus.com",
      "role": "employee",
      "status": "active",
      "job_info": {
        "department": "Engineering",
        "designation": "Software Developer"
      }
    }
  ]
}
```

**Features:**
- Sorted alphabetically by first_name
- Password excluded from results
- Returns both employees and managers

---

### 3. **GET** `/hr/employee/{employee_id}`
**Get employee by ID (HR only)**

**Success Response (200):**
```json
{
  "message": "Employee fetched successfully",
  "employee": {
    "_id": "507f1f77bcf86cd799439011",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@sunfocus.com",
    "phone": "+91-9876543210",
    "current_address": {...},
    "permanent_address": {...},
    "job_info": {...},
    "education": [...],
    "work_experience": [...]
  }
}
```

---

### 4. **PUT** `/hr/employee/{employee_id}/basic`
**Update basic employee information (HR only)**

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+91-9876543210",
  "date_of_birth": "1995-05-15",
  "gender": "Male"
}
```

**Success Response (200):**
```json
{
  "message": "Basic info updated"
}
```

---

### 5. **PUT** `/hr/employee/{employee_id}/current_address`
**Update current address (HR only)**

**Request Body:**
```json
{
  "street": "456 New Street",
  "city": "Chandigarh",
  "state": "Punjab",
  "postal_code": "160001",
  "country": "India"
}
```

---

### 6. **PUT** `/hr/employee/{employee_id}/permanent_address`
**Update permanent address (HR only)**

---

### 7. **PUT** `/hr/employee/{employee_id}/job_info`
**Update job information (HR only)**

**Request Body:**
```json
{
  "department": "DevOps",
  "designation": "Senior Engineer",
  "job_title": "Lead DevOps Engineer",
  "employee_type": "Full-time",
  "salary": 850000,
  "manager_email": "manager@sunfocus.com"
}
```

---

### 8. **POST** `/hr/employee/{employee_id}/education`
**Add education record (HR only)**

**Request Body:**
```json
{
  "degree": "B.Tech",
  "institution": "IIT Delhi",
  "field_of_study": "Computer Science",
  "graduation_year": 2018,
  "grade": "8.5 CGPA"
}
```

**Success Response (200):**
```json
{
  "message": "Education info updated"
}
```

---

### 9. **PUT** `/hr/employee/{employee_id}/education/{index}`
**Update education record by array index (HR only)**

---

### 10. **POST** `/hr/employee/{employee_id}/work_experience`
**Add work experience (HR only)**

**Request Body:**
```json
{
  "company": "Tech Corp",
  "position": "Junior Developer",
  "start_date": "2018-07-01",
  "end_date": "2021-12-31",
  "responsibilities": "Developed web applications using React and Node.js"
}
```

---

### 11. **PUT** `/hr/employee/{employee_id}/work_experience/{index}`
**Update work experience by array index (HR only)**

---

### 12. **POST** `/hr/employees/search`
**Search employees (HR only)**

**Request Body:**
```json
{
  "first_name": "John",
  "department": "Engineering",
  "designation": "Developer"
}
```

**Success Response (200):**
```json
{
  "message": "3 employees found",
  "employees": [...]
}
```

**Search Features:**
- Case-insensitive regex search
- Partial match support (e.g., "Jo" matches "John")
- Search by: first_name, last_name, department, designation, job_title
- Sorted alphabetically

---

### 13. **PUT** `/hr/employee/{employee_id}/activate`
**Activate employee (HR only)**

**Success Response (200):**
```json
{
  "message": "Employee activated successfully"
}
```

---

### 14. **DELETE** `/hr/employee/{employee_id}`
**Deactivate employee - Soft delete (HR only)**

**Success Response (200):**
```json
{
  "message": "Employee deactivated successfully"
}
```

**Note:** This is a soft delete - sets status to "inactive" instead of removing the record.

---

## 📊 Attendance Management APIs

### 15. **POST** `/hr/attendance/mark`
**Mark attendance (HR only)**

**Request Body (using employee_id):**
```json
{
  "employee_id": "507f1f77bcf86cd799439011",
  "date": "2025-10-22",
  "status": "Present",
  "check_in": "09:00:00",
  "check_out": "18:00:00",
  "remarks": "On time"
}
```

**Request Body (using email):**
```json
{
  "email": "john.doe@sunfocus.com",
  "date": "2025-10-22",
  "status": "Present",
  "check_in": "09:00:00",
  "check_out": "18:00:00"
}
```

**Success Response (201):**
```json
{
  "message": "Attendance marked successfully"
}
```

**Valid Status Values:**
- `Present`
- `Absent`
- `Leave`
- `Half-Day`

---

### 16. **GET** `/hr/attendance`
**Fetch attendance records (HR only)**

**Query Parameters:**
- `employee_id` (optional) - Filter by employee ID
- `email` (optional) - Filter by employee email
- `date` (optional) - Filter by date (YYYY-MM-DD)

**Example Request:**
```
GET /hr/attendance?email=john.doe@sunfocus.com&date=2025-10-22
```

**Success Response (200):**
```json
{
  "message": "5 records found",
  "data": [
    {
      "employee_id": "507f1f77bcf86cd799439011",
      "date": "2025-10-22",
      "status": "Present",
      "check_in": "09:00:00",
      "check_out": "18:00:00",
      "remarks": "On time"
    }
  ]
}
```

---

### 17. **GET** `/hr/attendance/summary/today`
**Get today's attendance summary (HR only)**

**Success Response (200):**
```json
{
  "message": "Today's attendance summary",
  "summary": {
    "present": 45,
    "absent": 3,
    "leave": 2,
    "half_day": 1,
    "total": 51
  }
}
```

**Features:**
- Real-time count for current day
- Automatically filters records between 00:00:00 and 23:59:59 today
- Perfect for HR dashboard

---

### 18. **PUT** `/hr/attendance/{employee_id}/{date}`
**Update attendance record (HR only)**

**Example:**
```
PUT /hr/attendance/507f1f77bcf86cd799439011/2025-10-22
```

**Request Body:**
```json
{
  "status": "Half-Day",
  "check_out": "13:00:00",
  "remarks": "Left early due to personal reason"
}
```

**Success Response (200):**
```json
{
  "message": "Attendance updated successfully"
}
```

---

## 🏖️ Leave Management APIs (HR View)

### 19. **GET** `/hr/leaves`
**Get all leave requests (HR only)**

**Success Response (200):**
```json
{
  "message": "15 leave request found",
  "data": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "employee_id": "507f1f77bcf86cd799439011",
      "employee_name": "John Doe",
      "manager_id": "manager@sunfocus.com",
      "manager_name": "Sarah Smith",
      "leave_type": "annual",
      "start_date": "2025-11-01",
      "end_date": "2025-11-05",
      "reason": "Family vacation",
      "status": "Pending",
      "applied_date": "2025-10-20T10:30:00Z"
    }
  ]
}
```

**Serialization Features:**
- Employee and manager names auto-fetched from DB
- DateTime objects converted to ISO format
- MongoDB ObjectId converted to string

---

### 20. **GET** `/hr/leave/{leave_id}`
**Get leave request by ID (HR only)**

**Success Response (200):**
```json
{
  "message": "Leave request found",
  "data": {
    "_id": "507f1f77bcf86cd799439012",
    "employee_name": "John Doe",
    "leave_type": "sick",
    "status": "Approved",
    "approved_by": "manager@sunfocus.com",
    "approved_at": "2025-10-21T14:30:00Z"
  }
}
```

---

### 21. **GET** `/hr/leaves/pending`
**Get only pending leave requests (HR only)**

---

### 22. **GET** `/hr/leaves/approved`
**Get only approved leave requests (HR only)**

---

### 23. **GET** `/hr/leaves/rejected`
**Get only rejected leave requests (HR only)**

---

### 24. **GET** `/hr/employee/{employee_id}/leave_balance`
**Get employee's leave balance (HR only)**

**Success Response (200):**
```json
{
  "employee_id": "507f1f77bcf86cd799439011",
  "leave_balance": {
    "annual": 12,
    "sick": 6,
    "personal": 3,
    "emergency": 2,
    "annual_used": 3,
    "sick_used": 1,
    "personal_used": 0,
    "emergency_used": 0
  }
}
```

**Calculated Remaining:**
- Annual: 12 - 3 = 9 days left
- Sick: 6 - 1 = 5 days left

---

## 👨‍💼 Manager Leave Approval APIs

### 25. **GET** `/hr/manager/leaves/pending`
**Get my team's pending leaves (Manager only)**

**Success Response (200):**
```json
{
  "message": "3 pending leave request(s) found for your team",
  "data": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "employee_name": "John Doe",
      "leave_type": "annual",
      "start_date": "2025-11-01",
      "end_date": "2025-11-05",
      "status": "Pending"
    }
  ]
}
```

**Features:**
- Filters by manager's email (not _id)
- Only shows leaves assigned to current manager
- Only pending status

---

### 26. **PUT** `/hr/manager/leave/{leave_id}/approve`
**Approve or reject leave (Manager only)**

**Request Body:**
```json
{
  "status": "Approved",
  "remarks": "Approved for team coverage"
}
```

**Valid Status Values:**
- `Approved`
- `Rejected`

**Success Response (200):**
```json
{
  "message": "Leave request approved successfully"
}
```

**Authorization Check:**
- Verifies leave is assigned to current manager
- Returns 403 if trying to approve another manager's team leave

**Auto-updates on Approval:**
- Sets `approved_by` to manager's email
- Sets `approved_at` to current UTC timestamp
- Deducts leave days from employee's balance
- Increments `{leave_type}_used` field

---

### 27. **GET** `/hr/manager/leaves`
**Get all my team's leaves (Manager only)**

Returns all leaves (Pending, Approved, Rejected) for manager's team.

---

### 28. **GET** `/hr/manager/leaves/approved`
**Get my team's approved leaves (Manager only)**

---

### 29. **GET** `/hr/manager/leaves/rejected`
**Get my team's rejected leaves (Manager only)**

---

## 📊 Database Schema

### Employee Collection (employee_db)
```json
{
  "_id": ObjectId("..."),
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@sunfocus.com",
  "password": "$2b$12$...", // bcrypt hash
  "phone": "+91-9876543210",
  "date_of_birth": "1995-05-15",
  "gender": "Male",
  "role": "employee", // employee | manager | HR
  "status": "active", // active | inactive
  
  "current_address": {
    "street": "123 Main St",
    "city": "Ludhiana",
    "state": "Punjab",
    "postal_code": "141001",
    "country": "India"
  },
  
  "permanent_address": {...},
  
  "job_info": {
    "department": "Engineering",
    "designation": "Software Developer",
    "job_title": "Senior Developer",
    "employee_type": "Full-time",
    "joining_date": "2025-01-20",
    "salary": 750000,
    "manager_email": "manager@sunfocus.com"
  },
  
  "leave_balance": {
    "annual": 12,
    "sick": 6,
    "personal": 3,
    "emergency": 2,
    "annual_used": 0,
    "sick_used": 0,
    "personal_used": 0,
    "emergency_used": 0
  },
  
  "education": [
    {
      "degree": "B.Tech",
      "institution": "IIT Delhi",
      "field_of_study": "Computer Science",
      "graduation_year": 2018,
      "grade": "8.5 CGPA"
    }
  ],
  
  "work_experience": [
    {
      "company": "Tech Corp",
      "position": "Junior Developer",
      "start_date": "2018-07-01",
      "end_date": "2021-12-31",
      "responsibilities": "..."
    }
  ]
}
```

---

### Attendance Collection (attendance_db)
```json
{
  "_id": ObjectId("..."),
  "employee_id": "507f1f77bcf86cd799439011",
  "date": ISODate("2025-10-22T00:00:00Z"),
  "status": "Present", // Present | Absent | Leave | Half-Day
  "check_in": "09:00:00",
  "check_out": "18:00:00",
  "remarks": "On time"
}
```

---

### Leave Collection (leave_db)
```json
{
  "_id": ObjectId("..."),
  "employee_id": "507f1f77bcf86cd799439011",
  "manager_id": "manager@sunfocus.com",
  "leave_type": "annual", // annual | sick | personal | emergency
  "start_date": ISODate("2025-11-01"),
  "end_date": ISODate("2025-11-05"),
  "reason": "Family vacation",
  "status": "Pending", // Pending | Approved | Rejected
  "applied_date": ISODate("2025-10-20T10:30:00Z"),
  "approved_by": "manager@sunfocus.com", // Set on approval
  "approved_at": ISODate("2025-10-21T14:30:00Z"), // Set on approval
  "remarks": "Approved for team coverage"
}
```

---

## 🔄 Business Logic Flows

### Employee Registration Flow
```
1. HR submits employee data
2. Validate email domain (must be in whitelist)
3. Check if employee already exists
4. Hash password using bcrypt
5. Set status = "active"
6. Initialize leave balance (12, 6, 3, 2)
7. Save to employee_db
8. Return employee data (password excluded)
```

---

### Attendance Marking Flow
```
1. HR provides employee_id OR email
2. If email provided → Fetch employee_id from DB
3. Validate employee exists
4. Convert date to datetime (00:00:00)
5. Save attendance record
6. Return success message
```

---

### Leave Approval Flow (Manager)
```
1. Manager views pending leaves for their team
2. Manager clicks approve/reject
3. System verifies:
   - Leave request exists
   - Manager is authorized (assigned manager)
4. Update leave status
5. Set approved_by = manager_email
6. Set approved_at = current UTC time
7. If Approved:
   - Calculate days: (end_date - start_date) + 1
   - Update employee leave_balance
   - Increment {leave_type}_used by days
8. Return success
```

**Example Leave Deduction:**
```
Leave: 5 days of Annual leave
Before: annual_used = 3
After: annual_used = 8 (3 + 5)
Remaining: 12 - 8 = 4 days
```

---

## 🛠️ Utility Functions (crud.py)

### Employee Functions
| Function | Purpose |
|----------|---------|
| `create_employee()` | Register new employee with hashed password |
| `get_all_employees()` | Fetch all employees & managers |
| `get_employee_by_id()` | Fetch single employee by ObjectId |
| `get_by_email()` | Fetch employee by email (case-insensitive) |
| `update_employee_basic()` | Update basic info |
| `update_current_address()` | Update current address |
| `update_permanent_address()` | Update permanent address |
| `update_job_info()` | Update job details |
| `add_education()` | Append education record |
| `update_education()` | Update education by array index |
| `add_work_experience()` | Append work experience |
| `update_work_experience()` | Update work exp by index |
| `search_employees()` | Multi-field regex search |
| `activate_employee()` | Set status to "active" |
| `deactivate_employee()` | Set status to "inactive" |

### Attendance Functions
| Function | Purpose |
|----------|---------|
| `add_attendance()` | Mark attendance record |
| `get_attendance()` | Fetch with filters (employee, date) |
| `get_today_attendance_summary()` | Count by status for today |
| `update_attendance()` | Modify existing record |

### Leave Functions
| Function | Purpose |
|----------|---------|
| `get_all_leave_requests()` | Fetch leaves with optional query filter |
| `update_leave_status()` | Approve/reject + auto-deduct balance |

---

## 🔐 Authorization Helpers (helper.py)

### `require_hr_role()`
**Protects HR-only endpoints**
```python
def require_hr_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "HR":
        raise HTTPException(status_code=403, detail="Not authorized, HR access only")
    return current_user
```

**Usage:**
```python
@router.post("/hr/register_employee")
def register_employee(
    employee: EmployeeRegister,
    _current_user: dict = Depends(require_hr_role),
    db: Database = Depends(get_db)
):
    ...
```

---

### `require_manager_role()`
**Protects Manager-only endpoints**
```python
def require_manager_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "manager":
        raise HTTPException(status_code=403, detail="Not authorized, Manager access only")
    return current_user
```

---

## 🧪 Testing Examples

### Test Employee Registration
```bash
curl -X POST "http://localhost:8000/hr/register_employee" \
  -H "Authorization: Bearer YOUR_HR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Employee",
    "email": "test@sunfocus.com",
    "password": "Test@123",
    "role": "employee",
    "job_info": {
      "department": "IT",
      "designation": "Trainee",
      "joining_date": "2025-10-22"
    }
  }'
```

---

### Test Attendance Marking (Email-based)
```bash
curl -X POST "http://localhost:8000/hr/attendance/mark" \
  -H "Authorization: Bearer YOUR_HR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@sunfocus.com",
    "date": "2025-10-22",
    "status": "Present",
    "check_in": "09:30:00",
    "check_out": "18:00:00"
  }'
```

---

### Test Search Employees
```bash
curl -X POST "http://localhost:8000/hr/employees/search" \
  -H "Authorization: Bearer YOUR_HR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "Engineering",
    "designation": "Developer"
  }'
```

---

### Test Manager Leave Approval
```bash
curl -X PUT "http://localhost:8000/hr/manager/leave/507f1f77bcf86cd799439012/approve" \
  -H "Authorization: Bearer YOUR_MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Approved",
    "remarks": "Enjoy your vacation"
  }'
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Employee Not Found (Email-based lookup)
**Problem:** `GET /hr/attendance?email=Test@sunfocus.com` returns 404

**Solution:**
- Email is converted to lowercase in DB
- Use `test@sunfocus.com` instead of `Test@sunfocus.com`
- Check `get_by_email()` uses `.lower().strip()`

---

### Issue 2: Manager Cannot Approve Leave
**Problem:** 403 Forbidden when manager tries to approve

**Cause:** Leave request uses `manager_id` as email, not ObjectId

**Solution:**
- Ensure `job_info.manager_email` is set correctly
- Verify leave request's `manager_id` matches current manager's email
- Check token has `role: "manager"`

---

### Issue 3: Leave Balance Not Deducting
**Problem:** Leave approved but balance not updated

**Debug:**
```python
# In crud.py update_leave_status()
print(f"Days requested: {days_requested}")
print(f"Leave type: {leave_type}")
print(f"Field to update: leave_balance.{leave_type}_used")
```

**Common Causes:**
- `leave_type` case mismatch (should be lowercase: "annual", not "Annual")
- `start_date` or `end_date` missing/invalid
- Employee document missing `leave_balance` field

---

### Issue 4: Attendance Date Format Error
**Problem:** `datetime` vs `date` confusion

**Solution:**
```python
# In crud.py add_attendance()
if isinstance(attendance_data['date'], date):
    attendance_data['date'] = datetime.combine(
        attendance_data['date'], 
        datetime.min.time()
    )
```

This converts `2025-10-22` (date) → `2025-10-22T00:00:00` (datetime)

---

## 💡 Best Practices

### ✅ Best Do's
1. **Always hash passwords** before saving to DB
2. **Exclude password** from all API responses
3. **Convert ObjectId to string** before returning to frontend
4. **Use email.lower().strip()** for case-insensitive lookups
5. **Validate employee exists** before marking attendance
6. **Check manager authorization** before leave approval
7. **Use exclude_unset=True** to allow partial updates
8. **Handle date/datetime conversions** properly


---

## 🔗 Integration with Other Modules

### Auth Module
```python
from app.Auth.helper import get_current_user
from app.Auth.utils import hash_password

# Used for:
# - Authentication middleware
# - Password hashing during registration
```

### Common Module
```python
from app.common.utils import serialize_leave

# Used for:
# - Converting MongoDB leave documents to API-friendly format
# - Fetching employee/manager names
# - DateTime serialization
```

### Database Module
```python
from app.database import get_db

# Used for:
# - MongoDB connection injection
# - Accessing employee_db, attendance_db, leave_db collections
```

---
