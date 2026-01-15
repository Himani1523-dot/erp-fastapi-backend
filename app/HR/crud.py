from pymongo.database import Database
from app.HR.schemas import EmployeeRegister
from fastapi import status
from bson import ObjectId
from typing import Optional, Dict
from bson.errors import InvalidId
from .schemas import EmployeeSearch
from datetime import datetime, date
from app.common.utils import serialize_leave, serialize_attendance

#---------------Create employee--------------------------------------------------
def create_employee(db: Database, employee: EmployeeRegister, hashed_password: str):
    existing_employee = db["employee_db"].find_one({"email": employee.email})
    if existing_employee:
        return {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Employee already exists"
        }
    
    employee_data = employee.model_dump()            #convert pydantic model to dict as mongodb only accepts dict
    employee_data["password"] = hashed_password      #password saved in DB 
    employee_data["status"] = "active"               #Set default active status for new employees

    employee_data["leave_balance"] = {
        "annual": 12,
        "sick": 6,
        "personal": 3,
        "emergency": 2,

        "annual_used": 0,
        "sick_used": 0,
        "personal_used": 0,
        "emergency_used": 0,
    }
    db["employee_db"].insert_one(employee_data)

    response_data = employee.model_dump(exclude={"password"})       #excluding password from API response 
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Employee registered successfully",
        "employee": response_data
    }

#old working code---------------Create employee--------------------------------------------------
"""def create_employee(db: Database, employee: EmployeeRegister, hashed_password: str):
    existing_employee = db["employee_db"].find_one({"email": employee.email})
    if existing_employee:
        return {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Employee already exists"
        }
    
    employee_data = employee.model_dump()
    employee_data["password"] = hashed_password      #password saved in DB 
    db["employee_db"].insert_one(employee_data)

    response_data = employee.model_dump(exclude={"password"})       #excluding password from API response 
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Employee registered successfully",
        "employee": response_data
    }"""

#---------------GET ALL employee AND managers----------------------------------------------------
def get_all_employees(db:Database):
        # Get both employees and managers (managers are also employees with extra privileges)
        employees = list(db["employee_db"].find({"role": {"$in": ["employee", "manager"]}},{"password" :0}).sort("first_name",1))     #sort with acending order,first alphabetically
        for emp in employees:
             emp["_id"] = str(emp["_id"])                                  #convert obj id into string as obj id 
        return employees

#---------------GET employee by ID--------------------------------------------------
def get_employee_by_id(db: Database, employee_id: str) -> Optional[Dict]:
    try:
        employee = db["employee_db"].find_one({"_id": ObjectId(employee_id)},{"password": 0})
        if employee:
            employee["_id"] = str(employee["_id"])
        return employee
    except InvalidId:
         return None 

#---------------GET employee by EMAIL------------------------------------------------
def get_by_email(db: Database, email: str) -> Optional[Dict]:
        employee = db["employee_db"].find_one({"email": email.lower()}, {"password": 0})
        if employee:
            employee["_id"] = str(employee["_id"])
        return employee


# ---------------- Basic Info ---------------------------------------------------
def update_employee_basic(db: Database, employee_id: str, update_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": update_data}
    )

# ---------------- Current Address ----------------------------------------------
def update_current_address(db: Database, employee_id: str, address_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"current_address": address_data}}
    )

# ---------------- Permanent Address ---------------------------------------------
def update_permanent_address(db: Database, employee_id: str, address_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"permanent_address": address_data}}
    )

# ---------------- Job Info ----------------------------------------------------
def update_job_info(db: Database, employee_id: str, job_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"job_info": job_data}}
    )


# ---------------- Education -----------------------------------------------------
def add_education(db: Database, employee_id: str, edu_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$push": {"education": edu_data}}                      #$push automatically appends a new element at the end of the education array...You don’t need an index, because MongoDB just adds it at the next available position. 
    )

