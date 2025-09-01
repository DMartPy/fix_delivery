from fastapi import APIRouter, HTTPException
from services.ship_price import clear_usd_rub_cache, fetch_usd_rub_rate

usd_rub_router = APIRouter()


@usd_rub_router.get("/usd-rate")
async def get_usd_rate():
    """Получить текущий курс USD→RUB (с кэшированием)"""
    rate = await fetch_usd_rub_rate()
    return {
        "usd_rate": rate,
    }



@usd_rub_router.delete("/usd-rate/cache")
async def clear_usd_rate_cache():
    """Очистить кэш курса USD→RUB"""

    success = await clear_usd_rub_cache()
    if success:
        return {"message": "Cache cleared successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear cache")
