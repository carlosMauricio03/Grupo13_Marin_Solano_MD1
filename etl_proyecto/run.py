import os
import logging

from config import settings
from config.database import get_connection
from etl_proyecto.aggregator import compute_daily_averages, compute_volatility
from etl_proyecto.calculator import compute_pct_change, compute_spread
from etl_proyecto.loader import load_summary


def main():
    logging.info("Iniciando ETL Proyecto — transformaciones internas...")

    conn = get_connection()

    try:
        daily_avg = compute_daily_averages(conn)
        logging.info(f"Promedios diarios calculados: {len(daily_avg)} registros")

        volatility = compute_volatility(conn)
        logging.info(f"Volatilidad calculada: {len(volatility)} registros")

        pct_change = compute_pct_change(conn)
        logging.info(f"Variación porcentual calculada: {len(pct_change)} registros")

        spread = compute_spread(conn)
        logging.info(f"Spread calculado: {len(spread)} registros")

        load_summary(conn, daily_avg, volatility, pct_change, spread)
        conn.commit()
        logging.info("Resultados cargados correctamente.")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error en ETL Proyecto: {e}")
        raise

    finally:
        conn.close()
        logging.info("Conexión cerrada.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
