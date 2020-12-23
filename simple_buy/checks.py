from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .render_page import render_index_page
from .models import Product, Customer, Order


# def check_identity(func):
#     def wrap(*args, **kwargs):
#         request = args[0]
#         if 'Authorization' not in request.headers and 'HTTP_AUTHORIZATION' not in request.META:
#             response = HttpResponse(status=401)
#             response['WWW-Authenticate'] = 'Token <invite_code>'
#             return response
#
#         authorization = request.headers.get('Authorization', None) or request.META.get('HTTP_AUTHORIZATION', None)
#         auth_type, token = authorization.split(' ') if len(authorization.split(' ')) >= 2 else ('', '')
#         if not auth_type or not token or auth_type.lower() != 'token' or token != os.getenv('INVITE_CODE'):
#             response = HttpResponse(status=403)
#             return response
#
#         return func(*args, **kwargs)
#     return wrap


def check_product_exist(func):
    def wrap(*args, **kwargs):
        request = args[0]
        product_id = request.POST.get('product_id')
        if not product_id.isnumeric():
            render_index_page(request, 'error', _('Invalid product id.'))
            return redirect(reverse('simple_buy:index'))

        try:
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            render_index_page(request, 'error', _('Product dose not exist.'))
            return redirect(reverse('simple_buy:index'))

        return func(*args, **kwargs, product=product)
    return wrap


def check_vip(func):
    """
    即使customer已存在db且為vip，但只要創建訂單時vip參數設為False則無法下該商品
    """
    def wrap(*args, **kwargs):
        request = args[0]
        product = kwargs['product']
        is_vip = True if request.POST.get('vip', None) else False
        if product.vip_only and not is_vip:
            render_index_page(request, 'error', _('VIP only.'))
            return redirect(reverse('simple_buy:index'))

        return func(*args, **kwargs)
    return wrap


def check_stock_pcs(func):
    """
    即使customer已存在db且為vip，但只要創建訂單時vip參數設為False則無法下該商品
    """
    def wrap(*args, **kwargs):
        request = args[0]
        qty = request.POST.get('qty', 0)
        if not qty.isnumeric():
            render_index_page(request, 'error', _('Invalid quantity.'))
            return redirect(reverse('simple_buy:index'))

        qty = int(qty)
        product = kwargs['product']
        if product.stock_pcs == 0:
            product.restock = False
            product.save()
            render_index_page(request, 'error', _('Out of stock.'))
            return redirect(reverse('simple_buy:index'))

        if product.stock_pcs - qty == 0:
            product.restock = False

        return func(*args, **kwargs, qty=qty)
    return wrap


def check_quantity(func):
    def wrap(*args, **kwargs):
        request = args[0]
        qty = kwargs['qty']
        if qty <= 0:
            render_index_page(request, 'error', _('Quantity must be greater than 0.'))
            return redirect(reverse('simple_buy:index'))
        return func(*args, **kwargs)
    return wrap


def check_restock(func):
    def wrap(*args, **kwargs):
        request = args[0]
        order_id = kwargs['order_id']
        try:
            order = Order.objects.get(pk=order_id)
        except ObjectDoesNotExist:
            render_index_page(request, 'error', _('Order dose not exist'))
            return redirect(reverse('simple_buy:index'))

        if order.product.stock_pcs == 0:
            order.product.restock = True
            msg1 = order.product.product_id
            msg2 = _('restock.')
            render_index_page(request, 'success', f'Product {msg1} {msg2}')

        return func(*args, **kwargs, order=order)

    return wrap


def check_if_create_customer(func):
    """
    customer不存在則依據當下訂單的資料來創建新customer，否則使用已創建好的customer
    已存在的customer的vip資訊不會影響到check_vip decorator
    """
    def wrap(*args, **kwargs):
        request = args[0]
        customer_id = request.POST.get('customer_id')
        if not customer_id or not customer_id.isnumeric():
            render_index_page(request, 'warning', _('Invalid customer id.'))
            return redirect(reverse('simple_buy:index'))

        is_vip = True if request.POST.get('vip', None) else False
        try:
            customer = Customer.objects.create(pk=customer_id, is_vip=is_vip)
        except IntegrityError:
            Customer.objects.filter(pk=customer_id).update(is_vip=is_vip)
            customer = Customer.objects.get(pk=customer_id)

        return func(*args, **kwargs, customer=customer)
    return wrap


def check_get_range_parameter(func):
    def wrap(*args, **kwargs):
        request = args[0]
        order_by = request.GET.get('order_by', 'pk')
        order = request.GET.get('order', 'desc')
        limit = int(request.GET.get('limit', 10))
        if order not in ('desc', 'asc'):
            render_index_page(request, 'warning', 'Parameter require: ?order=desc or asc')
            return redirect(reverse('simple_buy:index'))

        if limit <= 0:
            render_index_page(request, 'warning', 'Parameter requireL ?limit=a number greater then 0')
            return redirect(reverse('simple_buy:index'))

        return func(*args, **kwargs, order=order, limit=limit, order_by=order_by)
    return wrap
