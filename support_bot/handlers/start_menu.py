import logging
from aiogram import Router, F
from aiogram.types import (
    Message, KeyboardButton,
    ReplyKeyboardRemove, ChatMemberUpdated,
    ErrorEvent
    )
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, KICKED
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.support_bot.handlers.txt_for_menu import start_menu_kb, mmenu_staff, NO_AUTH_TXT
from tg_bot.support_bot.states.state_bot import FSMMenu, FSMMenuStaff
from tg_bot.support_bot.keyboards.inlinekb import build_inline_kb
from tg_bot.support_bot.filters.is_persons import IsManager, IsMentor, IsBan
from tg_bot.support_bot.db_utils.for_users import (
    entry_tg_userid, set_tg_username_and_id, get_phone
    )
from tg_bot.support_bot.db_utils.table_requests import unset_all_flag_is_work
from tg_bot.support_bot.db_utils.lids import create_lid

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart(), IsBan(), F.chat.type == "private")
async def start_command_ban(message: Message):
    await message.answer("Доступ запрещен!")

@router.message(CommandStart(), IsManager(), F.chat.type == "private")
@router.message(CommandStart(), IsMentor(), F.chat.type == "private")
async def start_command_staff(message: Message, state: FSMContext):
    """
    Меню для сотрудников
    """
    inline_kb = await build_inline_kb(mmenu_staff)
    await unset_all_flag_is_work(message.from_user.id)
    try:
        await state.clear()
        await state.set_state(FSMMenuStaff.mmenu)
    except (Exception) as err:
        print(err)
        logger.exception(err)
    await message.answer(f"Здравствуйте {hbold(message.from_user.full_name)}!\n"
                        "Выберите действие:",
                        reply_markup=inline_kb.as_markup()
                    )

@router.message(CommandStart(), F.chat.type == "private")
async def start_command_all(message: Message, state: FSMContext):
    """
    Команда старт для не авторизованых пользователей и учеников 
    """
    await state.clear()
    try:
        await state.set_state(FSMMenu.mmenu)
    except (Exception) as err:
        print(err)
        logger.exception(err)
    if not await entry_tg_userid(tg_id=message.from_user.id):
        kb = ReplyKeyboardBuilder()
        kb.add(KeyboardButton(text="Авторизоваться", request_contact=True))
        await message.answer(NO_AUTH_TXT,
                            reply_markup=kb.as_markup(
                                resize_keyboard=True,
                                show_alert=True
                                )
                            )
    else:
        inline_kb = await build_inline_kb(start_menu_kb)
        await message.answer(text=f"Здравствуйте {hbold(message.from_user.full_name)}!\n"
                            "бла бла бла бл",
                            reply_markup=inline_kb.as_markup()
                        )

@router.message(F.contact, F.contact.user_id == F.from_user.id)
async def gt_contact(message: Message, state: FSMContext):
    """
    Если поделился контактом
    """
    phone = message.contact.phone_number
    if await get_phone(phone):
        await message.answer("Вы успешно авторизованы", reply_markup=ReplyKeyboardRemove())
        await set_tg_username_and_id(phone, message.from_user.username, message.from_user.id)
        inline_kb = await build_inline_kb(start_menu_kb)
        try:
            await state.update_data(tg_userid=message.from_user.id)
            await state.set_state(FSMMenu.mmenu)
        except (Exception) as err:
            print(err)
            logger.exception(err)
        await message.answer(text=f"Здравствуйте {hbold(message.from_user.full_name)}!\n"
                            "бла бла бла бл",
                            reply_markup=inline_kb.as_markup()
                        )
    else:
        await message.answer(
            "К сожалению, ученика с таким номером телефона нет в базе. Вы можете обратится в поддержку",
            reply_markup=ReplyKeyboardRemove()
            )
        inline_kb = await build_inline_kb(start_menu_kb)
        try:
            await state.update_data(tg_userid=message.from_user.id)
            await state.set_state(FSMMenu.mmenu)
        except (Exception) as err:
            print(err)
            logger.exception(err)
        print("phone----->", phone)
        await create_lid(
            phone,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            message.from_user.id
            )
        await message.answer(text="Здравствуйте! бла бла бла бл",
                            reply_markup=inline_kb.as_markup()
                        )

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    pass

@router.errors()
async def error_handler(exception: ErrorEvent):
    logger.exception('handler error', exc_info=exception)
    print('handler error', exception)
