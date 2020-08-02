from django.core.management.base import BaseCommand, CommandError
from quickbooks.payments import Payments

class Command(BaseCommand):
    help = "Refreshes QuickBooks API token"

    def handle(self, *args, **options):
        payments = Payments()

        payments.refresh()
