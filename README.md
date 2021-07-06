# Setup

Para correr el trabajo, primero es necesario tener una base de datos en PostgreSQL con el nombre "infovis", corriendo en localhost en el puerto 5432.
El nombre de usuario y contraseña de psql deben ser por defecto postgres:postgres.
Dada la simplicidad del proyecto, cualquier personalización en cuanto a la base de datos se debe hacer directamente desde el archivo api/persistence/persistence.py.
La conexión por default se hace por medio del siguiente url.

'postgresql://postgres:postgres@localhost:5432/infovis'

Las tablas necesarias se crean con los siguientes comandos:

```
create table nomivac(
id serial primary key,
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
```

# API - Ejecución

FastAPI y uvicorn deben estar instalados:

```
pip3 install fastapi
pip3 install uvicorn
```

Para correr la API es necesario ejecutar los siguientes comandos desde el directorio raíz:

```
cd api;
uvicorn main:app;
```

## API - Consideraciones

Actualizar las bases de datos, dado el peso de los datasets (mayor a 3GB), puede ser costoso desde la API.
Si se quiere descargar, descomprimir e importar manualmente los datos, se puede comentar el código de la función "updateDataBases" del archivo api/main.py
Para importar directamente se puede utilizar el comando desde una consola, siendo datos_nomivac_covid19.csv el archivo del dataset:

```
\copy nomivac(sexo, grupo_etario, jurisdiccion_residencia, jurisdiccion_residencia_id, depto_residencia, depto_residencia_id, jurisdiccion_aplicacion, jurisdiccion_aplicacion_id, depto_aplicacion, depto_aplicacion_id, fecha_aplicacion, vacuna, condicion_aplicacion, orden_dosis, lote_vacuna) from './datos_nomivac_covid19.csv' delimiter ',' csv header" -U postgres -d infovis
```

# Visualizaciones - Ejecución

Altair debe estar instalado:

```
pip3 install altair
```

Para mostrar las visualizaciones, desde el directorio raíz ejecutar:

```
python3 viz/viz.py
```

Las consultas pueden tomar su tiempo ya que la base de datos no está optimizada para un dataset de este tamaño...
