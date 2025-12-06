from django.urls import path
from . import views

urlpatterns = [
    path('professors/', views.getProfessors, name='getProfessors'),
    path('professors/create/', views.createProfessor, name='createProfessor'),
    path('professors/<int:pk>/', views.getProfessor, name='getProfessor'),
    path('professors/<int:pk>/delete/', views.deleteProfessor, name='deleteProfessor'),
    path('professors/<int:pk>/review/', views.createReview, name='createReview'),
]
