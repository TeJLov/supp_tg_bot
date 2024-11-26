from aiogram import Router

from tg_bot.support_bot.handlers import (
    start_menu,
    supp_menu,
    menu_feedback,
    mentor_menu,
    staff_menu
)

def get_routers() -> list[Router]:
    routers = [
        start_menu.router,
        supp_menu.router,
        menu_feedback.router,
        mentor_menu.router,
        staff_menu.router
    ]

    return routers

__all__ = (
    'get_routers',
)
