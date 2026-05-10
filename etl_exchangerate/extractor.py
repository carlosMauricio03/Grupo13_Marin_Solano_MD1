import requests
import logging

def extract_rates(api_key: str, base_currency: str):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "conversion_rates" not in data:
            raise ValueError("La respuesta no contiene tasas de cambio")

        return data

    except requests.exceptions.Timeout:
        logging.error("La petición a la API excedió el tiempo límite.")
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error HTTP: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error general en la petición: {e}")
    except ValueError as e:
        logging.error(f"Error en estructura de datos: {e}")

    return None