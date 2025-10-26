from rest_framework import serializers
from .models import CustomUser, BankAccount,Transaction,LoanApplication
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from datetime import datetime
from django.contrib.auth import authenticate
from django.db import transaction as db_transaction
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- A. JWT Serializer (Email Login + KYC claims) ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field ='email'  # use email as login field

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate using email
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({
                "detail": "No active account found with the given credentials"
            })

        data = super().validate({
            "username": user.username,  # internally JWT expects username
            "password": password
        })

        # Add custom claims
        data['email'] = user.email
        data['kyc_status'] = user.kyc_status
        data['kyc_verified'] = user.kyc_status == 'VERIFIED'
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['kyc_status'] = user.kyc_status
        token['kyc_verified'] = user.kyc_status == 'VERIFIED'
        return token


# --- B. User Registration Serializer ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    id_proof_document = serializers.CharField(required=True)
    address_proof_document = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True, format='%Y-%m-%d')

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'password2', 'first_name', 'last_name',
            'date_of_birth', 'phone_number', 'address',
            'id_proof_document', 'address_proof_document'
        )
        extra_kwargs = {'email': {'required': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # Set username = email for login purposes
        user = CustomUser.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            id_proof_document=validated_data.get('id_proof_document', ''),
            address_proof_document=validated_data.get('address_proof_document', ''),
            kyc_status='PENDING',
            kyc_uploaded_at=datetime.now(),
            is_active=True
        )
        user.set_password(password)
        user.save()
        return user

    # Optional helper for returning tokens after registration
    def get_tokens(self, user):
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# --- C. Bank Account Serializer ---
class BankAccountSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(write_only=True)  # declare extra field

    class Meta:
        model = BankAccount
        fields = ['customer_email', 'account_number', 'account_type', 'balance', 'created_at']  # include it here
        read_only_fields = ['account_number', 'created_at']

    def create(self, validated_data):
        email = validated_data.pop('customer_email')
        customer = CustomUser.objects.get(email=email)
        return BankAccount.objects.create(customer=customer, **validated_data)

    def validate_balance(self, value):
        account_type = self.initial_data.get('account_type')
        if account_type == 'SAVINGS' and value < 500:
            raise serializers.ValidationError("Minimum initial deposit for savings is 500.")
        if account_type == 'CURRENT' and value < 1000:
            raise serializers.ValidationError("Minimum initial deposit for current account is 1000.")
        return value


DAILY_LIMIT = 100000  # Example daily limit

class MoneyTransferSerializer(serializers.Serializer):
    sender_account_number = serializers.CharField()
    receiver_account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    remark = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        sender_acc_num = data['sender_account_number']
        receiver_acc_num = data['receiver_account_number']
        amount = data['amount']

        if sender_acc_num == receiver_acc_num:
            raise serializers.ValidationError("Sender and receiver cannot be the same.")

        try:
            sender_account = BankAccount.objects.get(account_number=sender_acc_num)
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError("Sender account not found.")

        try:
            receiver_account = BankAccount.objects.get(account_number=receiver_acc_num)
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError("Receiver account not found.")

        if sender_account.balance < amount:
            raise serializers.ValidationError("Insufficient funds in sender account.")

        # Check daily transfer limit
        today = timezone.now().date()
        daily_total = Transaction.objects.filter(
        sender_account=sender_account,
        created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

        if daily_total + amount > DAILY_LIMIT:
            raise serializers.ValidationError(f"Daily transfer limit of {DAILY_LIMIT} exceeded.")

        data['sender_account'] = sender_account
        data['receiver_account'] = receiver_account
        return data

    def create(self, validated_data):
        sender_account = validated_data['sender_account']
        receiver_account = validated_data['receiver_account']
        amount = validated_data['amount']
        remark = validated_data.get('remark', '')

        with db_transaction.atomic():
            # Debit sender
            sender_account.balance -= amount
            sender_account.save()

            # Credit receiver
            receiver_account.balance += amount
            receiver_account.save()

            # Log transaction
            txn = Transaction.objects.create(
                sender=sender_account.customer,
                receiver=receiver_account.customer,
                sender_account=sender_account,
                receiver_account=receiver_account,
                amount=amount,
                transaction_type='DEBIT',
                remark=remark
            )

        return txn
    
class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['id', 'customer', 'loan_type', 'amount', 'tenure_months', 'interest_rate', 'emi', 'status', 'applied_at']
        read_only_fields = ['customer', 'emi', 'status', 'applied_at']
        

    