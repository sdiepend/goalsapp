from django.contrib import admin

# Register your models here.

from .models import Goal, DailyProgress, ProcessProgress, Reflection

admin.site.register(Goal)
admin.site.register(DailyProgress)
admin.site.register(ProcessProgress)
admin.site.register(Reflection)