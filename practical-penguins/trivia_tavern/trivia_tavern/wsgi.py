"""
WSGI config for trivia_tavern project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import read_dotenv
trivia_tavern_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
read_dotenv(os.path.join(trivia_tavern_root, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trivia_tavern.settings')

application = get_wsgi_application()
