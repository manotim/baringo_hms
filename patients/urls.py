from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('register/', views.patient_register, name='patient_register'),
    path('<str:mrn>/', views.patient_detail, name='patient_detail'),
    path('<str:mrn>/edit/', views.patient_edit, name='patient_edit'),
    path('api/search/', views.patient_search_api, name='patient_search_api'),
]