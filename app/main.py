from fastapi import FastAPI, HTTPException, status
from .schemas import User

app = FastAPI()

users = []

#Register a new user
@app.post("/user/register/")
def register_user(user: User):
    for u in users:
        if u.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    users.append(user)
    return {"message": "User registered successfully", "user": user}

#Update an existing user
@app.put("/user/update/{user_id}")
def update_user(user_id: int, updated_user: User):
    for i, e in enumerate(users):
        if e.id == user_id:
            users[i] = updated_user
            return {"message": "User updated successfully", "user": updated_user}
    raise HTTPException(status_code=404, detail="User not found")

#Delete a user
@app.delete("/user/delete_user/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user.id == user_id:
            users.pop(i)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

#Get user details
@app.get("/user/get_user/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

#Get all users
@app.get("/user/get_users/")
def get_users():
    return users

#Update user password
@app.put("/user/update_password/{user_id}")
def update_password(user_id: int, new_password: str):
    for i, user in enumerate(users):
        if user.id == user_id:
            users[i].password = new_password
            return {"message": "Password updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")