from django.contrib import admin

from .models import *

admin.site.register(MainDairy)
admin.site.register(Dairy)
admin.site.register(User)
admin.site.register(DairyUserProfile)
admin.site.register(MilkCollection)
admin.site.register(BuySubscriptionPlan)



