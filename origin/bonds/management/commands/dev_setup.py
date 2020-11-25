from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bonds.models import Currency

User = get_user_model()


class Command(BaseCommand):
    help = "Load plans"

    def handle(self, *args, **kwargs):
        Currency.objects.populate()
        User.objects.create_user('admin', password='test')
