import logging

from asgiref.sync import sync_to_async
from nb1school.models import Leads

logger = logging.getLogger(__name__)

@sync_to_async
def create_lid(
    phone: int, first_name: str, last_name: str,
    tg_username: str, tg_userid: int
    ):
    try:
        Leads.objects.update_or_create(
            phone=phone,
            defaults={
                "phone": phone,
                "tg_username": tg_username,
                "tg_userid": tg_userid,
                "is_archived": False
                },
            create_defaults={
                "phone": phone, "first_name": first_name, "last_name": last_name,
                "tg_username": tg_username, "tg_userid": tg_userid,
                "is_archived": False
                }
            )
    except ExceptionGroup as err:
        print(err)
        logger.error(err)
