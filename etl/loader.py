from etl.db_connection import get_connection

def insert_currencies_bulk(cursor, currencies):
    cursor.executemany("""
        INSERT INTO currencies (code)
        VALUES (%s)
        ON CONFLICT (code) DO NOTHING;
    """, [(c,) for c in currencies])


def get_currency_map(cursor, currencies):
    cursor.execute("""
        SELECT id, code FROM currencies 
        WHERE code = ANY(%s);
    """, (list(currencies),))

    rows = cursor.fetchall()
    return {code: id for (id, code) in rows}


def load_rates(conn, records):
    cursor = conn.cursor()

    try:
        # 1. Obtener todas las monedas únicas
        currencies = set()

        for r in records:
            currencies.add(r["base_currency"])
            currencies.add(r["target_currency"])

        # 2. Insertar todas de una vez
        insert_currencies_bulk(cursor, currencies)

        # 3. Obtener IDs
        currency_map = get_currency_map(cursor)

        # 4. Preparar inserts masivos
        values = []
        for r in records:
            values.append((
                currency_map[r["base_currency"]],
                currency_map[r["target_currency"]],
                r["rate"],
                r["timestamp"]
            ))

        # 5. Insert masivo
        cursor.executemany("""
            INSERT INTO exchange_rates 
            (base_currency_id, target_currency_id, rate, timestamp)
            VALUES (%s, %s, %s, %s);
        """, values)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise

    finally:
        cursor.close()