from django.urls import path
from . import views

urlpatterns = [
    path('', views.consultation_list, name='consultation_list'),
    path('<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('new/<str:mrn>/', views.new_consultation, name='new_consultation'),
    path('<int:consultation_id>/lab/', views.order_lab_test, name='order_lab_test'),
]