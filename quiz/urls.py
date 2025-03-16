from django.urls import path
from .views import quiz_list, quiz_detail, question_list_quiz, save_quiz_attempt, get_fetch_attempt

urlpatterns = [
    path('', quiz_list, name='quiz-list'),         # /quiz/
    path('<int:pk>/', quiz_detail, name='quiz-detail'),  # /quiz/1/
    path('questions/<int:quiz_id>/', question_list_quiz, name='question_list_quiz'),  # /questions/1/ 선택한 퀴즈id값에 대한 모든 질문목록과 선택지를 같이 조회함.
    path('attempts/save/', save_quiz_attempt, name='save_quiz_attempt'),  # 퀴즈 응시 제출 및 자동 채점.
    path('attempts/fetch/', get_fetch_attempt, name='get_fetch_attempt'),  # 새로고침시 유저의 최근 응시상태 유지.
]