#PRACTICE FILE 

# @router.post("/register_employee")
# def register_employee(employee: EmployeeRegister,res: Response,current_user: dict = Depends(get_current_user),db: Database = Depends(get_db)):
#     try:
#         if current_user.get("role") != "HR":
#             res.status_code = status.HTTP_403_FORBIDDEN
#             return {"message": "Not authorized"}
        
#         temp_password = generate_temporary_password()
#         hashed_password = hash_password(temp_password)
        
#         result = crud.create_employee(db, employee, hashed_password)
        
        
#         res.status_code = result["status"]
#         return {
#             "message": "Employee registered successfully",
#             "employee": result["employee"],
#             "temporary_password": temp_password
#         }
        
#     except Exception as e:
#         print(f"Registration error: {str(e)}")
#         res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return {"message": f"Error: {str(e)}"}


# ====================================================================
# #---------search employee by anything in SEARCH BAR-------------------
# def search_employees(db, search_params: EmployeeSearch):
#     query = {}

#     if search_params.first_name:
#         query["first_name"] = {"$regex": search_params.first_name, "$options": "i"}
#     if search_params.last_name:
#         query["last_name"] = {"$regex": search_params.last_name, "$options": "i"}
#     if search_params.department:
#         query["job_info.department"] = {"$regex": search_params.department, "$options": "i"}
#     if search_params.designation:
#         query["job_info.designation"] = {"$regex": search_params.designation, "$options": "i"}
#     if search_params.job_title:
#         query["job_info.job_title"] = {"$regex": search_params.job_title, "$options": "i"}

#     employees = list(db["employee_db"].find(query, {"password": 0}))
#     for emp in employees:
#         emp["_id"] = str(emp["_id"])
#     return employees

# ====================================================================

# class EmployeeRegister(BaseModel):
#     first_name: str
#     last_name: Optional[str] = None
#     email: EmailStr
#     password: str
#     phone: Optional[str] = None
#     gender: Optional[str] = None
#     dob: Optional[datetime] = None
#     blood_group: Optional[str] = None
#     material_status: Optional[str] = None
#     emergency_contact: Optional[str] = None
#     official_email: Optional[EmailStr] = None
#     role: Optional[str] = "employee"   


# class EmployeeBasicUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     phone: Optional[str] = None
#     gender: Optional[str] = None
#     dob: Optional[datetime] = None
#     blood_group: Optional[str] = None
#     material_status: Optional[str] = None
#     emergency_contact: Optional[str] = None
#     official_email: Optional[EmailStr] = None


# ===============REGISTER NEW EMPLOYEE IN CRUD.PY ===========================
##------------------------------------------------------------------------------------------
# @router.post("/register_employee")
# def register_employee(employee: EmployeeRegister,res: Response,current_user: dict = Depends(get_current_user),db: Database = Depends(get_db)):
#     try:
#         if current_user.get("role") != "HR":
#             res.status_code = status.HTTP_403_FORBIDDEN
#             return {"message": "Not authorized"}
        
#         if not employee.password:
#             res.status_code = status.HTTP_400_BAD_REQUEST
#             return{"message": "Password is required for employee registration"}
        
#         hashed_password = hash_password(employee.password.strip())
        
#         result = crud.create_employee(db, employee, hashed_password)
#         res.status_code = result["status"]
#         return {
#             "message": "Employee registered successfully",
#             "employee": result["employee"],
#         }
#     except Exception as e:
#         print(f"Registration error: {str(e)}")
#         res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return {"message": f"Error: {str(e)}"}





















































# @router.post("/register_employee")
# def register_employee(employee: EmployeeRegister,res: Response,current_user: dict = Depends(get_current_user),db: Database = Depends(get_db)):
#     try:
#         if current_user.get("role") != "HR":
#             res.status_code = status.HTTP_403_FORBIDDEN
#             return {
#                 "message": "Not authorized",
#                 "status": status.HTTP_403_FORBIDDEN
#             }

#         result = crud.create_employee(db, employee)     #from CRUD.py add employee to db

#         password = generate_temporary_password()       #send temporary password to empoyee email 
#         send_password_email(employee.email,password)

#         res.status_code = result["status"]
#         return {
#             "status": result["status"],
#             "message": "Employee registered & password sent",
#             "employee": result.get("employee"),
#         }
#         # return result

#     except Exception as e:
#         print("FOR DEBUG: Error occurred =", str(e))
#         res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return {
#             "message": (f"An error occurred: {str(e)}"),
#             "status": status.HTTP_500_INTERNAL_SERVER_ERROR
#         }




























