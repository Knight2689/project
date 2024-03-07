"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from myapp import views



urlpatterns = [
    #管理者
    path('admin/', admin.site.urls),
    path('adduser/', views.adduser), #新增管理者
    path('adminlogin/', views.adminlogin),  #管理者登入
    path('adminlogout/', views.adminlogout),  #管理者登出
    path('backgroundhome/',views.backgroundhome),  #後台首頁
    path('product/create/', views.product_create, name='product_create'),
    path('managementlist/',views.managementlist),  #權限管理
    path('managementcreatedata/',views.managementcreatedata),  #新增權限管理
    path('managementedit/<int:id>/',views.managementedit),  #編輯權限管理
    path('managementdelete/<int:id>/',views.managementdelete),  #刪除權限管理
    path('listall/',views.listall),  #會員管理
    path('createdata/',views.createdata),  #新增會員管理
    path('edit/<int:id>/',views.edit),  #編輯會員管理
    path('delete/<int:id>/',views.delete),  #刪除會員管理
    path('orders/',views.orders),  #收件管理
    path('ordersedit/<int:id>/',views.ordersedit),  #編輯收件管理
    path('ordersdelete/<int:id>/',views.ordersdelete),  #刪除收件管理
    path('ordertable/',views.ordertable),  #商品訂單
    path('ordertableedit/<int:id>/',views.ordertableedit),  #編輯商品訂單
    path('ordertabledelete/<int:id>/',views.ordertabledelete),  #刪除商品訂單

    #使用者
    #path('',views,subject),
    path('subject/',views.subject, name='subject'),
    path('login/', views.login, name='login'),  #登入
    path('signup/',views.signup, name='signup'),  #註冊
    path('captcha/',include('captcha.urls')), #驗證碼
    path('check_email/', views.check_email),  #檢查email
    path('signupsuccessfulemail/', views.signupsuccessfulemail, name='signupsuccessfulemail'),  #註冊成功信
    path('getpassword/',views.getpassword, name='getpassword'),  #忘記密碼
    path('resetpasswordemail/', views.resetpasswordemail, name='resetpasswordemail'),  #重設密碼信
    path('resetpassword/',views.resetpassword, name='resetpassword'),  #重設Encounter U服飾會員
    path('resetpasswordsuccessfulemail/', views.resetpasswordsuccessfulemail, name='resetpasswordsuccessfulemail'),  #重設密碼成功信
    path('logout/', views.logout, name='logout'),  #登出
]

