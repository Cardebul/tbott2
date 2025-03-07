import asyncio
from time import sleep
from django.core.management.base import BaseCommand

from aiogram import Bot
from app.const import TKEY
from app.models import Notification, User


async def main(tids, texts):
    bot = Bot(token=TKEY)
    for text in texts:
        try: await asyncio.gather(*[bot.send_message(chat_id=tid, text=text) for tid in tids])
        except: ...
    

class Command(BaseCommand):
    help = 'TBot'

    def handle(self, *args, **options):
        while True:
            sleep(30)
            if not (texts:=Notification.objects.filter(delivered=False).values_list('text', flat=True)): continue
            tids = User.objects.all().values_list('tid', flat=True)
            asyncio.run(main(tids, texts))
