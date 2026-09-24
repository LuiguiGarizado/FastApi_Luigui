from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import select
from src.models.product_model import Product, CreateProduct, UpdateProduct, ProductCategories
from src.shared.database.session_db import SessionDep

app = FastAPI(
    title = "FastAPI - CRUD"
)

# ----------------- RUTAS -----------------

@app.post("/product")
def create_product(product: CreateProduct, session: SessionDep):
    existing_product = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()

    if existing_product:
        raise HTTPException(status_code=422, detail="Product added already.")
    else:
        if product.category not in ProductCategories:
            raise HTTPException(status_code=422, detail="Category not allowed")

        if product.price < 10000: 
            raise HTTPException(status_code=422, detail="Price must be greater than 10.000")

        if product.quantity <= 0: 
            raise HTTPException(status_code=422, detail="Quantity must be greater than zero")

        new_product = Product(
            name=product.name,
            category=product.category, 
            price=product.price, 
            quantity=product.quantity
        )

        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return new_product


@app.get("/product")
def get_products(session: SessionDep):
    products = session.exec(select(Product)).all()
    return products


@app.get("/product/{product_id}")
def get_product(product_id: int, session: SessionDep):
    product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    return product


@app.put("/product/{product_id}", status_code=201)
def put_product(product_id: int, product: CreateProduct, session: SessionDep):
    existing_product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()
    
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    else:
        if product.name != existing_product.name:
            name_in_use = session.exec(select(Product).where(Product.name == product.name)).first()
            if name_in_use:
                raise HTTPException(status_code=422, detail="Product added already.")
        
        if product.category not in ProductCategories:
            raise HTTPException(status_code=422, detail="Category not allowed")
        
        if product.price < 10000: 
            raise HTTPException(status_code=422, detail="Price must be greater than 10.000")
        
        if product.quantity <= 0: 
            raise HTTPException(status_code=422, detail="Quantity must be greater than zero")

        existing_product.name = product.name
        existing_product.category = product.category
        existing_product.price = product.price
        existing_product.quantity = product.quantity
        
        session.add(existing_product)
        session.commit()
        session.refresh(existing_product)
        
        return existing_product


@app.patch("/product/{product_id}", status_code=201)
def patch_product(product_id: int, product: UpdateProduct, session: SessionDep):
    existing_product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()
    
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    else:
        if product.name is not None and product.name != existing_product.name:
            name_in_use = session.exec(select(Product).where(Product.name == product.name)).first()
            if name_in_use:
                raise HTTPException(status_code=422, detail="Product added already.")
        
        if product.category is not None and product.category not in ProductCategories:
            raise HTTPException(status_code=422, detail="Category not allowed")
        
        if product.price is not None and product.price <= 10000: 
            raise HTTPException(status_code=422, detail="Price must be greater than 10.000")
        
        if product.quantity is not None and product.quantity <= 0: 
            raise HTTPException(status_code=422, detail="Quantity must be greater than zero")

        # Actualizar únicamente los datos presentes sin sobreescribir otros
        product_data = product.model_dump(exclude_unset=True)
        
        for key, value in product_data.items():
            setattr(existing_product, key, value)
        
        session.add(existing_product)
        session.commit()
        session.refresh(existing_product)
        
        return existing_product


@app.delete('/product/{product_id}')
def delete_product(product_id: int, session: SessionDep):
    product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()
    
    if not product:
         raise HTTPException(status_code=404, detail="Product not found.")
         
    session.delete(product)
    session.commit()
    return {"detail": "Product deleted successfully"}
