from sqlalchemy.orm import Session
from persistence.persistence import engine
from sqlalchemy import text

from . import models

## Useful for mappings with a single value per key
def convertAllNupleMappingsToDict(aM, keyColumn, valueColumns):
    theDict = {}
    if len(aM) > 0:
        for mapping in aM:
            theDict[mapping[keyColumn]] = {}
            for valueColumnName in valueColumns:
                theDict[mapping[keyColumn]][valueColumnName] = mapping[valueColumnName]
    return theDict

def convertAllPairMappingsToDict(aM, key, value):
    theDict = {}
    if len(aM) > 0:
        for mapping in aM:
            theDict[mapping[key]].append(mapping[value])
    
    return theDict

def get_vaccines_per_day(db: Session):
    
    res = db.execute(
        "with primerasDosis as (\
            select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas\
            from nomivac\
            where orden_dosis = 1 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')\
            group by fecha_aplicacion\
        ),\
        segundasDosis as (\
            select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas\
            from nomivac\
            where orden_dosis = 2 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')\
            group by fecha_aplicacion\
        )\
        select pd.fecha_appl as fecha_appl, pd.totalVacunas as primerasDosis, sd.totalVacunas as segundasDosis, pd.totalVacunas + sd.totalVacunas as totalVacunas\
        from primerasDosis pd join segundasDosis sd on pd.fecha_appl = sd.fecha_appl;"\
    )

    return res.mappings().all()

def get_first_doses_per_day(db: Session):
    
    res = db.execute(
        "select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas\n \
        from nomivac\n \
        where orden_dosis = 1 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')\n \
        group by fecha_aplicacion;"
    )

    return res.mappings().all()

def get_second_doses_per_day(db: Session):
    
    res = db.execute(
        "select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas\n \
        from nomivac\n \
        where orden_dosis = 2 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')\n \
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
    result = res.mappings().all()
    return result


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

    return res.mappings().all() 

def get_total_doses_per_vaccine_to_date(db:Session):

    res = db.execute("\
        with totalvacunas as (\
        select count(*) as total from nomivac\
        ), dosesPerVaccine as (\
        select vacuna, count(*) as dosesGiven\
        from nomivac, totalvacunas\
        group by vacuna\
        )\
        select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas.total as percentage\
        from totalvacunas, dosesPerVaccine;\
    ")

    return res.mappings().all()

def get_doses_per_vaccine_to_date(db:Session):

    res = db.execute("\
        with primeraDosis as (\
            with totalvacunas1raDosis as (\
            select count(*) as total1 from nomivac where orden_dosis = 1\
            ), dosesPerVaccine as (\
            select vacuna, count(*) as dosesGiven\
            from nomivac, totalvacunas1raDosis\
            where orden_dosis = 1\
            group by vacuna\
            )\
            select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas1raDosis.total1 as ratio\
            from totalvacunas1raDosis, dosesPerVaccine\
        ), segundaDosis as (\
            with totalvacunas2daDosis as (\
                select count(*) as total2 from nomivac where orden_dosis = 2\
            ), dosesPerVaccine as (\
            select vacuna, count(*) as dosesGiven\
            from nomivac, totalvacunas2daDosis\
            where orden_dosis = 2\
            group by vacuna\
            )\
            select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas2daDosis.total2 as ratio\
            from totalvacunas2daDosis, dosesPerVaccine\
        )\
        select pD.vacuna as vacuna, pD.dosesGiven as firstDose, pD.ratio as firstDoseRatio, sD.dosesGiven as secondDose, sD.ratio as secondDoseRatio, pD.dosesGiven + sD.dosesGiven as total\
        from primeraDosis pD join segundaDosis sD on pD.vacuna = sD.vacuna; \
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
        select SecondDoseProv.jurisdiccion_aplicacion, total1Dosis, total2Dosis, total1Dosis + total2Dosis as total\
        from FirstDoseProv, SecondDoseProv\
        where FirstDoseProv.jurisdiccion_aplicacion = SecondDoseProv.jurisdiccion_aplicacion;\
    ")

    return res.mappings().all()

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
        select SecondDoseCond.condicion_aplicacion, total1Dosis, total2Dosis, total1Dosis + total2Dosis as total\
        from FirstDoseCond, SecondDoseCond\
        where FirstDoseCond.condicion_aplicacion = SecondDoseCond.condicion_aplicacion;\
        ")

    return res.mappings().all()

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

    return res.mappings().all()


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