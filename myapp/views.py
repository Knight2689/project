import datetime
import random
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader 
from email.mime.multipart import MIMEMultipart #允許在一封郵件中包含多個部分，每個部分可以是文本、圖像、附件等。這在發送 HTML 郵件時特別有用，因為可以同時包含 HTML 和純文本版本，以便接收者的郵件客戶端可以根據其支持的格式來顯示郵件內容。
from email.mime.text import MIMEText #創建 MIME 文本類型的郵件內容，例如純文本或 HTML 內容。
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from myapp import forms
from .models import *
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from .models import ProductTypeModel, ColorModel, SizeModel, ImageModel ,Products, ProductColorSizeStockModel
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

def get_product_types(request):
    # 查詢資料庫取得所有的產品分類信息
    product_types = ProductTypeModel.objects.all()
    
    # 將查詢結果序列化為字典列表
    serialized_product_types = [{'id': type.type_id, 'name': type.type_name} for type in product_types]
    
    # 傳回 JSON 格式的數據
    return JsonResponse(serialized_product_types, safe=False)

def get_product_colors(request):
    # 查詢資料庫取得所有的產品分類信息
    product_colors = ColorModel.objects.all()
    
    # 將查詢結果序列化為字典列表
    serialized_product_colors = [{'id': type.color_id, 'name': type.color_name} for type in product_colors]
    
    # 傳回 JSON 格式的數據
    return JsonResponse(serialized_product_colors, safe=False)

def get_product_sizes(request):
    # 查詢資料庫取得所有的產品分類信息
    product_sizes = SizeModel.objects.all()
    
    # 將查詢結果序列化為字典列表
    serialized_product_sizes = [{'id': type.size_id, 'name': type.size_name} for type in product_sizes]
    
    # 傳回 JSON 格式的數據
    return JsonResponse(serialized_product_sizes, safe=False)

# 建立一個信號量，用於在 Products 模型保存後更新 ProductColorSizeStockModel 記錄
@receiver(post_save, sender=Products)
def update_product_color_size_stock(sender, instance, **kwargs):
    # 檢查信號量是否為建立新記錄，而不是更新現有記錄
    if kwargs['created']:
        # 如果是建立新記錄，則建立對應的 ProductColorSizeStockModel 記錄
        product_color_size_stock = ProductColorSizeStockModel.objects.create(
            product=instance,
            color=instance.color,
            size=instance.size,
            stock=instance.stock
        )
    else:
        # 如果是更新現有記錄，則更新對應的 ProductColorSizeStockModel 記錄
        product_color_size_stock = ProductColorSizeStockModel.objects.get(product=instance)
        product_color_size_stock.stock = instance.stock
        product_color_size_stock.save()

# 新增分類的視圖
@csrf_exempt
def add_product_type(request):
    if request.method == 'POST':
        type_name = request.POST.get('type_name')
        new_type = ProductTypeModel.objects.create(type_name=type_name)
        return JsonResponse({'type_id': new_type.type_id, 'type_name': new_type.type_name})
    return JsonResponse({'error': '請求方法無效'})

# 新增顏色的視圖
@csrf_exempt
def add_product_color(request):
    if request.method == 'POST':
        color_name = request.POST.get('color_name')
        new_color = ColorModel.objects.create(color_name=color_name)
        return JsonResponse({'color_id': new_color.color_id, 'color_name': new_color.color_name})
    return JsonResponse({'error': '請求方法無效'})

# 新增尺寸的視圖
@csrf_exempt
def add_product_size(request):
    if request.method == 'POST':
        size_name = request.POST.get('size_name')
        new_size = SizeModel.objects.create(size_name=size_name)
        return JsonResponse({'size_id': new_size.size_id, 'size_name': new_size.size_name})
    return JsonResponse({'error': '請求方法無效'})




message_purchase = ''
cartlist = []  #購買商品串列
subtotal = ''  #購物金額
shipping = ''  #運費
grandtotal = ''  #購物總金額  
customname = ''  #購買者姓名
customphone = ''  #購買者手機
shipping_method = ''  #物流
customaddress = ''  #購買者地址
customemail = ''  #購買者電子郵件
paytype = ''  #付款方式

#管理者
def adduser(request):  #新增管理者
	try:
		user=User.objects.get(username="user")
	except:
		user=None
	if user!=None:
		message = user.username + " 帳號已建立!"
		return HttpResponse(message)
	else:	# 建立 test 帳號			
		user=User.objects.create_user("user","user@gmail.com.tw","123456")
		user.first_name="er" # 姓名
		user.last_name="us"  # 姓氏
		user.is_staff=True	# 工作人員狀態
		user.save()
		return redirect('/admin/')


