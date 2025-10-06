from fastapi import FastAPI, HTTPException, status
from .schemas import User

app = FastAPI()
users: list[User] = []

# Get all users
@app.get("/users")
def get_users():
    return users

# Get user by email
@app.get("/users/{email}")
def get_user(email: str):
    for u in users:
        if u.email == email:
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# Create user, checks if email or phone no. already exists
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    if any(u.phone_number == user.phone_number for u in users):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")
    users.append(user)
    return user

# Update user info
@app.put("/users/{email}")
def update_user(email: str, user: User):
    for i,e in enumerate(users): # e = members of 'users' list/User object & i = index of the object
        if e.email == email:
            users[i] = user
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

# Delete user by email
@app.delete("/users/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(email: str):
    for i,e in enumerate(users):
        if e.email == email:
            users.pop(i)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

