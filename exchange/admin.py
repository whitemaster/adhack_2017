from django.contrib import admin
from exchange.models import ExtUser, Task, Type


admin.site.register(ExtUser)
admin.site.register(Task)
admin.site.register(Type)