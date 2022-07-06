from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, UpdateView, DeleteView, MeView, ActivateView, LikeView, BanView, UnbanView, \
    MatchingUsersView, UsersView, GetMatchesView, ForgotPasswordView, \
    ResetPasswordView, UploadAvatarView, MatchView, GetMessagesView, CreateMessageView, LikesView

router = routers.DefaultRouter()

urlpatterns = [
                  path('register', RegisterView.as_view(), name='register'),  # create user account
                  path('me', MeView.as_view(), name='get_connected_user'),  # get user account
                  path('update', UpdateView.as_view(), name='update'),  # maj user
                  path('delete', DeleteView.as_view(), name='delete'),  # delete user
                  path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login user
                  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # idk how to use this
                  path('activate/<str:token>', ActivateView.as_view(), name='activate'),  # activate user
                  path('like/<int:id>', LikeView.as_view(), name='like'),
                  path('ban/<int:id>', BanView.as_view(), name='ban'),
                  path('unban/<int:id>', UnbanView.as_view(), name='unban'),
                  path('matching_users', MatchingUsersView.as_view(), name='matching_users'),
                  path('users', UsersView.as_view(), name='all_users'),  # get all users except the connected user
                  path('messages/<int:id>', GetMessagesView.as_view(), name='get_messages'),
                  path('message/<int:id>', CreateMessageView.as_view(), name='create_message'),
                  path('matches', GetMatchesView.as_view(), name='get_matches'),
                  path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password'),
                  path('reset-password/<str:token>', ResetPasswordView.as_view(), name='reset_password'),
                  path('upload_avatar', UploadAvatarView.as_view(), name='upload_avatar'),
                  path('match/<int:id>', MatchView.as_view(), name='match'),
                  path('likes', LikesView.as_view(), name='likes'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
