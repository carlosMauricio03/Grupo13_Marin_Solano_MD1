# AGENTS.md — Grupo13_Marin_Solano_MD1

## Quick start

```bash
# Iniciar Postgres + Jupyter (Docker)
docker compose -f docker/docker-compose.yml up --build

# Detener servicios
docker compose -f docker/docker-compose.yml down

# Ejecutar dashboards Streamlit localmente (fuera de Docker)
streamlit run streamlit_exchangerate/app.py  # puerto 8501
streamlit run streamlit_proyecto/app.py       # puerto 8502

# Ejecutar ETL scripts (requiere API_KEY y BASE_CURRENCY en .env)
python -m etl_exchangerate.run
python -m etl_proyecto.run
```

## Services (Docker)

| Service | Port | Description |
|---|---|---|
| `postgres` | 5433 | PostgreSQL 16 (container name: `grupo13_postgres`) |
| `jupyter` | 8888 | Jupyter Notebook |

## Environment

- `notebooks/.env` se usa dentro del contenedor Jupyter (DB_HOST=postgres, DB_PORT=5432)
- `.env.local` se usa para ejecutar Streamlit localmente (DB_HOST=localhost, DB_PORT=5433)
- `config/settings.py` carga `.env.local` por defecto y `.env.prod` cuando ENV=prod

## Database

- PostgreSQL 16 via Docker: host **5433** → container 5432
- Schema in `db/schema.sql` — auto-loaded by initdb mount
- Tables: `currencies`, `exchange_rates` (raw); `exchange_rate_daily_avg`, `exchange_rate_volatility`, `exchange_rate_pct_change`, `exchange_rate_spread` (created by `etl_proyecto/loader.py`)
- `config/database.py` provides `get_connection()` — remaps `DB_HOST=postgres` to `localhost:5433` for local connections

## Project structure

| Path | Role |
|---|---|
| `config/settings.py` | Env file loader |
| `config/database.py` | `get_connection()` factory |
| `db/schema.sql` | DDL |
| `docker/docker-compose.yml` | Postgres + Jupyter |
| `docker/Dockerfile` | Image for Jupyter |
| `etl_exchangerate/` | Raw data ingestion |
| `etl_proyecto/` | Aggregations, volatility, ML tables |
| `streamlit_exchangerate/app.py` | Dashboard — datos crudos |
| `streamlit_proyecto/app.py` | Dashboard — análisis y métricas |
| `notebooks/regresion_lineal/exchange_analysis.ipynb` | Statistical notebook |

## Dependencies

- **App/ETL/Streamlit**: `requirements.txt`
- **Notebooks**: `requirements-notebook.txt`
- No lockfiles — always `pip install -r requirements.txt`

## Notable quirks

- No linting, typechecking, or tests
- Streamlit apps use `sys.path.append('..')` — run from project root
- `st.cache_data(ttl=300)` — force refresh by waiting 5 min
- `ON CONFLICT DO NOTHING` — idempotent inserts throughout
