__all__ = "router"

from aiogram import Router
from .admins import router as admins_router
from .marks import router as marks_router
from .points import router as points_router

router = Router()
router.include_router(marks_router)
router.include_router(admins_router)
router.include_router(points_router)

