from fastapi import HTTPException
import json
from utils.database import execute_query_json
from models.Epiccatalog import EpicCatalog

async def get_epic_catalog() -> list[EpicCatalog]:
    query = "select * from epic.catalogs"
    result = await execute_query_json(query)
    dict_ = json.loads(result)
    
    if not dict_:
        raise HTTPException(status_code=404, detail="No series catalogs found")
    
    return [EpicCatalog(**item) for item in dict_]
