from fastapi import FastAPI, HTTPException
from schemas import User

app = FastAPI()

users = []

@app.post("/user/register/")
def register_user(user: User):
    for existing_user in users:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    users.append(user)
    return {"message": "User registered successfully", "user": user}


@app.put("/user/update/")
def update_user(user_id: int, updated_user: User):
    for index, existing_user in enumerate(users):
        if existing_user.id == user_id:
            users[index] = updated_user
            return {"message": "User updated successfully", "user": updated_user}
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/user/delete_user/")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user.id == user_id:
            users.pop(index)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/user/get_user/")
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/user/get_users/")
def get_users():
    return {"users": users}


@app.put("/user/update_password/")
def update_password(user_id: int, new_password: str):
    for index, user in enumerate(users):
        if user.id == user_id:
            users[index].password = new_password
            return {"message": "Password updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")