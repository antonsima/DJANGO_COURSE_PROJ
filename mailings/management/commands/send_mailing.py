from django.core.management.base import BaseCommand
from mailings.services import send_mailing
from mailings.models import Mailing

class Command(BaseCommand):
    help = 'Отправляет указанную рассылку'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            send_mailing(mailing_id)
            self.stdout.write(f'Рассылка #{mailing_id} отправлена!')
        except Mailing.DoesNotExist:
            self.stderr.write(f'Рассылка #{mailing_id} не найдена!')