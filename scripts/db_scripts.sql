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

-- Vacunas de los últimos 14 días

select to_date(fecha_aplicacion, 'yyyy-MM-dd'), count(*) as totalVacunas
from nomivac
where fecha_aplicacion != 'S.I.' and TO_TIMESTAMP(fecha_aplicacion, 'yyyy-MM-dd') >= (NOW()::timestamp - interval '90 days')
group by fecha_aplicacion;

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
