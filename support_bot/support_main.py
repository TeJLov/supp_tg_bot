import logging
import tracemalloc
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio.client import Redis
from tg_bot.support_bot.settings import bot_token, redis_host, redis_port
from tg_bot.support_bot.handlers.include_routers import get_routers

logger = logging.getLogger(__name__)

routers = get_routers()
TOKEN = bot_token

async def main_supp() -> None:
    """Initialize Bot instance with a default parse mode which will be passed to all API calls"""
    # await bot.delete_webhook(drop_pending_updates=True)
    # And the run events dispatching
    storage = RedisStorage(redis=Redis(host=redis_host, port=redis_port))
    dp_supp = Dispatcher(storage=storage)
    tracemalloc.start()
    dp_supp.include_routers(*routers)
    #dp_supp.include_router(router)
    bot_supp = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp_supp.start_polling(bot_supp)

'''
if __name__ == "__main__":
    asyncio.run(main_supp())
'''
