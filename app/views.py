from datetime import datetime, timezone
from itertools import chain
from operator import attrgetter
from secrets import token_urlsafe

from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Soolmates_back import settings
from app.models import User, VerificationLink, Like, Report, Message, Match
from app.serializers import UserSerializer, MeSerializer, MatchingUserSerializer, UserForDashboardSerializer, \
    MatchSerializer, AvatarSerializer, MessageSerializer


# API route to register a new user
# POST
# /register
class RegisterView(APIView):

    def post(self, request):
        verif_token = token_urlsafe(64)
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        # test if the email is already used
        if User.objects.filter(email=user['email']).exists():
            return Response(status=status.HTTP_409_CONFLICT)
        serializer.save()
        self.send_verification_mail(user, verif_token)
        VerificationLink.objects.create(user=serializer.instance, id=verif_token)
        return Response(user, status=status.HTTP_201_CREATED)

    def send_verification_mail(self, user, verif_token):
        email_subject = 'Soolmates - Vérifiez votre compte'
        html_message = render_to_string('activation_mail.html',
                                        {'url': settings.FRONTEND_HOST + '/verify/' + verif_token})
        send_mail(
            subject=email_subject,
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user['email']],
            message=''
        )


# API route to get the current user
# GET
# /me
class MeView(APIView):
    def get(self, request):
        user = request.user
        serializer = MeSerializer(user)
        return Response(serializer.data)


# API route to modify a user by id
# PUT
# /update/:id
class UpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# API route to delete a user by id
# DELETE
# /delete/{id}
class DeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_410_GONE)


# API route to activate a user account
# PATCH
# /activate/{token}
class ActivateView(APIView):
    def patch(self, request, token):
        verification_link = VerificationLink.objects.filter(id=token).first()
        if verification_link:
            if verification_link.expire_at > datetime.now(timezone.utc):  # not expired
                verification_link.user.is_active = True
                verification_link.user.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# API route to get the matching users with the current user
# GET
# /matching_users
# TODO: Optimize the query
class MatchingUsersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        my_user = request.user
        matching_users = User.objects.filter(
            is_active=True,
            lf_gender__contains=[my_user.gender],
            lf_age_to__gte=my_user.age,
            lf_age_from__lte=my_user.age,
            # lf_criteria__overlap=my_user.lf_criteria,
            is_banned=False,
        )
        # if the matching user is being liked by the current user, we remove it from the list
        for matching_user in matching_users:
            if Like.objects.filter(user=my_user, user_target=matching_user).exists():
                matching_users = matching_users.exclude(id=matching_user.id)
        # make sure the current user is not in the list
        matching_users = matching_users.exclude(id=my_user.id)

        return Response(MatchingUserSerializer(matching_users, many=True).data, status=status.HTTP_200_OK)


# API route to like a user
# POST
# /like/{id}
class LikeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        me = request.user.id
        my_user = request.user
        user = User.objects.get(id=id)
        matching_users = User.objects.filter(
            is_active=True,
            lf_gender__contains=[my_user.gender],
            lf_age_to__gte=my_user.age,
            lf_age_from__lte=my_user.age,
            # lf_criteria__overlap=my_user.lf_criteria,
            is_banned=False,
        )

        if user is None:
            raise AuthenticationFailed('User not found')
        # stop the user from liking anyone that is not in the list of matching users
        if user not in matching_users:
            raise AuthenticationFailed('User not found')
        Like.objects.create(user_id=me, user_target_id=user.id)
        return Response(status=status.HTTP_201_CREATED)


# API route to ban a user
# POST
# /ban/{id}
class BanView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def patch(self, request, id):
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if user.is_banned:
            raise AuthenticationFailed('User is already banned')
        user.is_banned = True
        user.save()
        return Response(status=status.HTTP_200_OK)


