from fastapi import FastAPI, HTTPException, Header 
import hashlib
from pydantic import BaseModel
import datetime
from datetime import date, timedelta
from typing import Optional

from starlette.responses import HTMLResponse

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

app.tab = list()

@app.post("/register", status_code=201, response_model=RegisterResponse)
def register(item: RegisterRequest,date: Optional[datetime.datetime] = Header(None),):
    app.counter += 1
    current_date = datetime.date.today() if not isinstance(date,datetime.datetime) else date.date() 
    count_letters = 0
    for i in item.name:
        count_letters += 1 if i.isalpha() else 0
    for i in item.surname:
        count_letters += 1 if i.isalpha() else 0
    register_response = RegisterResponse(id = app.counter, 
            name = item.name,
            surname = item.surname,
            register_date = current_date,
            vaccination_date = (current_date + timedelta(count_letters))
            )
    app.tab.append(register_response)
    return register_response
    
@app.get("/patient/{id}", response_model=RegisterResponse)
def patient(id: int):
    if len(app.tab) < id:
        raise HTTPException(status_code=404)
    if id < 1:
        raise HTTPException(status_code=400)
    return app.tab[id-1]
  

@app.get("/hello", response_class=HTMLResponse)
def hello():
    return f"<h1>Hello! Today date is {datetime.date.today()}</h1>"

