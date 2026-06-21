"""
URL configuration for townprojec t project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from townapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('login',views.login),
    path('logindata',views.logindata),
    path('logout', views.logout),
    path('register',views.register),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('addproduct', views.addproduct),
    path('insertproductdata',views.insertproductdata),
    path('singleproduct/<int:id>', views.singleproduct),
    path('manageproduct',views.manageproduct),
     path('removeproduct/<int:id>', views.removeproduct),
    path('editproduct/<int:id>',views.editproduct),
   path('editsubproduct/<int:id>', views.editsubproduct),
    path('removesubproduct/<int:id>', views.removesubproduct),
    path('updateproduct',views.updateproduct),
    path('about/',views.about),
    path('shoppingcart/', views.shoppingcart, name='shoppingcart'),
    path('insertintocart/', views.insertintocart, name='insertintocart'),
    path('increase/<int:id>', views.increase, name='increase'),
    path('decrease/<int:id>', views.decrease, name='decrease'),
    path('deletecart/<int:id>', views.deletecart, name='deletecart'),

    path('orderhistory/',views.orderhistory),
    path('placeorder', views.placeorder),
    path('payment-success', views.payment_success),
    path('orderdetails/<int:id>', views.orderdetails, name='orderdetails'),
    path('manageorders/', views.manageorders, name='manageorders'),
    path('updateorderstatus', views.updateorderstatus, name='updateorderstatus'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/<int:id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('feedback/', views.feedback, name='feedback'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('submit_feedback', views.submit_feedback),
    path('viewfeedback/', views.viewfeedback, name='viewfeedback'),
    path('deletefeedback/<int:id>', views.deletefeedback, name='deletefeedback'),
    path('singlesubproduct/<int:id>', views.singlesubproduct),
    path('invoice/<int:id>', views.invoice, name='invoice'),
path('forgot-password', views.forgot_password),
    path('update-password', views.update_password),

path('myprofile/', views.myprofile, name='myprofile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path('update_seller_profile/', views.update_seller_profile, name='update_seller_profile'),




]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)