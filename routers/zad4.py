import aiosqlite
from fastapi import APIRouter, HTTPException, BaseModel
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
    zad4.db_connection.row_factory = aiosqlite.Row
    data = await zad4.db_connection.execute("""
    SELECT ProductID id, ProductName name
    FROM Products
    where id = ?
    """, (id,))
    data = await data.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found")
    return data

EMP_SET = {"order", "first_name", "last_name", "city"}

@zad4.get("/employees")
async def employees(limit: int = 0, offset: int = 0, order: str = None):
    if order and (order not in EMP_SET):
        raise HTTPException(status_code=400)
    order = order if order else "id"
    zad4.db_connection.row_factory = aiosqlite.Row
    data = await zad4.db_connection.execute(f"""
    SELECT EmployeeID id, LastName last_name, FirstName first_name, City city
    FROM Employees
    ORDER BY {order}
    LIMIT {limit}
    OFFSET {offset}
    """)
    data = await data.fetchall()
    return {"employees": data}
    
@zad4.get("/products_extended")
async def products_extended():
    zad4.db_connection.row_factory = aiosqlite.Row
    data = await zad4.db_connection.execute(f"""
    SELECT Products.ProductID id, Products.ProductName name, 
    Categories.CategoryName category, Suppliers.CompanyName supplier
    FROM Products
    LEFT JOIN Categories on Products.CategoryID = Categories.CategoryID
    LEFT JOIN Suppliers on Products.SupplierID = Suppliers.SupplierID
    ORDER BY id
    """)
    data = await data.fetchall()
    return {"products_extended": data}


@zad4.get("/products/{id}/orders")
async def products_extended(id: int):
    zad4.db_connection.row_factory = aiosqlite.Row
    product = await zad4.db_connection.execute(f"""
            SELECT ProductId FROM Products
            WHERE ProductId = {id}
            """)
    product = await product.fetchone()
    if not product:
        raise HTTPException(status_code=404)
    data = await zad4.db_connection.execute(f"""
    SELECT Orders.OrderId id, Customers.CompanyName customer,
    OrderDetails.Quantity quantity, ROUND(OrderDetails.Quantity * OrderDetails.UnitPrice -
    (OrderDetails.Discount * (OrderDetails.UnitPrice * OrderDetails.Quantity)), 2)
    total_price
    FROM Orders
    INNER JOIN 'Order Details' OrderDetails on Orders.OrderId = OrderDetails.OrderId
    INNER JOIN Products on OrderDetails.ProductId = Products.ProductId
    INNER JOIN Customers on Orders.CustomerId = Customers.CustomerId
    WHERE OrderDetails.ProductId = {id}
    ORDER BY Orders.OrderId
    """)
    data = await data.fetchall()
    return {"orders": data}
class CategoryGet(BaseModel):
    name : str

class Category(BaseModel):
    name: str
    id: int


@zad4.post("/categories", status_code=201, response_model=Category)
async def post_category(category: CategoryGet):
    cursor = zad4.db_connection.cursor()
    cursor.execute("INSERT INTO Categories (CategoryName) VALUES (?);", (category.name,))
    category_added = Category(name=category.name, id=cursor.lastrowid)
    zad4.db_connection.commit()
    return category_added


@zad4.put("/categories/{id}", response_model=Category)
async def put_category(id: int, category: CategoryGet):
    cursor = await zad4.db_connection.cursor()
    await cursor.execute(
            f"UPDATE Categories SET CategoryName = :cname WHERE CategoryID = {id}"
                   )
    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="Id not found")
    category_added = Category(name=category.name, id=id)
    await zad4.db_connection.commit()
    return category_added


@zad4.delete("/categories/{id}")
async def delete_category(id: int):
    cursor = await zad4.db_connection.cursor()
    await cursor.execute("DELETE FROM Categories WHERE CategoryID = ?;", (id,))
    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="Id not found")
    await zad4.db_connection.commit()
    return {"deleted":cursor.rowcount}
