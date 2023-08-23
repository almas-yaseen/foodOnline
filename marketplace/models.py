from django.db import models
from accounts.models import User,Coupon
from menu.models import FoodItem

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at  =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.user
    
class Tax(models.Model):
    tax_type = models.CharField(max_length=20,unique=True)
    tax_percentage = models.DecimalField(decimal_places=2,max_digits=4,verbose_name='tax percentage')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'tax'
    
    def __str__(self):
        return self.tax_type
    


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(decimal_places=2, max_digits=10)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    def __str__(self):
        return self.code
    

        
    
    
