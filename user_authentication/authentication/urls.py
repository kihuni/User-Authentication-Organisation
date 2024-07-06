from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationView, OrganisationDetailView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('api/users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('api/organisations', OrganisationView.as_view(), name='organisations'),
    path('api/organisations/<uuid:orgId>/', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('api/organisations/<uuid:orgId>/users', OrganisationDetailView.as_view(), name='add-user-to-organisation'),
]
