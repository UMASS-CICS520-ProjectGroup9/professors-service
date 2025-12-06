from django.urls import path
from . import views

urlpatterns = [
    path('professors/', views.getProfessors, name='getProfessors'),
    path('professors/<int:pk>/', views.getProfessor, name='getProfessor'),
    path('professors/<int:pk>/review/', views.createReview, name='createReview'),
]
