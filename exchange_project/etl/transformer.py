from datetime import datetime

def transform_rates(data: dict):
    base_currency = data.get("base_code")
    timestamp_str = data.get("time_last_update_utc")
    rates = data.get("conversion_rates", {})

    # Convertir string a datetime
    timestamp = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %z")

    records = []

    for target_currency, rate in rates.items():
        records.append({
            "base_currency": base_currency,
            "target_currency": target_currency,
            "rate": rate,
            "timestamp": timestamp
        })

    return records