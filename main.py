import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validate_call
from sqlalchemy import create_engine, Column, Integer, DateTime, Float, func, and_, or_
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
    id: Optional[int] = None
    weight: Optional[float] = None
    length: Optional[float] = None
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

'''
@app.get("/api/coils")
def get_coils(filter: CoilFilter = None):
    db = SessionLocal()
    query = db.query(Coil)
    if filter:
        if filter.id_min is not None or filter.id_max is not None:
            if filter.id
            query = query.filter(Coil.id >= filter.id_min)
        if filter.id_max:
            query = query.filter(Coil.id <= filter.id_max)
        if filter.weight_min:
            query = query.filter(Coil.weight >= filter.weight_min)
        if filter.weight_max:
            query = query.filter(Coil.weight <= filter.weight_max)
        if filter.length_min:
            query = query.filter(Coil.length >= filter.length_min)
        if filter.length_max:
            query = query.filter(Coil.length <= filter.length_max)
        if filter.date_added:
            query = query.filter(Coil.date_added == filter.date_added)
        if filter.date_removed:
            query = query.filter(Coil.date_removed == filter.date_removed)
    coils = query.all()
    db.close()
    return coils
'''


@app.get("/api/coil")
def read_coils(filter: CoilFilter = None):
    db = SessionLocal()
    query = db.query(Coil)

    if filter:
        conditions = []

        if filter.id is not None:
            conditions.append(Coil.id.between(filter.id[0], filter.id[1]) if isinstance(filter.id, list) else Coil.id == filter.id)

        if filter.weight is not None:
            conditions.append(Coil.weight.between(filter.weight[0], filter.weight[1]) if isinstance(filter.weight, list) else Coil.weight == filter.weight)

        if filter.length is not None:
            conditions.append(Coil.length.between(filter.length[0], filter.length[1]) if isinstance(filter.length, list) else Coil.length == filter.length)

        if filter.date_added is not None:
            conditions.append(Coil.date_added.between(filter.date_added[0], filter.date_added[1]) if isinstance(filter.date_added, list) else Coil.date_added == filter.date_added)

        if filter.date_removed is not None:
            conditions.append(Coil.date_removed.between(filter.date_removed[0], filter.date_removed[1]) if isinstance(filter.date_removed, list) else Coil.date_removed == filter.date_removed)

        if conditions:
            query = query.filter(and_(*conditions))

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
