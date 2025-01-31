__all__ = "router"

from aiogram import Router
from .handlers.users_handler import router as users_router
from .handlers.mark_actions import router as add_mark_router
from .handlers.callback import router as callback_router
from .handlers.admin_actions import router as admins_router

router = Router()
router.include_router(add_mark_router)
router.include_router(admins_router)
router.include_router(users_router)
router.include_router(callback_router)
