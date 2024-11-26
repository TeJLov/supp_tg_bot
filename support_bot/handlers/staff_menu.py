import logging
import re
import jsonpickle
from contextlib import suppress
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.storage.base import StorageKey
#from aiogram.utils.formatting import Bold, as_list, as_key_value
from tg_bot.support_bot.states.state_bot import FSMMenuStaff
from tg_bot.support_bot.filters.is_persons import IsManager, IsMentor
from tg_bot.support_bot.db_utils.for_users import set_ban_user
from tg_bot.support_bot.db_utils.table_requests import (
    get_question_list, set_responder_for_question, get_dialog_msg,
    get_tgid_questioner, add_new_message_in_question, set_flag_is_work,
    unset_flag_is_work, end_question
    )
from tg_bot.support_bot.keyboards.inlinekb import build_inline_kb, Pagination, paginator
from tg_bot.support_bot.handlers.txt_for_menu import mmenu_staff
from tg_bot.support_bot.handlers.mentor_menu import dialog_complet_users

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(Pagination.filter(F.action.in_(["prev","next"])))
async def process(callback: CallbackQuery, callback_data: Pagination, state: FSMContext):
    """
    Пагинация
    """
    msg_txt_all = await state.get_data()
    page_num = int(callback_data.page)
    page_main = page_num - 1 if page_num > 0 else 0

    if callback_data.action == "next":
        page_main = page_num + 1 if page_num < (len(msg_txt_all['pagin'])-1) else page_num
    with suppress(TelegramBadRequest):
        msg_list = await callback.message.edit_text(
            "\n\n".join(msg_txt_all['pagin'][page_main]),
            reply_markup=paginator(page=page_main)
            )
        await state.update_data(msg_list={'chat_id': msg_list.chat.id, 'message_id':msg_list.message_id})
    await callback.answer("Готово!")

@router.message(F.text.startswith("/in_work"), FSMMenuStaff.list_referens)
@router.message(F.text.startswith("/to_work"), FSMMenuStaff.list_referens)
async def to_in_work(message: Message, state: FSMContext):
    """
    Взять в работу  
    """
    #prev_msg = await state.get_data()
    #prev_msg_chat_id = prev_msg['msg_list']['chat_id'] 'chat_id': msg_list.chat.id,
    #print('prev_msg  ----->', prev_msg['msg_list'], message)
    #await message.edit_text('fj', kwargs=prev_msg['msg_list'])

    ######_____- Не получилось сделать удаление листа работ(

    work_id = re.findall(r'\d+$', string=message.text)
    work_id = int(*work_id)
    await state.update_data(work_id=work_id)
    if message.text.startswith("/to_work"):
        await set_responder_for_question(work_id, message.from_user.id)
    msg_dialog = await get_dialog_msg(work_id)
    await set_flag_is_work(work_id)
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="*Назад к списку*"))
    kb.row(KeyboardButton(text="*Забанить*"), KeyboardButton(text="*Завершить диалог*"))
    for msg in msg_dialog:
        if msg['messages_message']:
            await message.answer(
                f'От: {msg['messages_from_who']}\n\n'
                f'{msg['messages_message']}\n\nОтправленно: {msg['messages_sent'].strftime('%d.%m.%Y %H:%M')}',
                reply_markup=kb.as_markup(resize_keyboard=True))
        elif msg['messages_image']:
            await message.answer_photo(
                msg['messages_image'],
                caption=f'{msg['messages_caption']}\n\nОтправленно: {msg['messages_sent'].strftime('%d.%m.%Y %H:%M')}',
                reply_markup=None
                )
        elif msg['messages_video']:
            await message.answer_video(
                msg['messages_video'],
                caption=f'{msg['messages_caption']}\n\nОтправленно: {msg['messages_sent'].strftime('%d.%m.%Y %H:%M')}',
                reply_markup=None
                )
        elif msg['messages_voice']:
            await message.answer_voice(
                msg['messages_voice'],
                caption=f'{msg['messages_caption']}\n\nОтправленно: {msg['messages_sent'].strftime('%d.%m.%Y %H:%M')}',
                reply_markup=None
                )
        elif msg['messages_file']:
            await message.answer_document(
                msg['messages_file'],
                caption=f'{msg['messages_caption']}\n\nОтправленно: {msg['messages_sent'].strftime('%d.%m.%Y %H:%M')}',
                reply_markup=None
                )
        await state.set_state(FSMMenuStaff.dialog)

@router.callback_query(F.data == "back_mmenu", FSMMenuStaff.list_referens)
async def back_to_mmenu(callback: CallbackQuery, state: FSMContext):
    """
    Назад к главному меню
    """
    inline_kb = await build_inline_kb(mmenu_staff)
    await state.clear()
    await state.set_state(FSMMenuStaff.mmenu)
    await callback.message.edit_text(
        "Выберите действие:", reply_markup=inline_kb.as_markup()
        )

