from sqlalchemy.orm import Session
from persistence.persistence import engine
from sqlalchemy import text

from . import models

## Useful for mappings with a single value per key
def convertAllNupleMappingsToDict(aM, keyColumn, valueColumns):
    theDict = {}
    if len(aM) > 0:
        for mapping in aM:
            theDict[mapping[keyColumn]] = []
            for valueColumnName in valueColumns:
                theDict[mapping[keyColumn]].append(mapping[valueColumnName])
    return theDict

def convertAllPairMappingsToDict(aM, key, value):
    theDict = {}
    if len(aM) > 0:
        for mapping in aM:
            theDict[mapping[key]].append(mapping[value])
    
    return theDict

def get_vaccines_per_day(db: Session):
    
    res = db.execute(
        "select to_date(fecha_aplicacion, 'yyyy-MM-dd'), count(*) as totalVacunas\n \
        from nomivac\n \
        where fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')\n \
        group by fecha_aplicacion;"
    )

    return res.mappings().all()

def get_first_doses_per_vaccine_to_date(db:Session):

    res = db.execute("\
    with totalvacunas1raDosis as (\
    select count(*) as total1 from nomivac where orden_dosis = 1\
    ), dosesPerVaccine as (\
    select vacuna, count(*) as dosesGiven\
    from nomivac, totalvacunas1raDosis\
    where orden_dosis = 1\
    group by vacuna\
    )\
    select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas1raDosis.total1 as percentage\
    from totalvacunas1raDosis, dosesPerVaccine;\
    ")

    return convertAllNupleMappingsToDict(res.mappings().all(), 'vacuna', ['dosesGiven', 'percentage'])


def get_second_doses_per_vaccine_to_date(db:Session):

    res = db.execute("\
        with totalvacunas2daDosis as (\
        select count(*) as total2 from nomivac where orden_dosis = 2\
        ), dosesPerVaccine as (\
        select vacuna, count(*) as dosesGiven\
        from nomivac, totalvacunas2daDosis\
        where orden_dosis = 2\
        group by vacuna\
        )\
        select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas2daDosis.total2 as percentage\
        from totalvacunas2daDosis, dosesPerVaccine;\
    ")

    return convertAllNupleMappingsToDict(res.mappings().all(), 'vacuna', ['dosesGiven', 'percentage']) 

def get_total_doses_per_vaccine_to_date(db:Session):

    res = db.execute("\
        with totalvacunas as (\
        select count(*) as total from nomivac\
        ), dosesPerVaccine as (\
        select vacuna, count(*) as dosesGiven\
        from nomivac, totalvacunas\
        group by vacuna\
        )\
        select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas.total as ratio\
        from totalvacunas, dosesPerVaccine;\
    ")

    return res.mappings().all()

def get_doses_per_province(db:Session):

    res = db.execute("\
        with FirstDoseProv as (\
            select jurisdiccion_aplicacion, count(*) as total1Dosis\
            from nomivac\
            where orden_dosis=1\
            group by jurisdiccion_aplicacion\
        ), SecondDoseProv as (\
            select jurisdiccion_aplicacion, count(*) as total2Dosis\
            from nomivac\
            where orden_dosis=2\
            group by jurisdiccion_aplicacion\
        )\
        select SecondDoseProv.jurisdiccion_aplicacion, total1Dosis, total2Dosis\
        from FirstDoseProv, SecondDoseProv\
        where FirstDoseProv.jurisdiccion_aplicacion = SecondDoseProv.jurisdiccion_aplicacion;\
    ")

    return convertAllNupleMappingsToDict(res.mappings().all(), 'jurisdiccion_aplicacion', ['total1Dosis', 'total2Dosis'])

def get_doses_per_condition(db:Session):

    res = db.execute("\
        with FirstDoseCond as (\
            select condicion_aplicacion, count(*) as total1Dosis\
            from nomivac\
            where orden_dosis=1\
            group by condicion_aplicacion\
        ), SecondDoseCond as (\
            select condicion_aplicacion, count(*) as total2Dosis\
            from nomivac\
            where orden_dosis=2\
            group by condicion_aplicacion\
        )\
        select SecondDoseCond.condicion_aplicacion, total1Dosis, total2Dosis\
        from FirstDoseCond, SecondDoseCond\
        where FirstDoseCond.condicion_aplicacion = SecondDoseCond.condicion_aplicacion;\
        ")

    return convertAllNupleMappingsToDict(res.mappings().all(), 'condicion_aplicacion', ['total1Dosis', 'total2Dosis'])

def get_doses_per_sex(db:Session):

    res = db.execute("\
            with FirstDoseSex as (\
                select sexo, count(*) as total1Dosis\
                from nomivac\
                where orden_dosis=1\
                group by sexo\
            ), SecondDoseSex as (\
                select sexo, count(*) as total2Dosis\
                from nomivac\
                where orden_dosis=2\
                group by sexo\
            )\
            select SecondDoseSex.sexo, total1Dosis, total2Dosis\
            from FirstDoseSex, SecondDoseSex\
            where FirstDoseSex.sexo = SecondDoseSex.sexo;\
        ")

    return convertAllNupleMappingsToDict(res.mappings().all(), 'sexo', ['total1Dosis', 'total2Dosis'])


def get_general_dose_stats(db:Session):

    totalFirstDoses = db.execute("\
        select count(*) as totalVacunados\
        from nomivac\
        where orden_dosis = 1;\
    ")

    totalSecondDoses = db.execute("\
        select count(*) as totalVacunados\
        from nomivac\
        where orden_dosis = 2;\
    ")

    first = [x for x in totalFirstDoses][0][0]
    second = [x for x in totalSecondDoses][0][0]
    total = first + second

    return {"firstDoses": first, "secondDoses": second, "totalRegistered": total}