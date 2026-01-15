from fastapi import Depends,HTTPException
from app.Auth.helper import get_current_user


def require_hr_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "HR":
        raise HTTPException(status_code=403, detail="Not authorized,HR access only")
    return current_user

def require_manager_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "manager":
        raise HTTPException(status_code=403, detail="Not authorized,Manager access only")
    return current_user




























#--------------------GET TODAY'S ATTENDANCE SUMMARY ----------------------------------------
#this code is much better than the code used in crud as it is faster than the previous one 

# def get_today_attendance_summary(db: Database):today = datetime.now().date()
    
#     records = list(db["attendance_db"].find({"date": today}))
    
#     summary = {
#         "present": sum(1 for r in records if r.get("status", "").lower() == "present"), 
#         "absent": sum(1 for r in records if r.get("status", "").lower() == "absent"),
#         "leave": sum(1 for r in records if r.get("status", "").lower() == "leave"),
#         "half_day": sum(1 for r in records if r.get("status", "").lower() == "half-day"),
#         "total": len(records)
#     }
    
#     return summary



#______________________________________________________________________________________________________________________________________________


# IMPORTANT
#using this function instead of  this :-
# @router.get("/employees")
# def list_employees(res: Response, current_user: dict = Depends(require_hr_role),db: Database = Depends(get_db)):
#         if current_user.get("role") != "HR":       <---------------------instead fo this
#             res.status_code = status.HTTP_403_FORBIDDEN
#             return{"message": "Not authorized"}
        
#         try:
#             employees = crud.get_all_employees(db)
#             res.status_code = status.HTTP_200_OK                                                       #this [status] is comming from the crud function in which the status is returing a message = 200 ok
#             return{
#             "message": "Employees data fetched succesfully",
#             "employees": employees
#             }







































