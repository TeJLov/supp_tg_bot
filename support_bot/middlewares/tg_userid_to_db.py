from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

'''
class EntryTGIDMiddleware(BaseMiddleware):
    """
    Проверяет наличие тг юзер_ид в дб, если еще нет то сохраняет
    """
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
        ) -> Any:

        entry_tg_userid(event.from_user.id)
        return await handler(event, data)
'''