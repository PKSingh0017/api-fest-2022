from django.contrib import admin
from . import models as core_models

admin.site.register(core_models.Item)
admin.site.register(core_models.Category)
admin.site.register(core_models.OrderItem)
admin.site.register(core_models.Order)
admin.site.register(core_models.SellerSale)
admin.site.register(core_models.Address)
admin.site.register(core_models.Payment)
admin.site.register(core_models.Coupon)
admin.site.register(core_models.MetaData)
admin.site.register(core_models.Table)
admin.site.register(core_models.TableOrder)