def update_education(db: Database, employee_id: str, edu_index: int, edu_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {f"education.{edu_index}": edu_data}}          #$set operator is used to add new fields or update the values of existing fields within a document. It is a commonly used update operator
    )

# ---------------- Work Experience -----------------------------------------------
def add_work_experience(db: Database, employee_id: str, work_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$push": {"work_experience": work_data}}     
    )

def update_work_experience(db: Database, employee_id: str, work_index: int, work_data: dict):
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {f"work_experience.{work_index}": work_data}}
    )

#---------search employee by anything in SEARCH BAR-------------------------------
def search_employees(db, search_params: EmployeeSearch):
    query = {}                                                #here query i used to store the search criteria like jaise agar first name me "ab" likha to wo abhay ko bhi laake dega
    search_dict = search_params.model_dump(exclude_none=True)  

    field_mapping = {
        "first_name": "first_name",
        "last_name": "last_name",
        "department": "job_info.department",
        "designation": "job_info.designation",
        "job_title": "job_info.job_title",
    }

    for key, value in search_dict.items():
        db_field = field_mapping.get(key)
        if db_field:
            query[db_field] = {"$regex": value, "$options": "i"}     #regex is used suppose if the employee name is abhay and we search only "ab" then also it will show results of abhay in the search bar 

    employees = employees = list(
    db["employee_db"].find(query, {"password": 0})
    .sort("first_name", 1)
)
    for emp in employees:
        emp["_id"] = str(emp["_id"])
    return employees

# ==================================================================================
# ---------Activate/Deactivate employee---------------------
def activate_employee(db: Database, employee_id: str):
    """Activate an employee (mark as active/at work)"""
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"status": "active"}}          
    )

def deactivate_employee(db: Database, employee_id: str):
    """Deactivate an employee (soft delete / mark as inactive)"""
    return db["employee_db"].update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"status": "inactive"}}
    )

# ===================ATTENDANCE===============================================================
# -----------ADD ATTENDANCE-------------------------------------
def add_attendance(db:Database, attendance_data: dict):
    # Convert date object to datetime for MongoDB compatibility
    if 'date' in attendance_data and isinstance(attendance_data['date'], date):   #isinstance(attendance_data['date'], date): = Ye ensure karta hai: “Jo date mili hai, wo Python ka date object hai, datetime ya string nahi.”
        attendance_data['date'] = datetime.combine(attendance_data['date'], datetime.min.time())
    return db["attendance_db"].insert_one(attendance_data)


"""Summary in plain words ->
Backend check karta hai: “Date hai? Aur sahi format me hai?”
Agar sahi hai → date ko standard datetime me convert karta hai (midnight)
Fir → record ko MongoDB me save karta hai
Return → DB ka confirmation deta hai"""

#--------------------VIEW EMPLOYEES ATTENDANCE ----------------------------------------
def get_attendance(db: Database, query: dict):
    attendance_records = list(db["attendance_db"].find(query, {"_id": 0}))
    # Serialize each attendance record with employee details
    return [serialize_attendance(record, db) for record in attendance_records]
    
#check-------------------GET TODAY'S ATTENDANCE SUMMARY ----------------------------------------
def get_today_attendance_summary(db: Database):
    today = datetime.now().date()                         #takes only date not time

    start = datetime.combine(today, datetime.min.time())  # 00:00:00
    end = datetime.combine(today, datetime.max.time())    # 23:59:59

    records = list(db["attendance_db"].find({"date": {"$gte": start, "$lte": end}}))         # MongoDB cursor ko Python list me convert kar diya taaki aage iterate ya return kar sake.  
    summary = {
        "present": 0,
        "absent": 0,
        "leave": 0,
        "half_day": 0,
        "total": len(records)
    }
    
    for record in records:
        status = record.get("status", "").lower()
        if status == "present":
            summary["present"] += 1
        elif status == "absent":
            summary["absent"] += 1
        elif status == "leave":
            summary["leave"] += 1
        elif status == "half-day":
            summary["half_day"] += 1
    
    return summary

