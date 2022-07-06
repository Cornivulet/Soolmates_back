from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Message, Match, Like


# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        # cache le mdp dans la réponse et bdd
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        if len(password) < 8:
            raise serializers.ValidationError("Password must have at least 8 characters")
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Password must have at least one capital letter")
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Password must have at least one number")
        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError("Password must have at least one special character")
        instance.save()
        return instance


# Serializer for User card
class UserForCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'age', 'description', 'image')


class UserForDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'age', 'is_banned')


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'age', 'gender', 'description', 'image', 'lf_gender', 'lf_age_from',
            'lf_age_to', 'lf_criteria', 'is_staff', 'is_banned')

    required_fields = ['name', 'email', 'age']

    def validate(self, data):
        for required_field in self.required_fields:
            if (not self.partial or required_field in data) and data[required_field] == '':
                raise serializers.ValidationError(required_field + ' is required')

        # if 'lf_age_to' in data and 'lf_age_from' not in data:
        #     raise serializers.ValidationError('lf_age_from is required')
        # if 'lf_age_from' in data and 'lf_age_to' not in data:
        #     raise serializers.ValidationError('lf_age_to is required')

        # if ('lf_age_to' in data and 'lf_age_from' in data) and data['lf_age_to'] < data['lf_age_from']:
        #     raise serializers.ValidationError("Age to must be greater than age from")

        if (not self.partial or 'age' in data) and data['age'] <= 18:
            raise serializers.ValidationError('Age cannot be inferior than 18')
        return data


class MatchingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'age', 'gender', 'description', 'image', 'lf_gender', 'lf_age_from',
                  'lf_age_to', 'lf_criteria', 'is_staff')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'content', 'sender', 'created_at')


class MatchSerializer(serializers.ModelSerializer):
    user = MatchingUserSerializer(read_only=True)
    match_user = MatchingUserSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ('id', 'user', 'match_user')


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('image',)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user_id', 'user_target_id')
