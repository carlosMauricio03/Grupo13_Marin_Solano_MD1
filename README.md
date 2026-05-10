# Grupo13_Marin_Solano_MD1

Sistema de analisis de tasas de cambio con componentes ETL, dashboards Streamlit y analisis estadistico en Jupyter.

## Descripcion

Proyecto que extrae datos de tasas de cambio desde una API externa, los almacena en PostgreSQL, y proporciona visualizaciones y modelos predictivos.

## Requisitos

- Python 3.x
- Docker y Docker Compose

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

### Levantar servicios con Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

Servicios:
- PostgreSQL: puerto 5433 (localhost) -> 5432 (contenedor)
- Jupyter Notebook: http://localhost:8888

### Ejecutar dashboards Streamlit (desde proyecto root, fuera de Docker)

```bash
streamlit run streamlit_exchangerate/app.py  # Puerto 8501
streamlit run streamlit_proyecto/app.py     # Puerto 8502
```

### Ejecutar scripts ETL (requiere variables API_KEY y BASE_CURRENCY en .env)

```bash
python -m etl_exchangerate.run   # Extraccion y carga de datos crudos
python -m etl_proyecto.run       # Transformaciones internas
```

## Proceso ETL

### 1. Extraccion (etl_exchangerate/extractor.py)
- API: ExchangeRate-API v6 (https://v6.exchangerate-api.com/v6/)
- Obtiene tasas de cambio para una moneda base
- Respuesta JSON con conversion_rates, base_code, time_last_update_utc

### 2. Transformacion (etl_exchangerate/transformer.py)
- Convierte timestamps UTC a objetos datetime
- Normaliza estructura de datos a registros individuales
- Formato: {base_currency, target_currency, rate, timestamp}

### 3. Carga (etl_exchangerate/loader.py)
- Tablas PostgreSQL: currencies, exchange_rates
- Inserts idempotentes con ON CONFLICT DO NOTHING

### 4. Transformaciones internas (etl_proyecto/)
- compute_daily_averages: Promedio diario por par de monedas
- compute_volatility: Desviacion estandar movil
- compute_pct_change: Variacion porcentual entre dias
- compute_spread: Diferencia entre tasa maxima y minima

## Notebooks

| Notebook | Proposito |
|----------|-----------|
| notebooks/exchange_analysis.ipynb | EDA, pruebas estadisticas (normalidad, heteroscedasticidad, VIF), series de tiempo (ARIMA) |
| notebooks/regresion_lineal/exchange_analysis.ipynb | Regresion lineal para prediccion de tasas de cambio |
| notebooks/regresion_logistica_binaria/regresion_logistica_binaria.ipynb | Clasificacion binaria: direccion del cambio (sube=1, baja/estable=0) |
| notebooks/arbol_decision_clasificacion/arbol_decision_clasificacion.ipynb | Arbol de decision para clasificacion binaria |
| notebooks/arbol_decision_regresion/arbol_decision_regresion.ipynb | Arbol de decision para regresion |

## Estructura del Proyecto

```
├── config/              # Configuracion (settings.py, database.py)
├── db/                 # Schema SQL y DDL
├── docker/            # Docker Compose y Dockerfile
├── etl_exchangerate/   # Extraccion de datos crudos
├── etl_proyecto/       # Transformaciones internas
├── streamlit_exchangerate/  # Dashboard datos crudos
├── streamlit_proyecto/     # Dashboard analisis y metricas
├── notebooks/          # Analisis estadistico y ML
└── requirements.txt    # Todas las dependencias
```

## Autores

- Cmarin-2022@corhuila.edu.com
- iesolano-2022a@corhuila.edu.co