#--------------------UPDATE EMPLOYEES ATTENDACE --------------------------------------------
def update_attendance(db: Database, employee_id: str, date_value: str, update_data: dict):
    if isinstance(date_value, str):
        date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
    
    return db["attendance_db"].update_one(
        {"employee_id": employee_id, "date": date_value},
        {"$set": update_data}
    )

# ===================LEAVE MODULE===============================================================
# ------------------GET ALL LEAVES ------------------------------------------------------------
#  def get_all_leave_requests(db:Database, query : dict = {}):      # never pass { } mutable objects,meaning if Python reuses it between function calls,it can accidentally remember old data.

def get_all_leave_requests(db: Database, query: Optional[dict] = None):
    if query is None:
        query = {}                                                 # default to empty query so all records are fetched
    leaves = list(db["leave_db"].find(query))
    return [serialize_leave(leave, db) for leave in leaves]        #Pass db to serialize_leave to fetch employee and manager names
     

#    """ # for leave in leaves:
#     #     leave["_id"] = str(leave["_id"])
#     #     # Convert datetime objects to ISO format strings
#     #     if "created_at" in leave and isinstance(leave["created_at"], datetime):
#     #         leave["created_at"] = leave["created_at"].isoformat()
#     #     if "applied_date" in leave and isinstance(leave["applied_date"], datetime):
#     #         leave["applied_date"] = leave["applied_date"].isoformat()
#     #     if "start_date" in leave and isinstance(leave["start_date"], date):
#     #         leave["start_date"] = leave["start_date"].isoformat()
#     #     if "end_date" in leave and isinstance(leave["end_date"], date):
#     #         leave["end_date"] = leave["end_date"].isoformat()
#     # return leaves"""

 #-----------------------UPDATE LEAVE REQUEST-----------------------------------------------------
def update_leave_status(db: Database, leave_id: str, update_data: dict, approver_id: str = None):    

    leave_request = db["leave_db"].find_one({"_id": ObjectId(leave_id)})     # 1. Fetch leave request
    if not leave_request:
        return None 

    approver_id = update_data.get("approved_by")         #if approved id provided, check authorization of approver   
    if approver_id:                                          
        assigned_manager = leave_request.get("manager_id")
        if assigned_manager and assigned_manager != approver_id:
            raise ValueError("Not authorized to approve this leave request")
        
        
        update_data["approved_by"] = approver_id      #approved_by and approved_at to update_data
        update_data["approved_at"] = datetime.utcnow()
    
    result = db["leave_db"].update_one(              #3. Update leave request
        {"_id": ObjectId(leave_id)},
        {"$set": update_data}
    )

    new_status = update_data.get("status")           #4. if approved, update employee leave balance
    if new_status and new_status.lower() == "approved":
        employee = leave_request["employee_id"]
        leave_type = leave_request.get("leave_type").lower()
        start_date = leave_request.get("start_date")
        end_date = leave_request.get("end_date")
        
        if not start_date or not end_date or not leave_type:
            raise ValueError("Invalid leave request data")

        # Calculate number of days
        days_requested = (end_date - start_date).days + 1

         # Update leave balance
        leave_balance_field = f"{leave_type}_used"
        db["employee_db"].update_one(
            {"_id": ObjectId(employee)},
            {"$inc": {f"leave_balance.{leave_balance_field}": days_requested}})      #$inc operator increments the value of the field by the specified amount. If the field does not exist, it will be created and set to the specified value.
  
    return result



""" Flow
Frontend sends leave ID as string (/leave/6523b4e6a9f09cbd12345678).
Backend converts string → ObjectId to query MongoDB.
MongoDB returns document with _id as ObjectId.
Backend converts _id → string before returning to frontend.
This is standard practice for all MongoDB CRUD APIs."""
















