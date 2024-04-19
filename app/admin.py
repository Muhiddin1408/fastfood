from django.contrib import admin

from app.models import *

# Register your models here.


admin.site.register(User)
admin.site.register(ImageMenu)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderItem)
