from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
from app.Auth.helper import EmailPasswordValidator
import re

class EmployeeBase(BaseModel):                                       #inheratance 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    emergency_contact: Optional[str] = None
    official_email: Optional[EmailStr] = None
    # email field removed - comes from EmailPasswordValidator in EmployeeRegister

    @field_validator("gender", "blood_group", "marital_status", mode="before")    #Convert empty strings to None for optional fields
    def convert_empty_to_none(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):                                 #isinstance() function checks if the value is of type string
            raise ValueError("Must be a string")
        v = v.strip()
        if not v:
            return None
        return v

    @field_validator("official_email", mode="before")        
    def normalize_email(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Official email must be a valid email address (e.g. example@company.com).")
        v = v.strip()
        if not v:
            return None
        return v.lower()

    @field_validator("dob", mode="before")
    def ensure_date(cls, v):                      

        if v is None:             
            return None
        if isinstance(v, str) and not v.strip():
            return None
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, datetime.min.time())
        return v 
    
    @field_validator("first_name", "last_name")                         # Only allow letters, spaces, hyphens, and apostrophes (no numbers)
    def validate_name(cls, v):
        if v:
            v = v.strip()
            
            if not re.match(r"^[A-Za-z\s\-']+$", v):                    #regexpattern = it is pattern used to validate name string 
                raise ValueError("Name must contain only letters, spaces, hyphens, and apostrophes")
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters long")
            return v
        return v
    
    @field_validator("phone", "emergency_contact")
    def validate_phone(cls, v):
        if v is None:         # None is valid for optional fields
            return None
        if not isinstance(v, str):  # Reject non-string types
            raise ValueError("Phone number must be a string")
        v = v.strip()
        if not v:  # Empty string after strip -> None
            return None
        # Must start with +91 and have exactly 10 digits after it
        pattern = re.compile(r"^\+91[6-9]\d{9}$")
        if not pattern.match(v):
            raise ValueError("Phone number must be in format +91XXXXXXXXXX (10 digits)")
        return v
    
    model_config = {"extra": "forbid"}  
                                            

class EmployeeRegister(EmailPasswordValidator, EmployeeBase):   #inherited the email validator from auth.helper.py
    first_name: str
    role: Optional[str] = "employee"

    model_config = {"extra": "forbid"}


class EmployeeBasicUpdate(EmployeeBase):                     # inherits all fields from EmployeeBase
    pass  

class CurrentAddress(BaseModel):
    street : Optional[str] = None
    city : Optional[str] = None
    state : Optional[str] = None
    country : Optional[str] = None
    zip_code : Optional[str] = None
    model_config = {"extra": "forbid"}

class PermanentAddress(BaseModel):
    street : Optional[str] = None
    city : Optional[str] = None
    state : Optional[str] = None
    country : Optional[str] = None
    zip_code : Optional[str] = None
    model_config = {"extra": "forbid"}


class JobInfo(BaseModel):
    employee_code : Optional[str] = None
    job_title : Optional[str] = None
    designation : Optional[str] = None
    department : Optional[str] = None
    date_of_joining : Optional[datetime] = None
    reporting_manager : Optional[str] = None

    @field_validator("date_of_joining", mode="before")   #Parse the input string/datetime into a proper date object,mode = before , means it will validate before the data is saved in the database
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        if isinstance(v, datetime):
            return v.date()
        return v

    @field_validator("date_of_joining")                 # Validate date_of_joining is not in the future
    def validate_date(cls, v):
        if v and v > date.today():
            raise ValueError("Date of joining cannot be in the future.")
        return v

    model_config = {"extra": "forbid"}


class Education(BaseModel):
    institution_name : Optional[str] = None
    degree : Optional[str] = None
    field_of_study : Optional[str] = None
    start_year : Optional[int] = None
    end_year : Optional[int] = None
    grade : Optional[str] = None 

    @field_validator("start_year", "end_year")
    def validate_year(cls, v):
        if v and (v < 1900 or v > 2100):
            raise ValueError("Year must be between 1900 and 2100")
        return v

    model_config = {"extra": "forbid"}


class WorkExperience(BaseModel):
    company_name : Optional[str] = None
    job_title : Optional[str] = None
    from_date : Optional[datetime] = None
    to_date : Optional[datetime] = None
    responsibilities : Optional[str] = None
    model_config = {"extra": "forbid"}

class EmployeeSearch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    job_title: Optional[str] = None
    model_config = {"extra": "forbid"}


class AttendanceBase(BaseModel):
    email : Optional[EmailStr] = None
    employee_id: str              # Reference to employee
    date: date                    # Attendance date (unique per employee)
    status: str                   # "Present", "Absent", "Leave", "Half-Day"
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

    @field_validator("date", mode="before")
    def parse_date(cls, v):
        if isinstance(v, str):
            # Parse string date to date object
            return datetime.strptime(v, "%Y-%m-%d").date()
        if isinstance(v, datetime):
            return v.date()
        return v
    
    @field_validator("check_in", "check_out", mode="before")
    def parse_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Parse datetime string without timezone info (local time)
            # Supports both "2024-10-29T09:29:00" and "2024-10-29T09:29:00.000Z" formats
            v = v.replace('Z', '').replace('.000', '')
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                # Fallback to strptime for other formats
                return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
        return v

    model_config = {"extra": "forbid"}

class AttendanceCreate(AttendanceBase):
    pass
    
class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    
    @field_validator("check_in", "check_out", mode="before")
    def parse_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # Parse datetime string without timezone info (local time)
            v = v.replace('Z', '').replace('.000', '')
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
        return v

    model_config = {"extra": "forbid"}


# ==================================================================================
# LEAVE MANAGEMENT SCHEMAS
# ==================================================================================
class LeaveRequestBase(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str

    @field_validator("leave_type")
    def validate_leave_type(cls, v):
        allowed_types = ["Annual", "Sick", "Personal", "Emergency", "Maternity", "Paternity"]
        if v not in allowed_types:
            raise ValueError(f"Leave type must be one of {allowed_types}")
        return v

    @field_validator("start_date", "end_date", mode="before")
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        if isinstance(v, datetime):
            return v.date()
        return v

    @model_validator(mode="after")
    def check_date_order(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        return self

    model_config = {"extra": "forbid"}



class LeaveRequest(LeaveRequestBase):        #inherited from LeaveRequestBase
    employee_id: str
    manager_id: Optional[str] = None


class LeaveApproval(BaseModel):
    status: str                             # "Approved" or "Rejected"
    remarks: Optional[str] = None
    
    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["Approved", "Rejected"]:
            raise ValueError("Status must be 'Approved' or 'Rejected'")
        return v
    
    model_config = {"extra": "forbid"} 


class LeaveBalance(BaseModel):
    employee_id: str
    annual: int = 12
    sick: int = 6
    personal: int = 3
    emergency: int = 2

    annual_used: int = 0
    sick_used: int = 0
    personal_used: int = 0
    emergency_used: int = 0


    @field_validator("annual", "sick", "personal", "emergency")
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Leave balance cannot be negative")
        return v

    model_config = {"extra": "forbid"}


    









