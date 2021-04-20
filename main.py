from fastapi import FastAPI, HTTPException
import hashlib
from pydantic import BaseModel
from datetime import date, timedelta

app = FastAPI()
app.counter = 0 

@app.get("/")
def root():
    return {"message": "Hello world!"}

@app.post("/method", status_code=201)
def method():
    return{"method": "POST"}

@app.get("/method")
def method():
    return{"method": "GET"}

@app.put("/method")
def method():
    return{"method": "PUT"}

@app.delete("/method")
def method():
    return{"method": "DELETE"}

@app.options("/method")
def method():
    return{"method": "OPTIONS"}

@app.get("/auth", status_code=204)
def auth(password: str = "", password_hash: str = ""):
    pwdhash = hashlib.sha512(password.encode())
    if len(password) > 0 and len(password_hash) > 0 and pwdhash.hexdigest() == password_hash:
        return
    else:
        raise HTTPException(status_code=401)

class RegisterRequest(BaseModel):
    name: str
    surname: str

class RegisterResponse(BaseModel):
    id: int
    name: str
    surname: str
    register_date: date
    vaccination_date: date

@app.post("/register", status_code=201, response_model=RegisterResponse)
def register(item: RegisterRequest):
    app.counter += 1
    return RegisterResponse(id = app.counter, 
            name = item.name,
            surname = item.surname,
            register_date = date.today(),
            vaccination_date = (date.today() + timedelta(days = len(item.name)+ len(item.surname)))
            )
    
