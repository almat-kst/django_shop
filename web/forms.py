from django import forms
from django.contrib.contenttypes import fields
from .models import Order

class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получение заказа'

    order_date = forms.DateField(widget=forms.TextInput(attrs={'type':'date'}))
    
    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'cart', 'status', 'delivery_type', 'order_date'
        )
