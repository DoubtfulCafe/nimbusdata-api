
from fastapi import FastAPI, Response, Request
import uvicorn
from utils.database import get_db_connection
import logging

from controllers.firebase import register_user_firebase, login_user_firebase
from models.Userlogin import UserLogin
from models.Userregister import UserRegister

from utils.security import validate

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
@validate
async def read_root(request: Request, response: Response):
    return {
        "hello": "world"
    }



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

@app.post("/signup")
async def signup(user: UserRegister):
    result = await register_user_firebase(user)
    return result

@app.post("/login")
async def login(user: UserLogin):
    result = await login_user_firebase(user)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
