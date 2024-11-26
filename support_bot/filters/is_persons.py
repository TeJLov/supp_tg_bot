from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import Message

from tg_bot.support_bot.db_utils.for_users import (
    get_groupstaff_tgid, get_ban_is_tg_userid, get_learner
    )

class IsAdmin(BaseFilter):
    """
    Фильтр админов
    """
    def __init__(self, user_ids: int | List[int]) -> None:
        self.user_ids = user_ids

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.user_ids, int):
            return message.from_user.id == self.user_ids
        return message.from_user.id in self.user_ids

class IsManager(BaseFilter):
    """
    Фильтр менеджеров по бд
    """
    async def __call__(self, message: Message) -> bool:
        x = await get_groupstaff_tgid(member=message.from_user.id, group="Менеджеры")
        print("get_groupstaff_tgid Manger --->>", x)
        return x

class IsMentor(BaseFilter):
    """
    Фильтр наставников по бд
    """
    async def __call__(self, message: Message) -> bool:
        return await get_groupstaff_tgid(member=message.from_user.id, group="Наставники")

class IsLearner(BaseFilter):
    """
    Фильтр учеников по бд
    """
    async def __call__(self, message: Message) -> bool:
        return await get_learner(message.from_user.id)

class IsBan(BaseFilter):
    """
    Фильтр забаненых
    """
    async def __call__(self, message: Message) -> bool:
        return await get_ban_is_tg_userid(message.from_user.id)
