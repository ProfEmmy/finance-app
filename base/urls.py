from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.logoutUser, name='logout'),
    path('login/', views.loginUser, name='login'),
    path('register/', views.register, name='register'),

    path('', views.home, name='home'),

    path('transfer/<str:pk>/', views.transferPage, name='transfer'),
    path('confirm-transfer/<str:pk>/', views.confirmTransferPage, name='confirm-transfer'),
    path('go-back/<str:pk>/', views.go_back, name='go_back'),

    path('add', views.addPage, name='add-money'),

    path('transaction-history', views.historyPage, name='transaction-history'),

    path('change-password', views.changePassword, name='change-password'),
    path('edit-account', views.editAccount, name='edit-account'),
]