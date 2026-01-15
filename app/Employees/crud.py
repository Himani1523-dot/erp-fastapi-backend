from pymongo.database import Database
from app.Auth.utils import verify_password, create_access_token
from datetime import timedelta, datetime, date
from bson import ObjectId
import os
from app.common.utils import serialize_leave, serialize_attendance

ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", 30))

def login_employee(db:Database, email: str, password: str):
    print("🔹 Attempting login for email:", email)
    employee = db["employee_db"].find_one({"email" : email , "role": "employee"})      #find employee with role 
    if not employee:
        print(" Employee not found or role mismatch")
        return None
    
    print(" Employee found:", employee["email"])
    print("Stored hashed password:", employee["password"])
    print("Password provided:", password)

    if not verify_password(password,employee["password"]):
        print(" Password verification failed")
        return None 
    
    print("Password verified, creating access token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN)


    # Create JWT
    token = create_access_token(
        data={"sub": employee["email"], "role": "employee"},
        expires_delta=access_token_expires
    )
    
    return{
        "access_token" : token,
        "token_type" : "bearer",
        "role" : "employee",
        "email": employee["email"]
        }

#=========================================================================================================
#===================HOME PAGE ========================================================================
#------------------ GET OWN FULL PROFILE --------------------------------
def get_employee_profile(db: Database, email: str):                # Employee/Manager can view their own full profile
    # Allow both employees and managers
    employee = db["employee_db"].find_one({"email": email, "role": {"$in": ["employee", "manager"]}}, {"password": 0})
    if employee:
        employee["_id"] = str(employee["_id"])
    return employee

#-------------------UPDATE OWN PROFILE ------------------------------------
def update_employee_self(db: Database, email: str, update_data: dict):         
    # Allow both employees and managers to update their profile
    return db["employee_db"].update_one(
        {"email": email, "role": {"$in": ["employee", "manager"]}},
        {"$set": update_data}
    )

#------------------ UPDATE CURRENT ADDRESS --------------------------------
def update_employee_address(db: Database, email: str, address_data: dict):
    # Allow both employees and managers to update address
    return db["employee_db"].update_one(
        {"email": email, "role": {"$in": ["employee", "manager"]}},
        {"$set": {"current_address": address_data}}
    )

#=========================ATTENDANCE================================================
#CHECK--------------------VIEW OWN ATTENDANCE --------------------------------------
def get_attendance_records(db: Database, employee_id: str, start_date=None, end_date=None):
    query = {"employee_id": employee_id}
    
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    attendance_records = list(db["attendance_db"].find(query, {"_id": 0}).sort("date", -1))
    # Serialize each attendance record with employee details
    return [serialize_attendance(record, db) for record in attendance_records]


#=======================APPLY LEAVE MODULE ====================================================
#FIXED CODE -----------------------CREATE LEAVE-----------------------------------------------------------
def create_employee_leave(db: Database, employee_id: str, leave_data: dict):
    # Convert date objects to datetime for MongoDB compatibility
    if "start_date" in leave_data and isinstance(leave_data["start_date"], date):
        leave_data["start_date"] = datetime.combine(leave_data["start_date"], datetime.min.time())
    if "end_date" in leave_data and isinstance(leave_data["end_date"], date):
        leave_data["end_date"] = datetime.combine(leave_data["end_date"], datetime.min.time())

    # 1: Get employee's leave balance
    employee = db["employee_db"].find_one({"_id": ObjectId(employee_id)})
    if not employee:
        raise ValueError("Employee not found")
    
    # 2: Get reporting manager id
    manager_id = employee["job_info"].get("reporting_manager")
    if not manager_id:
        raise ValueError("No reporting manager assigned to employee")
    
    leave_type = leave_data.get("leave_type").lower()
    total = employee["leave_balance"].get(f"{leave_type}", 0)
    used = employee["leave_balance"].get(f"{leave_type}_used", 0)

    #3. Calculate number of days leave requested
    start_date = leave_data.get("start_date")
    end_date = leave_data.get("end_date")
    day_requested = (end_date - start_date).days + 1
    
    #4. Check if enough leave balance is available
    if used + day_requested > total:            
        raise ValueError(f"Not enough {leave_type} balance. Available: {total - used} days")
    
    #5.IMPORTANT FIX: Store both IDs as STRINGS for consistency
    # This matches how manager queries (using string user_id)
    leave_data.update({
        "employee_id": str(employee_id),      # Always string
        "manager_id": str(manager_id),        # Always string - THIS IS THE FIX!
        "status": "Pending",
        "created_at": datetime.now(),
        "applied_date": datetime.now(),
        "approved_by": None,
        "approved_date": None,
        "remarks": None,
        "days_requested": day_requested
    })
    
    result = db["leave_db"].insert_one(leave_data)
    return str(result.inserted_id)


#serialize all---------------------GET MY ALL LEAVES(---------------------------------------------
def get_employee_leaves(db:Database, employee_id: str):
    query = {"employee_id": employee_id}
    leaves = list(db["leave_db"].find(query))
    return [serialize_leave(leave, db) for leave in leaves]  #Pass db to fetch manager name

#------------------------CANCEL LEAVE---------------------------------------------------
def cancel_leave_request(db: Database, employee_id: str, leave_id: str):
    result = db["leave_db"].delete_one({
        "_id": ObjectId(leave_id), 
        "employee_id": employee_id, 
        "status": "Pending"
    })
    return result.deleted_count

#----------------------- UPDATE LEAVE STATUS (Not used in Employee module) --------------
def update_leave_status(db: Database, leave_id: str, update_data: dict):
    result = db["leave_db"].update_one(
        {"_id": ObjectId(leave_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

#=======================BUDGET REQUEST MODULE======================================================
#===============Create Budget request===============================================================
def create_budget_request(db: Database,employee_id: str, request_data:dict):
    employee = db["employee_db"].find_one({"_id": ObjectId(employee_id)})
    if not employee:
        raise ValueError("Employee not found")
   
    #get manager id 
    manager_id = employee.get("job_info",{}).get("reporting_manager")
    if not manager_id:
        raise ValueError("No reporting manager assigned to this employee")
    
    # Get manager details
    manager = db["employee_db"].find_one({"_id": ObjectId(manager_id)})
    if not manager:
        raise ValueError("Reporting manager not found in system")
    
    request_data.update({
        "employee_id" : str(employee_id),
        "employee_name": f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip(),
        "department" : employee.get("job_info",{}).get("department", ""),
        "manager_id": str(manager_id),
        "manger_name": employee["job_info"].get("reporting_manager", ""),
        "status": "Pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "approved_by": None,
        "approved_date": None,
        "remarks": None
    })
    result = db["budget_request_db"].insert_one(request_data)
    return str(result.inserted_id)

#----------------------GET MY BUDGET REQUESTS -------------------------------------------------
def get_employee_budget_requests(db: Database, employee_id: str):
        requests = list(db["budget_requests"].find({"employee_id": employee_id}))
        return requests
            
#----------------------CANCEL BUDGET REQUEST ---------------------------------------------------
def cancel_budget_request(db: Database, employee_id: str, request_id: str):
    result = db["budget_requests"].delete_one({
        "_id": ObjectId(request_id),
        "employee_id": employee_id,
        "status": "Pending"
    })
    return result.deleted_count






