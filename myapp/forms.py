from django import forms
from captcha.fields import CaptchaField
from .models import Products

class PostForm(forms.Form):
    captcha = CaptchaField()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['ProductName', 'Price', 'Type', 'Color', 'Size', 'Stock', 'Image']

