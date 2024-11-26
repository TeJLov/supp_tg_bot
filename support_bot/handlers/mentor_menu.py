import logging
from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.support_bot.filters.is_persons import IsLearner
from tg_bot.support_bot.states.state_bot import FSMMenu
from tg_bot.support_bot.filters.is_persons import IsBan
from tg_bot.support_bot.keyboards.inlinekb import build_inline_kb
from tg_bot.support_bot.db_utils.for_users import check_subs, get_learner
from tg_bot.support_bot.db_utils.table_requests import (
    create_new_question, create_chat_message, add_new_message_in_question,
    get_responder_for_question
    )
from tg_bot.support_bot.handlers.txt_for_menu import (
    mentor_menu, back, start_menu_kb, MMENU_TXT, work_eval,
    WORK_EVAL_TXT
    )

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "key1st", FSMMenu.mmenu, IsLearner())
async def callback_menu_mentor(callback: CallbackQuery,
                            state: FSMContext
                            ):
    '''
    Меню работы с наставником
    '''
    await state.set_state(FSMMenu.menu_mentor)
    inline_kb = await build_inline_kb(mentor_menu)
    await callback.message.edit_text("Выберите пункт из меню:",
                                    reply_markup=inline_kb.as_markup())

@router.callback_query(F.data == "key1st", FSMMenu.mmenu)
async def callback_not_learner(callback: CallbackQuery,
                            state: FSMContext
                            ):
    """
    Сработает если не ученик хочет 
    """
    inline_kb = await build_inline_kb(back)
    await state.set_state(FSMMenu.menu_mentor)
    await callback.message.edit_text(
        "Работа с наставником доступна только ученикам", reply_markup=inline_kb.as_markup()
        )

@router.callback_query(F.data == "back", FSMMenu.menu_mentor)
async def callback_back_to_mmenu(callback: CallbackQuery,
                            state: FSMContext
                            ):
    """
    Назад к главному меню
    """
    inline_kb = await build_inline_kb(start_menu_kb)
    await state.set_state(FSMMenu.mmenu)
    await callback.message.edit_text(
        MMENU_TXT, reply_markup=inline_kb.as_markup()
        )

@router.callback_query(or_f(F.data == "key1mtrm", F.data == "key2mtrm"), FSMMenu.menu_mentor)
async def callback_mentor_theme(callback: CallbackQuery,
                            state: FSMContext
                            ):
    """
    Тема обращения
    """
    if await check_subs(callback.from_user.id, callback.data):
        await state.update_data(menu_mentor=callback.data)
        await state.set_state(FSMMenu.them_mentor)
        await callback.message.edit_text(
            "Напишите кратко тему вопроса. Ограничение: только текст, 80 символов"
            )
    else:
        inline_kb = await build_inline_kb(back)
        await callback.message.edit_text(
            "Не найдена активная подписка, для покупки или продления оюратитесь техподдержку",
            reply_markup=inline_kb.as_markup()
            )

@router.message(F.text, FSMMenu.them_mentor)
async def message_to_theme(message: Message,
                            state: FSMContext
                            ):
    """
    Проверка лимита темы и запрос текста обращения к ментеру
    """
    if len(message.text) > 80:
        await message.answer(
            f"Вы привисли лимит текста на {len(message.text) - 80} символа\n"
            f"Постарайтесь сократить.\n"
            f"Еще раз напишите кратко тему вопроса. Ограничение: только текст, 80 символов"
            )
    else:
        await state.update_data(them_mentor=message.text)
        await state.set_state(FSMMenu.question)
        kb = ReplyKeyboardBuilder()
        kb.add(KeyboardButton(text="Отправить"))
        await message.answer(
            "Напишите текст. Можно приложить Фото. Видео, Аудио либо Документ\n"
            "Когда изложите свои мысли и приложите все необходимые файлы, нажмите кнопку 'Отправить'",
            reply_markup=kb.as_markup(resize_keyboard=True)
            )

@router.message(F.text.startswith('Отправить'), FSMMenu.question)
async def message_question(message: Message, state: FSMContext):
    """
    Создает запрос и сообщения в бд
    """
    msg_id = []
    full_name = message.from_user.full_name
    tg_userid = message.from_user.id
    data_fsm = await state.get_data()
    if not data_fsm.get("msg"):
        await message.answer("Сначала нужно что то написать")
    else:
        data_msg = data_fsm['msg']
    for key, value in data_msg.items():
        msg_id.append(await create_chat_message(
            tg_userid,
            value['message_txt'], value['image'], value['video'], value['voice'],
            value['file'], value['caption'], who=full_name)
            )
    if await get_learner(message.from_user.id):
        question_id = await create_new_question(data_fsm, tg_userid, msg_id, from_lid=False)
    else: question_id = await create_new_question(data_fsm, tg_userid, msg_id, from_lid=True)
    await state.update_data(question_id=question_id)
    await message.answer("Ожидайте ответа", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMMenu.dialog)

@router.message(FSMMenu.question)
async def question_msg(message: Message, state: FSMContext):
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

@router.message(~IsBan(), FSMMenu.dialog)
async def now_message(message: Message, state: FSMContext):
    """
    Сохраняет новое сообщение в бд
    """
    data_question_id = await state.get_data()

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
            id_question=data_question_id['question_id']
            ) # Нет логики пересылки ментору

@router.callback_query(F.data == "dialog_complet", ~IsBan(), FSMMenu.dialog)
async def dialog_complet_users(callback: CallbackQuery, state: FSMContext):

    await state.set_state(FSMMenu.work_eval)
    kb = await build_inline_kb(work_eval)
    await callback.message.answer(WORK_EVAL_TXT, reply_markup=kb.as_markup()) ################

@router.callback_query(F.data.startswith("work_eval_"), FSMMenu.work_eval)
async def finish_question(callback: CallbackQuery, state: FSMContext):

    num_eval = callback.data.split("_")[2]
    print("num_eval ------>", num_eval)
    await callback.message.answer("/start")
