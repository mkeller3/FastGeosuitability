from fastapi import APIRouter


router = APIRouter()

@router.post("/enrich_map/", tags=["Services"])
async def enrich_map():
    """
    
    """

    return {"status": "UP"}