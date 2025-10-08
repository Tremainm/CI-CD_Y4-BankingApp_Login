from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int 
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\+?\d{7,15}$") #Phone number must contain only digits and may start with + 
    password: str = Field(..., min_length=8)