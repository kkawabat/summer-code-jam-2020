"""
ASGI config for trivia_tavern project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application
from dotenv import read_dotenv
trivia_tavern_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
read_dotenv(os.path.join(trivia_tavern_root, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trivia_tavern.settings')
django.setup()
application = get_asgi_application()
