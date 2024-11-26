import logging
from datetime import date
from users.models import User
from nb1school.models import Learners, Leads
from django.contrib.auth.models import Group
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@sync_to_async
def get_groupstaff_tgid(member: int, group: str):
    """
    Ищет по тг юзер ид, вхождение в группу пользователей
    """
    group_cur = Group.objects.get(name=group)
    user_groups = User.objects.filter(
        tg_userid=member, is_active=True, groups=group_cur).exists()
    return user_groups

@sync_to_async
def entry_tg_userid(tg_id: int):
    """
    Возвращает True, если tg userid уже есть в бд 
    """
    staff = User.objects.filter(tg_userid=tg_id, is_active=True).exists()
    learner = Learners.objects.filter(tg_userid=tg_id, is_active=True).exists()
    lead = Leads.objects.filter(tg_userid=tg_id, is_archived=False).exists()
    bools = [staff, learner, lead]
    if True in bools:
        result = True
    else: result = False
    return result

@sync_to_async
def entry_tg_username(tg_username: str):   # wrong
    """
    Возвращает True, если tg username уже есть в бд 
    """
    if User.objects.filter(tg_username=tg_username):
        result = True
    else: result = False
    return result

@sync_to_async
def set_tg_username_and_id(phone: int, tg_username: str, tg_id: int):
    """
    Обновляет tg id и username в профиле пользователя или ученика в бд
    """
    try:
        User.objects.filter(numphone=phone).update(tg_username=tg_username, tg_userid=tg_id)
        Learners.objects.filter(phone=phone).update(tg_username=tg_username, tg_userid=tg_id)
    except Exception as err:
        print("set_tg_username_and_id - ", err)
        logger.exception(err)

@sync_to_async
def get_phone(phone: int):
    """
    Возвращает True, если номер телефона есть в бд 
    """
    users = User.objects.filter(numphone=phone, is_active=True).exists()
    learner = Learners.objects.filter(phone=phone, is_ban=False, is_active=True).exists()
    lead = Leads.objects.filter(phone=phone, is_ban=False, is_archived=False).exists()
    bools = [users, learner, lead]
    if True in bools:
        result = True
    else: result = False
    return result

@sync_to_async
def get_learner(tg_id: int):
    """
    Вернет True если есть такой ученик в бд и ему не заприщен доступ
    """
    if Learners.objects.filter(tg_userid=tg_id, is_active=True, is_ban=False).exists():
        result = True
    else: result = False
    return result

@sync_to_async
def check_subs(tg_id: int, subs_name: str):
    '''
    Проверка срока подписки на доп с наставником, с привязкой к курсу
    '''
    if subs_name == "key1mtrm":
        subs_name = 1 # "Ремонт ноутбуков"
    else: subs_name = 2 # "Ремонт видеокарт"
    subs = Learners.objects.filter(
        tg_userid=tg_id, course__pk=subs_name).prefetch_related(
            "end_extra").values_list("end_extra", flat=True)
    if subs and subs[0] > date.today():
        result = True   # Если есть ученик с тг_ид и срок подписки не окончен
    else: result = False
    return result

@sync_to_async
def get_ban_is_tg_userid(tg_id: int):
    """
    Возвращает True если пользователь забанен
    """
    staff = User.objects.filter(tg_userid=tg_id, is_active=False).exists()
    learner = Learners.objects.filter(tg_userid=tg_id, is_ban=True).exists()
    lead = Leads.objects.filter(tg_userid=tg_id, is_ban=True).exists()
    bools = [staff, learner, lead]
    if True in bools:
        result = True
    else: result = False
    return result

@sync_to_async
def set_ban_user(tg_id: int):
    lead = Leads.objects.get(tg_userid=tg_id)
    learner = Learners.objects.get(tg_userid=tg_id)
    if learner:
        learner.is_ban = True
        learner.save()
    else:
        lead.is_ban = True
        lead.save()
