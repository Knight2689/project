from django.db import models
import datetime


class PageView(models.Model):
    page_name = models.CharField(max_length=255)  #頁面名稱
    total_views = models.IntegerField(default=0)  # 累計瀏覽次數
    date = models.DateField(default=datetime.date.today)  # 日期
    daily_views = models.IntegerField(default=0)  # 當日瀏覽次數

class registered_user(models.Model):
    Username = models.CharField(max_length=20, null=False) #會員姓名
    Usersex = models.CharField(max_length=2, default='M', null=False) #會員性別
    Passwd = models.CharField(max_length=128, null=False) #會員密碼
    Userbirthday = models.DateField(null=False) #會員生日
    Usermail = models.EmailField(max_length=100, blank=True, default='') #會員信箱
    Usertel = models.CharField(max_length=50, blank=True, default='') #會員手機
    Useraddress = models.CharField(max_length=255,blank=True, default='') #會員地址
    Isblacklisted = models.BooleanField(default=False)  # 黑名單欄位

class Products(models.Model):
    ProductID = models.AutoField(primary_key=True, verbose_name='商品ID')
    ProductName = models.CharField(max_length=100, verbose_name='商品名稱' , default='')
    Price = models.IntegerField(default=0, verbose_name='價格') 
    Type = models.ForeignKey('ProductTypeModel', on_delete=models.CASCADE, verbose_name='商品分類',default='')
    Color = models.ForeignKey('ColorModel', on_delete=models.CASCADE, verbose_name='顏色',default='')
    Size = models.ForeignKey('SizeModel', on_delete=models.CASCADE, verbose_name='尺寸',default='')
    Stock = models.PositiveIntegerField(default=0, verbose_name='庫存')
    Image = models.ImageField(upload_to='products/', verbose_name='商品圖片',default='')  # 圖片上傳字段

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

class ProductTypeModel(models.Model):
    TypeID = models.AutoField(primary_key=True, verbose_name='分類ID')
    TypeName = models.CharField(max_length=50, verbose_name='分類名稱')

    class Meta:
        verbose_name = '商品分類'
        verbose_name_plural = '商品分類'

class ColorModel(models.Model):
    ColorID = models.AutoField(primary_key=True, verbose_name='顏色ID')
    ColorName = models.CharField(max_length=50, verbose_name='顏色名稱')

    class Meta:
        verbose_name = '顏色'
        verbose_name_plural = '顏色'

class SizeModel(models.Model):
    SizeID = models.AutoField(primary_key=True, verbose_name='尺寸ID')
    SizeName = models.CharField(max_length=50, verbose_name='尺寸名稱')

    class Meta:
        verbose_name = '尺寸'
        verbose_name_plural = '尺寸'

class ImageModel(models.Model):
    ImageID = models.AutoField(primary_key=True, verbose_name='圖片ID')
    Product = models.ForeignKey('Products', on_delete=models.CASCADE, verbose_name='商品', related_name='images',null=True)
    ImageName = models.CharField(max_length=100, verbose_name='圖片名稱')

    class Meta:
        verbose_name = '圖片'
        verbose_name_plural = '圖片'

class DescriptionModel(models.Model):
    DescriptionID = models.AutoField(primary_key=True, verbose_name='敘述ID')
    Product = models.ForeignKey('Products', on_delete=models.CASCADE, verbose_name='商品', related_name='descriptions',default='')
    Description = models.TextField(verbose_name='敘述')

    class Meta:
        verbose_name = '商品敘述'
        verbose_name_plural = '商品敘述'