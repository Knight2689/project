from django import forms
from captcha.fields import CaptchaField
from .models import ProductTypeModel, ColorModel, SizeModel

class PostForm(forms.Form):
    captcha = CaptchaField()


# class ProductTypeForm(forms.ModelForm):
#     class Meta:
#         model = ProductTypeModel
#         fields = ['type_name']

# class ColorForm(forms.ModelForm):
#     class Meta:
#         model = ColorModel
#         fields = ['color_name']

# class SizeForm(forms.ModelForm):
#     class Meta:
#         model = SizeModel
#         fields = ['size_name']
