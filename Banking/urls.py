from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import BankAccountCreateView, BankAccountListView
# Import your views from the core_banking app
from Banking.views import (
    UserRegistrationView, 
    CustomTokenObtainPairView,MoneyTransferView,LoanApplicationCreateView,LoanApplicationReviewView,LoanApplicationListView
   
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 
    # Allows a user to sign up and returns JWT tokens immediately.
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    
    # JWT Token Refresh - Gets a new Access Token using the Refresh Token
    # Essential for maintaining a session after the Access Token expires.
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #Account creation
    path('accounts/', BankAccountListView.as_view(), name='list-accounts'),
    path('accounts/create/', BankAccountCreateView.as_view(), name='create-account'),

    #Money transfer
    path('transfer/', MoneyTransferView.as_view(), name='money-transfer'),

    #Loan Application
    path('loans/apply/', LoanApplicationCreateView.as_view(), name='loan-apply'),
    path('loans/', LoanApplicationListView.as_view(), name='loan-list'),
    path('loans/review/<int:id>/', LoanApplicationReviewView.as_view(), name='loan-review'),
]