from django import forms
from .models import Product, Order, Customer


class OrderForm(forms.Form):
    product_choices = [('--- Select Product ---', '--- Select Product ---')]
    product_choices.extend([(item['product_id'], item['product_id']) for item in Product.objects.values().all().order_by('pk')])
    product_id = forms.CharField(widget=forms.Select(choices=product_choices))
    qty = forms.CharField(widget=forms.TextInput(), initial='數量')
    # class Meta:
    #     model = Order
    #     fields = ('product', 'qty')


class CustomerForm(forms.Form):
    customer_id = forms.CharField(initial='Customer ID')
    vip = forms.BooleanField(required=False)
