__all__ = (
    "router"
)

from aiogram import Router
from .handlers.users_handler import router as users_router

router = Router()
router.include_router(users_router)
