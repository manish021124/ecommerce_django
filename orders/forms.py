from django import forms
from .models import Order

class PaymentMethodAddForm(forms.ModelForm):
  class Meta:
    model = Order
    fields = ['payment_method']