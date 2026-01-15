# 🔧 Common Module

## 📋 Overview

The Common Module serves as a **shared utility hub** for the entire ERP system. It provides reusable helper functions that handle data serialization, type conversions, and cross-module operations. This module follows the **DRY (Don't Repeat Yourself)** principle, ensuring consistent data formatting across all modules.

---

## ✨ Key Features

### 🔄 Data Serialization
- **MongoDB to JSON Conversion** - Convert BSON ObjectId and datetime to JSON-safe formats
- **Leave Document Serialization** - Enrich leave data with employee and manager names
- **ISO Format DateTime** - Standardized date/time representation

### 🔗 Cross-Module Utilities
- **Employee Name Fetching** - Auto-resolve employee names from IDs
- **Manager Name Resolution** - Fetch approver details
- **Date Type Conversion** - Convert Python date to datetime

### ⚡ Performance Optimized
- **Optional DB Injection** - Fetch names only when needed
- **Single Query Operations** - Efficient database lookups
- **Reusable Functions** - Used by HR, Employee, and Manager modules

---

## 🏗️ Architecture

### Module Structure
```
common/
├── utils.py           # Utility functions
└── README.md          # This file
```

### Technology Stack
- **Python 3.10+** - Type hints, datetime handling
- **MongoDB (PyMongo)** - Database operations
- **BSON** - ObjectId handling

---

## 🛠️ Utility Functions

### 1. `serialize_leave(leave: dict, db: Database = None)`
**Convert MongoDB leave document to JSON-safe format with enriched data**

**Purpose:**
- Convert ObjectId to string
- Convert datetime/date to ISO format
- Fetch employee name and email
- Fetch manager (approver) name and email

**Parameters:**
- `leave` (dict) - Raw leave document from MongoDB
- `db` (Database, optional) - MongoDB database instance for fetching names

**Returns:**
- `dict` - JSON-safe leave document with enriched data

---

#### Usage Example

**Without DB (Basic Serialization):**
```python
from app.common.utils import serialize_leave

leave = db["leave_db"].find_one({"_id": ObjectId(leave_id)})
serialized = serialize_leave(leave)

# Result:
{
  "_id": "670def123abc456789012347",  # ObjectId → string
  "start_date": "2025-11-10T00:00:00",  # datetime → ISO format
  "created_at": "2025-10-23T10:30:00"
}
```

**With DB (Full Enrichment):**
```python
leave = db["leave_db"].find_one({"_id": ObjectId(leave_id)})
serialized = serialize_leave(leave, db)

# Result:
{
  "_id": "670def123abc456789012347",
  "employee_id": "670abc123def456789012345",
  "employee_name": "John Doe",           # ← Auto-fetched
  "email": "john@sunfocus.com",          # ← Auto-fetched
  "manager_id": "670abc123def456789012346",
  "approved_by": "manager@sunfocus.com",
  "approved_by_name": "Sarah Smith",     # ← Auto-fetched
  "approved_by_email": "manager@sunfocus.com",
  "start_date": "2025-11-10T00:00:00",
  "end_date": "2025-11-14T00:00:00",
  "created_at": "2025-10-23T10:30:00Z",
  "applied_date": "2025-10-23T10:30:00Z"
}
```

---

#### Implementation Details

**Step 1: Convert ObjectId to String**
```python
leave["_id"] = str(leave["_id"])
# ObjectId("670def123...") → "670def123..."
```

**Step 2: Convert All DateTime/Date Fields to ISO Format**
```python
for key, value in leave.items():
    if isinstance(value, (datetime, date)):
        leave[key] = value.isoformat()

# datetime(2025, 10, 23, 10, 30) → "2025-10-23T10:30:00"
# date(2025, 11, 10) → "2025-11-10"
```

**Step 3: Fetch Employee Name (if DB provided)**
```python
if db is not None and "employee_id" in leave:
    employee = db["employee_db"].find_one({
        "_id": ObjectId(leave["employee_id"])
    })
    
    if employee:
        leave["employee_name"] = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        leave["email"] = employee.get("email", "N/A")
```

**Step 4: Fetch Manager Name (if approved)**
```python
if db is not None and "approved_by" in leave and leave["approved_by"]:
    # approved_by stores manager's email (string)
    manager = db["employee_db"].find_one({
        "email": leave["approved_by"]
    })
    
    if manager:
        leave["approved_by_name"] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}".strip()
        leave["approved_by_email"] = manager.get("email", "N/A")
    else:
        leave["approved_by_name"] = "Unknown"
        leave["approved_by_email"] = "N/A"
```

---

#### Why This Approach is Better

**❌ Old Approach (Limited):**
```python
def serialize_leave(leave: dict) -> dict:
    leave["_id"] = str(leave["_id"])
    for field in ["created_at", "applied_date", "start_date", "end_date"]:
        if field in leave and isinstance(leave[field], (datetime, date)):
            leave[field] = leave[field].isoformat()
    return leave
```

**Problems:**
- Hard-coded field names
- Must update function when new date fields added
- No employee/manager name enrichment
- Not scalable

**✅ New Approach (Dynamic):**
```python
for key, value in leave.items():
    if isinstance(value, (datetime, date)):
        leave[key] = value.isoformat()
```

**Benefits:**
- ✅ Automatically handles ALL date/datetime fields
- ✅ Works with new fields without code changes
- ✅ Enriches with employee/manager names
- ✅ Scalable and maintainable

---

### 2. `date_to_datetime(date_obj: date)`
**Convert Python date object to datetime object**

**Purpose:**
MongoDB stores dates as datetime (with time component). This utility ensures consistent date handling.

**Parameters:**
- `date_obj` (date) - Python date object

**Returns:**
- `datetime` - DateTime object with time set to 00:00:00

**Usage:**
```python
from datetime import date
from app.common.utils import date_to_datetime

# Convert date to datetime
my_date = date(2025, 11, 10)
my_datetime = date_to_datetime(my_date)

# Result:
# date(2025, 11, 10) → datetime(2025, 11, 10, 0, 0, 0)
```

**Implementation:**
```python
def date_to_datetime(date_obj: date):
    return datetime.combine(date_obj, datetime.min.time())
```

**Breakdown:**
- `datetime.combine()` - Combines date with time
- `datetime.min.time()` - Returns time(0, 0, 0) = 00:00:00
- Result: `2025-11-10T00:00:00`

---

### 3. `get_leave_request_by_id(db: Database, leave_id: str)`
**Fetch a single leave request by ID with full serialization**

**Purpose:**
Single utility to fetch and serialize leave requests used across modules.

**Parameters:**
- `db` (Database) - MongoDB database instance
- `leave_id` (str) - Leave request ID (as string)

**Returns:**
- `dict` - Fully serialized leave document with enriched data
- `None` - If leave not found

**Usage:**
```python
from app.common.utils import get_leave_request_by_id

leave = get_leave_request_by_id(db, "670def123abc456789012347")

if leave:
    print(f"Leave Type: {leave['leave_type']}")
    print(f"Employee: {leave['employee_name']}")
    print(f"Status: {leave['status']}")
else:
    print("Leave not found")
```

**Implementation:**
```python
def get_leave_request_by_id(db: Database, leave_id: str):
    # Convert string ID to ObjectId for MongoDB query
    leave = db["leave_db"].find_one({"_id": ObjectId(leave_id)})
    
    if leave:
        return serialize_leave(leave, db)  # Full serialization with names
    return None
```

**Features:**
- ✅ Handles string to ObjectId conversion
- ✅ Returns None if not found (no exceptions)
- ✅ Full serialization with employee/manager names
- ✅ Ready for JSON response

---

## 🔄 Data Flow Examples

### Example 1: HR Fetching All Leaves
```python
# In HR/crud.py
from app.common.utils import serialize_leave

def get_all_leave_requests(db: Database, query: dict = None):
    if query is None:
        query = {}
    
    leaves = list(db["leave_db"].find(query))
    
    # Serialize each leave with full enrichment
    return [serialize_leave(leave, db) for leave in leaves]
```

**Before Serialization:**
```python
{
  "_id": ObjectId("670def123..."),
  "employee_id": "670abc123...",
  "start_date": datetime(2025, 11, 10, 0, 0),
  "created_at": datetime(2025, 10, 23, 10, 30)
}
```

**After Serialization:**
```json
{
  "_id": "670def123abc456789012347",
  "employee_id": "670abc123def456789012345",
  "employee_name": "John Doe",
  "email": "john@sunfocus.com",
  "start_date": "2025-11-10T00:00:00",
  "created_at": "2025-10-23T10:30:00"
}
```

---

### Example 2: Employee Viewing Own Leaves
```python
# In Employees/crud.py
from app.common.utils import serialize_leave

def get_employee_leaves(db: Database, employee_id: str):
    query = {"employee_id": employee_id}
    leaves = list(db["leave_db"].find(query))
    
    # Serialize with manager name enrichment
    return [serialize_leave(leave, db) for leave in leaves]
```

**Response to Frontend:**
```json
[
  {
    "_id": "670def123abc456789012347",
    "employee_name": "John Doe",
    "email": "john@sunfocus.com",
    "manager_id": "670abc123def456789012346",
    "approved_by": "manager@sunfocus.com",
    "approved_by_name": "Sarah Smith",
    "status": "Approved"
  }
]
```

---

### Example 3: Date Conversion in Leave Request
```python
# In Employees/crud.py
from app.common.utils import date_to_datetime

def create_employee_leave(db: Database, employee_id: str, leave_data: dict):
    # Frontend sends: "start_date": "2025-11-10" (string)
    # Pydantic converts to: date(2025, 11, 10)
    
    if isinstance(leave_data["start_date"], date):
        leave_data["start_date"] = date_to_datetime(leave_data["start_date"])
    
    # Now ready for MongoDB
    # datetime(2025, 11, 10, 0, 0, 0)
```

---

## 🎯 Integration Points

### Used By HR Module
```python
from app.common.utils import serialize_leave, get_leave_request_by_id

# In HR/crud.py
def get_all_leave_requests(db, query):
    leaves = list(db["leave_db"].find(query))
    return [serialize_leave(leave, db) for leave in leaves]

# In HR/router.py
@router.get("/leave/{leave_id}")
def fetch_leave_by_id(leave_id: str, db: Database = Depends(get_db)):
    result = get_leave_request_by_id(db, leave_id)
    if not result:
        raise HTTPException(status_code=404, detail="Leave not found")
    return {"data": result}
```

---

### Used By Employee Module
```python
from app.common.utils import serialize_leave, get_leave_request_by_id

# In Employees/crud.py
def get_employee_leaves(db: Database, employee_id: str):
    query = {"employee_id": employee_id}
    leaves = list(db["leave_db"].find(query))
    return [serialize_leave(leave, db) for leave in leaves]

# In Employees/router.py
@router.delete("/leave/{leave_id}")
def cancel_leave(leave_id: str, db: Database = Depends(get_db)):
    leave = get_leave_request_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code=404)
    # Verify ownership and cancel
```

---

### Used By Manager Module
```python
from app.common.utils import serialize_leave

# In Manager/router.py (if separate from HR)
@router.get("/manager/leaves/pending")
def fetch_my_team_pending_leaves(db: Database = Depends(get_db)):
    leaves = list(db["leave_db"].find({"manager_id": manager_email}))
    return [serialize_leave(leave, db) for leave in leaves]
```

---

## 💡 Best Practices

### ✅ Do's

1. **Always pass db when fetching names**
   ```python
   serialize_leave(leave, db)  # ✅ With names
   ```

2. **Use get_leave_request_by_id for single leave fetches**
   ```python
   leave = get_leave_request_by_id(db, leave_id)  # ✅ Clean
   ```

3. **Convert dates before MongoDB operations**
   ```python
   if isinstance(date_obj, date):
       date_obj = date_to_datetime(date_obj)
   ```

4. **Check for None before using**
   ```python
   leave = get_leave_request_by_id(db, leave_id)
   if leave:
       # Process leave
   ```

---

### ❌ Don'ts

1. **Don't serialize without db if names needed**
   ```python
   serialize_leave(leave)  # ❌ No names
   ```

2. **Don't hard-code date field names**
   ```python
   # ❌ Bad
   leave["start_date"] = leave["start_date"].isoformat()
   
   # ✅ Good
   for key, value in leave.items():
       if isinstance(value, datetime):
           leave[key] = value.isoformat()
   ```

3. **Don't assume leave exists**
   ```python
   leave = db["leave_db"].find_one({"_id": ObjectId(id)})
   leave["_id"] = str(leave["_id"])  # ❌ Can fail if None
   
   # ✅ Good
   leave = get_leave_request_by_id(db, id)
   if leave:
       # Safe to use
   ```

---

## 🔧 Technical Details

### Why `isinstance(value, (datetime, date))`?

**Correct Syntax:**
```python
if isinstance(value, (datetime, date)):  # ✅ Tuple
```

**Why Tuple?**
- `isinstance()` requires tuple for multiple types
- `(datetime, date)` = tuple of types
- Checks if value is datetime OR date

**Wrong Syntax:**
```python
if isinstance(value, datetime, date):  # ❌ SyntaxError
if isinstance(value, [datetime, date]):  # ❌ TypeError
```

---

### Why `if db is not None:`?

**Problem with `if db:`**
```python
if db:  # ❌ Doesn't work with MongoDB Database objects
```

**MongoDB Database objects don't support truthiness check**

**Correct Approach:**
```python
if db is not None:  # ✅ Explicit None check
```

---

### ObjectId Handling

**String to ObjectId:**
```python
from bson import ObjectId

# Frontend sends: "670def123abc456789012347"
leave_id = "670def123abc456789012347"

# Convert for MongoDB query
leave = db["leave_db"].find_one({"_id": ObjectId(leave_id)})
```

**ObjectId to String:**
```python
# MongoDB returns: ObjectId("670def123...")
leave["_id"] = str(leave["_id"])

# Result: "670def123abc456789012347"
```

---

## 📊 Performance Impact

### Efficient Name Fetching
```python
# Single query per leave (acceptable for small datasets)
employee = db["employee_db"].find_one({"_id": ObjectId(employee_id)})

# For large datasets, consider:
# - Caching frequently accessed employees
# - Batch fetching with $lookup aggregation
```

### Example Optimization (Future)
```python
# Using MongoDB aggregation for bulk operations
pipeline = [
    {"$match": query},
    {"$lookup": {
        "from": "employee_db",
        "localField": "employee_id",
        "foreignField": "_id",
        "as": "employee_details"
    }},
    {"$unwind": "$employee_details"}
]

leaves = list(db["leave_db"].aggregate(pipeline))
```

---

## 🎓 Code Quality Highlights

### 1. DRY Principle
Instead of repeating serialization code in every module:
```python
# ❌ Repeated in HR, Employee, Manager modules
leave["_id"] = str(leave["_id"])
for field in ["created_at", "start_date"]:
    leave[field] = leave[field].isoformat()

# ✅ Single reusable function
from app.common.utils import serialize_leave
serialized = serialize_leave(leave, db)
```

---

### 2. Single Responsibility
Each function does ONE thing well:
- `serialize_leave()` - Serialization only
- `date_to_datetime()` - Date conversion only
- `get_leave_request_by_id()` - Fetch by ID only

---

### 3. Scalability
New date fields? No code changes needed:
```python
# Automatically handles any new datetime fields
for key, value in leave.items():
    if isinstance(value, (datetime, date)):
        leave[key] = value.isoformat()
```

---

### 4. Defensive Programming
```python
# Safe name fetching
leave["employee_name"] = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()

# Handles:
# - Missing first_name or last_name
# - None values
# - Extra whitespace
```

---

## 📄 Summary

### What This Module Provides
✅ **Consistent Data Formatting** - All modules use same serialization  
✅ **Name Resolution** - Auto-fetch employee/manager names  
✅ **Type Conversions** - Handle date/datetime/ObjectId properly  
✅ **Reusable Utilities** - DRY principle applied  
✅ **JSON-Safe Output** - Ready for API responses  

### Used By
- **HR Module** - All leave operations
- **Employee Module** - View/apply/cancel leaves
- **Manager Module** - Team leave management

### Key Benefits
🎯 **Maintainability** - Update once, applies everywhere  
🚀 **Performance** - Optimized queries  
🛡️ **Reliability** - Defensive error handling  
📦 **Scalability** - Handles new fields automatically  

---

