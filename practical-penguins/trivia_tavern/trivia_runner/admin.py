from django.contrib import admin
from .models import Player, TriviaSession, ScoreCardAnswer, ScoreCard

# Register your models here.
admin.site.register(Player)
admin.site.register(TriviaSession)
admin.site.register(ScoreCard)
admin.site.register(ScoreCardAnswer)