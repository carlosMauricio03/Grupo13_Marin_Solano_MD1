import os
import logging

from config import settings

from etl.extractor import extract_rates
from etl.transformer import transform_rates
from etl.loader import load_rates
from etl.db_connection import get_connection


def main():
    api_key = os.getenv("API_KEY")
    base_currency = os.getenv("BASE_CURRENCY")

    if not api_key:
        raise ValueError("No se encontró la API_KEY en el entorno.")

    logging.info("Iniciando proceso ETL...")

    # 1. EXTRACT
    data = extract_rates(api_key, base_currency)

    if not data:
        logging.warning("No se pudieron obtener datos.")
        return

    # 2. TRANSFORM
    records = transform_rates(data)

    if not records:
        logging.warning("No hay registros para procesar.")
        return

    logging.info(f"Total registros transformados: {len(records)}")
    logging.info(f"Ejemplo registro: {records[0]}")

    # 3. LOAD
    conn = get_connection()

    try:
        load_rates(conn, records)
        logging.info("Datos cargados correctamente en la base de datos.")

    except Exception as e:
        logging.error(f"Error durante el proceso ETL: {e}")
        raise

    finally:
        conn.close()
        logging.info("Conexión cerrada.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()