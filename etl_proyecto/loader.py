SUMMARY_TABLES_DDL = """
CREATE TABLE IF NOT EXISTS exchange_rate_daily_avg (
    id SERIAL PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    day DATE NOT NULL,
    avg_rate NUMERIC(20,10) NOT NULL,
    sample_count INTEGER NOT NULL,
    UNIQUE (base_currency, target_currency, day)
);

CREATE TABLE IF NOT EXISTS exchange_rate_volatility (
    id SERIAL PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    day DATE NOT NULL,
    stddev_rate NUMERIC(20,10) NOT NULL,
    UNIQUE (base_currency, target_currency, day)
);

CREATE TABLE IF NOT EXISTS exchange_rate_pct_change (
    id SERIAL PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    current_rate NUMERIC(20,10) NOT NULL,
    previous_rate NUMERIC(20,10),
    pct_change NUMERIC(10,4),
    UNIQUE (base_currency, target_currency)
);

CREATE TABLE IF NOT EXISTS exchange_rate_spread (
    id SERIAL PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    day DATE NOT NULL,
    spread NUMERIC(20,10) NOT NULL,
    UNIQUE (base_currency, target_currency, day)
);
"""


def _ensure_tables(cursor):
    cursor.execute(SUMMARY_TABLES_DDL)


def load_summary(conn, daily_avg, volatility, pct_change, spread):
    cursor = conn.cursor()

    try:
        _ensure_tables(cursor)

        for record in daily_avg:
            cursor.execute("""
                INSERT INTO exchange_rate_daily_avg 
                    (base_currency, target_currency, day, avg_rate, sample_count)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (base_currency, target_currency, day) DO UPDATE
                    SET avg_rate = EXCLUDED.avg_rate,
                        sample_count = EXCLUDED.sample_count
            """, (
                record["base_currency"],
                record["target_currency"],
                record["day"],
                record["avg_rate"],
                record["sample_count"],
            ))

        for record in volatility:
            cursor.execute("""
                INSERT INTO exchange_rate_volatility 
                    (base_currency, target_currency, day, stddev_rate)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (base_currency, target_currency, day) DO UPDATE
                    SET stddev_rate = EXCLUDED.stddev_rate
            """, (
                record["base_currency"],
                record["target_currency"],
                record["day"],
                record["stddev_rate"],
            ))

        for record in pct_change:
            cursor.execute("""
                INSERT INTO exchange_rate_pct_change 
                    (base_currency, target_currency, current_rate, previous_rate, pct_change)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (base_currency, target_currency) DO UPDATE
                    SET current_rate = EXCLUDED.current_rate,
                        previous_rate = EXCLUDED.previous_rate,
                        pct_change = EXCLUDED.pct_change
            """, (
                record["base_currency"],
                record["target_currency"],
                record["current_rate"],
                record["previous_rate"],
                record["pct_change"],
            ))

        for record in spread:
            cursor.execute("""
                INSERT INTO exchange_rate_spread 
                    (base_currency, target_currency, day, spread)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (base_currency, target_currency, day) DO UPDATE
                    SET spread = EXCLUDED.spread
            """, (
                record["base_currency"],
                record["target_currency"],
                record["day"],
                record["spread"],
            ))

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
