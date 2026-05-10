from datetime import datetime, timedelta


def compute_daily_averages(conn):
    """
    Calcula el promedio diario de tasa de cambio por par de monedas.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c1.code AS base_currency,
            c2.code AS target_currency,
            DATE(er.timestamp) AS day,
            AVG(er.rate) AS avg_rate,
            COUNT(*) AS sample_count
        FROM exchange_rates er
        JOIN currencies c1 ON er.base_currency_id = c1.id
        JOIN currencies c2 ON er.target_currency_id = c2.id
        GROUP BY c1.code, c2.code, DATE(er.timestamp)
        ORDER BY day DESC
    """)

    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "base_currency": r[0],
            "target_currency": r[1],
            "day": r[2],
            "avg_rate": float(r[3]),
            "sample_count": r[4],
        }
        for r in rows
    ]


def compute_volatility(conn, window_days=7):
    """
    Calcula la volatilidad (desviación estándar) de tasas por ventana móvil.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c1.code AS base_currency,
            c2.code AS target_currency,
            DATE(er.timestamp) AS day,
            STDDEV(er.rate) AS stddev_rate
        FROM exchange_rates er
        JOIN currencies c1 ON er.base_currency_id = c1.id
        JOIN currencies c2 ON er.target_currency_id = c2.id
        WHERE er.timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY c1.code, c2.code, DATE(er.timestamp)
        ORDER BY day DESC
    """, (window_days,))

    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "base_currency": r[0],
            "target_currency": r[1],
            "day": r[2],
            "stddev_rate": float(r[3]) if r[3] else 0.0,
        }
        for r in rows
    ]
