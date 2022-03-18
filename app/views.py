from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import User
from app.serializers import UserSerializer, MeSerializer


# API route to register a new user
# POST
# /register
class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
# /update/me
class UpdateView(APIView):
    def put(self, request, id):
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# API route to delete a user by id
# DELETE
# /delete/{id}
class DeleteView(APIView):
    def delete(self, request, id):
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        user.delete()
        return Response({'message': 'User deleted'})


# API route to logout a user
# POST
# /logout
class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out'})
