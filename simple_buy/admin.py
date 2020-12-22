from django.contrib import admin
from .models import Order, Customer, Product
# Register your models here.


class OrderInline(admin.TabularInline):
    model = Order
    extra = 1


class CustomerInline(admin.StackedInline):
    model = Customer
    extra = 1


class ProductInline(admin.StackedInline):
    model = Product
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'qty', 'order_date', 'product_detail', 'customer_detail')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'is_vip')
    inlines = (OrderInline, )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'stock_pcs', 'price', 'shop_id', 'vip_only', 'restock')
    inlines = (OrderInline, )
