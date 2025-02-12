__all__ = "router"

from aiogram import Router
from .handlers.users_handler import router as users_router
from .handlers.mark_actions import router as marks_router
from .handlers.callbacks import router as callback_router
from .handlers.admin_actions import router as admins_router
from .handlers.point_action import router as points_router

router = Router()
router.include_router(marks_router)
router.include_router(admins_router)
router.include_router(points_router)

router.include_router(users_router)
router.include_router(callback_router)
