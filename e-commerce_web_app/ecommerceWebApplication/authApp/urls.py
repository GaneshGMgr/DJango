from django.urls import path
from authApp import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name="activate"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('request-reset-email/', views.RequestResetEmailView.as_view(), name='request-reset-email'),
    path('set-new-password/<uidb64>/<token>/', views.SetNewPasswordView.as_view(), name='set-new-password'),

]