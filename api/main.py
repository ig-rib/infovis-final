from fastapi import Depends, FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from typing import Optional
from persistence import queries
from persistence.persistence import SessionLocal, engine
from urllib import request
import zipfile

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/vaccines/")
def home(db: Session = Depends(get_db)):
    return queries.get_vaccines_per_day(db)

@app.get("/vaccines/last_updated")
def home(db: Session = Depends(get_db)):
    return queries.get_last_updated_date(db)

@app.get("/vaccines/first_doses")
def home(db: Session = Depends(get_db)):
    return queries.get_first_doses_per_day(db)

@app.get("/vaccines/second_doses")
def home(db: Session = Depends(get_db)):
    return queries.get_second_doses_per_day(db)

@app.get("/vaccines/companies/first_doses")
def firstDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_first_doses_per_vaccine_to_date(db)

@app.get("/vaccines/companies/second_doses")
def secondDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_second_doses_per_vaccine_to_date(db)

@app.get("/vaccines/companies/total_doses")
def totalDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_total_doses_per_vaccine_to_date(db)

@app.get("/vaccines/companies/total_data")
def totalDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_doses_per_vaccine_to_date(db)

@app.get("/vaccines/provinces/total_doses")
def totalDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_doses_per_province(db)

@app.get("/vaccines/conditions/total_doses")
def totalDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_doses_per_condition(db)

@app.get("/vaccines/sexes/total_doses")
def totalDosesPerCompany(db: Session = Depends(get_db)):
    return queries.get_doses_per_sex(db)

@app.get("/vaccines/general_stats")
def general_stats(db: Session = Depends(get_db)):
    return queries.get_general_dose_stats(db)

# Weird committing behaviour, TODO find bypass
@app.on_event("startup")
@repeat_every(seconds = 60 * 60 * 24)
def updateDataBases() -> None:
    request.urlretrieve('https://sisa.msal.gov.ar/datos/descargas/covid-19/files/datos_nomivac_covid19.zip', 'files/datos_nomivac_covid19.zip')
    print("extracting")
    with zipfile.ZipFile('files/datos_nomivac_covid19.zip') as zip_ref:
        zip_ref.extractall('files')
    print("extracted!")
    with open('files/datos_nomivac_covid19.csv', 'r') as f, SessionLocal() as db:
        print("doing")
        deleteConn = engine.connect()
        deleteConn.execute("delete from nomivac")
        print("delet]ed")
        # deleteConn.commit()
        deleteConn.close()
        conn = engine.raw_connection()
        cursor = conn.cursor()
        print("creating")
        cmd = "COPY nomivac(sexo,\
                grupo_etario,\
                jurisdiccion_residencia,\
                jurisdiccion_residencia_id,\
                depto_residencia,\
                depto_residencia_id,\
                jurisdiccion_aplicacion,\
                jurisdiccion_aplicacion_id,\
                depto_aplicacion,\
                depto_aplicacion_id,\
                fecha_aplicacion,\
                vacuna,\
                condicion_aplicacion,\
                orden_dosis,\
                lote_vacuna) FROM STDIN CSV DELIMITER ',' HEADER"
        cursor.copy_expert(cmd, f)
        print("committing")
        conn.commit()
        conn.close()
        print("saving update")
        conn = engine.connect()
        conn.execute("insert into updates values(NOW()::timestamp)")
        # conn.commit()
        conn.close()
    print("done")
