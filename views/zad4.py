import aiosqlite
from fastapi import APIRouter, HTTPException
zad4 = APIRouter()

@zad4.on_event("startup")
async def startup():
    zad4.db_connection = await aiosqlite.connect("northwind.db")
    zad4.db_connection.text_factory = lambda b:b.decode(errors="ignore")

@zad4.on_event("shutdown")
async def shutdown():
    await zad4.db_connection.close()

@zad4.get("/categories")
async def categories():
    cursor = await zad4.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories")
    data = await cursor.fetchall()
    data.sort(key = lambda tup: tup[0])
    return {"categories":[{"id": tup[0], "name": tup[1]} for tup in data]}

@zad4.get("/customers")
async def categories():
    zad4.db_connection.row_factory = aiosqlite.Row
    cursor = await zad4.db_connection.execute( """SELECT CustomerID id, COALESCE(CompanyName, '') name, 
        COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || 
        COALESCE(Country, '') full_address 
        FROM Customers c ORDER BY UPPER(CustomerID);"""
    )
    data = await cursor.fetchall()
    print(data)
    return {"customers": data}

@zad4.get("/products/{id}")
async def products_id(id: int):

    data = await zad4.db_connection.execute("""
    SELECT ProductID id, ProductName name
    FROM Products
    where id = ?
    """, (id,))
    data = await data.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found")
    return data

