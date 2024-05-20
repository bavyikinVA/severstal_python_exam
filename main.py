import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validate_call
from sqlalchemy import create_engine, Column, Integer, DateTime, Float, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./coils.db"


@app.get("/")
def main():
    html_content = """
                <html>
                    <head>
                        <title>Some HTML in here</title>
                    </head>
                    <body>
                        <h1>Look ma! HTML!</h1>
                    </body>
                </html>
                """
    return HTMLResponse(content=html_content, status_code=200)


def test_db_connection():
    try:
        sqlite_url = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(sqlite_url)
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
        return False


if not test_db_connection():
    raise HTTPException(status_code=500, detail="Database not available")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Coil(Base):
    __tablename__ = "coils"
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float)
    weight = Column(Float)
    date_added = Column(DateTime, default=datetime.now())
    date_removed = Column(DateTime)


Base.metadata.create_all(bind=engine)


class CoilCreate(BaseModel):
    length: float
    weight: float


class CoilFilter(BaseModel):
    id_min: Optional[int] = None
    id_max: Optional[int] = None
    weight_min: Optional[float] = None
    weight_max: Optional[float] = None
    length_min: Optional[float] = None
    length_max: Optional[float] = None
    date_added: Optional[datetime] = None
    date_removed: Optional[datetime] = None


@app.post("/api/coil")
def create_coil(coil: CoilCreate):
    db = SessionLocal()
    new_coil = Coil(length=coil.length, weight=coil.weight)
    try:
        db.add(new_coil)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return {"detail": "Database error"}

    response = {"id": new_coil.id}
    db.close()
    return response


@app.delete("/api/coil/{coil_id}")
def delete_coil(coil_id: int):
    db = SessionLocal()
    coil = db.query(Coil).filter(Coil.id == coil_id).first()
    if not coil:
        return {"detail": "Coil not found"}
    db.delete(coil)
    db.commit()
    return {"detail": "Coil deleted"}


@app.get("/api/coil")
def get_coils(filter: CoilFilter = None):
    db = SessionLocal()
    query = db.query(Coil)

    if filter and filter.id is not None:
        query = query.filter(Coil.id == filter.id)

    if filter and filter.weight is not None:
        query = query.filter(Coil.weight == filter.weight)

    if filter and filter.length is not None:
        query = query.filter(Coil.length == filter.length)

    if filter and filter.date_added is not None:
        query = query.filter(Coil.date_added == filter.date_added)

    if filter and filter.date_removed is not None:
        query = query.filter(Coil.date_removed == filter.date_removed)

    coils = query.all()
    db.close()
    return coils


@app.get("/api/coil/stats")
def get_stats(start_date: datetime, end_date: datetime):
    db = SessionLocal()
    query = db.query(
        func.count(Coil.id).label("total_coils"),
        func.count(Coil.date_removed).label("removed_coils"),
        func.avg(Coil.weight).label("avg_weight"),
        func.avg(Coil.length).label("avg_length"),
        func.max(Coil.weight).label("max_weight"),
        func.min(Coil.weight).label("min_weight"),
        func.max(Coil.length).label("max_length"),
        func.min(Coil.length).label("min_length"),
        func.sum(Coil.weight).label("total_weight"),
    ).filter(Coil.date_added <= end_date, Coil.date_removed >= start_date)
    stats = query.first()
    db.close()
    return stats
