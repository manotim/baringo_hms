from django.urls import path
from . import views

urlpatterns = [
    path('', views.prescription_list, name='prescription_list'),
    path('<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('new/<int:consultation_id>/', views.new_prescription, name='new_prescription'),
    path('<int:prescription_id>/add-item/', views.add_prescription_item, name='add_prescription_item'),
    path('item/<int:item_id>/dispense/', views.dispense_medication, name='dispense_medication'),
    path('api/search-medications/', views.search_medications_api, name='search_medications_api'),
]