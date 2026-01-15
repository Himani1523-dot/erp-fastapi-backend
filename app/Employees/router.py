from fastapi import APIRouter, Depends, Response, status, UploadFile, File , Form
from pymongo.database import Database
from app.HR import crud as hr_crud
from app.database import get_db  
from app.Auth.helper import get_current_user
from app.Employees.crud import login_employee,get_employee_profile,update_employee_self,update_employee_address,get_attendance_records,create_employee_leave,get_employee_leaves,cancel_leave_request,create_budget_request
from app.Employees.schemas import EmployeeLogin,EmployeeSelfUpdate,EmployeeAddressUpdate,EmployeeLeaveRequest,EmployeeBudgetRequest
from app.common.utils import get_leave_request_by_id
import os
import shutil
from datetime import datetime

router = APIRouter()

@router.post("/employee_login")
def employee_login(payload: EmployeeLogin, res: Response, db: Database = Depends(get_db)):
    result = login_employee(db, payload.email, payload.password)
    if not result:
        res.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid email or password", 
                "status": status.HTTP_401_UNAUTHORIZED}
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
    }

#=========================================================================================================
#===================HOME PAGE ============================================================================
#------------------ GET OWN FULL PROFILE -----------------------------------------------------------------
@router.get("/profile")
def get_my_profile(res: Response,current_user: dict = Depends(get_current_user),db: Database = Depends(get_db)):
    try:
        if current_user.get("role") not in ["employee", "manager"]:  #manager
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Access denied, Not authorized"}
        
        profile = get_employee_profile(db, current_user["email"])   #will check the email of logged in user and fetch its profile 
        if not profile:
            res.status_code = status.HTTP_404_NOT_FOUND
            return{"message": "Profile not found"}  
        
        res.status_code = status.HTTP_200_OK
        return{
            "message": "Profile fetched successfully",
            "profile": profile
        }
    except Exception as e:
        print(f"Profile fetch error: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "An error occurred while fetching the profile",
            "error":f"Error: {str(e)}"       
            }
    
#-------------------UPDATE PERSONAL PROFILE INFO ---------------------------------------------------------
@router.put("/profile/personal_info")
def update_my_profile( payload: EmployeeSelfUpdate,res: Response, current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    if current_user.get("role") not in ["employee", "manager"]:
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Access denied"}
    
    try:
        update_data = payload.model_dump(exclude_unset=True)    
        if not update_data:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "No data provided for updata"}
        
        result = update_employee_self(db, current_user["email"],update_data)
   
        if result.modified_count == 0:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "No changes made to the profile"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": "Profile information updated successfully"
        }
    
    except Exception as e:
        res.status_coode = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "An error occurred while updating the profile",
            "error": f"Error: {str(e)}"
        }
    
#------------------UPDATE CURRENT ADDRESS ----------------------------------------------------------------
@router.put("/profile/current_address")
def update_my_address(payload: EmployeeAddressUpdate,res: Response,current_user:  dict = Depends(get_current_user),db: Database = Depends(get_db)):
    if current_user.get("role") not in ["employee", "manager"]:
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Access denied"}
    try:
        address_data = payload.model_dump(exclude_unset=True)
        if not address_data:
             res.status_code = status.HTTP_400_BAD_REQUEST
             return {"message": "No address data provided for update"}
        
        result = update_employee_address(db, current_user["email"], address_data)
        if result.modified_count == 0:
             res.status_code = status.HTTP_400_BAD_REQUEST
             return {"message": "No changes made to the address"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Address updated successfully"}
 
    except Exception as e:
         res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
         return {
            "message": "An error occurred while updating the profile",
            "error": f"Error: {str(e)}"
        }
    
#-----------------------VIEW OWN ATTENDANCE-----------------------------------------------------------------------------------
@router.get("/attendance")
def view_my_attendance(res: Response, current_user: dict = Depends(get_current_user),db: Database = Depends(get_db), start_date: str =None, end_date: str = None):
    if current_user.get("role") not in ["employee", "manager"]:
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "Access denied"}
    
    try:
         profile = hr_crud.get_by_email(db, current_user["email"])
         if not profile:
              res.status_code = status.HTTP_404_NOT_FOUND
              return {"message": "Employee Profile not found"}
         
         employee_id = str(profile["_id"])
         
         attendance_records = get_attendance_records(db, employee_id ,start_date,end_date)
         res.status_code = status.HTTP_200_OK
         return {
              "message": f"{len(attendance_records)} Attendance records fetched successfully",
              "attendance": attendance_records
              }
    except Exception as e:
         res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
         return {
            "message": "An error occurred while updating the profile",
            "error": f"Error: {str(e)}"
        }

