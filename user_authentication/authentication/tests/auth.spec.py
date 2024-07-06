import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from datetime import timedelta
from django.utils import timezone
from user_authentication.settings import SECRET_KEY
from ..models import User, Organisation

# Unit Tests
@pytest.mark.django_db
def test_token_generation():
    client = APIClient()
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    
    response = client.post(reverse('register'), user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    token = response.data['data']['accessToken']
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    assert decoded_token['email'] == user_data['email']
    assert decoded_token['exp'] > timezone.now() + timedelta(minutes=5)

@pytest.mark.django_db
def test_organisation_access():
    client = APIClient()
    # Create users and organization
    user1 = User.objects.create_user(email='user1@example.com', password='password')
    user2 = User.objects.create_user(email='user2@example.com', password='password')
    organisation = Organisation.objects.create(name="User1's Organisation", description="Description", created_by=user1)

    client.login(email='user1@example.com', password='password')
    response = client.get(reverse('organisation-detail', kwargs={'orgId': organisation.orgId}))
    assert response.status_code == status.HTTP_200_OK

    client.login(email='user2@example.com', password='password')
    response = client.get(reverse('organisation-detail', kwargs={'orgId': organisation.orgId}))
    assert response.status_code == status.HTTP_403_FORBIDDEN

# End-to-End Tests
@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    
    response = client.post(reverse('register'), user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['user']['firstName'] == user_data['firstName']
    assert response.data['data']['user']['email'] == user_data['email']
    assert response.data['data']['accessToken']

    organisation_name = f"{user_data['firstName']}'s Organisation"
    organisation = Organisation.objects.get(name=organisation_name)
    assert organisation

@pytest.mark.django_db
def test_register_user_missing_fields():
    client = APIClient()
    user_data = {
        "firstName": "",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    
    response = client.post(reverse('register'), user_data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data['errors'][0]['field'] == 'firstName'

@pytest.mark.django_db
def test_register_user_duplicate_email():
    client = APIClient()
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    
    client.post(reverse('register'), user_data, format='json')
    response = client.post(reverse('register'), user_data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data['errors'][0]['field'] == 'email'

@pytest.mark.django_db
def test_login_user_success():
    client = APIClient()
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    
    client.post(reverse('register'), user_data, format='json')
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    response = client.post(reverse('login'), login_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['user']['email'] == login_data['email']
    assert response.data['data']['accessToken']
