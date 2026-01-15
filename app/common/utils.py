from datetime import datetime,date 
from bson import ObjectId
from pymongo.database import Database



#===========LEAVE MODULE ===========================================
#----------Serialize leave docs to json safe format -----------------

def serialize_leave(leave: dict, db: Database = None):
    leave["_id"] = str(leave["_id"])                                                           #Convert Mongo leave document fields to JSON-safe format
    for key, value in leave.items():
        if isinstance(value,(datetime,date)):                                                  #isinstance() requires a tuple when checking multiple types: (datetime, date)
            leave[key] = value.isoformat()
   
    # Fetch employee name and email if db is provided
    if db is not None and "employee_id" in leave:                                              #MongoDB Database objects don't support if db: check. You need if db is not None:.
        employee = db["employee_db"].find_one({"_id": ObjectId(leave["employee_id"])})
        if employee:
            leave["employee_name"] = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
            leave["email"] = employee.get("email", "N/A")
    
    # Fetch manager name and email who approved (if approved_by exists)
    if db is not None and "approved_by" in leave and leave["approved_by"]:
        # approved_by is now stored as email (string), not ObjectId
        manager = db["employee_db"].find_one({"email": leave["approved_by"]})
        if manager:
            leave["approved_by_name"] = f"{manager.get('first_name', '')} {manager.get('last_name', '')}".strip()
            leave["approved_by_email"] = manager.get("email", "N/A")
        else:
            leave["approved_by_name"] = "Unknown"
            leave["approved_by_email"] = "N/A"
    else:
        leave["approved_by_name"] = None
        leave["approved_by_email"] = None
    #####
    return leave

""" OLDER CODE  = not good if the field increases in future=============
 def serialize_leave(leave: dict) -> dict:
    
    leave["_id"] = str(leave["_id"])
     for field in ["created_at", "applied_date", "start_date", "end_date"]:
        if field in leave and isinstance(leave[field], (datetime, date)):
             leave[field] = leave[field].isoformat()
     return leave """

#===========ATTENDANCE MODULE ===========================================
#----------Serialize attendance docs to json safe format -----------------
def serialize_attendance(attendance: dict, db: Database = None):
    """Convert attendance document to JSON-safe format with employee details"""
    # Serialize datetime fields to ISO format
    for key, value in attendance.items():
        if isinstance(value, (datetime, date)):
            attendance[key] = value.isoformat()
    
    # Fetch employee details if db is provided and employee_id exists
    if db is not None and "employee_id" in attendance:
        employee_id = attendance["employee_id"]
        try:
            employee = db["employee_db"].find_one(
                {"_id": ObjectId(employee_id)},
                {"first_name": 1, "last_name": 1, "job_info.department": 1}
            )
            if employee:
                # Add employee name
                first_name = employee.get("first_name", "")
                last_name = employee.get("last_name", "")
                attendance["employee_name"] = f"{first_name} {last_name}".strip()
                
                # Add department from job_info
                job_info = employee.get("job_info", {})
                attendance["department"] = job_info.get("department", "N/A")
            else:
                attendance["employee_name"] = "Unknown"
                attendance["department"] = "N/A"
        except Exception as e:
            print(f"Error fetching employee details for {employee_id}: {str(e)}")
            attendance["employee_name"] = "Unknown"
            attendance["department"] = "N/A"
    
    return attendance


#----------CONVERT Date to datetime ----------------------------------------------------------------------------------
def date_to_datetime(date_obj: date):
    """Convert a date object to datetime object"""
    return datetime.combine(date_obj, datetime.min.time())
    


#---------------get leave for its unique object_id -------------------------------------------------------------------
def get_leave_request_by_id(db: Database, leave_id: str):
    Leave = db["leave_db"].find_one({"_id": ObjectId(leave_id)})           # Convert leave_id to ObjectId as its comming from the frontend 
    if Leave:
         return serialize_leave(Leave, db)  # Add db parameter
    return None

   
