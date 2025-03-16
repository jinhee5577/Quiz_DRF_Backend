from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice, Attempt, Answer
# 기존 장고는 Queryset을 templeate로 넘겨 html로 렌더링 했다.
# 하지만 RESTful API는 JSON으로 데이터를 보내기 때문에 장고 template를 사용할수 없다.
# 즉 Queryset과 이러한 json형태의 데이터를 매핑하기 위한 도구로 Seriallizer를 이용한다.
# DRF에서는 Serializer를 사용해 모델 인스턴스와 JSON 데이터를 변환함.


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    # Django의 User모델을 기반으로 회원가입을 처리하는 시리얼라이저.
    password = serializers.CharField(write_only=True)
    # write_only=True로 설정하면 응답(Response)에는 포함되지 않고, 요청(Request)에서만 받는다.

    class Meta: # Meta클래스 (시리얼라이저에 포함할 필드 정의)
        model = User
        fields = ['id', 'username', 'email', 'password']

    # 사용자 생성 (create 메서드 오버라이딩), 새로운 사용자를 생성하는 메서드
    def create(self, validated_data): # 입력값이 DRF의 검증(validation)을 통과한후 validated_data로 전달됨.
        # Django의 User모델에서 제공하는 create_user() 메서드를 사용하여 새로운 사용자를 생성.
        user = User.objects.create_user(
            username=validated_data['username'],
            # email필드는 선택적 일수 있으므로 .get()을 사용하여 기본값 ''(빈 문자열)를 설정.
            email=validated_data.get('email', ''),
            password=validated_data['password'] # create_user()는 password를 자동으로 해싱(암호화)하여 저장함.
        )

        return user    

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True) # 관련된 모든 선택지를 포함

    class Meta:
        model = Question
        fields = ["id", "text", "choices"]

class QuizSerializer(serializers.ModelSerializer):
   # QuizSerializer는 Quiz 모델을 JSON 데이터로 변환해 줌. 
    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "question_count", "shuffle_questions", "shuffle_choices"]

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "question_count", "shuffle_questions", "shuffle_choices", "questions"]

# class AttemptSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attempt
#         fields = ["id", "user", "quiz", "submitted_at"]

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "question", "selected_choice"]  # 'attempt' 없음!


class AttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attempt
        fields = ['id', 'quiz', 'submitted_at', 'score', 'answers'] # user제거

    # DRF create()메서드로, 사용자가 퀴즈를 응시할때 답안 저장과 자동 채점을 처리함.
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user  # 현재 요청 유저

        # 유저가 보낸 데이터중 answers목록만 추출하고, validated_data에서는 제거.
        answers_data = validated_data.pop('answers') # answers_data는 각문제의 답안 정보가 담긴 리스트.
        # 추출후 남은 데이터(user, quiz)로 Attempt 객체(DB응시 기록)를 생성.
        attempt = Attempt.objects.create(user=user, **validated_data)

        score = attempt.score  # 기존 저장된 점수 불러오기
        for answer_data in answers_data:
            # 사용자가 응답한 답안에서 문제와 선택지를 추출.
            question = answer_data['question']
            selected_choice = answer_data['selected_choice']

            # 수정: Choice의 is_correct 값으로 채점
            if selected_choice.is_correct: # 자동채점은 Choice모델의 is_correct=True 여부로 처리됨.
                score += 1  # 유저의 선택이 정답이면 점수 1점 추가.
                
            # 응시 기록(attempt)과 함께 개별답안(Answer)을 DB에 저장.    
            Answer.objects.create(attempt=attempt, **answer_data)

        attempt.score = score
        # 최종 점수를 Attempt객체에 저장하고 DB에 반영.
        attempt.save()

        # 생성된 Attempt객체를 반환, DRF가 JSON응답 생성.
        return attempt
       