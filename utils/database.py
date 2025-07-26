import os
import pyodbc
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Leer variables
driver = os.getenv('SQL_DRIVER')
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

# Construir cadena de conexión
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Intentar conectar
try:
    conn = pyodbc.connect(connection_string)
    print("✅ Conectado a Azure SQL")
except Exception as e:
    print("❌ Error de conexión a SQL:", e)
    conn = None
