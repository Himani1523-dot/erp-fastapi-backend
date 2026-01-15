from fastapi import APIRouter, Depends, Response , status
from pymongo.database import Database
from app.database import get_db
from app.Auth.helper import get_current_user
from app.HR.schemas import LeaveApproval
from app.HR.crud import get_all_leave_requests,update_leave_status
from bson import ObjectId
from app.HR.helper import require_manager_role
from datetime import datetime

router = APIRouter()

# ============= MANAGER LEAVE APPROVAL ROUTES ====================================
# -------------------GET MY TEAM'S PENDING LEAVES (Manager only) -----------------
@router.get("/manager/leaves/pending")
def fetch_my_team_pending_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        manager_email = current_user.get("email")                                   #Use email instead of _id,Filter leaaves where current user is the assigned manager
        print(f"🔍 DEBUG - Manager's email: {manager_email}")
        query = {"manager_id": manager_email, "status": "Pending"}
        
        result = get_all_leave_requests(db, query=query)                             #query= query , means in crud.py the parameter is query = None
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No pending leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} pending leave request(s) found for your team",
            "data": result
        }
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}

#ISSUE -------------------GET MY TEAM'S PENDING LEAVES (Manager only) -----------------
"""@router.get("/manager/leaves/pending")
def fetch_my_team_pending_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        user_id = str(current_user["_id"])       #filter leaaves where current user is the assigned manager
        query = {"manager_id": user_id,
                 "status": "Pending"
                 }
        
        result = get_all_leave_requests(db, query = query)  #why query = query bcuz in crud.py the parameter is query = None
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No pending leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} pending leave request(s) found for your team",
            "data": result
        }
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}"""

#-------------------APPROVE/REJECT LEAVE (assigned Manager only) -------------------------
@router.put("/manager/leave/{leave_id}/approve")
def approve_team_leave(leave_id: str, res: Response, payload: LeaveApproval, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        manager_email = current_user.get("email")  # Use email instead of _id

        leave_request = db["leave_db"].find_one({"_id": ObjectId(leave_id)})

        if not leave_request:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found"}
        
        # Verify current user is the assigned manager
        if leave_request.get("manager_id") != manager_email:
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "You are not authorized to approve this leave request"}
        
        update_data = payload.model_dump(exclude_unset=True)
        update_data["approved_by"] = manager_email
        update_data["approved_at"] = datetime.utcnow()

        result = update_leave_status(db, leave_id, update_data)
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found "}
        
        res.status_code = status.HTTP_200_OK
        return {"message": f"Leave request {payload.status.lower()} successfully"}
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}

#ERROR-------------------APPROVE/REJECT LEAVE (assigned Manager only) -------------------------
"""@router.put("/manager/leave/{leave_id}/approve")
def approve_team_leave(leave_id: str, res: Response, payload: LeaveApproval,db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        user_id = str(current_user["_id"]) 

        leave_request = db["leave_db"].find_one({"_id": ObjectId(leave_id)})     

        if not leave_request:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found"}
        
         # Verify current user is the assigned manager
        if leave_request.get("manager_id") != user_id:
            res.status_code = status.HTTP_403_FORBIDDEN
            return {"message": "You are not authorized to approve this leave request"}
        
        update_data = payload.model_dump(exclude_unset=True)  #exclude_unset=True means only include fields that were explicitly set in the request payload
        update_data["approved_by"] = user_id
        update_data["approved_at"] = datetime.utcnow()

        result = update_leave_status(db, leave_id, update_data)
        if result.matched_count == 0:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Leave request not found "}
        
        res.status_code = status.HTTP_200_OK
        return {"message": f"Leave request {payload.status.lower()} successfully"}
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}"""

#-------------------GET MY TEAM'S ALL LEAVES (All statuses - Manager) --------------------------
@router.get("/manager/leaves")
def fetch_my_team_all_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        manager_email = current_user.get("email")  # Use email instead of _id
        print(f"🔍 DEBUG - Manager's email: {manager_email}")
        query = {"manager_id": manager_email}    # Get ALL leaves (Pending, Approved, Rejected)
        
        result = get_all_leave_requests(db, query=query)
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No leave requests for your team"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} leave request(s) for your team", 
            "data": result
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}

#-------------------GET MY TEAM'S APPROVED LEAVES (Manager) --------------------------
@router.get("/manager/leaves/approved")
def fetch_my_team_approved_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        manager_email = current_user.get("email")
        query = {"manager_id": manager_email, "status": "Approved"}
        
        result = get_all_leave_requests(db, query=query)
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No approved leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} approved leave request(s) found", 
            "data": result
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}

#-------------------GET MY TEAM'S REJECTED LEAVES (Manager) --------------------------
@router.get("/manager/leaves/rejected")
def fetch_my_team_rejected_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        manager_email = current_user.get("email")
        query = {"manager_id": manager_email, "status": "Rejected"}
        
        result = get_all_leave_requests(db, query=query)
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No rejected leave requests found"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} rejected leave request(s) found", 
            "data": result
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}

#-------------------GET MY TEAM'S ALL LEAVES (Manager) --------------------------
"""@router.get("/manager/leaves")
def fetch_my_team_all_leaves(res: Response, db: Database = Depends(get_db), current_user: dict = Depends(require_manager_role)):
    try:
        user_id = str(current_user["_id"])      #converting manager ObjectID into str
        print(f"🔍 DEBUG - Manager's _id: {user_id}")
        print(f"🔍 DEBUG - Manager's email: {current_user.get('email')}")
        query = {"manager_id": user_id,"status": "Pending"}
        
        result = get_all_leave_requests(db, query=query)   #crud
        
        if not result:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "No leave requests for your team"}
        
        res.status_code = status.HTTP_200_OK
        return {
            "message": f"{len(result)} leave request(s) for your team", 
            "data": result
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Error: {str(e)}"}"""


        
