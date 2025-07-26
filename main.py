import uvicorn
import logging

from fastapi import FastAPI, Response, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.Epiccatalog import get_epic_catalog

from models.Userregister import UserRegister
from models.Userlogin import UserLogin
from models.Epiccatalog import EpicCatalog

from utils.security import validateadmin
from utils.telemetry import setup_simple_telemetry, instrument_fastapi_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

telemetry_enabled = setup_simple_telemetry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Epic Games Catalog API",
    description="API para la gestión del catálogo de videojuegos de Epic",
    version="0.0.1",
    lifespan=lifespan
)

if telemetry_enabled:
    instrument_fastapi_app(app)
    logger.info("Application Insights enabled")
    logger.info("FastAPI Instrumented")
else:
    logger.warning("Application Insight disabled")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.0.1"}

@app.get("/")
async def read_root(request: Request, response: Response):
    return {"message": "Bienvenido a la API de Epic Games"}

@app.post("/signup")
async def signup(user: UserRegister):
    result = await register_user_firebase(user)
    return result

@app.post("/login")
async def login(user: UserLogin):
    result = await login_user_firebase(user)
    return result

@app.get("/epic", response_model=list[EpicCatalog])
async def get_epic_games():
    """Obtener todos los videojuegos del catálogo Epic"""
    games = await get_epic_catalog()
    return games

@app.post("/epic", response_model=EpicCatalog, status_code=201)
@validateadmin
async def create_new_game(request: Request, response: Response, game_data: EpicCatalog):
    """Agregar un nuevo videojuego al catálogo"""
    new_game = await create_game(game_data)
    return new_game

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
