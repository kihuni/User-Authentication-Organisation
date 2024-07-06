from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer, OrganisationSerializer
from .models import Organisation, User

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400,
            "errors": serializer.errors['errors']
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": str(refresh.access_token),
                        "user": UserSerializer(user).data
                    }
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401,
            "errors": serializer.errors['errors']
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        if id:
            user = User.objects.filter(id=id).first()
            if user:
                return Response({
                    "status": "success",
                    "message": "User details",
                    "data": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Bad request",
                "message": "User not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": "Bad request",
            "message": "User ID not provided",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "User organisations",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": OrganisationSerializer(organisation).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400,
            "errors": serializer.errors['errors']
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        organisation = Organisation.objects.filter(org_id=orgId, users=request.user).first()
        if organisation:
            return Response({
                "status": "success",
                "message": "Organisation details",
                "data": OrganisationSerializer(organisation).data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Organisation not found or access denied",
            "statusCode": 404
        }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, orgId):
        organisation = Organisation.objects.filter(org_id=orgId).first()
        if organisation:
            user_id = request.data.get('userId')
            user = User.objects.filter(user_id=user_id).first()
            if user:
                organisation.users.add(user)
                return Response({
                    "status": "success",
                    "message": "User added to organisation successfully"
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Bad request",
                "message": "User not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": "Bad request",
            "message": "Organisation not found",
            "statusCode": 404
        }, status=status.HTTP_404_NOT_FOUND)
