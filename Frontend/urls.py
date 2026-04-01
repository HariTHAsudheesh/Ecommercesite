from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  
    path('cart/', views.cart, name='cart'),
    path('update-cart/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment_page, name='payment'),           # <--- important
    path('payment-success/', views.payment_success, name='payment_success'),

]

