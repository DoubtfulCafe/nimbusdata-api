from fastapi import FastAPI
from utils.database import get_db_connection
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
def read_root():
    """
    Endpoint de prueba para verificar que la API está corriendo.
    """
    return {"message": "API NimbusData corriendo correctamente 🚀"}


@app.get("/test-db")
async def test_db_connection():
    """
    Verifica si se puede establecer una conexión con la base de datos SQL.
    """
    try:
        conn = await get_db_connection()
        conn.close()
        return {"message": "✅ Conexión a la base de datos exitosa"}
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {str(e)}")
        return {"error": "❌ Fallo la conexión con la base de datos", "details": str(e)}
