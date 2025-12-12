from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict

# reusable constrained strings
NameStr = Annotated[str, StringConstraints(min_length=2, max_length=100)]
PhoneStr = Annotated[str, StringConstraints(min_length=7, max_length=20)]
PasswordStr = Annotated[str, StringConstraints(min_length=6, max_length=128)]


class UserCreate(BaseModel):
    full_name: NameStr
    email: EmailStr
    phone_number: PhoneStr
    password: PasswordStr


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str

    model_config = ConfigDict(from_attributes=True)
