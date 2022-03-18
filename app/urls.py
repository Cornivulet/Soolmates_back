from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, UpdateView, DeleteView, MeView, LogoutView

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register', RegisterView.as_view(), name='register'),
    # path('login', LoginView.as_view(), name='login'),
    path('me', MeView.as_view(), name='get_connected_user'),
    path('update/<int:id>', UpdateView.as_view(), name='update'),
    path('delete/<int:id>', DeleteView.as_view(), name='delete'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
]
