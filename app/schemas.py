from pydantic import BaseModel, EmailStr, constr, conint, Field

class User(BaseModel):
    username: constr(min_length=3, max_length=30)
    email: EmailStr
    phone_number: str = Field(pattern=r'^\d{9}$')
    password: constr(min_length=8, max_length=50)