#=======================LEAVE MANAGEMENT (EMPLOYEE) ==================================================================
#-----------------------APPLY FOR LEAVE-------------------------------------------------------------------------------
@router.post("/leave-request")
def apply_leave(payload: EmployeeLeaveRequest, res: Response, current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    
    if current_user.get("role") not in ["employee", "manager"]:    #only employee and manager can apply leave
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Access denied"}
    
    try:
        # Get employee profile to get employee_id
        profile = hr_crud.get_by_email(db, current_user["email"])
        if not profile:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee profile not found"}
        
        employee_id = str(profile["_id"])
        employee_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()   #will get first name and last name(if exist) from profile and concatenate them with a space in between. and strip() is used to remove any leading or trailing spaces.
        
        # Create leave request data
        leave_data = payload.model_dump()                                                          #model_dump() in old python version was written as model.dict() ..means convert pydantic model (mtlb schema) to a dict so that data can be easily sent to database into dict form.
        leave_data['employee_name'] = employee_name
        leave_data['email'] = current_user["email"]
        
        # Create leave request
        leave_id = create_employee_leave(db, employee_id, leave_data)
        
        res.status_code = status.HTTP_201_CREATED
        return {
            "message": "Leave request submitted successfully",
            "leave_id": leave_id
        }
    
    except ValueError as ve:                     # Handle validation errors (insufficient leave balance, no manager assigned, etc.)
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ve)}             #str(ve) will convert the ValueError exception msg to string. So the exact text inside raise ValueError("...") from crud.py 112 is what the user will see in the response message.
    
    except Exception as e:
        print(f"Leave application error: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to submit leave request. Please try again."}

#-----------------------VIEW OWN LEAVES-------------------------------------------------------------------------------
@router.get("/leaves")
def view_my_leaves(res: Response, current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    if current_user.get("role") not in ["employee", "manager"]:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Access denied"}
    
    try:
        # Get employee profile to get employee_id
        profile = hr_crud.get_by_email(db, current_user["email"])
        if not profile:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee profile not found"}
        
        employee_id = str(profile["_id"])
        
        leaves = get_employee_leaves(db, employee_id)     # Get all leaves of my profile
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(leaves)} leave records found",
            "data": leaves
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "An error occurred while fetching leaves",
            "error": f"Error: {str(e)}"
        }

#-----------------------CANCEL OWN PENDING LEAVE-------------------------------------------------------------------------------
@router.delete("/leave/{leave_id}")
def cancel_leave(leave_id: str, res: Response, current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    if current_user.get("role") not in ["employee", "manager"]:
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Access denied"}

    try:
        # Get employee profile
        profile = hr_crud.get_by_email(db, current_user["email"])
        if not profile:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee profile not found"}
        
        employee_id = str(profile["_id"])
        
        # Get leave to verify 
        leave = get_leave_request_by_id(db, leave_id)
        if not leave:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found"}
        
        # Check if leave belongs to this employee
        if leave.get("employee_id") != employee_id:                                  #leave is that dictionary representing the leave request.
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "You can only cancel your own leave requests"}
        
        # Check if leave is still pending
        if leave.get("status") != "Pending":
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Cannot cancel leave with status: {leave.get('status')}"}
        
        # Delete the leave request
        deleted_count = cancel_leave_request(db, employee_id, leave_id)
        if deleted_count == 0:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Failed to cancel leave request"}
        
        res.status_code = status.HTTP_200_OK
        return {"message": "Leave request cancelled successfully"}
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "An error occurred while cancelling leave",
            "error": f"Error: {str(e)}"
        }

#=======================BUDGET REQUEST MODULE======================================================
#===============Create Budget request===============================================================
@router.post("/budget-request")
async def create_request(
    title: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    justification: str = Form(...),
    expected_date: str = Form(...),
    attachment: UploadFile = File(None),  # File upload
    res: Response = None,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if current_user.get("role") != "employee":
        res.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Access denied"}
    
    try:
        # Get employee profile to get employee_id
        profile = hr_crud.get_by_email(db, current_user["email"])
        if not profile:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Employee profile not found"}
        
        employee_id = str(profile["_id"])
        
        # Handle file upload if attachment is provided
        attachment_url = None
        if attachment:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/budget_attachments"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(attachment.filename)[1]
            unique_filename = f"{employee_id}_{timestamp}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file locally
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(attachment.file, buffer)
            
            attachment_url = file_path
        
        # Create budget request data
        budget_data = {
            "title": title,
            "category": category,
            "amount": amount,
            "justification": justification,
            "expected_date": expected_date,
            "attachment_url": attachment_url
        }
        
        # Create budget request
        budget_id = create_budget_request(db, employee_id, budget_data)
        
        res.status_code = status.HTTP_201_CREATED
        return {
            "message": "Budget request submitted successfully",
            "budget_id": budget_id
        }
    
    except ValueError as ve:                     # Handle validation errors (no manager assigned, etc.)
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ve)}
    
    except Exception as e:
        print(f"Budget request error: {str(e)}")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "Failed to submit budget request. Please try again.",
            "error": f"Error: {str(e)}"
        }





    



    





