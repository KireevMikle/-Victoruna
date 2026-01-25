from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('register/', views.register, name='register'),

    path(
        'quiz/<int:quiz_id>/question/<int:question_number>/',
        views.quiz_question,
        name='quiz_question'
    ),

    path(
        'quiz/<int:quiz_id>/result/',
        views.quiz_result,
        name='quiz_result'
    ),
]