import logging
from datetime import date
from django.db.models import F, Subquery, OuterRef
from tg_bot.models import SuppBotTableRequests as SBTR, FeedBack, ChatMessages
from tg_bot.support_bot.handlers.txt_for_menu import (
    mentor_menu, start_menu_kb,
    menu_supp_theme
    )
from users.models import User
from nb1school.models import Learners, Leads
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@sync_to_async
def create_new_question(data: dict, tg_userid: int, msg_id: list, from_lid: bool):
    if from_lid:
        id_lead = Leads.objects.filter(
            tg_userid=tg_userid).values_list('id', flat=True)

        now = SBTR.objects.create(
            lead_id = id_lead[0],
            first_menu = start_menu_kb.get(data.get("where")),
            theme = menu_supp_theme.get(data.get("menu_supp_1"))
            )
        now.messages.set(msg_id)
        now.save()
        result = now.id
    else:
        id_learner = Learners.objects.filter(
            tg_userid=tg_userid).values_list('id', flat=True)

        now = SBTR.objects.create(
            learner_id = id_learner[0],
            first_menu = mentor_menu.get(
                data.get("menu_mentor")
                ) or start_menu_kb.get(data.get("where")),
            theme = data.get("them_mentor") or menu_supp_theme.get(data.get("menu_supp_1"))
            )
        now.messages.set(msg_id)
        now.save()
        result = now.id
    return result

@sync_to_async
def create_chat_message(
    tg_userid: int,
    message: str | None,
    image: str | None,
    video: str | None,
    voice: str | None,
    file: str | None,
    caption: str | None,
    who: str
):
    """
    Сохраняейт сообщение в бд
    """
    obj_id = ChatMessages.objects.create(
        tg_userid = tg_userid,
        from_who = who,
        message = message,
        image = image,
        video = video,
        voice = voice,
        file = file,
        caption = caption
    ).pk
    return obj_id

@sync_to_async
def create_feedback(
    full_name: str,
    tg_username: str,
    tg_userid: int,
    msg_id: list
    ):
    """
    Сохраняет новый отзыв в бд
    """
    try:
        now = FeedBack.objects.create(
            full_name = full_name,
            tg_username = tg_username,
            tg_userid = tg_userid,
            )
        now.messages.set(msg_id)
    except ExceptionGroup as err:
        print("create_feedback -->", err)
        logger.exception(err)

@sync_to_async
def get_question_list(
    direction: str,
    status: str,
    tg_id: int = None
    ):
    """
    Возвращает список обращений в бот.

    direction = first_menu - Направление (Наставник по ноутбукам | Обращение в Техподдержку)
    status = {
        "NEW": "Открыт",
        "INWORK": "В работе",
        "WAITING": "В ожидании",
        "COMPLET": "Выполнен"
    }
    tg_id нужен для статуса INWORK (ответственного)
    """
    if status == "INWORK" and tg_id:
        result = list(
            SBTR.objects.filter(
                first_menu=direction, status=status, who_answered__tg_userid=tg_id
                ).annotate(
                    learner_lname=F("learner__last_name"), learner_fname=F("learner__first_name"),
                    who_answered_tgid=F("who_answered__tg_userid")
                    ).values(
                        "id", "date_start", "learner_lname", "learner_fname", "first_menu",
                        "theme", "who_answered_tgid", "is_new_message"
                        ).order_by("date_start")
            )
    elif status != "INWORK":
        result = list(
            SBTR.objects.filter(
                first_menu=direction, status=status
                ).annotate(
                    learner_lname=F("learner__last_name"), learner_fname=F("learner__first_name"),
                    who_answered_tgid=F("who_answered__tg_userid")
                    ).values(
                        "id", "date_start", "learner_lname", "learner_fname", "first_menu",
                        "theme", "who_answered_tgid"
                        ).order_by("date_start")
            )
    return result

@sync_to_async
def set_responder_for_question(id_question: int, tg_id: int):
    """
    Назначает ответственного и статус в работе
    """
    from_user = User.objects.get(tg_userid=tg_id).pk
    SBTR.objects.filter(pk=id_question).update(who_answered=from_user, status="INWORK")
    #question.objects.select_for_update(who_answered=from_user)

@sync_to_async
def get_dialog_msg(id_question: int):
    question = list(
        SBTR.objects.filter(pk=id_question).order_by('messages__sent').annotate(
            learner_tgid=F("learner__tg_userid"), lead_tgid=F("lead__tg_userid"),
            messages_from_who=F("messages__from_who"), messages_message=F("messages__message"),
            messages_sent=F("messages__sent"), messages_edited=F("messages__edited"),
            messages_image=F("messages__image"), messages_video=F("messages__video"),
            messages_voice=F("messages__voice"), messages_file=F("messages__file"),
            messages_caption=F("messages__caption")
            ).values()
        )
    return question

@sync_to_async
def get_tgid_questioner(id_question: int):
    """
    Принимает ИД тикета, возвращает tg userid Лида(lead_tgid) либо Ученика(learner_tgid)
    """
    result = list(
        SBTR.objects.filter(pk=id_question).annotate(
            learner_tgid=F("learner__tg_userid"), lead_tgid=F("lead__tg_userid")
            ).values()
        )
    return result

@sync_to_async
def get_responder_for_question(id_question: int):
    result = SBTR.objects.filter(pk=id_question).annotate(
            who_answered_tgid=F("who_answered__tg_userid")).values()
    print("get_responder_for_question ------->>", result)
    return result

@sync_to_async
def add_new_message_in_question(
    tg_userid: int,
    message: str | None,
    image: str | None,
    video: str | None,
    voice: str | None,
    file: str | None,
    caption: str | None,
    who: str,
    id_question: int
):
    obj_id = ChatMessages.objects.create(
        tg_userid = tg_userid,
        from_who = who,
        message = message,
        image = image,
        video = video,
        voice = voice,
        file = file,
        caption = caption
    ).pk

    now = SBTR.objects.get(pk=id_question)
    now.messages.add(obj_id)
    now.is_new_message = True
    now.save()

@sync_to_async
def set_flag_is_work(id_question: int):
    """
    Ставит флаг is_work и уберает is_new_message
    """
    now = SBTR.objects.get(pk=id_question)
    now.is_new_message = False
    now.save()
    now.is_work = True
    now.save()

@sync_to_async
def unset_flag_is_work(id_question: int):
    """
    Уберает флаг is_work
    """
    now = SBTR.objects.get(pk=id_question)
    now.is_new_message = False
    now.save()
    now.is_work = False
    now.save()

@sync_to_async
def unset_all_flag_is_work(tg_id: int):
    """
    Уберает все флаги is_work конкретного менеджера
    """
    userid = User.objects.get(tg_userid=tg_id).pk
    SBTR.objects.filter(who_answered=userid).update(is_work=False)

@sync_to_async
def end_question(id_question: int):

    SBTR.objects.filter(pk=id_question).update(status="COMPLET")
