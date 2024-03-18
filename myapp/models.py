from django.db import models
import datetime

# 網頁瀏覽量模型
class PageView(models.Model):
    # 頁面名稱
    page_name = models.CharField(max_length=255)
    # 累計瀏覽次數
    total_views = models.IntegerField(default=0)
    # 日期
    date = models.DateField(default=datetime.date.today)
    # 當日瀏覽次數
    daily_views = models.IntegerField(default=0)

# 註冊用戶模型
class registered_user(models.Model):
    # 會員姓名
    username = models.CharField(max_length=20, null=False)
    # 會員性別
    user_sex = models.CharField(max_length=2, default='M', null=False)
    # 會員密碼
    password = models.CharField(max_length=128, null=False)
    # 會員生日
    user_birthday = models.DateField(null=False)
    # 會員信箱
    user_mail = models.EmailField(max_length=100, blank=True, default='')
    # 會員手機
    user_tel = models.CharField(max_length=50, blank=True, default='')
    # 會員地址
    user_address = models.CharField(max_length=255, blank=True, default='')
    # 黑名單欄位
    is_blacklisted = models.BooleanField(default=False)
    # 活動狀態
    is_active = models.BooleanField(default=True)

# 訂單模型
class OrdersModel(models.Model):
    # 購物金額
    subtotal = models.IntegerField(default=0)
    # 運費
    shipping = models.IntegerField(default=0)
    # 購物總金額
    grand_total = models.IntegerField(default=0)
    # 購買者姓名
    customer_name = models.CharField(max_length=100, default='')
    # 購買者信箱
    customer_email = models.ForeignKey('registered_user', on_delete=models.CASCADE, related_name='orders')
    # 購買者地址
    customer_address = models.CharField(max_length=100, default='')
    # 購買者手機
    customer_phone = models.CharField(max_length=100, default='')
    # 寄送方式
    shipping_method = models.CharField(max_length=50, default='')
    # 付款方式
    pay_type = models.CharField(max_length=50, default='')

# 訂單詳情模型
class DetailModel(models.Model):
    # 訂單
    order = models.ForeignKey('OrdersModel', on_delete=models.CASCADE)
    # 商品名稱
    product_name = models.ForeignKey('Products', on_delete=models.CASCADE)
    # 顏色
    color = models.ForeignKey('ColorModel', on_delete=models.CASCADE)
    # 尺寸
    size = models.ForeignKey('SizeModel', on_delete=models.CASCADE)
    # 商品單價
    unit_price = models.IntegerField(default=0)
    # 商品數量
    quantity = models.IntegerField(default=0)
    # 商品總價
    total = models.IntegerField(default=0)

# 商品模型
class Products(models.Model):
    # 商品ID
    product_id = models.AutoField(primary_key=True, verbose_name='商品ID')
    # 商品名稱
    product_name = models.CharField(max_length=100, verbose_name='商品名稱', default='')
    # 價格
    price = models.IntegerField(default=0, verbose_name='價格')
    # 商品分類
    type = models.ForeignKey('ProductTypeModel', on_delete=models.CASCADE, verbose_name='商品分類', null=True, blank=True)
    # 顏色
    color = models.ForeignKey('ColorModel', on_delete=models.CASCADE, verbose_name='顏色', null=True, blank=True)
    # 尺寸
    size = models.ForeignKey('SizeModel', on_delete=models.CASCADE, verbose_name='尺寸', null=True, blank=True)
    # 庫存
    stock = models.PositiveIntegerField(default=0, verbose_name='庫存')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

# 商品分類模型
class ProductTypeModel(models.Model):
    # 分類ID
    type_id = models.AutoField(primary_key=True, verbose_name='分類ID')
    # 分類名稱
    type_name = models.CharField(max_length=50, verbose_name='分類名稱')

    class Meta:
        verbose_name = '商品分類'
        verbose_name_plural = '商品分類'

# 顏色模型
class ColorModel(models.Model):
    # 顏色ID
    color_id = models.AutoField(primary_key=True, verbose_name='顏色ID')
    # 顏色名稱
    color_name = models.CharField(max_length=50, verbose_name='顏色名稱')

    class Meta:
        verbose_name = '顏色'
        verbose_name_plural = '顏色'

# 尺寸模型
class SizeModel(models.Model):
    # 尺寸ID
    size_id = models.AutoField(primary_key=True, verbose_name='尺寸ID')
    # 尺寸名稱
    size_name = models.CharField(max_length=50, verbose_name='尺寸名稱')

    class Meta:
        verbose_name = '尺寸'
        verbose_name_plural = '尺寸'

# 圖片模型
class ImageModel(models.Model):
    # 圖片ID
    id = models.AutoField(primary_key=True, verbose_name='圖片ID')
    # 商品
    product = models.ForeignKey('Products', on_delete=models.CASCADE, verbose_name='商品', related_name='images')
    # 圖片
    image = models.ImageField(upload_to='images/', verbose_name='圖片')
    # 圖片名稱
    name = models.CharField(max_length=100, verbose_name='圖片名稱', null=True, blank=True)

    class Meta:
        verbose_name = '圖片'
        verbose_name_plural = '圖片'

# 商品敘述模型
class DescriptionModel(models.Model):
    # 敘述ID
    description_id = models.AutoField(primary_key=True, verbose_name='敘述ID')
    # 商品
    product = models.ForeignKey('Products', on_delete=models.CASCADE, verbose_name='商品', related_name='descriptions', default='')
    # 敘述
    description = models.TextField(verbose_name='敘述')

    class Meta:
        verbose_name = '商品敘述'
        verbose_name_plural = '商品敘述'

   
# 商品顏色尺寸庫存模型
class ProductColorSizeStockModel(models.Model):
    # ID
    inventory_id = models.AutoField(primary_key=True, verbose_name='ID')
    # 商品ID
    product = models.ForeignKey('Products', on_delete=models.CASCADE, verbose_name='商品ID', related_name='product_color_size_stocks')
    # 顏色ID
    color = models.ForeignKey('ColorModel', on_delete=models.CASCADE, verbose_name='顏色ID', related_name='product_color_size_stocks')
    # 尺寸ID
    size = models.ForeignKey('SizeModel', on_delete=models.CASCADE, verbose_name='尺寸ID', related_name='product_color_size_stocks')
    # 庫存
    stock = models.PositiveIntegerField(default=0, verbose_name='庫存')