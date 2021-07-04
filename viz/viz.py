import urllib.request, json
import altair as alt
from altair.vegalite.v4.api import condition
from altair.vegalite.v4.schema.channels import Tooltip
import pandas as pd

BASE_URL = 'http://localhost:8000/vaccines/'
COMPANIES_FIRST_DOSES = 'companies/first_doses'
COMPANIES_SECOND_DOSES = 'companies/second_doses'
COMPANIES_TOTAL_DOSES = 'companies/total_doses'
COMPANIES_TOTAL_DATA = 'companies/total_data'
PROVINCES_TOTAL_DOSES = 'provinces/total_doses'
CONDITIONS_TOTAL_DOSES = 'conditions/total_doses'
SEXES_TOTAL_DOSES = 'sexes/total_doses'
GENERAL_STATS = 'general_stats'

# with urllib.request.urlopen(BASE_URL + COMPANIES_FIRST_DOSES) as cfdUrl:
#     companiesFirstDoses = json.loads(cfdUrl.read())
# with urllib.request.urlopen(BASE_URL + COMPANIES_SECOND_DOSES) as csdUrl:
#     companiesSecondDoses = json.loads(csdUrl.read())
# with urllib.request.urlopen(BASE_URL + COMPANIES_TOTAL_DOSES) as ctdUrl:
#     companiesTotalDoses = json.loads(ctdUrl.read())


###
# Texto Con Stats Generales
###

# with urllib.request.urlopen(BASE_URL + COMPANIES_TOTAL_DOSES) as ctdUrl:
#     generalStats = json.loads(ctdUrl.read())



###
# Area Plot con Dosis de los últimos 90 días
###

with urllib.request.urlopen(BASE_URL) as last90DaysUrl:
    last90DaysTotal = json.loads(last90DaysUrl.read())

df = pd.DataFrame(last90DaysTotal).rename(columns={"primerasdosis": "Primera Dosis", "segundasdosis": "Segunda Dosis", "totalvacunas": "Total"})

areaPlot = alt.Chart(df)\
    .mark_area()\
    .transform_fold(['Primera Dosis', 'Segunda Dosis'],
        as_=['Orden de Dosis', 'Cantidad Aplicada'])\
    .encode(x=alt.X('fecha_appl:T', title='Fecha de Aplicación'), y='Cantidad Aplicada:Q', color='Orden de Dosis:N', tooltip=[alt.Tooltip('fecha_appl:T', title='Fecha de Aplicación'), 'Orden de Dosis:N', 'Cantidad Aplicada:Q', alt.Tooltip('Total:Q', title='Total (Cualquier Dosis)')])\
    .properties(width=700)
# areaPlot.show()

###
# Bar Chart de Dosis por Tipo de Vacuna
###

with urllib.request.urlopen(BASE_URL + COMPANIES_TOTAL_DATA) as ctdataUrl:
    companiesTotalData = json.loads(ctdataUrl.read())

df = pd.DataFrame(companiesTotalData).rename(columns={"firstdose": "Primera Dosis", "seconddose": "Segunda Dosis"})

barChart = alt.Chart(df[['vacuna', 'Primera Dosis','Segunda Dosis']])\
.transform_fold(['Primera Dosis', 'Segunda Dosis'], as_=['Orden de Dosis', 'Cantidad Aplicada'])\
.mark_bar().encode(
    x='vacuna:N',
    y='Cantidad Aplicada:Q',
    color='Orden de Dosis:N',
    tooltip=[alt.Tooltip('vacuna:N', title="Vacuna"), alt.Tooltip('Primera Dosis:Q'), alt.Tooltip('Segunda Dosis:Q')]
).properties(width=700)

# barChart.show()

###
# One-Column Bubble Chart Para Vacunas Por Condición 
###

with urllib.request.urlopen(BASE_URL + CONDITIONS_TOTAL_DOSES) as condtdUrl:
    conditionsTotalDoses = json.loads(condtdUrl.read())