@router.callback_query(F.data == "key1msf", IsMentor(), FSMMenuStaff.mmenu)
async def mentor_list_work(callback: CallbackQuery, state: FSMContext):
    """
    "key1msf": "Обработать обращения"
    """
    await callback.message.delete()
    await state.set_state(FSMMenuStaff.list_referens)
    list_question = await get_question_list("Наставник по ноутбукам", "NEW")
    list_question_inwork = await get_question_list("Наставник по ноутбукам", "INWORK", callback.from_user.id)
    list_question_waiting = await get_question_list("Наставник по ноутбукам", "WAITING")
    msg_txt_all = []

    for item in list_question_waiting:
        msg_waiting_txt = (
            f"<b>ID:</b> {item['id']}\n"
            f'<b>Статус:</b> В ожидании   🔴\n'
            f'<b>Дата:</b> {item['date_start'].strftime('%d.%m.%Y %H:%M')}\n'
            f'<b>Курс:</b> {item['first_menu']}\n'
            f'<b>Тема:</b> {item['theme']}\n'
            f'<b>Взять в работу:   /to_work_{item['id']}</b>'
            )
        msg_txt_all.append(msg_waiting_txt)

    for item in list_question:
        msg_work_txt = (
            f"<b>ID:</b> {item['id']}\n"
            f'<b>Статус:</b> Открыт   🟢\n'
            f'<b>Дата:</b> {item['date_start'].strftime('%d.%m.%Y %H:%M')}\n'
            f'<b>Курс:</b> {item['first_menu']}\n'
            f'<b>Тема:</b> {item['theme']}\n'
            f'<b>Взять в работу:   /to_work_{item['id']}</b>'
            )
        msg_txt_all.append(msg_work_txt)

    for item in list_question_inwork:
        if item['who_answered_tgid'] == callback.from_user.id:
            msg_inwork_txt = (
                f"<b>ID:</b> {item['id']}\n"
                f'<b>Статус:</b> В работе   🟡\n'
                f'<b>Дата:</b> {item['date_start'].strftime('%d.%m.%Y %H:%M')}\n'
                f'<b>Курс:</b> {item['first_menu']}\n'
                f'<b>Тема:</b> {item['theme']}\n'
                f'Новое сообщение {"🟢" if item['is_new_message'] else "🔴"}\n'
                f'<b>Продолжить диалог:   /in_work_{item['id']}</b>'
                )
            msg_txt_all.append(msg_inwork_txt)

    pages = []

    for indx in range(0, len(msg_txt_all), 5):
        pages.append(msg_txt_all[indx:indx+5])
    await state.update_data(pagin=pages)
    await callback.message.answer(
        text="\n\n".join(pages[0]),
        reply_markup=paginator(page=0))
    #msg_dump = jsonpickle.dumps(callback.message)
    #print('msg_list -------->>', msg_dump)
    #await state.update_data(msg_list={'chat_id': msg_list.chat.id, 'message_id': msg_list.message_id})

@router.message(F.text.startswith("*Назад к списку*"), FSMMenuStaff.dialog)
async def back_to_list_work(message: Message, state: FSMContext):

    class XClass(object):
        def __init__(self):
            self.message = message
            self.from_user = message.from_user
            self.data = 'key1msf'

    data =  await state.get_data()
    await unset_flag_is_work(data['work_id'])
    await mentor_list_work(XClass(), state)

@router.message(F.text.startswith("/in_work"), FSMMenuStaff.dialog)
@router.message(F.text.startswith("/to_work"), FSMMenuStaff.dialog)
async def pass_word(message: Message):
    """
    Пасует при повторном нажатии команд
    """

@router.message(F.text.startswith("*Завершить диалог*"), FSMMenuStaff.dialog)
async def end_dialog(message: Message, state: FSMContext):
    """
    Меняет 
    """
    data =  await state.get_data()
    tgid_user = await get_tgid_questioner(data['work_id'])

    class ZClass(object):
        def __init__(self):
            self.message = message
            self.from_user = tgid_user
            self.data = 'dialog_complet' ###########
    #hzhz = StorageKey(chat_id=tgid_user)
    state_user = state.get_state(tgid_user)
    print("state_user ------>>>>", state_user)
    await dialog_complet_users(ZClass(), state)
    await end_question(data['work_id'])
    await back_to_list_work(message, state)

@router.message(F.text.startswith("*Забанить*"), FSMMenuStaff.dialog)
async def ban_user(message: Message, state: FSMContext):
    await set_ban_user(message.from_user.id)
    await message.answer("Пользователь забанен!")
    await back_to_list_work(message, state)

@router.message(FSMMenuStaff.dialog)
async def messages_dialog(message: Message, state: FSMContext):
    """
    Захватывает все входящие сообщения, сохраняет в бд и пересылает пользователю
    """
    work_id = await state.get_data()
    tgids_questioner = await get_tgid_questioner(work_id['work_id'])
    tgids_questioner = dict(*tgids_questioner)

    if message.photo:
        image = message.photo[-1].file_id
    else: image = None
    if message.video:
        video = message.video.file_id
    else: video = None
    if message.voice:
        voice = message.voice.file_id
    else: voice = None
    if message.document:
        file = message.document.file_id
    else: file = None
    await add_new_message_in_question(
            message.from_user.id,
            message.text,
            image,
            video,
            voice,
            file,
            message.caption,
            who=message.from_user.full_name,
            id_question=work_id['work_id']
            )
    await message.send_copy(tgids_questioner['learner_tgid'] or tgids_questioner['lead_tgid'])
