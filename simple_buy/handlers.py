from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db import connection, IntegrityError
from .render_page import render_index_page
from .models import Product, Order
from .checks import check_product_exist, check_vip, check_stock_pcs, check_quantity, check_if_create_customer


def get_orders_handler(order, limit, order_by):
    o = False if order == 'asc' else True
    order_list = [item for item in Order.objects.values().all()]
    order_list.sort(reverse=o, key=lambda l: l[order_by] if order_by in l else l['order_date'])

    return JsonResponse(order_list[:limit], status=200, safe=False)


@check_product_exist
@check_vip
@check_stock_pcs
@check_quantity
@check_if_create_customer
def post_order_handler(*args, product, customer, qty):
    request = args[0]
    try:
        Order.objects.create(product=product, customer=customer, qty=qty)
    except (ValidationError, IntegrityError) as e:
        render_index_page(request, 'error', e)
        return redirect(reverse('simple_buy:index'))

    product.save()
    render_index_page(request, 'success', _('Successfully post 1 order.'))
    return redirect(reverse('simple_buy:index'))


def delete_order_handler(request, order):
    try:
        order.delete()
    except AssertionError:
        render_index_page(request, 'error', _('Something wrong'))
        return redirect(reverse('simple_buy:index'))

    order.product.save()

    render_index_page(request, 'success', _('Successfully deleted 1 order.'))
    return redirect(reverse('simple_buy:index'))


def get_products_handler(order, limit, order_by):
    o = False if order == 'asc' else True
    top_list = [dict(Product.objects.values().get(pk=item['product_id']), **{'total_sold': item['total_sold']})
                for item in Order.objects.values('product_id').annotate(total_sold=Sum('qty'))]
    top_list.sort(reverse=o, key=lambda l: l[order_by] if order_by in l else l['total_sold'])

    return JsonResponse(top_list[:limit], status=200, safe=False)


def get_shop_handler(detail_type, order, limit, order_by):
    def show_sales_detail():
        with connection.cursor() as cursor:
            cursor.execute(
                'select p.shop_id, sum(qty*price) as total_amount, Sum(qty) as total_qty, Count(shop_id) as total_order '
                'from simple_buy_order o inner join simple_buy_product p on o.product_id = p.product_id '
                'group by p.shop_id;')
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

    handler = {
        'sales': show_sales_detail
    }.get(detail_type, None)
    if not handler:
        return HttpResponse(_('Something wrong'), status=500)

    result = handler()
    o = False if order == 'asc' else True
    result.sort(reverse=o, key=lambda l: l[order_by] if order_by in l else l['total_amount'])

    if limit == -1:
        return JsonResponse(result, status=200, safe=False)

    return JsonResponse(result[:limit], status=200, safe=False)
