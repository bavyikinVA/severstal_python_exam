import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
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
    date_removed_start: Optional[datetime] = None
    date_removed_end: Optional[datetime] = None
    date_added_start: Optional[datetime] = None
    date_added_end: Optional[datetime] = None


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
    coil = db.query(Coil).filter(Coil.id == coil_id is True).first()
    if not coil:
        return {"detail": "Coil not found"}
    db.delete(coil)
    db.commit()
    return {"detail": "Coil deleted"}


@app.get("/api/coil")
def get_coils(filter: CoilFilter = Depends(CoilFilter)):
    db = SessionLocal()
    query = db.query(Coil)
    print(filter.dict())
    if filter:
        if filter.id_min is not None and filter.id_max is not None:
            query = query.filter(Coil.id.between(filter.id_min, filter.id_max))
        elif filter.id_min is not None:
            query = query.filter(Coil.id >= filter.id_min)
        elif filter.id_max is not None:
            query = query.filter(Coil.id <= filter.id_max)

        if filter.weight_min is not None and filter.weight_max is not None:
            query = query.filter(Coil.weight.between(filter.weight_min, filter.weight_max))
        elif filter.weight_min is not None:
            query = query.filter(Coil.weight >= filter.weight_min)
        elif filter.weight_max is not None:
            query = query.filter(Coil.weight <= filter.weight_max)

        if filter.length_min is not None and filter.length_max is not None:
            query = query.filter(Coil.length.between(filter.length_min, filter.length_max))
        elif filter.length_min is not None:
            query = query.filter(Coil.length >= filter.length_min)
        elif filter.length_max is not None:
            query = query.filter(Coil.length <= filter.length_max)

        if filter.date_removed_start is not None and filter.date_removed_end is not None:
            query = query.filter(Coil.date_removed.between(filter.date_removed_start, filter.date_removed_end))
        elif filter.date_removed_start is not None:
            query = query.filter(Coil.date_removed >= filter.date_removed_start)
        elif filter.date_removed_end is not None:
            query = query.filter(Coil.date_removed <= filter.date_removed_end)

        if filter.date_added_start is not None and filter.date_added_end is not None:
            query = query.filter(Coil.date_added.between(filter.date_added_start, filter.date_added_end))
        elif filter.date_added_start is not None:
            query = query.filter(Coil.date_added >= filter.date_added_start)
        elif filter.date_added_end is not None:
            query = query.filter(Coil.date_added <= filter.date_added_end)

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
