from fastapi import APIRouter, HTTPException

from src.services.shipping import clear_usd_rub_cache, get_usd_rub_rate

usd_rub_router = APIRouter()


@usd_rub_router.get("/usd-rate")
async def get_usd_rate():
    """Получить текущий курс USD к RUB."""
    try:
        rate = await get_usd_rub_rate()
        return {"usd_rate": rate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения курса: {str(e)}")


@usd_rub_router.post("/clear-cache")
async def clear_cache():
    """Очистить кеш курса USD/RUB."""
    try:
        await clear_usd_rub_cache()
        return {"message": "Кеш очищен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки кеша: {str(e)}")