@csrf_exempt
def adminlogin(request):  #管理者登入
    if request.method == 'POST':
        postform = forms.PostForm(request.POST)
        name = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not name or not password:
            error_message = '管理者帳號或密碼為空!'
        else:
            user = authenticate(username=name, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    postform = forms.PostForm()
                    return redirect('/backgroundhome/')
                else:
                    error_message = '管理者帳號已停用!'
            else:
                error_message = '管理者帳號或密碼或驗證碼錯誤!'
    else:
        postform = forms.PostForm()
    return render(request, "adminlogin.html", locals())
	
def adminlogout(request):  #管理者登出
	auth.logout(request)
	return redirect('/adminlogin/')	

@csrf_exempt
def backgroundhome(request):  #後台首頁
    return render(request, "backgroundhome.html", locals())

@csrf_exempt
def managementlist(request):  #權限管理
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                if keyword == "是":
                    q_objects.add(Q(is_superuser=1) | Q(is_staff=1) | Q(is_active=1), Q.OR) #1啟用
                elif keyword == "否":
                    q_objects.add(Q(is_superuser=0) | Q(is_staff=0) | Q(is_active=0), Q.OR) #0關閉
                else:
                    q_objects.add(Q(id__contains=keyword), Q.OR)
                    q_objects.add(Q(last_login__contains=keyword), Q.OR)
                    q_objects.add(Q(username__contains=keyword), Q.OR)
                    q_objects.add(Q(first_name__contains=keyword), Q.OR)
                    q_objects.add(Q(last_name__contains=keyword), Q.OR)
                    q_objects.add(Q(email__contains=keyword), Q.OR)
                    q_objects.add(Q(date_joined__contains=keyword), Q.OR)
            resultList = User.objects.filter(q_objects)
    else:   
        resultList =  User.objects.all().order_by('id') 
    if not resultList:
        errormessage="無資料"
        status = False
    else:
        errormessage=""
        status = True
    return render(request,"managementlist.html",locals())  

@csrf_exempt
def managementcreatedata(request):  #新增權限管理
    if request.method =="POST":
        username = request.POST.get("username",None)
        password = request.POST.get("password", None)
        if password is not None:
            hashed_password = make_password(password)
        email = request.POST.get("email",None)
        first_name = request.POST.get("first_name",None)
        last_name = request.POST.get("last_name",None)
        is_superuser= request.POST.get("is_superuser",None)
        is_staff = request.POST.get("is_staff",None)
        is_active= request.POST.get("is_active",None)
        add = User(username=username,password=hashed_password,email=email,first_name=first_name,last_name=last_name,is_superuser=is_superuser,is_staff=is_staff,is_active=is_active)
        add.save()
        return redirect("/managementlist/")
    else:
        return render(request,"managementcreatedata.html",locals()) 

@csrf_exempt
def managementedit(request, id=None):  #編輯權限管理
    if request.method == "POST":
        username = request.POST.get("username",None)
        password = request.POST.get("password", None)
        if password is not None:
            hashed_password = make_password(password)
        email = request.POST.get("email",None)
        first_name = request.POST.get("first_name",None)
        last_name = request.POST.get("last_name",None)
        is_superuser= int(request.POST.get("is_superuser", 0))
        is_staff = int(request.POST.get("is_staff", 0))
        is_active= int(request.POST.get("is_active", 0))
        print('is_superuser=',is_superuser,'is_staff=',is_staff,'is_active',is_active) #除錯用
        update = User.objects.get(id=id)
        update.username = username
        update.password = hashed_password
        update.email = email
        update.first_name = first_name
        update.last_name = last_name
        update.is_superuser = is_superuser
        update.is_staff = is_staff
        update.is_active = is_active
        update.save()
        return redirect('/managementlist/')
    
    else:
        update = User.objects.get(id=id)
        return render(request,"managementedit.html",locals()) 

@csrf_exempt    
def managementdelete(request, id=None):  #刪除權限管理
    if request.method == "POST":
        data = User.objects.get(id=id)
        data.delete()
        return redirect("/managementlist/")
    else:
        dict_data = User.objects.get(id=id)
        return render(request,"managementdelete.html",locals())   

@csrf_exempt
def listall(request):  #會員管理
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                if keyword == "男":
                    keyword = "M"
                elif keyword == "女":
                    keyword = "F"
                elif keyword == "是":
                    q_objects.add(Q(Isblacklisted=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(Isblacklisted=0), Q.OR)
                q_objects.add(Q(Username__contains=keyword),Q.OR)
                q_objects.add(Q(Usersex__contains=keyword),Q.OR)
                q_objects.add(Q(Userbirthday__contains=keyword),Q.OR)
                q_objects.add(Q(Usertel__contains=keyword),Q.OR)
                q_objects.add(Q(Usermail__contains=keyword),Q.OR)
                q_objects.add(Q(Passwd__contains=keyword),Q.OR)
                q_objects.add(Q(Useraddress__contains=keyword),Q.OR)
            resultList = registered_user.objects.filter(q_objects)
    else:   
        resultList =  registered_user.objects.all().order_by('id') 

    if not resultList:
        errormessage="無資料"
        status = False
    else:
        errormessage=""
        status = True
    return render(request,"listall.html",locals())

@csrf_exempt
def createdata(request):  #新增會員管理
    if request.method =="POST":
        Username = request.POST.get("user-name",None)
        Usersex = request.POST.get("user-sex",None)
        Userbirthday = request.POST.get("user-birthday",None)
        Usertel = request.POST.get("user-tel",None)
        Usermail= request.POST.get("user-mail",None)
        Passwd = request.POST.get("pass-wd",None)
        Useraddress= request.POST.get("user-address",None)
        Isblacklisted= int(request.POST.get("Isblacklisted", 0))
        add = registered_user(username=Username,user_sex=Usersex,user_birthday=Userbirthday,user_tel=Usertel,user_mail=Usermail,password=Passwd,user_address=Useraddress,is_blacklisted=Isblacklisted)
        add.save()
        return redirect("/listall/")
        # return HttpResponse("Hello World")
    else:
        return render(request,"createdata.html",locals())
    
@csrf_exempt
def edit(request, id=None):  #編輯會員管理
    if request.method == "POST":
        Username=request.POST['Username']
        Usersex=request.POST['Usersex']
        Passwd=request.POST['Passwd']
        Userbirthday=request.POST['Userbirthday']
        Usermail=request.POST['Usermail']
        Usertel=request.POST['Usertel']
        Useraddress=request.POST['Useraddress']
        Isblacklisted= int(request.POST.get("Isblacklisted", 0))

        update = registered_user.objects.get(id=id)
        update.username = Username
        update.user_sex = Usersex
        update.password = Passwd
        update.user_birthday = Userbirthday
        update.user_mail = Usermail
        update.user_tel = Usertel
        update.user_address = Useraddress
        update.is_blacklisted = Isblacklisted
        update.save()
        return redirect('/listall/')
    
    else:
        update = registered_user.objects.get(id=id)
        # print(dict_data)
        return render(request,"edit.html",locals())    
    
@csrf_exempt    
def delete(request, id=None):  #刪除會員管理
    # print(id)
    if request.method == "POST":
        data = registered_user.objects.get(id=id)
        data.delete()
        return redirect("/listall/")
    else:
        dict_data = registered_user.objects.get(id=id)
        return render(request,"delete.html",locals()) 
    
@csrf_exempt   
def orders(request):  # 收件管理
    resultList = []  # 初始化為空列表
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip()  # 去空白
        keywords = site_search.split(" ")  # 字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                print('keyword=', keyword)
                
                if keyword == "是":
                    q_objects.add(Q(customer_email__Isblacklisted=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(customer_email__Isblacklisted=0), Q.OR)
                q_objects.add(Q(id__contains=keyword),Q.OR)
                q_objects.add(Q(customer_email__Username__contains=keyword),Q.OR)
                q_objects.add(Q(customer_email__Usermail__contains=keyword),Q.OR)
                q_objects.add(Q(customer_name__contains=keyword),Q.OR)
                q_objects.add(Q(customer_phone__contains=keyword),Q.OR)
                q_objects.add(Q(shipping_method__contains=keyword),Q.OR)
                q_objects.add(Q(customer_address__contains=keyword),Q.OR)
                q_objects.add(Q(pay_type__contains=keyword),Q.OR)
                q_objects.add(Q(subtotal__contains=keyword),Q.OR)
                q_objects.add(Q(shipping__contains=keyword),Q.OR)
                q_objects.add(Q(grand_total__contains=keyword),Q.OR)
        resultList = OrdersModel.objects.filter(q_objects)
        
    else:
        resultList = OrdersModel.objects.all().order_by('id')
        # print('resultList=',resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request, "orders.html", locals())


@csrf_exempt
def ordersedit(request, id=None):  #編輯收件管理
    if request.method == "POST":
        customname = request.POST.get("customname", None)
        customphone = request.POST.get("customphone",None)
        subtotal = request.POST.get("subtotal",None)
        shipping = request.POST.get("shipping",None)
        grandtotal = request.POST.get("grandtotal",None)
        shipping_method = request.POST.get("shipping_method",None)
        customaddress = request.POST.get("customaddress",None)
        paytype = request.POST.get("paytype",None)
        update = OrdersModel.objects.get(id=id)
        update.customer_name = customname
        update.customer_phone = customphone
        update.subtotal = subtotal
        update.grand_total = grandtotal
        update.shipping_method = shipping_method
        update.customer_address = customaddress
        update.pay_type = paytype
        update.save()
        return redirect('/orders/')
    
    else:
        update = OrdersModel.objects.get(id=id)
        return render(request,"ordersedit.html",locals()) 

@csrf_exempt    
def ordersdelete(request, id=None):  #刪除收件管理
    if request.method == "POST":
        data = OrdersModel.objects.get(id=id)
        data.delete()
        return redirect("/orders/")
    else:
        dict_data = OrdersModel.objects.get(id=id)
        return render(request,"ordersdelete.html",locals())   
    
@csrf_exempt
def ordertable(request):  #商品訂單
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                q_objects.add(Q(dorder__id__contains=keyword), Q.OR)
                q_objects.add(Q(product_name__contains=keyword), Q.OR)
                q_objects.add(Q(color__contains=keyword), Q.OR)
                q_objects.add(Q(size__contains=keyword), Q.OR)
                q_objects.add(Q(unit_price__contains=keyword), Q.OR)
                q_objects.add(Q(quantity__contains=keyword), Q.OR)
                q_objects.add(Q(total__contains=keyword), Q.OR)
            resultList = DetailModel.objects.filter(q_objects)
    else:    
        resultList = DetailModel.objects.all().order_by('dorder_id')
        print('resultList=',resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request,"ordertable.html",locals())  

@csrf_exempt#商品新增
def productcreate(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name", None)
        price = request.POST.get("product_price", 0)
        type_id = request.POST.get("type_id", None)
        color_id = request.POST.get("color_id", None)
        size_id = request.POST.get("size_id", None)
        stock = request.POST.get("stock", 0)
        image = request.FILES.get("image_file", None)  # 取得上傳的圖像文件

        print("Product Name:", product_name)
        print("Price:", price)
        print("Type ID:", type_id)
        print("Color ID:", color_id)
        print("Size ID:", size_id)
        print("Stock:", stock)
        print("Image:", image)

        # 處理圖像上傳
        new_image = None
        if image:
            # 將圖像儲存到資料庫中，假設 ImageModel 模型中有一個名為 name 的欄位來保存圖像的名稱
            new_image = ImageModel.objects.create(name=product_name, image=image)
            print("Image uploaded successfully. Image ID:", new_image.id)

        # 建立產品實例，並將影像關聯到產品中
        add = Products(product_name=product_name, price=price, type_id=type_id, color_id=color_id, size_id=size_id, stock=stock)
        add.save()

        # 將圖像關聯到產品
        if new_image:
            add.image = new_image
            add.save()

        return JsonResponse({'message': '商品新增成功'})  # 返回成功信息
    else:
        product_types = ProductTypeModel.objects.all()
        colors = ColorModel.objects.all()
        sizes = SizeModel.objects.all()
        return render(request, "productcreate.html", locals())

@csrf_exempt
def get_image(request, image_id):
    try:
        image = ImageModel.objects.get(image_id=image_id)
        # 返回圖片路徑或其他相關數據，這取決於您的需求
        return JsonResponse({'image_url': image.image.url})
    except ImageModel.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)


@csrf_exempt
def ordertableedit(request, id=None):  #編輯商品訂單
    if request.method == "POST":
        dname = request.POST.get("product_name", None)
        dcolor = request.POST.get("color",None)
        dsize = request.POST.get("size",None)
        dunitprice = request.POST.get("unit_price",0)
        dquantity = request.POST.get("quantity",0)
        dtotal = request.POST.get("total",0)
        update = DetailModel.objects.get(id=id)
        update.product_name = dname
        update.color = dcolor
        update.size = dsize
        update.unit_price = dunitprice
        update.quantity = dquantity
        update.total = dtotal
        update.save()
        return redirect('/ordertable/')
    
    else:
        update = DetailModel.objects.get(id=id)
        return render(request,"ordertableedit.html",locals()) 


@csrf_exempt    
def ordertabledelete(request, id=None):  #刪除商品訂單
    if request.method == "POST":
        data = DetailModel.objects.get(id=id)
        data.delete()
        return redirect("/ordertable/")
    else:
        dict_data = DetailModel.objects.get(id=id)
        return render(request,"ordertabledelete.html",locals())   

@csrf_exempt
def inventorysheet(request):  #庫存查詢
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        color_filter = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                q_objects.add(Q(type__type_id__contains=keyword), Q.OR)
                q_objects.add(Q(type__type_name__contains=keyword), Q.OR)
                q_objects.add(Q(product_name__contains=keyword), Q.OR)
                q_objects.add(Q(price__contains=keyword), Q.OR)
                q_objects.add(Q(product_color_size_stocks__color__color_name__contains=keyword), Q.OR)
                q_objects.add(Q(product_color_size_stocks__size__size_name__contains=keyword), Q.OR)
                q_objects.add(Q(product_color_size_stocks__stock__contains=keyword), Q.OR)
            
            resultList = Products.objects.prefetch_related('product_color_size_stocks', 'product_color_size_stocks__color', 'product_color_size_stocks__size').filter(q_objects)
            product_color_size_stocks = ProductColorSizeStockModel.objects.all()
            print('resultList:', resultList)
    else:   
        resultList = Products.objects.prefetch_related('product_color_size_stocks', 'product_color_size_stocks__color', 'product_color_size_stocks__size').all().order_by('type')
        print('resultList=',resultList)
        product_color_size_stocks = ProductColorSizeStockModel.objects.all()

    if resultList:  # 如果 resultList 不為空，則設置 status 為 True
        status = True
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request,"inventorysheet.html",locals())     


#使用者
def subject(request):#首頁
    return render(request, "subject.html")

@csrf_exempt
def login(request):  #登入
    if request.method == 'POST':
        postform = forms.PostForm(request.POST)
        if postform.is_valid():
            captcha_response = postform.cleaned_data.get('captcha')
            Usermail = request.POST.get("email", '')
            Passwd = request.POST.get("pass-wd", '')
            if captcha_response:  
                request.session['verified_captcha'] = True
            else:
                request.session['verified_captcha'] = False
            if Usermail == '' or Passwd == '':
                return redirect("/login/")
            else:
                try:
                    user = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd)
                except registered_user.DoesNotExist:
                    user = None
                if user is not None:
                    postform = forms.PostForm()
                    request.session['user_id'] = user.id
                    return redirect("/subject/")
                else:
                    error_message = "信箱或密碼或驗證碼不正確"
                    postform = forms.PostForm()
        # 返回登入表單頁面
        error_message = "信箱或密碼或驗證碼不正確"
        return render(request, "login.html",locals())
    else:
        postform = forms.PostForm()
        return render(request, "login.html",locals())
    
@csrf_exempt
def ordertable(request):  #商品訂單
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                q_objects.add(Q(order__id__contains=keyword), Q.OR)
                q_objects.add(Q(product_name__contains=keyword), Q.OR)
                q_objects.add(Q(color__contains=keyword), Q.OR)
                q_objects.add(Q(size__contains=keyword), Q.OR)
                q_objects.add(Q(unit_price__contains=keyword), Q.OR)
                q_objects.add(Q(quantity__contains=keyword), Q.OR)
                q_objects.add(Q(total__contains=keyword), Q.OR)
            resultList = DetailModel.objects.filter(q_objects)
    else:    
        resultList = DetailModel.objects.all().order_by('order_id')
        print('resultList=',resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request,"ordertable.html",locals())  


@csrf_exempt
def ordertableedit(request, id=None):  #編輯商品訂單
    if request.method == "POST":
        dname = request.POST.get("dname", None)
        dcolor = request.POST.get("dcolor",None)
        dsize = request.POST.get("dsize",None)
        dunitprice = request.POST.get("dunitprice",0)
        dquantity = request.POST.get("dquantity",0)
        dtotal = request.POST.get("dtotal",0)
        update = DetailModel.objects.get(id=id)
        update.dname = dname
        update.dcolor = dcolor
        update.dsize = dsize
        update.dunitprice = dunitprice
        update.dquantity = dquantity
        update.dtotal = dtotal
        update.save()
        return redirect('/ordertable/')
    
    else:
        update = DetailModel.objects.get(id=id)
        return render(request,"ordertableedit.html",locals()) 


@csrf_exempt    
def ordertabledelete(request, id=None):  #刪除商品訂單
    if request.method == "POST":
        data = DetailModel.objects.get(id=id)
        data.delete()
        return redirect("/ordertable/")
    else:
        dict_data = DetailModel.objects.get(id=id)
        return render(request,"ordertabledelete.html",locals())  
        
@csrf_exempt
def signup(request):  #註冊
    if request.method == "POST":
        Username = request.POST.get("user-name",'')
        Usersex = request.POST.get("user-sex",'')
        Userbirthday = request.POST.get("user-birthday",'')
        Usertel = request.POST.get("user-tel",'')
        Usermail= request.POST.get("user-mail",'')
        Passwd = request.POST.get("pass-wd",'')
        Useraddress= request.POST.get("user-address",'')
        strSmtp = "smtp.gmail.com:587"  # 主機
        strAccount = "rc5601684797@gmail.com"  # 帳號
        template = loader.get_template('signupsuccessfulemail.html')
        content = ""  # 郵件內容
        msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
        msg["Subject"] = "註冊成功信"  # 郵件標題
        msg["From"] = strAccount
        mailto = [Usermail]
        body_part = MIMEText(template.render({}, request), "html")
        msg.attach(body_part)  # 附加 HTML 內容到訊息中
        server = SMTP(strSmtp)  # 建立SMTP連線
        server.ehlo()  # 跟主機溝通
        server.starttls()  # TTLS 安全認證
        if Username=="" or Usersex =="" or Userbirthday=="" or Usertel=="" or Usermail=="" or Passwd=="" or Useraddress=="":
            return redirect("/signup/")
        try:
            existing_user = registered_user.objects.filter(Usermail=Usermail).first()
            if  existing_user:
                return render(request, "signup.html", locals())
            else:
                unit =registered_user.objects.create(Username=Username,Usersex=Usersex,Userbirthday=Userbirthday, Usertel= Usertel,Usermail=Usermail,Passwd=Passwd,Useraddress=Useraddress)
                unit.save()
                server.login(strAccount, 'rrckulvlhcnxssmx')  # 登入 (信箱兩步驟驗證應用程式密碼)
                server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
                hint = "郵件已發送！"
                return render(request, "signupsuccessful.html", locals())
        except SMTPAuthenticationError:
            hint = "無法登入！"
        except SMTPException as e:
            hint = f"郵件發送產生錯誤: {str(e)}"
        finally:
            server.quit()  # 關閉連線  
    else:
        return render(request, "signup.html", locals())  
    
@csrf_exempt
def check_email(request):  #檢查email
    if request.method == "POST":
        email = request.POST.get("email", "")
        # 檢查信箱是否已經註冊
        try:
            user = registered_user.objects.get(Usermail=email)
            return JsonResponse({'email': email})
        except registered_user.DoesNotExist:
            return JsonResponse({'email': ''})       
               
    return render(request, "signup.html", locals())  

def signupsuccessfulemail(request):  #註冊成功信
    return render(request, "signupsuccessfulemail.html", locals())   

@csrf_exempt
def getpassword(request):  #忘記密碼
    if request.method == "POST":
        Usermail= request.POST.get("user-email",'')
        if Usermail=="":
            return redirect("/getpassword/")
        try:
            user = registered_user.objects.get(Usermail=Usermail)
        except registered_user.DoesNotExist:#錯誤訊息(該email不存在)
            message = "此信箱尚未註冊過!"
            return render(request, "getpassword.html", locals())
        random_password = ''.join(str(random.randint(0, 9)) for _ in range(8))
        user.Passwd = random_password # 設置為新生成的隨機密碼。
        user.save()
    
        strSmtp = "smtp.gmail.com:587"  # 主機
        strAccount = "rc5601684797@gmail.com"  # 帳號
        template = loader.get_template('resetpasswordemail.html')
        content = ""  # 郵件內容
        msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
        msg["Subject"] = "重設密碼信"  # 郵件標題
        msg["From"] = strAccount
        mailto = [Usermail]
        body_part = MIMEText(template.render({}, request), "html")
        msg.attach(body_part)  # 附加 HTML 內容到訊息中
        server = SMTP(strSmtp)  # 建立SMTP連線
        server.ehlo()  # 跟主機溝通
        server.starttls()  # TTLS 安全認證
        try:
            server.login(strAccount, 'rrckulvlhcnxssmx')  # 登入 (信箱兩步驟驗證應用程式密碼)
            server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
            hint = "郵件已發送！"
        except SMTPAuthenticationError:
            hint = "無法登入！"
        except SMTPException as e:
            hint = f"郵件發送產生錯誤: {str(e)}"
        finally:
            server.quit()  # 關閉連線
        return render(request, "resetpasswordemail.html", locals())
    return render(request, "getpassword.html", locals())   

def resetpasswordemail(request):  #重設密碼信
    return render(request, "resetpasswordemail.html", locals())  

@csrf_exempt
def resetpassword(request):  #重設Encounter M服飾會員
    if request.method == "POST":
        Usermail= request.POST.get("user-mail",None)
        Passwd = request.POST.get("verification-code", None)
        Newpasswd = request.POST.get("pass-wd",None)
        if Usermail=="" or Passwd=="" or Newpasswd=="":
            return redirect("/resetpassword/")
        else:
            try:
                user = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd)
            except registered_user.DoesNotExist:
                user = None
                message_user = "信箱或驗證碼輸入錯誤!"
            if user is not None:
                update = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd) 
                update.Passwd = Newpasswd 
                update.save() 
                strSmtp = "smtp.gmail.com:587"  # 主機
                strAccount = "rc5601684797@gmail.com"  # 帳號
                template = loader.get_template('resetpasswordsuccessfulemail.html')
                content = ""  # 郵件內容
                msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
                msg["Subject"] = "重設密碼成功信"  # 郵件標題
                msg["From"] = strAccount
                mailto = [Usermail]
                body_part = MIMEText(template.render({}, request), "html")
                msg.attach(body_part)  # 附加 HTML 內容到訊息中
                server = SMTP(strSmtp)  # 建立SMTP連線
                server.ehlo()  # 跟主機溝通
                server.starttls()  # TTLS 安全認證
                try:
                    server.login(strAccount, 'rrckulvlhcnxssmx')  # 登入 (信箱兩步驟驗證應用程式密碼)
                    server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
                    hint = "郵件已發送！"
                except SMTPAuthenticationError:
                    hint = "無法登入！"
                except SMTPException as e:
                    hint = f"郵件發送產生錯誤: {str(e)}"
                finally:
                    server.quit()  # 關閉連線
                return redirect(reverse('resetpasswordsuccessfulemail'))
            else:
                return render(request, "resetpassword.html", locals())
    else:
        return render(request, "resetpassword.html", locals())
    
