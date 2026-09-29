import os
import boto3
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from botocore.exceptions import NoCredentialsError
from pydantic import BaseModel, field_validator
from sqlmodel import select
from src.models.product_model import Product, CreateProduct, UpdateProduct, ProductCategories, ImageRecord
from src.shared.database.session_db import SessionDep

app = FastAPI(
    title="FastAPI - CRUD"
)

# Configuración de S3 con Boto3 leyendo del archivo .env / variables de entorno
# .strip() porque un espacio tras el "=" en el .env queda como parte del valor
S3_BUCKET = (os.getenv("AWS_BUCKET_NAME") or "").strip() or None
AWS_REGION = (os.getenv("AWS_REGION") or "us-east-2").strip()
_AWS_ACCESS_KEY_ID = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip() or None
_AWS_SECRET_ACCESS_KEY = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip() or None


def get_s3_client():
    """Crea el cliente S3. Si hay keys explícitas las usa, si no usa la cadena
    por defecto de boto3 (incluye el IAM Role de la EC2)."""
    import boto3

    kwargs = {"region_name": AWS_REGION}
    if _AWS_ACCESS_KEY_ID and _AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = _AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = _AWS_SECRET_ACCESS_KEY
    return boto3.client("s3", **kwargs)

# Formatos de imagen permitidos
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/jpg", "image/webp"}


# ----------------- RUTAS DE UTILIDAD / AWS S3 -----------------

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "La aplicación está funcionando correctamente"}


@app.post("/images")
async def upload_image(session: SessionDep, file: UploadFile = File(...)):
    # 1. Validar que sea un archivo permitido
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Solo se aceptan imágenes (JPEG, PNG, WEBP)."
        )

    if not S3_BUCKET:
        raise HTTPException(
            status_code=500,
            detail="AWS_BUCKET_NAME no está configurado en el servidor."
        )

    try:
        file_content = await file.read()

        # 2. Subir la imagen a Amazon S3 usando Boto3 (SDK oficial)
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file.filename,
            Body=file_content,
            ContentType=file.content_type
        )
        
        # Construir la referencia (URL pública o la ruta del objeto en S3)
        file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"
        
        # 3. Guardar la referencia en PostgreSQL
        db_image = ImageRecord(filename=file.filename, url=file_url)
        session.add(db_image)
        session.commit()
        session.refresh(db_image)
        
        return {
            "success": True,
            "message": "Imagen subida a S3 y registrada en la base de datos correctamente",
            "filename": file.filename,
            "url": file_url
        }
        
    except NoCredentialsError:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se encontraron credenciales de AWS en la instancia EC2."
        )
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )


# ----------------- RUTAS DE PRODUCTOS -----------------

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
