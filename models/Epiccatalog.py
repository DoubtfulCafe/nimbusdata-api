from pydantic import BaseModel, Field
from typing import Optional


class EpicCatalog(BaseModel):
    appid: Optional[int] = Field(
        default=None,
        ge=1,
        description="ID único de la aplicación (Steam App ID)"
    )

    name: Optional[str] = Field(
        default=None,
        description="Nombre del videojuego"
    )

    release_date: Optional[str] = Field(
        default=None,
        description="Fecha de lanzamiento (formato: YYYY-MM-DD)"
    )

    developer: Optional[str] = Field(
        default=None,
        description="Desarrollador del videojuego"
    )

    positive_ratings: Optional[int] = Field(
        default=None,
        ge=0,
        description="Número de valoraciones positivas"
    )

    price: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Precio del videojuego en dólares"
    )