def resetpasswordsuccessfulemail(request):  #重設密碼成功信
    return render(request, "resetpasswordsuccessfulemail.html", locals())    

def logout(request):  #登出
    global cartlist
    if 'cartlist' in request.session: 
        cartlist = request.session['cartlist']
        cartlist = [] #賦予空值，清空購物車內容
    user_id = request.session.get('user_id')
    request.session.pop('cartlist', None) #清空購物車
    # images = ImageModel.objects.all()
    # productall = Products.objects.all()
    # descriptions = DescriptionModel.objects.all()
    # first_images = {}
    # for i in productall:
    #     product_images = images.filter(Product_id=i.ProductID)
    #     if product_images:
    #         first_images[i.ProductID] = product_images[0]
    page_name = 'subject'  # 此處使用您的頁面名稱

    # 查找或創建 PageView 對象
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    # 增加瀏覽次數
    page.total_views += 1
    page.daily_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow = datetime.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)

    if 'user_id' in request.session:
        del request.session['user_id']
    if 'verified_captcha' in request.session:
        del request.session['verified_captcha']
    # return render(request, "subject.html",locals())
    return redirect('subject')

def classification(request, type=None):  #分類頁面
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    products = Products.objects.all()  #取得資料庫所有商品
    images = ImageModel.objects.all()
    descriptions = DescriptionModel.objects.all()
    first_images = {}
    for i in products:
        product_images = images.filter(Product_id=i.ProductID)
        if product_images:
            first_images[i.ProductID] = product_images[0]
    page_name = 'subject'  # 此處使用您的頁面名稱

    # 查找或創建 PageView
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    page.total_views = PageView.objects.aggregate(Sum('daily_views'))['daily_views__sum'] or 0
    # 增加瀏覽次數
    page.daily_views += 1
    page.total_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = timezone.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = timezone.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)
    if type == 'brand':
        type = 'EncounterU品牌款'
        products = products.filter(Type_id__TypeName='EncounterU品牌款')
    elif type == 'hot':
        type = '熱賣商品'
        products = products.filter(Type_id__TypeName='熱賣商品')
    elif type == 'caot':
        type = '外套'
        products = products.filter(Type_id__TypeName='外套')
    elif type == 'short':
        type = '短袖'
        products = products.filter(Type_id__TypeName='短袖') 
    elif type == 'sleeves':
        type = '長袖 / 7分袖'
        products = products.filter(Type_id__TypeName='長袖 / 7分袖') 
    elif type == 'vest':
        type = '背心'
        products = products.filter(Type_id__TypeName='背心') 
    elif type == 'shirt':
        type = '襯衫'
        products = products.filter(Type_id__TypeName='襯衫') 
    elif type == 'shorts':
        type = '短褲'
        products = products.filter(Type_id__TypeName='短褲') 
    elif type == 'pants':
        type = '長褲'
        products = products.filter(Type_id__TypeName='長褲') 
    elif type == 'jeans':
        type = '牛仔褲'
        products = products.filter(Type_id__TypeName='牛仔褲') 
    elif type == 'culottes':
        type = '短/長/褲裙'
        products = products.filter(Type_id__TypeName='短/長/褲裙') 
    elif type == 'overalls':
        type = '短/長吊帶褲'
        products = products.filter(Type_id__TypeName='短/長吊帶褲')
    elif type == 'sleevelessdress':
        type = '無袖洋裝'
        products = products.filter(Type_id__TypeName='無袖洋裝') 
    elif type == 'shortsleevedress':
        type = '短袖洋裝'
        products = products.filter(Type_id__TypeName='短袖洋裝') 
    elif type == 'longsleevedress':
        type = '長袖洋裝'
        products = products.filter(Type_id__TypeName='長袖洋裝') 
    elif type == 'jumpsuit':
        type = '連身套裝'
        products = products.filter(Type_id__TypeName='連身套裝') 
    elif type == 'suit':
        type = '無袖套裝'
        products = products.filter(Type_id__TypeName='無袖套裝') 
    elif type == 'shortsleevedresssuit':
        type = '短袖套裝'
        products = products.filter(Type_id__TypeName='短袖套裝') 
    elif type == 'longsleevedresssuit':
        type = '長袖套裝'
        products = products.filter(Type_id__TypeName='長袖套裝') 
    elif type == 'bag':
        type = '包包'
        products = products.filter(Type_id__TypeName='包包') 
    elif type == 'discount':
        type = '特價商品'
        products = products.filter(Type_id__TypeName='特價商品') 
   
    return render(request, "classification.html", locals())

