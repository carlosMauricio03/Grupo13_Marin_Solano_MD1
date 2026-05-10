def compute_pct_change(conn):
    """
    Calcula la variación porcentual entre la última y la penúltima tasa
    para cada par de monedas.
    """
    cursor = conn.cursor()

    cursor.execute("""
        WITH ranked_rates AS (
            SELECT 
                c1.code AS base_currency,
                c2.code AS target_currency,
                er.rate,
                er.timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY c1.code, c2.code 
                    ORDER BY er.timestamp DESC
                ) AS rn
            FROM exchange_rates er
            JOIN currencies c1 ON er.base_currency_id = c1.id
            JOIN currencies c2 ON er.target_currency_id = c2.id
        )
        SELECT 
            curr.base_currency,
            curr.target_currency,
            curr.rate AS current_rate,
            prev.rate AS previous_rate,
            CASE 
                WHEN prev.rate IS NOT NULL AND prev.rate != 0 
                THEN ((curr.rate - prev.rate) / prev.rate) * 100
                ELSE NULL
            END AS pct_change
        FROM ranked_rates curr
        LEFT JOIN ranked_rates prev 
            ON curr.base_currency = prev.base_currency 
            AND curr.target_currency = prev.target_currency
            AND prev.rn = 2
        WHERE curr.rn = 1
    """)

    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "base_currency": r[0],
            "target_currency": r[1],
            "current_rate": float(r[2]),
            "previous_rate": float(r[3]) if r[3] else None,
            "pct_change": float(r[4]) if r[4] else None,
        }
        for r in rows
    ]


def compute_spread(conn):
    """
    Calcula el spread (diferencia entre tasa máxima y mínima) por día
    para cada par de monedas.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c1.code AS base_currency,
            c2.code AS target_currency,
            DATE(er.timestamp) AS day,
            MAX(er.rate) - MIN(er.rate) AS spread
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
            "spread": float(r[3]),
        }
        for r in rows
    ]
