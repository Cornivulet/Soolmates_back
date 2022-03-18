from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, UserLookingFor, UserProfile


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
        instance.save()
        return instance


# Serializer for User card
class UserForCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'age', 'description', 'image')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'age', 'gender', 'description', 'image')

    def validate(self, data):
        if data['age'] <= 18:
            raise serializers.ValidationError('Age cannot be inferior than 18')
        return data

    def create(self, validated_data):
        return UserProfile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data('gender', instance.age)
        instance.description = validated_data('description', instance.description)
        instance.image = validated_data('image', instance.description)
        instance.save()
        return instance


class UserLookingForSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLookingFor
        fields = ('lfGender', 'lfAgeFrom', 'lfAgeTo')

    def validate(self, data):
        if data['lfAgeTo'] < data['lfAgeFrom']:
            raise serializers.ValidationError("Age to must be greater than age from")
        return data

    def create(self, validated_data):
        return UserLookingFor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.lfGender = validated_data.get('lfGender', instance.lfGender)
        instance.lfAgeFrom = validated_data.get('lfAgeFrom', instance.lfAgeFrom)
        instance.lfAgeTo = validated_data.get('lfAgeTo', instance.lfAgeTo)
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'age', 'gender', 'description', 'image', 'lfGender', 'lfAgeFrom', 'lfAgeTo')