@csrf_exempt     
def productcontent(request,productid=None):  #商品資訊
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    productall = Products.objects.all()
    product = Products.objects.get(ProductID=productid)  #取得商品
    images = ImageModel.objects.filter(Product_id=product)
    description = DescriptionModel.objects.get(Product_id=product)
    color_set = set()  # 創建一個空集合來儲存唯一的顏色
    unique_colors = []  # 創建一個空列表來儲存唯一的顏色
    size_set = set()  # 創建一個空集合來儲存唯一的尺寸
    unique_sizes = []  # 創建一個空列表來儲存唯一的尺寸
    stocks = ProductColorSizeStockModel.objects.filter(Product_id=product)
    for stock in stocks:
        color_name = stock.Color_id.ColorName
        size_name = stock.Size_id.SizeName
        if color_name not in color_set:
        # 如果顏色名稱不在集合中，將其添加到集合和唯一顏色列表
            color_set.add(color_name)
            unique_colors.append(color_name)
        if size_name not in size_set:
        # 如果尺寸名稱不在集合中，將其添加到集合和唯一尺寸列表
            size_set.add(size_name)
            unique_sizes.append(size_name)
    page_name = 'subject'  # 頁面名稱

    # 查找或創建 PageView
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    page.total_views = PageView.objects.aggregate(Sum('daily_views'))['daily_views__sum'] or 0

    # 增加瀏覽次數
    page.daily_views += 1
    page.total_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = timezone.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = timezone.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)

    return render(request, "productcontent.html", locals())