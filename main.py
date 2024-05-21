import argparse
import sqlite3
from datetime import datetime, timedelta
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from utils import config_parser
from Models import Coil, CoilCreate, CoilFilter

app = FastAPI()

config = config_parser('config.txt')


@app.get("/")
def main():
    return {"message": "Home page Fastapi!"}


if config['DATABASE_TYPE'] == 'sqlite':
    DATABASE_URL = config['DATABASE_URL_SQLITE']
else:
    DATABASE_URL = config['DATABASE_URL_POSTGRES']


def test_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        connection.close()
        return True
    except (SQLAlchemyError, sqlite3.Error) as e:
        print(f"The error '{e}' occurred")
        return False


if not test_db_connection():
    raise HTTPException(status_code=500, detail="Database not available")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)


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
def get_coils(filter: CoilFilter = Depends(CoilFilter)):
    db = SessionLocal()
    query = db.query(Coil)
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
def get_coils_stats(date_start: datetime, date_end: datetime):
    db = SessionLocal()

    date_end += timedelta(days=1)

    query_added = db.query(Coil).filter(Coil.date_added.between(date_start, date_end))
    query_removed = db.query(Coil).filter(Coil.date_removed.between(date_start, date_end))

    coils_added = query_added.filter(Coil.date_removed.is_(None)).count()
    coils_removed = query_removed.filter(Coil.date_removed.isnot(None)).count()

    avg_length = query_added.with_entities(func.avg(Coil.length)).scalar()
    avg_weight = query_added.with_entities(func.avg(Coil.weight)).scalar()

    max_length = query_added.with_entities(func.max(Coil.length)).scalar()
    min_length = query_added.with_entities(func.min(Coil.length)).scalar()

    max_weight = query_added.with_entities(func.max(Coil.weight)).scalar()
    min_weight = query_added.with_entities(func.min(Coil.weight)).scalar()

    total_weight = query_added.filter(Coil.date_removed.is_(None)).with_entities(func.sum(Coil.weight)).scalar()

    max_interval = query_removed.filter(Coil.date_removed.isnot(None)).with_entities(
        func.max(Coil.date_removed - Coil.date_added)).scalar()
    min_interval = query_removed.filter(Coil.date_removed.isnot(None)).with_entities(
        func.min(Coil.date_removed - Coil.date_added)).scalar()

    day_min_coils_date = (db.query(Coil.date_added)
                          .filter(and_(Coil.date_added >= date_start, Coil.date_added < date_end))
                          .group_by(Coil.date_added).order_by(func.count(Coil.id)).limit(1).scalar())

    day_max_coils_date = (db.query(Coil.date_added)
                          .filter(and_(Coil.date_added >= date_start, Coil.date_added < date_end))
                          .group_by(Coil.date_added).order_by(func.count(Coil.id).desc()).limit(1).scalar())

    day_min_weight = (db.query(Coil.date_added).filter(Coil.date_added.between(date_start, date_end))
                      .group_by(Coil.date_added).order_by(func.sum(Coil.weight)).first())

    day_max_weight = (db.query(Coil.date_added).filter(Coil.date_added.between(date_start, date_end))
                      .group_by(Coil.date_added).order_by(func.sum(Coil.weight).desc()).first())

    if day_min_coils_date:
        day_min_coils_date = day_min_coils_date.strftime('%Y-%m-%d')

    if day_max_coils_date:
        day_max_coils_date = day_max_coils_date.strftime('%Y-%m-%d')

    if day_min_weight:
        day_min_weight = day_min_weight[0].strftime('%Y-%m-%d')

    if day_max_weight:
        day_max_weight = day_max_weight[0].strftime('%Y-%m-%d')

    db.close()

    return {
        "coils_added": coils_added,
        "coils_removed": coils_removed,
        "avg_length": avg_length,
        "avg_weight": avg_weight,
        "max_length": max_length,
        "min_length": min_length,
        "max_weight": max_weight,
        "min_weight": min_weight,
        "total_weight": total_weight,
        "max_interval": max_interval.days if max_interval else None,
        "min_interval": min_interval.days if min_interval else None,
        "day_min_coils_date": day_min_coils_date,
        "day_max_coils_date": day_max_coils_date,
        "day_min_weight": day_min_weight,
        "day_max_weight": day_max_weight
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, dest='config')
    args = parser.parse_args()

    server_host = config['SERVER_HOST']
    server_port = int(config['SERVER_PORT'])

    uvicorn.run(app, host=server_host, port=server_port)
