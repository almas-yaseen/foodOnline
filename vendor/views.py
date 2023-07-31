from django.shortcuts import render
from .forms import VendorForm
from django.shortcuts import get_object_or_404,render,redirect
from accounts.forms import UserProfileForm
from accounts.models import Userprofile
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Vendor
from menu.models import Category,FoodItem
from accounts.views import check_role_vendor
# Create your views here.


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(Userprofile,user=request.user)
    vendor = get_object_or_404(Vendor,user=request.user)
    
    if request.method=="POST":
        profile_form = UserProfileForm(request.POST,request.FILES,instance=profile)
        vendor_form  = VendorForm(request.POST,request.FILES,instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request,'Settings updated')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
            
        
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
    context = { 
               'profile_form':profile_form,
               'vendor_form':vendor_form,
               'profile':profile,
               'vendor':vendor,
               }
    
    return render(request,'vendor/vprofile.html',context)

def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    context = { 
               'categories':categories,
               }
    return render(request,'vendor/menu_builder.html',context)
def fooditems_by_category(request,pk=None):
     vendor = Vendor.objects.get(user=request.user)
     category = get_object_or_404(Category,pk=pk)
     fooditems = FoodItem.objects.filter(vendor=vendor,category=category)
     context = { 
                'fooditems':fooditems,
                'category':category,
                
                
                }
     print(fooditems)
     return render(request,'vendor/fooditems_by_category.html',context)