"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# JWT관련
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # JWT 로그인 (액세스 & 리프레시 토큰 발급)
    TokenRefreshView,  # JWT 리프레시 토큰 갱신
)
from quiz.views import register_user, current_user  # quiz 폴더의 views.py에서 가져옴.


urlpatterns = [
    path('admin/', admin.site.urls),

    # 사용자 인증 관련 엔드포인트
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신
    path('api/register/', register_user, name='register_user'),  # 회원가입
    path('api/user/', current_user, name='current_user'),  # 현재 로그인된 사용자 정보 조회
    path('quiz/', include('quiz.urls')),  # quiz 앱의 URL 연결
]