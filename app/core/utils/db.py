import time
from django.db import connections
from django.db.utils import OperationalError

def wait_for_db(retries=5, delay=2):
    for attempt in range(retries):
        try:
            connections['default'].cursor()
            return True
        except OperationalError:
            print(f"Db not ready, retrying {attempt+1}/{retries}")
            time.sleep(delay)
    raise Exception("Database unavailable")