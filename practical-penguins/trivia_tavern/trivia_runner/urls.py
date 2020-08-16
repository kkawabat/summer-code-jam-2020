from django.urls import path

from trivia_runner.views import setup, active_trivia, TriviaQuizDeleteView, ActiveTriviaSessionListView

urlpatterns = [
    path('', ActiveTriviaSessionListView.as_view(), name='trivia-session-list'),
    path('<int:pk>/', active_trivia, name='trivia-session'),
    path('<int:pk>/setup/', setup, name='trivia-session-setup'),
    path('<int:pk>/delete/', TriviaQuizDeleteView.as_view(), name='trivia-session-delete'),
]
