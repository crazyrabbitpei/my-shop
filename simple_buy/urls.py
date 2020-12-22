from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as simple_buy_views

app_name = 'simple_buy'
urlpatterns = [
    path('index/', simple_buy_views.index, name='index'),
    path('orders/', simple_buy_views.orders, name='orders'),  # GET, POST
    path('orders/<int:order_id>', simple_buy_views.delete_order, name='delete_order'),  # DELETE, POST
    path('products/', simple_buy_views.products, name='products'),  # GET
    path('shops/', simple_buy_views.shops, name='shops'),  # GET
]
