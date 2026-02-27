from db_connection import get_connection

def insert_currency(cursor, code):
    cursor.execute("""
        INSERT INTO currencies (code)
        VALUES (%s)
        ON CONFLICT (code) DO NOTHING
        RETURNING id;
    """, (code,))
    
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    cursor.execute("SELECT id FROM currencies WHERE code = %s;", (code,))
    return cursor.fetchone()[0]


def insert_exchange_rate(base_id, target_id, rate, timestamp):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exchange_rates (base_currency_id, target_currency_id, rate, timestamp)
        VALUES (%s, %s, %s, %s);
    """, (base_id, target_id, rate, timestamp))

    conn.commit()
    cursor.close()
    conn.close()