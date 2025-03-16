from rest_framework.decorators import api_view, permission_classes  #API View 함수 생성
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice, Attempt
from .serializers import QuizSerializer, QuestionSerializer, UserSerializer, RegisterSerializer, AttemptSerializer

# 함수형으로 api

# 새로운 user 회원가입.
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    # 사용자 회원가입
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "회원 가입 되셨습니다."}, status=201)
    return Response(serializer.errors, status=400)


# 로그인 기능.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    # 현재 로그인된 사용자 정보 조회
    serializer = UserSerializer(request.user) # request.user는 현재 로그인한 사용자 의미.
    return Response(serializer.data)


# 전체 퀴즈 조회 & 새 퀴즈 생성
@api_view(['GET', 'POST'])
def quiz_list(request):
    if request.method == 'GET':
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 특정 퀴즈 조회, 수정, 삭제
@api_view(['GET', 'PUT', 'DELETE'])
# 이 데코레이터는 이 뷰가 GET, PUT, DELETE 메서드를 지원한다는 것을 DRF에 알려줌.
def quiz_detail(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
        # 데이터베이스에서 primary key가 pk인 Quiz객체를 가져온다. (객체 하나)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuizSerializer(quiz)
        # 퀴즈 객체를 직렬화(serialize)해서 JSON 형식으로 변환함.
        return Response(serializer.data) # 직렬화된 데이터를 HTTP 응답으로 반환.

    elif request.method == 'PUT':
        serializer = QuizSerializer(quiz, data=request.data)
        # 기존 퀴즈 객체(quiz)를 업데이트하기 위해, 클라이언트가 보낸 데이터(request.data)로 직렬화 객체를 생성함.

        if serializer.is_valid(): # 전달된 데이터가 올바른지 검증
            serializer.save() 
            # 데이터를 DB에 저장(업데이트)함.
            return Response(serializer.data) # 업데이트된 데이터를 응답으로 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        quiz.delete()
        # DB에서 해당 퀴즈 객체를 삭제함.
        return Response({'message': 'Quiz deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    


 # 질문과 선택지 보기 조회
@api_view(["GET"])
def question_list_quiz(request, quiz_id):
    # 특정 quiz_id와 일치하는 Question목록을 가져오고, 각 Question에 해당하는 Choice선택지를 포함.
    # QuestionSerializer가 이렇게 해당 질문과 선택지를 가져오도록 Serializer됨.
    if request.method == 'GET':
        # 아래코드 일반 내림차순 정렬 목록
        # questions = Question.objects.filter(quiz_id=quiz_id).prefetch_related("choices")

     """ 특정 quiz_id와 일치하는 Question 목록을 랜덤하게 가져오고,
         각 Question에 대한 Choice 선택지도 랜덤하게 포함.  """
    # quiz_id에 해당하는 Question들을 랜덤한 순서로 가져옴.
    questions = Question.objects.filter(quiz_id=quiz_id).order_by("?")

    # Choice.objects.order_by("?")를 사용하여 각 Question에 속한 선택지들도 랜덤한 순서로 가져옴.
    # Prefetch 최적화
    # Choice를 랜덤한 순서로 가져오기 위해 Prefetch("choices", queryset=...) 사용.
    # Prefetch를 사용하여 Django ORM이 미리 데이터를 최적화하여 가져오므로 쿼리 성능을 향상시킴.
    choice_prefetch = Prefetch("choices", queryset=Choice.objects.order_by("?"))

    # 이렇게 작성하면 각Question에 속한 Choice도 랜덤한 순서로 가져옴.
    questions = questions.prefetch_related(choice_prefetch)

    if not questions.exists():
        return Response({"message": "No questions found for this quiz."}, status=status.HTTP_404_NOT_FOUND)

    # 직렬화 객체를 생성함.
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# 퀴즈 응시 제출 및 자동 채점.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_quiz_attempt(request):
    # 퀴즈 응시 제출 및 자동 채점
    # serializer = AttemptSerializer(data=request.data) (기존)
    serializer = AttemptSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        # AttemptSerializer내부 create()에서 저장과, 채점 기능을 오버라이딩후 attempt객체를 뱉어주니까 변수에 담자.
        attempt = serializer.save() 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 새로고침 시 유저의 최근 응시상태 유지
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fetch_attempt(request):
    user = request.user # 현재 로그인된 유저 
    quiz_id = request.query_params.get('quiz')

    if not quiz_id:
        return Response({"error": "quiz ID required"}, status=status.HTTP_400_BAD_REQUEST)

    # 가장 최근에 응시한 Attempt 1개를 가져오려면 내림차순 정렬후 첫번째 (first())가 필요.
    # -submitted_at -> (내림차순 정렬), submitted_at -> (오름차순 정렬)
    attempt = Attempt.objects.filter(user=user, quiz_id=quiz_id).order_by('-submitted_at').first()

    if not attempt:
        return Response({"error": "No attempt found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AttemptSerializer(attempt)  # 한개의 객체만{} 직렬화 해서 보내면됨.
    return Response(serializer.data)
