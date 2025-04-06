from django.urls import path
from ecommerceApp import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('checkoutview/', views.checkoutview, name="checkoutview"),
    path('checkout/', views.checkout, name="checkout"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),

]