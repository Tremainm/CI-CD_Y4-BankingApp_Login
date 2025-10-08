from pydantic import BaseModel, EmailStr, constr, conint, field_validator

class Customer(BaseModel):
    customer_id: int
    name: constr(min_length=2, max_length=50)
    full_name: constr(min_length=5, max_length=100)   # Customer’s full name (must be at least 5 characters)
    email: EmailStr
    age: conint(gt=18)  # Customer age (must be greater than 18)
    password: constr(min_length=8)  # must be at least 8 characters long

    # Custom password validation logic
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Password rules:
        - Must contain at least one letter
        - Must contain at least one digit
        """
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v

      