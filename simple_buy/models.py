from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models


def validate_customer_id(value: str):
    if not value.isdigit():
        raise ValidationError(_('user id illegal'), params={'value': value}, code='invalid')


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    stock_pcs = models.PositiveIntegerField(_('Stock'), default=0, null=False, blank=False)
    price = models.PositiveIntegerField(_('Price'), null=False, blank=False)
    shop_id = models.CharField(_('Shop category id'), null=False, blank=False, max_length=15)
    vip_only = models.BooleanField(_('Vip only'), default=False)
    restock = models.BooleanField(_('Restock'), default=False)

    class Meta:
        pass

    def __str__(self):
        return (f'product_id: {self.product_id}, stock_pcs: {self.stock_pcs}, '
                f'price: {self.price}, shop_id: {self.shop_id}, vip_only: {self.vip_only}')


class Customer(models.Model):
    customer_id = models.CharField(_('customer id'), primary_key=True, validators=[validate_customer_id], max_length=20, null=False, blank=False)
    is_vip = models.BooleanField(_('Is VIP'), default=False)
    orders = models.ManyToManyField('Product', through='Order', through_fields=('customer', 'product'),)

    class Meta:
        pass

    def __str__(self):
        return f'customer_id: {self.customer_id}, is_vip: {self.is_vip}'


class Order(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(_('Quantity'), null=False, blank=False, validators=[MinValueValidator(1)])
    order_date = models.DateTimeField(_('Order date'), auto_now_add=True)

    class Meta:
        pass

    def product_detail(self):
        return f'{self.product_id}, vip only: {self.product.vip_only}, shop id: {self.product.shop_id}'
    product_detail.short_description = _('Product detail')

    def customer_detail(self):
        return f'{self.customer_id}, is vip: {self.customer.is_vip}'
    customer_detail.short_description = _('Customer detail')

    def __str__(self):
        return (f'product: {self.product_id}, customer: {self.customer_id}, '
                f'qty: {self.qty}, vip product: {self.product.vip_only}')

    def clean(self, exclude=None, validate_unique=True):
        if self.product.vip_only and not self.customer.is_vip:
            raise ValidationError(_('VIP only'))
        if self.product.stock_pcs == 0:
            raise ValidationError(_('Out of stock'))
        if self.product.stock_pcs < self.qty:
            msg1 = _('Not sufficient')
            msg2 = _('In stock')
            raise ValidationError(f'{msg1}. {msg2}, {self.product.stock_pcs} units')

    def save(self, *args, **kwargs):
        self.clean()
        self.product.stock_pcs -= self.qty
        self.product.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.product.stock_pcs += self.qty
        self.product.save()
        super().delete(*args, **kwargs)
