from fastapi import APIRouter, Depends, status,Response, Body
from app.database import get_db
from pymongo.database import Database
import app.HR.crud as crud
from app.Auth.utils import hash_password
from .helper import require_hr_role
from .schemas import (EmployeeRegister,CurrentAddress,PermanentAddress,JobInfo, EmployeeBasicUpdate,Education,WorkExperience,EmployeeSearch,AttendanceCreate,AttendanceUpdate,LeaveApproval)
from typing import Optional
from pydantic import EmailStr
from datetime import datetime
from bson import ObjectId
from app.common.utils import get_leave_request_by_id


#Always convert Pydantic model → dict before passing to CRUD...as mongodb excepts dict only not a pydantic model object.

router = APIRouter()

#---------------Register employee--------------------------------------
@router.post("/register_employee")
def register_employee(employee: EmployeeRegister,res: Response,_current_user: dict = Depends(require_hr_role),db: Database = Depends(get_db)):
    try:
        print(f"DEBUG: Received employee data: {employee.model_dump()}")
        
        if not employee.password:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return{"message": "Password is required for employee registration"}
        
        hashed_password = hash_password(employee.password.strip())
        
        result = crud.create_employee(db, employee, hashed_password)
        res.status_code = result["status"]
        
        # Check if employee was created successfully
        if "employee" in result:
            return {
                "message": result["message"],
                "employee": result["employee"],
            }
        else:
            # Employee already exists or other error
            return {"message": result["message"]}                  #["message"] here is a dictionary key coming from crud.py file in create_employee function
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to register employee"}
    

# ---------------- get list of all employee ----------------------------
@router.get("/employees")
def list_employees(res: Response, _current_user: dict = Depends(require_hr_role),db: Database = Depends(get_db)):
        try:
            employees = crud.get_all_employees(db)
            res.status_code = status.HTTP_200_OK                                                       #this [status] is comming from the crud function in which the status is returing a message = 200 ok
            return{
            "message": "Employees data fetched succesfully",
            "employees": employees
            }
        
        except Exception as e:
            print(f"Error fetching employees: {str(e)}")
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "Failed to fetch employees"}

# ---------------- get employee by _id-----------------------------------
@router.get("/employee/{employee_id}")
def get_employee(employee_id: str, res: Response, _current_user: dict = Depends(require_hr_role),db: Database = Depends(get_db)):
    try:
        employee = crud.get_employee_by_id(db, employee_id)
        if not employee:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
        
        res.status_code = status.HTTP_200_OK
        return{
            "message": "Employee fetched successfully",
            "employee": employee
        }

    except Exception as e:
        print(f"Error fetching employee: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch employee"}


