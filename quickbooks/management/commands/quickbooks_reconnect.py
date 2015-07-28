from django.core.management.base import BaseCommand, CommandError
from quickbooks.payments import Payments

class Command(BaseCommand):
    help = "Reconnects to the QuickBooks API for a new Token"

    def handle(self, *args, **options):
        payments = Payments()

        payments.reconnect()