df = pd.DataFrame(conditionsTotalDoses)

bubbleChart = alt.Chart(df)\
    .mark_circle()\
    .encode(y=alt.Y('total:Q', title='Total Dosis Aplicadas', scale=alt.Scale(type='log')),
        color=alt.Color('condicion_aplicacion',
            type='nominal',
            title = 'Total de Dosis Aplicadas',
            scale=alt.Scale(scheme='category20c')),
        size=alt.Size('total',
            type='quantitative',
            scale=alt.Scale(type='log', range=[200, 2000]),
            title='Dosis Aplicadas'),
        tooltip=[alt.Tooltip('condicion_aplicacion:N', title='Condición de Aplicación'),
            alt.Tooltip('total1dosis', title='Primera Dosis'),
            alt.Tooltip('total2dosis', title='Segunda Dosis'),
            alt.Tooltip('total', title='Total Dosis')])\
    .properties(width=200, height=500)
# bubbleChart.show()

###
# Horizontal Bar Chart (would-be Pie Chart) Con Dosis por Sexo
###

with urllib.request.urlopen(BASE_URL + SEXES_TOTAL_DOSES) as stdUrl:
    sexesTotalDoses = json.loads(stdUrl.read())

df = pd.DataFrame(sexesTotalDoses).rename(columns={"total1dosis": "Primera Dosis", "total2dosis": "Segunda Dosis"})
df['sexo'].replace({'S.I.': 'No especifica', 'F': 'Femenino', 'M': 'Masculino'}, inplace=True)

horizontalBarChart = alt.Chart(df).mark_bar()\
    .transform_fold(['Primera Dosis', 'Segunda Dosis'], as_=['Orden de Dosis', 'Cantidad Aplicada'])\
    .encode(y='sexo:N',
        x='Cantidad Aplicada:Q',
        color='Orden de Dosis:N',
        tooltip=[alt.Tooltip('sexo:N', title='Sexo'), 'Primera Dosis', 'Segunda Dosis'])\
    .properties(width=300, height=200)

# horizontalBarChart.show()

###
# Choropleth de vacunaciones por provincia 
###

provincias = json.load(open('viz/provincias.geojson'))

with urllib.request.urlopen(BASE_URL + PROVINCES_TOTAL_DOSES) as ptdUrl:
    provincesTotalDoses = json.loads(ptdUrl.read())

provinciasFiltered = [ {'nombre': feature['properties']['nombre'], 'longitude': feature['geometry']['coordinates'][0], 'latitude': feature['geometry']['coordinates'][1]} for feature in provincias['features'] ]

df = pd.DataFrame(provinciasFiltered)
ptdDf = pd.DataFrame(provincesTotalDoses)

mergedData = df.merge(ptdDf, left_on='nombre', right_on='jurisdiccion_aplicacion')

geoShape = alt.Chart(mergedData)\
    .mark_circle(stroke='black', strokeWidth=1)\
    .encode(
        color=alt.Color('total',
            type='quantitative',
            scale=alt.Scale(scheme=alt.SchemeParams(name='lighttealblue', count=9), type='log'),
            title = 'Total de Dosis Aplicadas'),
        size=alt.Size('total',
            type='quantitative',
            scale=alt.Scale(type='log', range=[500, 5000])),
        longitude='longitude:Q',
        latitude='latitude:Q',
        tooltip=[alt.Tooltip('nombre:N', title='Provincia'), alt.Tooltip('total1dosis', title='Primeras Dosis Aplicadas'),
            alt.Tooltip('total2dosis', title='Segundas Dosis Aplicadas'),
            alt.Tooltip('total', title='Total de Dosis Aplicadas')]
    ).properties(
        width=500,
        height=500
    )
# geoShape.show()

dashboard = alt.vconcat(areaPlot, barChart, (bubbleChart | geoShape), horizontalBarChart)

dashboard.show()