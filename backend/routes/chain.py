"""Chain metadata routes"""
from fastapi import APIRouter, HTTPException
import json
from config import redis_client
from services.blockchain import get_chain_metadata

router = APIRouter(prefix="/chain", tags=["chain"])


@router.get("/meta")
async def chain_meta():
    """Get current gas price and block number with caching"""
    cache_key = "chain_meta"
    
    # Try cache first
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    
    try:
        result = get_chain_metadata()
        
        # Cache for 5 minutes
        if redis_client:
            redis_client.setex(cache_key, 300, json.dumps(result))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chain metadata: {str(e)}")
