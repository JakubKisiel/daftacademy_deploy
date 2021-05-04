from fastapi import FastAPI, HTTPException, Header , Depends, Response, Cookie, status
import random
import secrets
import hashlib
from pydantic import BaseModel
import datetime
from datetime import date, timedelta
from typing import Optional, Dict
from starlette.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
app.counter = 0 
LOGIN = "4dm1n"
PASSWORD = "NotSoSecurePa$$"
security = HTTPBasic()

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
  
app.access_tokens: str = "fhdsahdaskljghjldash"

@app.get("/hello", response_class=HTMLResponse)
def hello():
    return f"<h1>Hello! Today date is {datetime.date.today()}</h1>"

@app.post("/login_session", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, LOGIN)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_password and correct_username):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{random.random()}".encode()).hexdigest()
    app.access_tokens = session_token
    response.set_cookie(key="session_token", value=session_token)
    return "Hello"
    
app.token: str = "fdshjfdhsakjhfdag"

@app.post("/login_token", status_code=201)
def login_token(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, LOGIN)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_password and correct_username):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{random.random()}".encode()).hexdigest()
    app.token = session_token
    response.set_cookie(key="session_token", value=session_token)
    return {"token": session_token}

@app.get("/welcome_session")
def welcome_session(session_token: Optional[str] = Cookie(None), format: Optional[str] = "plain"):
    if app.access_tokens != session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if format.lower() == "json":
        return JSONResponse(content={"message": "Welcome!"})
    if format.lower() == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>")
    return Response(content="Welcome!")


@app.get("/welcome_token")
def welcome_session(token: Optional[str] = "", format: Optional[str] = "plain"):
    if app.token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if format.lower() == "json":
        return JSONResponse(content={"message": "Welcome!"})
    if format.lower() == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>")
    return Response(content="Welcome!")
