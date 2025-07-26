from fastapi import FastAPI
from utils import database

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Conexión a SQL OK" if database.conn else "Error de conexión"}
