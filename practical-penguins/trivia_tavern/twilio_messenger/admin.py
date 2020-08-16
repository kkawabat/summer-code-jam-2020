from django.contrib import admin
from .models import ScoreTracker, ScoreCardAnswer

# Register your models here.
admin.site.register(ScoreTracker)
admin.site.register(ScoreCardAnswer)
