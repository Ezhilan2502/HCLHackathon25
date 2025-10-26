from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import BankAccount,CustomUser,Transaction,LoanApplication


from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer,BankAccountSerializer,MoneyTransferSerializer,LoanApplicationSerializer

# --- A. User Registration View (Returns JWT) ---

class UserRegistrationView(generics.CreateAPIView):
    """
    Handles Customer Sign-up. Returns JWT tokens upon successful registration.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the user
        user = serializer.save()
        
        # 💥 Generate Tokens using the serializer's helper method
        tokens = serializer.get_tokens(user)

        response_data = {
            "message": "User registered successfully and automatically logged in. KYC review pending.",
            "username": user.username,
            "kyc_status": user.kyc_status,
            "tokens": tokens  # Contains access and refresh tokens
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

# --- B. JWT Login View ---

class CustomTokenObtainPairView(TokenObtainPairView):
   
    serializer_class = CustomTokenObtainPairSerializer

class BankAccountCreateView(generics.CreateAPIView):
   
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.AllowAny]

class BankAccountListView(generics.ListAPIView):
   
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BankAccount.objects.all()
    
class MoneyTransferView(generics.CreateAPIView):
    serializer_class = MoneyTransferSerializer
    permission_classes = [permissions.AllowAny]  # No JWT required

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        return Response({
            "message": "Transfer successful",
            "transaction_id": txn.id,
            "sender_account": txn.sender_account.account_number,
            "receiver_account": txn.receiver_account.account_number,
            "amount": txn.amount,
            "balance_sender": txn.sender_account.balance,
            "balance_receiver": txn.receiver_account.balance,
            "timestamp": txn.created_at
        }, status=status.HTTP_201_CREATED)

class LoanApplicationCreateView(generics.CreateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

# Customer lists own loan applications
class LoanApplicationListView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return LoanApplication.objects.filter(customer=self.request.user)

# Admin reviews loan applications
class LoanApplicationReviewView(generics.UpdateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = LoanApplication.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        loan = self.get_object()
        action = request.data.get('action')  # 'APPROVE' or 'REJECT'
        if action not in ['APPROVE', 'REJECT']:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        loan.status = 'APPROVED' if action == 'APPROVE' else 'REJECTED'
        loan.save()
        return Response({
            "message": f"Loan {loan.status.lower()} successfully",
            "loan_id": loan.id,
            "status": loan.status
        }, status=status.HTTP_200_OK)