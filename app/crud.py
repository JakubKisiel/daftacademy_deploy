from sqlalchemy.orm import Session

from . import models
from .schemas import NewSupplier

def get_all_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()

def get_supplier(db: Session, supplier_id: int):
    return(db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first())

def get_supplier_products(db: Session, supplier_id:int):
    return db.query(models.Product).join(models.Category).filter(models.Product.SupplierID == supplier_id).order_by(models.Product.ProductID.desc()).all()

def create_new_supplier(db: Session, new_supplier: NewSupplier):
    new_supplier_id = db.query(models.Supplier).count()+1
    new_supplier_output = models.Supplier(SupplierID = new_supplier_id,
                                          CompanyName = new_supplier.CompanyName,
                                          ContactName = new_supplier.ContactName,
                                          ContactTitle = new_supplier.ContactTitle,
                                          Address = new_supplier.Address,
                                          City = new_supplier.City,
                                          PostalCode = new_supplier.PostalCode,
                                          Country = new_supplier.Country,
                                          Phone = new_supplier.Phone)
    db.add(new_supplier_output)
    db.commit()
    return new_supplier_output
