from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import random

KYC_STATUS_CHOICES = [
    ('PENDING', 'Pending Review'),
    ('VERIFIED', 'Verified'),
    ('REJECTED', 'Rejected'),
    ('UPLOAD_REQUIRED', 'KYC Documents Required'),
]

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
  
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True)
    address = models.TextField(blank=True)

    # KYC Tracking Fields
    kyc_status = models.CharField(
        max_length=20,
        choices=KYC_STATUS_CHOICES,
        default='UPLOAD_REQUIRED' 
    )
    kyc_uploaded_at = models.DateTimeField(null=True, blank=True)
    id_proof_document = models.CharField(max_length=255, blank=True)
    address_proof_document = models.CharField(max_length=255, blank=True)

    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        related_name="custom_user_groups", 
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        related_name="custom_user_permissions", 
        related_query_name="custom_user_permission",
    )

    def __str__(self):
        return self.email or self.username
    
ACCOUNT_TYPES = [
    ('SAVINGS', 'Savings'),
    ('CURRENT', 'Current'),
    ('FD', 'Fixed Deposit'),
]

def generate_account_number():
    """Generate a random 12-digit account number."""
    while True:
        number = str(random.randint(10**11, 10**12 - 1))  # 12-digit
        if not BankAccount.objects.filter(account_number=number).exists():
            return number

class BankAccount(models.Model):
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} ({self.account_type})"
    

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_transactions',
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_transactions'
    )
    sender_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name='debits')
    receiver_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name='credits')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} from {self.sender_account} to {self.receiver_account}"
    

LOAN_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

LOAN_TYPES = [
    ('PERSONAL', 'Personal'),
    ('HOME', 'Home'),
    ('CAR', 'Car'),
]

class LoanApplication(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    tenure_months = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.0)  # Annual %
    emi = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(default=datetime.now)

    def calculate_emi(self):
        """
        EMI = (P * r * (1+r)^n) / ((1+r)^n - 1)
        where:
        P = principal amount (loan amount)
        r = monthly interest rate (annual_rate / 12 / 100)
        n = tenure in months
        """
        P = float(self.amount)
        r = float(self.interest_rate) / 12 / 100
        n = self.tenure_months
        if r == 0:
            self.emi = P / n
        else:
            self.emi = P * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return round(self.emi, 2)

    def save(self, *args, **kwargs):
        if not self.emi:
            self.calculate_emi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.id} - {self.customer.email} - {self.status}"