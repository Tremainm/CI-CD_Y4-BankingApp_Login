from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from typing import List
from .schemas import Customer 


app = FastAPI(title="Banking App • Customer Login Microservice")

# In-memory list to store customer data
customers: List[Customer] = []

#to check if the server is running
@app.get("/hello")
def hello():
    return {"message": "Customer Login service running"}

# GET ALL CUSTOMERS 
@app.get("/api/customers")
def list_customers():
    return customers

# GET CUSTOMER BY ID
@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int):
    for c in customers:
        if c.customer_id == customer_id:
            return c
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

# CREATE CUSTOMER
@app.post("/api/customers", status_code=status.HTTP_201_CREATED)
def register_customer(customer: Customer):
     # Check if the customer_id already exists
    if any(c.customer_id == customer.customer_id for c in customers):   
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="customer_id already exists")
        
    # Check if the email address is already registered
    if any(c.email == customer.email for c in customers):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

   # Add the new customer to the in-memory list
    customers.append(customer)
    return customer  # Return the created customer (including password)


# UPDATE CUSTOMER
@app.put("/api/customers/{customer_id}", status_code=status.HTTP_202_ACCEPTED)
def update_customer(customer_id: int, updated: Customer):
    updated.customer_id = customer_id # making sure that path ID and body ID are the same

      # Search for the customer by ID and replace their details
    for i, c in enumerate(customers):
        if c.customer_id == customer_id:
            customers[i] = updated # Update the customer
            return updated

       # If not found, return an error       
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="customer_id not found")

# DELETE CUSTOMER
@app.delete("/api/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int):
    for i, c in enumerate(customers):
        if c.customer_id == customer_id:
            customers.pop(i) # Remove the customer from the list
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

