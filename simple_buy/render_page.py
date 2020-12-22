from django.contrib import messages
from .forms import OrderForm, CustomerForm
from .models import Product, Order


def build_index_form():
    order_form = OrderForm()
    customer_form = CustomerForm()
    return {
        'order_form': order_form,
        'customer_form': customer_form,
    }


def build_product_table():
    return {
        'products': Product.objects.all().order_by('pk'),
    }


def build_order_table():
    return {
        'orders': Order.objects.all().order_by('-order_date'),
    }


def build_top3_product_table():
    return {
        'top3_products': 'top3_products',
    }


def render_index_page(request=None, message_type=None, message=None):
    sys_messages = {}
    if message:
        mt = {
            'success': messages.SUCCESS,
            'error': messages.ERROR,
            'warning': messages.WARNING,
        }.get(message_type, messages.ERROR)

        messages.add_message(request, mt, message)
        sys_messages = {
            'messages': messages.get_messages(request)
        }
    return dict(build_index_form(), **(build_product_table()), **(build_order_table()), **sys_messages)