from django.apps import AppConfig
import logging
import sys
import os

logger = logging.getLogger(__name__)


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    def ready(self):
        if 'runserver' in sys.argv and os.environ.get("RUN_MAIN", "false") != "true":
            from .trip import startup_function
            startup_function()