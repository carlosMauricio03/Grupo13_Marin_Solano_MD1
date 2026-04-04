import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "local")

if ENV == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.local")

print(f"[CONFIG] Entorno cargado: {ENV}")