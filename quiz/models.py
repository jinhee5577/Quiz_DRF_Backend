from django.db import models
from django.contrib.auth import get_user_model

# Django에서 사용자(User) 모델을 가져오는 함수
User = get_user_model()  # 현재 프로젝트의 User 모델 가져오기

class Quiz(models.Model):
    title = models.CharField(max_length=255)  # 퀴즈 제목
    description = models.TextField(blank=True, null=True)  # 퀴즈 설명 (선택)
    question_count = models.IntegerField(default=10)  # 랜덤으로 출제할 문제 개수
    shuffle_questions = models.BooleanField(default=True)  # 문제 랜덤 배치 여부
    shuffle_choices = models.BooleanField(default=True)  # 선택지 랜덤 배치 여부
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # 퀴즈를 만든 관리자 # User 모델과 연결
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")  # 어떤 퀴즈의 문제인지
    text = models.TextField()  # 문제 내용

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")  # 어떤 문제의 선택지인지
    text = models.CharField(max_length=255)  # 선택지 내용
    is_correct = models.BooleanField(default=False)  # 정답 여부 (True이면 정답)

    def __str__(self):
        return self.text


class Attempt(models.Model): 
    # Attempt모델에 추가될때는 {하나의 객체에 해당 quiz_id에 속한 사용자가 응시한(각문제와 정답이 배열로 들어옴.) answers: [{문제, 선택한 답변},{문제, 선택한 답변}....]}이런식으로
    # DB에 추가될때 이런식의 하나의 {}객체씩 저장된다.
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 응시한 사용자
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # 응시한 퀴즈
    submitted_at = models.DateTimeField(auto_now_add=True)  # 응시 완료 시간
    score = models.IntegerField(default=0)         # 점수

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")  # 어떤 응시 기록에 대한 답변인지
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # 어떤 문제의 답변인지
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)  # 사용자가 선택한 선택지

    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text} -> {self.selected_choice.text}"
