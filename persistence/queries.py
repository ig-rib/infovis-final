from sqlalchemy.orm import Session
from persistence.persistence import engine
from sqlalchemy import text

from . import models

def get_vaccines_per_day(db: Session):
    conn = db.connection()
    
    res = conn.execute(
        "select to_date(fecha_aplicacion, 'yyyy-MM-dd'), count(*) as totalVacunas\n \
        from nomivac\n \
        where fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '14 days')\n \
        group by fecha_aplicacion;"
    )

    return res.mappings().all()

