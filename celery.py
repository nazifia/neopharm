import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neopharm.settings')

app = Celery('neopharm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def sync_offline_transactions(self):
    from pharmacy.models import OfflineTransaction
    
    transactions = OfflineTransaction.objects.filter(synced=False)
    for transaction in transactions:
        try:
            # Process the transaction
            transaction.process()
            transaction.synced = True
            transaction.save()
        except Exception as e:
            self.retry(exc=e, countdown=60)  # Retry after 1 minute