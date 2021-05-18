from sqlalchemy.orm import Session

from . import models

def get_all_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()

def get_supplier(db: Session, supplier_id: int):
    return(db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first())

def get_supplier_products(db: Session, supplier_id:int):
    return db.query(models.Product).join(models.Category).filter(models.Product.SupplierID == supplier_id).order_by(models.Product.ProductID.desc()).all()

