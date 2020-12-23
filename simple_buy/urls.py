from django.urls import path, reverse
from django.views.generic import RedirectView
from . import views as simple_buy_views

app_name = 'simple_buy'
urlpatterns = [
    path('', RedirectView.as_view(url='/simple_buy/index/')),
    path('index/', simple_buy_views.index, name='index'),
    path('orders/', simple_buy_views.orders, name='orders'),  # GET, POST
    path('orders/<int:order_id>', simple_buy_views.delete_order, name='delete_order'),  # DELETE, POST
    path('products/', simple_buy_views.products, name='products'),  # GET
    path('shops/', simple_buy_views.shops, name='shops'),  # GET
]
