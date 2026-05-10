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
        currencies = set()

        for r in records:
            currencies.add(r["base_currency"])
            currencies.add(r["target_currency"])

        insert_currencies_bulk(cursor, currencies)

        currency_map = get_currency_map(cursor, currencies)

        values = []
        for r in records:
            values.append((
                currency_map[r["base_currency"]],
                currency_map[r["target_currency"]],
                r["rate"],
                r["timestamp"]
            ))

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
