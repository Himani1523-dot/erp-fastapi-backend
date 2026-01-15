from pydantic import BaseModel,EmailStr, field_validator,model_validator, Field
from typing import Optional
from app.HR.schemas import EmployeeBase, CurrentAddress, LeaveRequestBase
import re
from datetime import date,datetime
from enum import Enum



class EmployeeLogin(BaseModel):
    email: EmailStr
    password: str
    model_config = {"extra": "forbid"}

class EmployeeSelfUpdate(BaseModel):

    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    

    @field_validator("phone", "emergency_contact")
    def validate_phone(cls, v):
        if v:
            v = v.strip()                                          #.strip() to remove leading/trailing spaces
            
            pattern = re.compile(r"^\+91[6-9]\d{9}$")              # Must start with +91 and have exactly 10 digits after it
            if not pattern.match(v):
                raise ValueError("Phone number must be in format +91XXXXXXXXXX (10 digits starting with 0-9)")
            return v
        return v

    model_config = {"extra": "forbid"}


class EmployeeAddressUpdate(CurrentAddress):         #inherits from HR.schemas.py
    pass


class EmployeeLeaveRequest(LeaveRequestBase):        #inherits from HR.schemas,follows DRY principle 
    pass
    

#===============Budget approval schema==========================
class RequestStatus(str, Enum):
    PENDING_MANAGER = "pending_manager"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    
class BudgetCategory(str, Enum):
    MARKETING = "Marketing"
    IT = "IT"
    OPERATIONS = "Operations"
    OFFICE_SUPPLIES = "Office Supplies"
    TRAINING = "Training"
    TRAVEL = "Travel"
    EQUIPMENT = "Equipment"
    OTHER = "Other"
    
    "no need,we need class method we we want to stritclty send the allowed categories to frontend like API for dropdown menu,but rn we dont need classmethod as frontend will manually type the dropdown values"
    # @classmethod                     
    #     return [item.value for item in cls] 


class BudgetRequestBase(BaseModel):
    title: str
    category: BudgetCategory         #calling enum 
    amount: float
    justification: str
    attachment_url: Optional[str] = None
    expected_date: date


    @field_validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Title must be at least 5 characters long")
        if len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return v
    
    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        if v > 10000000:
            raise ValueError("Amount cannot exceed ₹1,00,00,000")
        return v
    
    
    @field_validator("expected_date", mode="before")
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        if isinstance(v, datetime):
            return v.date()
        return v
    
    @field_validator("expected_date")
    def validate_expected_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Expected date cannot be in the past")
        return v
    
    model_config = {"extra": "forbid"}


class EmployeeBudgetRequest(BudgetRequestBase):   #inherits from BudgetRequestBase
    pass
    # employee_id: str
    # employee_name: str
    # department: str
    # remarks: Optional[str] = None
    # manager_id: Optional[str] =  None
    # status: RequestStatus                         #It is called type annotation or field type binding/type hinting! 
    
    # model_config = {"extra": "forbid"}



   
    






    