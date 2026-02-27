import os
import logging
from dotenv import load_dotenv

from extractor import extract_rates
from transformer import transform_rates
from loader import insert_currency
from db_connection import get_connection


def main():
    load_dotenv()

    api_key = os.getenv("API_KEY")
    base_currency = os.getenv("BASE_CURRENCY")

    if not api_key:
        raise ValueError("No se encontró la API_KEY en el entorno.")

    logging.info("Iniciando proceso ETL...")

    # EXTRACT
    data = extract_rates(api_key, base_currency)

    if not data:
        logging.warning("No se pudieron obtener datos.")
        return

    # TRANSFORM
    records = transform_rates(data)

    logging.info(f"Total registros transformados: {len(records)}")
    logging.info(f"Ejemplo registro: {records[0]}")

    # LOAD
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for record in records:
            base_id = insert_currency(cursor, record["base_currency"])
            target_id = insert_currency(cursor, record["target_currency"])

            cursor.execute("""
                INSERT INTO exchange_rates 
                (base_currency_id, target_currency_id, rate, timestamp)
                VALUES (%s, %s, %s, %s);
            """, (
                base_id,
                target_id,
                record["rate"],
                record["timestamp"]
            ))

        conn.commit()
        logging.info("Datos insertados correctamente en la base de datos.")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error durante la carga: {e}")
        raise

    finally:
        cursor.close()
        conn.close()
        logging.info("Conexión cerrada.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()