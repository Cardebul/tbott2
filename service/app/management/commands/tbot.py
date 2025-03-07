import asyncio
import logging

from app.abot.bot import main
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.INFO)



class Command(BaseCommand):
    help = 'TBot'

    def handle(self, *args, **options):
        asyncio.run(main())
        