# API route to unban a user
# PATCH
# /unban/{id}
class UnbanView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def patch(self, request, id):
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.is_banned:
            raise AuthenticationFailed('User is not banned')
        user.is_banned = False
        user.save()
        return Response(status=status.HTTP_200_OK)


# API route to get all the users
# GET
# /users
class UsersView(APIView):
    permission_classes = (IsAdminUser, IsAuthenticated)

    def get(self, request):
        # get all the users but filter the connected user
        users = User.objects.all().exclude(id=request.user.id)
        return Response(UserForDashboardSerializer(users, many=True).data, status=status.HTTP_200_OK)


# API route to send an email with a new password
# POST
# /forgot_password
class ForgotPasswordView(APIView):
    def post(self, request):
        reset_password_token = token_urlsafe(64)
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        html_message = render_to_string('forgot_password.html',
                                        {
                                            'url': settings.FRONTEND_HOST + '/reset-password/' + reset_password_token})
        send_mail(subject='Nouveau mot de passe',
                  message='',
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[email],
                  html_message=html_message)
        VerificationLink.objects.create(user=user, id=reset_password_token)
        return Response(status=status.HTTP_200_OK)


# API route to reset the password
# PATCH
# /reset_password/{token}
class ResetPasswordView(APIView):
    def patch(self, request, token):
        verification_link = VerificationLink.objects.get(pk=token)
        if verification_link is None:
            raise AuthenticationFailed('User not found')
        if verification_link:
            if verification_link.expire_at > datetime.now(timezone.utc):  # not expired
                verification_link.user.set_password(request.data.get('password'))
                verification_link.user.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# API route to report a user
# POST
# /report/{id}
class ReportView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if user is request.user:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        Report.objects.create(user=user, reason=request.data.get('reason'))
        return Response(status=status.HTTP_200_OK)


# API route to post a message
# POST
# /message/{id}
class CreateMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        match = Match.objects.filter(id=id).first()
        user = request.user
        if match.user.id != user.id and match.match_user.id != user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        Message.objects.create(sender=user, content=request.data.get('message'))
        return Response(status=status.HTTP_200_OK)


# API route to get a match
# GET
# /match/{id}
class MatchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        match = Match.objects.filter(id=id).first()
        if match is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(MatchSerializer(match).data, status=status.HTTP_200_OK)


# API route to get all the messages from a match
# GET
# /messages/{id}
class GetMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        match = Match.objects.filter(id=id).first()
        user = request.user

        if match.user.id != user.id and match.match_user.id != user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if match is None:
            raise AuthenticationFailed('Match not found')
        message_from_me = Message.objects.filter(sender=match.user)
        message_from_other = Message.objects.filter(sender=match.match_user)
        messages = sorted(chain(message_from_me, message_from_other), key=attrgetter('created_at'))
        return Response(MessageSerializer(messages, many=True).data,
                        status=status.HTTP_200_OK)


# API route to get all the matches for a user
# GET
# /matches
class GetMatchesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user is None:
            raise AuthenticationFailed('User not found')
        # get all the matches where the user is the sender or the receiver
        matches = Match.objects.union(Match.objects.filter(user=user)).order_by('-created_at')
        # matches = Match.objects.filter(user=user.id)
        return Response(MatchSerializer(matches, many=True).data, status=status.HTTP_200_OK)


# API route to upload an avatar
# POST
# /upload_image
class UploadAvatarView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API route to get the last messages from a match
# GET
# /last_message/{id}
class GetLastMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        match = Match.objects.filter(id=id).first()
        user = request.user
        if match.user.id != user.id and match.match_user.id != user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if match is None:
            raise AuthenticationFailed('Match not found')
        message_from_me = Message.objects.filter(sender=match.user)
        message_from_other = Message.objects.filter(sender=match.match_user)
        message = sorted(chain(message_from_me, message_from_other), key=attrgetter('created_at'))
        return Response(MessageSerializer(message, many=True).data,
                        status=status.HTTP_200_OK)
