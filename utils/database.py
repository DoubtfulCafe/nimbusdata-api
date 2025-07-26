"""
Módulo para manejar conexión y consultas a base de datos Azure SQL usando pyodbc.

Este módulo se conecta usando variables de entorno para mantener la seguridad y flexibilidad.
Incluye logging detallado y manejo de errores robusto.

Funciones:
- get_db_connection: crea y devuelve una conexión activa.
- execute_query_json: ejecuta una consulta y devuelve resultados en formato JSON.

Autor: Daniel Villeda
Proyecto: NimbusData
"""

from dotenv import load_dotenv
import os
import pyodbc
import logging
import json

# Carga el archivo .env y sus variables al entorno del sistema
load_dotenv()

# Configura el sistema de logging con formato y nivel de detalle
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Instancia de logger específico para este archivo

# Obtiene los parámetros de conexión desde las variables de entorno
driver = os.getenv('SQL_DRIVER')
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

# Construye el string de conexión en formato ODBC
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"


async def get_db_connection():
    """
    Establece una conexión con la base de datos utilizando pyodbc.

    Returns:
        conn (pyodbc.Connection): conexión activa a la base de datos.

    Raises:
        Exception: si ocurre un error durante la conexión.
    """
    try:
        logger.info(f"Intentando conectar a la base de datos...")
        conn = pyodbc.connect(connection_string, timeout=10)  # Tiempo de espera máximo: 10 segundos
        logger.info("Conexión exitosa a la base de datos.")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Error de conexión a la base de datos: {str(e)}")
        raise Exception(f"Error de conexión a la base de datos: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado durante la conexión: {str(e)}")
        raise


async def execute_query_json(sql_template, params=None, needs_commit=False):
    """
    Ejecuta una consulta SQL y devuelve el resultado como JSON.

    Args:
        sql_template (str): consulta SQL con o sin parámetros (ej. SELECT * FROM tabla WHERE id = ?)
        params (tuple): parámetros para la consulta si es necesario
        needs_commit (bool): si es True, se ejecutará commit (para INSERT/UPDATE/DELETE)

    Returns:
        str: resultado de la consulta en formato JSON

    Raises:
        Exception: si ocurre un error durante la ejecución o la conexión
    """
    conn = None
    cursor = None
    try:
        # Establece conexión a la base de datos
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Log informativo con el tipo de consulta (con o sin parámetros)
        param_info = "(sin parámetros)" if not params else f"(con {len(params)} parámetros)"
        logger.info(f"Ejecutando consulta {param_info}: {sql_template}")

        # Ejecuta la consulta
        if params:
            cursor.execute(sql_template, params)
        else:
            cursor.execute(sql_template)

        # Procesa los resultados en una lista de diccionarios
        results = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]  # Obtiene nombres de columnas
            logger.info(f"Columnas obtenidas: {columns}")
            for row in cursor.fetchall():
                # Convierte datos binarios a string para que no den error al hacer JSON
                processed_row = [str(item) if isinstance(item, (bytes, bytearray)) else item for item in row]
                results.append(dict(zip(columns, processed_row)))
        else:
            logger.info("La consulta no devolvió columnas (posiblemente INSERT/UPDATE/DELETE).")

        # Si se indicó que hay cambios persistentes, hacer commit
        if needs_commit:
            logger.info("Realizando commit de la transacción.")
            conn.commit()

        # Devuelve resultado serializado a JSON
        return json.dumps(results, default=str)

    # Manejo de errores
    except pyodbc.Error as e:
        logger.error(f"Error ejecutando la consulta (SQLSTATE: {e.args[0]}): {str(e)}")
        if conn and needs_commit:
            try:
                logger.warning("Realizando rollback debido a error.")
                conn.rollback()
            except pyodbc.Error as rb_e:
                logger.error(f"Error durante el rollback: {rb_e}")
        raise Exception(f"Error ejecutando consulta: {str(e)}") from e

    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución de la consulta: {str(e)}")
        raise

    # Siempre cierra recursos, haya o no haya error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Conexión cerrada.")
