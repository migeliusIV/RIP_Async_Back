from django.urls import path
from app import views

urlpatterns = [
    path('calculate_quantum_task/', views.perform_calculation, name='calc'),
]