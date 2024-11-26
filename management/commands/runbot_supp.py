import asyncio
from django.core.management.base import BaseCommand
from tg_bot.support_bot.support_main import main_supp

class Command(BaseCommand):
    help = 'RUN COMMAND: python manage.py runbot'

    def handle(self, *args, **options):
        asyncio.run(main_supp())
