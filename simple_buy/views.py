from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .render_page import render_index_page
from .checks import check_get_range_parameter, check_restock
from .handlers import get_orders_handler, post_order_handler, delete_order_handler, \
    get_products_handler, get_shop_handler
import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# Create your views here.
def record_meta(func):
    def wrap(*args, **kwargs):
        request = args[0]
        logger.info(f"{request.headers}, {request.META['REMOTE_ADDR']}, {request.META['REMOTE_HOST']}")
        return func(*args, **kwargs)
    return wrap


@record_meta
@login_required
def index(request):
    return render(request, 'simple_buy/index.html', render_index_page())


@record_meta
@login_required
@require_http_methods(['GET', 'POST'])
@check_get_range_parameter
def orders(request, order, limit, order_by=None):
    handler = {
        'GET': get_orders_handler,
        'POST': post_order_handler,
    }.get(request.method, None)

    if request.method == 'GET':
        return handler(order, limit, order_by)

    return handler(request)


@record_meta
@login_required
@require_http_methods(['DELETE', 'POST'])
@check_restock
def delete_order(request, order, order_id):
    handler = {
        'POST': delete_order_handler,
        'DELETE': delete_order_handler,
    }.get(request.method, None)

    return handler(request, order)


@record_meta
@login_required
@require_http_methods(['GET'])
@check_get_range_parameter
def products(request, order, limit, order_by=None):
    handler = {
        'GET': get_products_handler,
    }.get(request.method, None)

    limit = {
        'top3': 3,
    }.get(request.GET.get('type'), limit)

    return handler(order, limit, order_by)


@record_meta
@login_required
@require_http_methods(['GET'])
@check_get_range_parameter
def shops(request, order, limit, order_by=None):
    handler = {
        'GET': get_shop_handler,
    }.get(request.method, None)

    detail_type = {
        'sales': 'sales',
    }.get(request.GET.get('type'), None)

    if not detail_type:
        return HttpResponseBadRequest('Parameter require: ?type=sales')

    return handler(detail_type, order, limit, order_by)
