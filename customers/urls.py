from django.urls import path,include 
from accounts import views as AccountViews
from . import views
urlpatterns = [ 
               path('',AccountViews.custdashboard,name='customer'),
               path('profile/',views.cprofile,name='cprofile'),
               ]