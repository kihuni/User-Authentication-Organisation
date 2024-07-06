from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organisation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone']

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['org_id', 'name', 'description']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone']

    def validate(self, data):
        errors = []
        if not data.get('first_name'):
            errors.append({'field': 'first_name', 'message': 'First name is required'})
        if not data.get('last_name'):
            errors.append({'field': 'last_name', 'message': 'Last name is required'})
        if not data.get('email'):
            errors.append({'field': 'email', 'message': 'Email is required'})
        if not data.get('password'):
            errors.append({'field': 'password', 'message': 'Password is required'})
        if errors:
            raise serializers.ValidationError({'errors': errors})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        organisation = Organisation.objects.create(name=f"{validated_data['first_name']}'s Organisation")
        organisation.users.add(user)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
