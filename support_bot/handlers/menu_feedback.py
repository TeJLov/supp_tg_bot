import logging
from aiogram import Router, F
from aiogram.filters import or_f, Command
from aiogram.types import (
    CallbackQuery, Message, KeyboardButton, ReplyKeyboardRemove
    )
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.support_bot.states.state_bot import FSMMenu
from tg_bot.support_bot.handlers.txt_for_menu import start_menu_kb, back
from tg_bot.support_bot.keyboards.inlinekb import build_inline_kb
from tg_bot.support_bot.filters.is_persons import IsBan
from tg_bot.support_bot.db_utils.table_requests import create_feedback, create_chat_message

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "key3st", ~IsBan(), FSMMenu.mmenu)
async def callback_menu_fb(callback: CallbackQuery, state: FSMContext):
    '''
    Отзыв/Предложение
    '''
    await callback.message.delete()
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Отправить"))
    await callback.message.answer(
        "Напишите текст. Можно приложить Фото. Видео, Аудио либо Документ\n"
        "Когда изложите свои мысли и приложите все необходимые файлы, нажмите кнопку 'Отправить'",
        reply_markup=kb.as_markup(resize_keyboard=True)
        )
    await state.set_state(FSMMenu.feedback)

@router.message(F.text.startswith('Отправить'), FSMMenu.feedback)
async def callback_fin_feedbk(message: Message, state: FSMContext):
    """
    Создание сообщений и фидбека в бд
    Назад к главному меню
    """
    msg_id = []
    data = await state.get_data()
    full_name = message.from_user.full_name
    tg_username = message.from_user.username
    tg_userid = message.from_user.id
    data_msg = data['msg']
    for key, value in data_msg.items():
        msg_id.append(await create_chat_message(
            tg_userid,
            value['message_txt'], value['image'], value['video'], value['voice'],
            value['file'], value['caption'], who=full_name)
            )
    await create_feedback(
        full_name, tg_username, tg_userid, msg_id)
    await message.answer("Спасибо за Ваше мнение!", reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await state.set_state(FSMMenu.mmenu)
    inline_kb = await build_inline_kb(start_menu_kb)
    await message.answer("бла бла бла бл", reply_markup=inline_kb.as_markup())

@router.message(or_f((F.text),
                (F.photo),
                (F.video),
                (F.document),
                (F.voice)),
                FSMMenu.feedback)
async def feedback_msg(message: Message, state: FSMContext):
    image = None
    video = None
    voice = None
    file = None
    caption = None
    message_txt = message.text
    if message.photo:
        image = message.photo[-1].file_id
    if message.video:
        video = message.video.file_id
    if message.voice:
        voice = message.voice.file_id
    if message.document:
        file = message.document.file_id
    if message.caption:
        caption = message.caption
    msgs = {1:{
        "message_txt": message_txt, "image": image,
        "video": video, "voice": voice, "file": file,
        "caption": caption
        }}
    data = await state.get_data()
    if 'msg' in data:
        count = len(list(data['msg'])) + 1
        msgs[count] = msgs.pop(1)
        msgs.update(data["msg"])
    await state.update_data(msg=msgs)


"""    image = None
    video = None
    voice = None
    file = None
    caption = None
    full_name = message.from_user.full_name
    tg_username = message.from_user.username
    tg_userid = message.from_user.id
    message_txt = message.text
    if message.photo:
        image = message.photo[-1].file_id
    if message.video:
        video = message.video.file_id
    if message.voice:
        voice = message.voice.file_id
    if message.document:
        file = message.document.file_id
    if message.caption:
        caption = message.caption
    await create_feedback(
        full_name, tg_username, tg_userid, message_txt,
        image, video, voice,
        file, caption
        )
"""
