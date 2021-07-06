create table nomivac(
sexo text,
grupo_etario text,
jurisdiccion_residencia text,
jurisdiccion_residencia_id text,
depto_residencia text,
depto_residencia_id text,
jurisdiccion_aplicacion text,
jurisdiccion_aplicacion_id text,
depto_aplicacion text,
depto_aplicacion_id text,
fecha_aplicacion text,
vacuna text,
condicion_aplicacion text,
orden_dosis integer,
lote_vacuna text);

create table updates (
    updated timestamp
);

select * from nomivac limit 1;

create index fecha_appl_index on nomivac(fecha_aplicacion);

select to_timestamp('2021-05-03', 'yyyy-MM-dd') >= (NOW()::);

-- Primera dosis por vacuna

with totalvacunas1raDosis as (
    select count(*) as total1 from nomivac where orden_dosis = 1
), dosesPerVaccine as (
select vacuna, count(*) as dosesGiven
from nomivac, totalvacunas1raDosis
where orden_dosis = 1
group by vacuna
)
select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas1raDosis.total1 as ratio
from totalvacunas1raDosis, dosesPerVaccine;

-- Segundas dosis por vacuna

with totalvacunas2daDosis as (
    select count(*) as total2 from nomivac where orden_dosis = 2
), dosesPerVaccine as (
select vacuna, count(*) as dosesGiven
from nomivac, totalvacunas2daDosis
where orden_dosis = 2
group by vacuna
)
select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas2daDosis.total2 as ratio
from totalvacunas2daDosis, dosesPerVaccine;


-- Toda la info de vacunas por marca

with primeraDosis as (
    with totalvacunas1raDosis as (
    select count(*) as total1 from nomivac where orden_dosis = 1
    ), dosesPerVaccine as (
    select vacuna, count(*) as dosesGiven
    from nomivac, totalvacunas1raDosis
    where orden_dosis = 1
    group by vacuna
    )
    select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas1raDosis.total1 as ratio
    from totalvacunas1raDosis, dosesPerVaccine
), segundaDosis as (
    with totalvacunas2daDosis as (
        select count(*) as total2 from nomivac where orden_dosis = 2
    ), dosesPerVaccine as (
    select vacuna, count(*) as dosesGiven
    from nomivac, totalvacunas2daDosis
    where orden_dosis = 2
    group by vacuna
    )
    select vacuna, dosesGiven, dosesGiven::numeric / totalvacunas2daDosis.total2 as ratio
    from totalvacunas2daDosis, dosesPerVaccine
)
select pD.vacuna as vacuna, pD.dosesGiven as firstDose, pD.ratio as firstDoseRatio, sD.dosesGiven as secondDose, sD.ratio as secondDoseRatio, pD.dosesGiven + sD.dosesGiven as total, 
from primeraDosis pD join segundaDosis sD on pD.vacuna = sD.vacuna; 

-- Vacunas de los últimos 90 días

with primerasDosis as (
    select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas
    from nomivac
    where orden_dosis = 1 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')
    group by fecha_aplicacion
),
segundasDosis as (
    select to_date(fecha_aplicacion, 'yyyy-MM-dd') as fecha_appl, count(*) as totalVacunas
    from nomivac
    where orden_dosis = 2 and fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')
    group by fecha_aplicacion
)
select pd.fecha_appl as fecha_appl, pd.totalVacunas as primerasDosis, sd.totalVacunas as segundasDosis, pd.totalVacunas + sd.totalVacunas as totalVacunas
from primerasDosis pd join segundasDosis sd on pd.fecha_appl = sd.fecha_appl;

-- Dosis por provincia

with FirstDoseProv as (
    select jurisdiccion_aplicacion, count(*) as total1Dosis
    from nomivac
    where orden_dosis=1
    group by jurisdiccion_aplicacion
), SecondDoseProv as (
    select jurisdiccion_aplicacion, count(*) as total2Dosis
    from nomivac
    where orden_dosis=2
    group by jurisdiccion_aplicacion
)
select SecondDoseProv.jurisdiccion_aplicacion, total1Dosis, total2Dosis
from FirstDoseProv, SecondDoseProv
where FirstDoseProv.jurisdiccion_aplicacion = SecondDoseProv.jurisdiccion_aplicacion;

-- Dosis según condicion

with FirstDoseCond as (
    select condicion_aplicacion, count(*) as total1Dosis
    from nomivac
    where orden_dosis=1
    group by condicion_aplicacion
), SecondDoseCond as (
    select condicion_aplicacion, count(*) as total2Dosis
    from nomivac
    where orden_dosis=2
    group by condicion_aplicacion
)
select SecondDoseCond.condicion_aplicacion, total1Dosis, total2Dosis
from FirstDoseCond, SecondDoseCond
where FirstDoseCond.condicion_aplicacion = SecondDoseCond.condicion_aplicacion;

-- Dosis según sexo

with FirstDoseSex as (
    select sexo, count(*) as total1Dosis
    from nomivac
    where orden_dosis=1
    group by sexo
), SecondDoseSex as (
    select sexo, count(*) as total2Dosis
    from nomivac
    where orden_dosis=2
    group by sexo
)
select SecondDoseSex.sexo, total1Dosis, total2Dosis
from FirstDoseSex, SecondDoseSex
where FirstDoseSex.sexo = SecondDoseSex.sexo;

-- General dose stats

select count(*) as totalVacunados
from nomivac
where orden_dosis = 1;

select count(*) as totalVacunados
from nomivac
where orden_dosis = 2;

select count(*) as totalVacunados
from nomivac;

select * from updates order by updated desc limit 1;