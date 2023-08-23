from django.contrib import admin
from .models import Cart,Tax,Coupon

class CartAdmin(admin.ModelAdmin):
    list_display = ('user','fooditem','updated_at')

# Register your models here.
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type','tax_percentage','is_active')
    

admin.site.register(Cart,CartAdmin)
admin.site.register(Tax,TaxAdmin)
admin.site.register(Coupon)