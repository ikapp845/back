from django.contrib import admin

# Register your models here.

from .models import Like,AskedLike

admin.site.register([Like,AskedLike])