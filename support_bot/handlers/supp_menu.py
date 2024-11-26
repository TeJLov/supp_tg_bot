import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.support_bot.keyboards.inlinekb import build_inline_kb
from tg_bot.support_bot.states.state_bot import FSMMenu
from tg_bot.support_bot.filters.is_persons import IsBan
from tg_bot.support_bot.handlers.txt_for_menu import (
    menu_supp_theme,
    start_menu_kb,
    menu_supp_chavo
    )

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "key2st", FSMMenu.mmenu)
async def callback_supp_menu(callback: CallbackQuery,
                            state: FSMContext
                            ):
    '''
    Меню поддержки, тема обращения
    '''
    await state.update_data(where=callback.data)
    inline_kb = await build_inline_kb(menu_supp_theme)
    await callback.message.edit_text("Выберите тему обращения",
                                    reply_markup=inline_kb.as_markup())
    await state.set_state(FSMMenu.menu_supp_1)

@router.callback_query(F.data == 'back', FSMMenu.menu_supp_1)
async def callback_to_mmenu(callback: CallbackQuery, state: FSMContext):
    """
    Назад к главному меню
    """
    await state.update_data(where='')
    await state.set_state(FSMMenu.mmenu)
    inline_kb = await build_inline_kb(start_menu_kb)
    await callback.message.edit_text("бла бла бла бл",
                                    reply_markup=inline_kb.as_markup())

@router.callback_query(F.data == "back", FSMMenu.menu_supp_2)
async def callback_to_supmenu(callback: CallbackQuery, state: FSMContext):
    """
    Назад к меню поддержки (тема)
    """
    await state.update_data(menu_supp_1='')
    await callback_supp_menu(callback, state)

@router.callback_query(F.data == "key1mst", FSMMenu.menu_supp_1)
async def callback_supp_menu_chavo(callback: CallbackQuery, state: FSMContext):
    '''
    Меню поддержки, 1 пункт
    '''
    await state.update_data(menu_supp_1=callback.data)
    inline_kb = await build_inline_kb(menu_supp_chavo)
    await callback.message.edit_text("Попробуйте найти ответ в Чаво:",
                                    reply_markup=inline_kb.as_markup())
    await state.set_state(FSMMenu.menu_supp_2)

@router.callback_query(F.data == "key5mst", ~IsBan(), FSMMenu.menu_supp_2)
async def callback_msg_for_supp(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMMenu.question)
    await callback.message.edit_reply_markup(reply_markup=None)
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Отправить"))
    await callback.message.answer(
        "Напишите текст. Можно приложить Фото. Видео, Аудио либо Документ\n"
        "Когда изложите свои мысли и приложите все необходимые файлы, нажмите кнопку 'Отправить'",
        reply_markup=kb.as_markup(resize_keyboard=True)
        )
