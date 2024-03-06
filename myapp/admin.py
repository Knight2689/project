from django.contrib import admin
from .models import ProductTypeModel, ColorModel, SizeModel, Products, ImageModel, DescriptionModel


# Register your models here.
admin.site.register(ProductTypeModel)
admin.site.register(ColorModel)
admin.site.register(SizeModel)
admin.site.register(Products)
admin.site.register(ImageModel)
admin.site.register(DescriptionModel)