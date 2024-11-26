import asyncio
from django.core.management.base import BaseCommand
from tg_bot.search_tk_bot.tg_bot1 import main_supp_tk

class Command(BaseCommand):
    help = 'RUN COMMAND: python manage.py runbot'

    def handle(self, *args, **options):
        asyncio.run(main_supp_tk())
        #self.stdout.write(self.style.SUCCESS('Successfully finished run telegram client'))
