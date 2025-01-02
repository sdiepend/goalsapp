from django.contrib import admin

# Register your models here.

from .models import Standard, StandardCategory, StandardProgress

admin.site.register(Standard)
admin.site.register(StandardCategory)
admin.site.register(StandardProgress)