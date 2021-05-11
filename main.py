from fastapi import FastAPI, HTTPException, Header , Depends, Response, Cookie, status
import random
import secrets
import hashlib
from pydantic import BaseModel
import aiosqlite
import datetime
from datetime import date, timedelta
from typing import Optional, Dict, Set, Deque, List
from collections import deque
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
app.counter = 0 
LOGIN = "4dm1n"
PASSWORD = "NotSoSecurePa$$"
security = HTTPBasic()

@app.on_event("startup")
async def startup():
    app.db_connection = await aiosqlite.connect("northwind.db")
    app.db_connection.text_factory = lambda b:b.decode(errors="ignore")

@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()

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
  
app.access_tokens: Deque[str] = deque()

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
    if len(app.access_tokens) == 3:
        app.access_tokens.popleft()
    app.access_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return "Hello"
    
app.token: Deque[str] = deque() 

@app.post("/login_token", status_code=201)
def login_token(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, LOGIN)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_password and correct_username):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{random.random()}".encode()).hexdigest()
    if len(app.token) == 3:
        app.token.popleft()
    app.token.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return {"token": session_token}

@app.get("/welcome_session")
def welcome_session(response: Response, session_token: Optional[str] = Cookie(None), format: Optional[str] = "plain"):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if format.lower() == "json":
        response.headers["content-type"] = "application/json"
        return JSONResponse(content={"message": "Welcome!"})
    if format.lower() == "html":
        response.headers["content-type"] = "text/html"
        return HTMLResponse(content="<h1>Welcome!</h1>")
    response.headers["content-type"] = "text/plain"
    return Response(content="Welcome!", media_type="text/plain")


@app.get("/welcome_token")
def welcome_session(response: Response,token: Optional[str] = "", format: Optional[str] = "plain"):
    if token not in app.token :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if format.lower() == "json":
        response.headers["content-type"] = "application/json"
        return JSONResponse(content={"message": "Welcome!"})
    if format.lower() == "text/html":
        response.headers["content-type"] = "html"
        return HTMLResponse(content="<h1>Welcome!</h1>")
    response.headers["content-type"] = "text/plain"
    return Response(content="Welcome!", media_type="text/plain")

@app.delete("/logout_session")
def delete_session(response: Response, session_token: Optional[str] = Cookie(None), format: Optional[str] = "plain"):
    if  session_token not in app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    app.access_tokens.remove(session_token)
    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)

@app.delete("/logout_token")
def logout_token(response: Response,token: Optional[str] = "", format: Optional[str] = "plain"):
    if  token not in app.token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    app.token.remove(token)
    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)

@app.get("/logged_out")
def logged_out(response: Response, format: Optional[str] = "plain"):
    if format.lower() == "json":
        response.headers["content-type"] = "application/json"
        return JSONResponse(content={"message": "Logged out!"})
    if format.lower() == "text/html":
        response.headers["content-type"] = "html"
        return HTMLResponse(content="<h1>Logged out!</h1>")
    response.headers["content-type"] = "text/plain"
    return Response(content="Logged out!", media_type="text/plain")

@app.get("/categories")
async def categories():
    cursor = await app.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories")
    data = await cursor.fetchall()
    data.sort(key = lambda tup: tup[0])
    return {"categories":[{"id": tup[0], "name": tup[1]} for tup in data]}

@app.get("/customers")
async def categories():
    cursor = await app.db_connection.execute("SELECT * FROM Customers")
    data = await cursor.fetchall()
    data.sort(key= lambda tup: tup[0].upper())
    return {"categories":[{"id": tup[0], "name": tup[1] if tup[1] else '', "full_address": f"{tup[2] if tup[2] else ''} {tup[3] if tup[3] else ''} {tup[4] if tup[4] else ''} {tup[5] if tup[5] else ''}"} for tup in data]}


