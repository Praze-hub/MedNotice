from django.apps import AppConfig
from core.utils.db import wait_for_db


class CoreConfig(AppConfig):
    name = "core"
    
    def ready(self):
        wait_for_db()