from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL no está definida. Verifica el archivo .env en el host "
        "y que docker-compose.yml lo cargue con env_file."
    )

engine = create_engine(database_url)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
