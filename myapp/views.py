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
from .models import ProductTypeModel, ColorModel, SizeModel
from django.db.models import Q




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
def product_create(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name", None)
        price = request.POST.get("price", 0)
        type_id = request.POST.get("type_id", None)
        color_id = request.POST.get("color_id", None)
        size_id = request.POST.get("size_id", None)
        stock = request.POST.get("stock", 0)
        # Assuming you have a file input in your form for uploading images
        image = request.FILES.get("image", None)
        
        new_product = Products.objects.create(
            ProductName=product_name,
            Price=price,
            Type_id=type_id,
            Color_id=color_id,
            Size_id=size_id,
            Stock=stock,
            Image=image
        )
        
        # 可以在這裡根據需要執行其他邏輯，例如發送通知或執行其他處理。

        return redirect('/backgroundhome/')  # Redirect to the appropriate URL for viewing products
    
    else:
        product_types = ProductTypeModel.objects.all()
        colors = ColorModel.objects.all()
        sizes = SizeModel.objects.all()
        return render(request, "product_create.html", {'product_types': product_types, 'colors': colors, 'sizes': sizes})



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
        add = registered_user(Username=Username,Usersex=Usersex,Userbirthday=Userbirthday,Usertel=Usertel,Usermail=Usermail,Passwd=Passwd,Useraddress=Useraddress,Isblacklisted=Isblacklisted)
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
        update.Username = Username
        update.Usersex = Usersex
        update.Passwd = Passwd
        update.Userbirthday = Userbirthday
        update.Usermail = Usermail
        update.Usertel = Usertel
        update.Useraddress = Useraddress
        update.Isblacklisted = Isblacklisted
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
                    q_objects.add(Q(customemail__Isblacklisted=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(customemail__Isblacklisted=0), Q.OR)
                q_objects.add(Q(id__contains=keyword),Q.OR)
                q_objects.add(Q(customemail__Username__contains=keyword),Q.OR)
                q_objects.add(Q(customemail__Usermail__contains=keyword),Q.OR)
                q_objects.add(Q(customname__contains=keyword),Q.OR)
                q_objects.add(Q(customphone__contains=keyword),Q.OR)
                q_objects.add(Q(shipping_method__contains=keyword),Q.OR)
                q_objects.add(Q(customaddress__contains=keyword),Q.OR)
                q_objects.add(Q(paytype__contains=keyword),Q.OR)
                q_objects.add(Q(subtotal__contains=keyword),Q.OR)
                q_objects.add(Q(shipping__contains=keyword),Q.OR)
                q_objects.add(Q(grandtotal__contains=keyword),Q.OR)
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
        update.customname = customname
        update.customphone = customphone
        update.subtotal = subtotal
        update.grandtotal = grandtotal
        update.shipping_method = shipping_method
        update.customaddress = customaddress
        update.paytype = paytype
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