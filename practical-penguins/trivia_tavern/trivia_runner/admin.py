from django.contrib import admin
from .models import Player, TriviaSession, Answer
# Register your models here.
admin.site.register(Player)
admin.site.register(TriviaSession)
admin.site.register(Answer)