# ---------------- Basic Info ---------------------------------------
@router.put("/employee/{employee_id}/basic")    #error
def update_basic(employee_id: str, payload: EmployeeBasicUpdate, res: Response,
                 db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_employee_basic(db, employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}

    except Exception as e:
        print(f"Error updating basic info: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update basic info"}
    
    res.status_code = status.HTTP_200_OK
    return {"message": "Basic info updated"}


# ---------------- Current Address ----------------------------------
@router.put("/employee/{employee_id}/current_address")
def update_current(employee_id: str, payload: CurrentAddress, res: Response,
                   db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_current_address(db,employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error updating current address: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update current address"}
    
    res.status_code = status.HTTP_200_OK
    return {"message": "Current address updated"}


# ---------------- Permanent Address -----------------------------------
@router.put("/employee/{employee_id}/permanent_address")
def update_permanent(employee_id: str, payload: PermanentAddress, res: Response,
                     db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_permanent_address(db, employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error updating permanent address: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update permanent address"}
    res.status_code = status.HTTP_200_OK
    return {"message": "Permanent address updated"}


# ---------------- Job Info ---------------------------------------------
@router.put("/employee/{employee_id}/job_info")
def update_job(employee_id: str, payload: JobInfo, res: Response,
               db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_job_info(db, employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error updating job info: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update job info"}
    res.status_code = status.HTTP_200_OK
    return {"message": "Job info updated"}

# ---------------- Education Added---------------------------------------
@router.post("/employee/{employee_id}/education")
def add_edu(employee_id: str, payload: Education, res: Response,
            db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        # Convert Pydantic model to dict before saving to MongoDB
        result = crud.add_education(db, employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error adding education: {str(e)}")  # Log to console for debugging
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to add education"}
    res.status_code = status.HTTP_200_OK
    return {"message": "Education info updated"}

# ---------------- Education updated------------------------------------
@router.put("/employee/{employee_id}/education/{index}")
def update_edu(employee_id: str, index: int, payload: Education, res: Response,
               db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_education(db, employee_id, index, payload.model_dump(exclude_unset=True))

        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error updating education: {str(e)}")  # Log to console for debugging
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update education"}
    res.status_code = status.HTTP_200_OK
    return {"message": "Education updated"}
        
#------------------ Work Experience added -------------------------------
@router.post("/employee/{employee_id}/work_experience")
def add_work(employee_id: str, payload: WorkExperience, res: Response,
             db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        # Convert Pydantic model to dict before saving to MongoDB
        result = crud.add_work_experience(db, employee_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error adding work experience: {str(e)}")  # Log to console for debugging
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to add work experience"}
    res.status_code = status.HTTP_200_OK    
    return {"message": "Work experience added"}

#----------------- Work Experience updated -----------------------------
@router.put("/employee/{employee_id}/work_experience/{index}")
def update_work(employee_id: str, index: int, payload: WorkExperience, res: Response,
                db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        # Convert Pydantic model to dict before saving to MongoDB
        result = crud.update_work_experience(db, employee_id, index, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error updating work experience: {str(e)}")  # Log to console for debugging
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to update work experience"}
    res.status_code = status.HTTP_200_OK
    return {"message": "Work experience updated"}
   
#---------search employees by anything in SEARCH BAR---------------------
@router.post("/employees/search")
def search_employee(payload:EmployeeSearch,res: Response,db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.search_employees(db, payload)
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
        
        res.status_code = status.HTTP_200_OK
        return{"message":f"{len(result)} employees found"}
    
    except Exception as e:
        print(f"Error searching employees: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to search employees"}
        
# why i didn"t use ""(if result.matched_count == 0:)"" because here we are fetching multiple employees not single and even in CRUD.PY we are returning a list of employee and list doesn't have .matched_count attribute..its only in the update_one/delete_one methodd 0R single document fetch method
  
# ==================================================================================

# ---------Activate employee (mark as active/at work)---------------------
@router.put("/employee/{employee_id}/activate")
def activate_employee(employee_id: str, res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    """Activate an employee - marks them as active and at work"""
    try:
        result = crud.activate_employee(db, employee_id)
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Employee activated successfully"}
    
    except Exception as e:
        print(f"Error activating employee: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to activate employee"}

# ---------Deactivate employee (soft delete)---------------------
@router.delete("/employee/{employee_id}")
def deactivate_employee(employee_id: str,res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    """Deactivate an employee - marks them as inactive (soft delete)"""
    try:
        result = crud.deactivate_employee(db, employee_id)
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Employee deactivated successfully"}
    
    except Exception as e:
        print(f"Error deactivating employee: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to deactivate employee"}
    
# ==================================================================================
# -----------ATTENDANCE--------------------------------------------------------------
@router.post("/attendance/mark")
def mark_attendance(payload: AttendanceCreate,res: Response, db: Database = Depends(get_db),_current_user: dict = Depends(require_hr_role)
):
    try:
        if payload.email and not payload.employee_id:
            emp = crud.get_by_email(db, payload.email.lower().strip())
            if not emp:
                res.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Employee not found"}
            payload.employee_id = str(emp["_id"])
        
        elif payload.employee_id:
            emp = crud.get_employee_by_id(db, payload.employee_id)
            if not emp:
                res.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Employee not found"}
        
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Provide employee_id or email"}
        
        # Mark attendance
        crud.add_attendance(db, payload.model_dump())
        res.status_code = status.HTTP_201_CREATED
        return {"message": "Attendance marked successfully"}
        
    except Exception as e:
        print(f"Error marking attendance: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to mark attendance"}
    
#--------fetch_attendance(For SEARCHING/FILTERING attendance)------------------
@router.get("/attendance")
def fetch_attendance(employee_id: Optional[str] = None, email: Optional[EmailStr] = None, date: Optional[str] = None, res: Response = None, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        query = {}                    # Convert email to employee_id if provided .
        
        if email and not employee_id:
            emp = crud.get_by_email(db, email.lower().strip())
            if not emp:
                res.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Employee not found"}
            employee_id = str(emp["_id"])
        

        if employee_id:                         # Built query filter =  # Filter by employee_id 
            query["employee_id"] = employee_id
        if date:
            query["date"] = date                # Filter employee by date 
        
        result = crud.get_attendance(db, query)
        res.status_code = status.HTTP_200_OK
        return {"message": f"{len(result)} records found", "data": result}
        
    except Exception as e:
        print(f"Error fetching attendance: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch attendance"}

#----------GET TODAY'S ATTENDANCE SUMMARY-------------------------------------
@router.get("/attendance/summary/today")
def get_today_summary(res: Response,db: Database = Depends(get_db),_current_user: dict = Depends(require_hr_role)):      # Returns count of Present, Absent, Leave, Half-Day for today
    try:
        result = crud.get_today_attendance_summary(db)
        res.status_code = status.HTTP_200_OK
        return {
            "message": "Today's attendance summary",
            "summary": result
        }
    except Exception as e:
        print(f"Error fetching attendance summary: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch attendance summary"}

#----------UPDATE_Attendance-------------------------------------------------
@router.put("/attendance/{employee_id}/{date}")
def modify_attendance(employee_id: str, date: str,payload: AttendanceUpdate,res: Response = None,db=Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_attendance(db, employee_id, date, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Attendance record not found"}
        res.status_code = status.HTTP_200_OK
        return {"message": "Attendance updated successfully"}
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}



# ======================LEAVE MANAGEMENT ============================================================
#--------------------GET ALL LEAVE REQUESTS --------------------------------------------------------

@router.get("/leaves")
def fetch_all_leaves(res: Response,db: Database = Depends(get_db),_current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.get_all_leave_requests(db)
       
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No leave requests found"}
            
        res.status_code = status.HTTP_200_OK
        return {"message": f"{len(result)} leave request found", "data": result}
    except Exception as e:
        print(f"Error fetching leaves: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch leaves"}
    

#--------------------GET LEAVE REQUEST BY ID -------------------------------------------------------
@router.get("/leave/{leave_id}")
def fetch_leave_by_id(leave_id : str,res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = get_leave_request_by_id(db,leave_id)      
           
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "leave request not found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Leave request found", "data": result}
    
    except Exception as e:
        print(f"Error fetching leave: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch leave"}

#-------------------GET PENDING LEAVES ONLY ------------------------------------------------
@router.get("/leaves/pending")
def fetch_pending_leaves(res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.get_all_leave_requests(db, query={"status": "Pending"})
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No pending leave requests found"}

    
        res.status_code = status.HTTP_200_OK
        return {"message": f"{len(result)} pending leave request found", "data": result}
    
    except Exception as e:
        print(f"Error fetching pending leaves: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch pending leaves"}

#-------------------GET APPROVED LEAVES ONLY ------------------------------------------------
@router.get("/leaves/approved")
def fetch_approved_leaves(res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.get_all_leave_requests(db, query={"status": "Approved"})
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No approved leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": f"{len(result)} approved leave request found", "data": result}
    
    except Exception as e:
        print(f"Error fetching approved leaves: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch approved leaves"}

#-------------------GET REJECTED LEAVES ONLY ------------------------------------------------
@router.get("/leaves/rejected")
def fetch_rejected_leaves(res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.get_all_leave_requests(db, query={"status": "Rejected"})
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No rejected leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": f"{len(result)} rejected leave request found", "data": result}
    
    except Exception as e:
        print(f"Error fetching rejected leaves: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch rejected leaves"}

#-------------------LEAVE BALANCE UPDATE ------------------------------------------------------
@router.get("/hr/employee/{employee_id}/leave_balance")
def get_leave_balance(employee_id: str, res: Response, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        employee = db["employee_db"].find_one({"_id": ObjectId(employee_id)})
        if not employee:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee not found"}
        
        leave_balance = employee.get("leave_balance",{})
        res.status_code = status.HTTP_200_OK
        return {"employee_id": employee_id, "leave_balance": leave_balance}
    
    except Exception as e:
        print(f"Error fetching leave balance: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to fetch leave balance"}


#remove this route as HR will nto approve/reject the leave rquest,only assigned manager will do it 
"""#----------------------UPDATE LEAVE STATUS ACCEPT/REJECT -------------------------------------------
@router.put("/leave/{leave_id}")
def update_leave_status(leave_id : str,res: Response, payload: LeaveApproval, db: Database = Depends(get_db), _current_user: dict = Depends(require_hr_role)):
    try:
        result = crud.update_leave_status(db, leave_id, payload.model_dump(exclude_unset=True))
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Leave request updated successfully"}
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}"""