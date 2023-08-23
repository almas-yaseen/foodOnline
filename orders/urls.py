from django.urls import path 
from . import views
urlpatterns = [ 
               path('place_order/',views.place_order,name='place_order'),
               path('payments/',views.payments,name='payments'),
               path('order_complete/',views.order_complete,name='order_complete'),
                path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
                path('users',views.users,name='users'),
               path('block', views.block_user, name='block_user'),
    path('unblock', views.unblock_user, name='unblock_user'),
    path('myorder_status',views.myorder_status,name='myorder_status'),
    path('customer/cancel_order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('download_order_pdf/<str:order_number>/', views.download_order_pdf, name='download_order_pdf'),
    

]

   
               
       