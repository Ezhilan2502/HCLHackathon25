# Core Banking Backend System

## Objective
The objective of this project is to build a **secure, scalable backend system** that supports core banking operations such as:

- Account management  
- Transactions  
- Loan processing  
- Fraud detection  

The system ensures **financial correctness**, **regulatory compliance**, and **high availability**, while providing features for customers, bank administrators, and auditors.

---

## System Actors

| Actor | Responsibilities |
|-------|----------------|
| **Customer** | Registers and manages accounts, performs transactions, applies for loans, views account statements and loan status. |
| **Bank Administrator** | Approves loans, manages customer accounts, reviews flagged or suspicious transactions for fraud detection. |
| **Auditor** | Accesses audit logs, reviews system activity, ensures compliance with regulatory standards. |

---

## Features

- **Customer Features**:  
  - Register and manage accounts  
  - Perform deposits, withdrawals, and fund transfers  
  - Apply for loans and view loan status  
  - View account statements  

- **Bank Admin Features**:  
  - Approve or reject loan applications  
  - Manage customer accounts  
  - Review flagged transactions  

- **Auditor Features**:  
  - Access system audit logs  
  - Review all activities for compliance  

---

## Test Case Example

This module handles **customer registration** and triggers **KYC (Know Your Customer)** verification automatically.  
It ensures that user accounts are created securely and KYC documents are stored for validation.

---



## Technology Stack


- **Backend**: Django (Python) with REST APIs  
- **Frontend**: HTML, CSS, JavaScript  
- **API Testing**: Postman  
- **Database**: SQLite(Django ORM)  
- **Authentication**: JWT  
- **Server**: Run locally using Django `runserver`

**Description:**  
Registers a new customer and triggers KYC verification.



**Sample Postman Setup:**  
- **Method:** POST  
- **URL:** `http://localhost:8000/api/customers/register/`  
- **Body:** form-data including all fields and file uploads  
- **Headers:** Accept: application/json  

---

## Sample Responses

**Success (201 Created):**
```json
{
  "customer_id": "1001",
  "username": "xyz",
  "email": "xyz@example.com",
  "status": "Pending KYC Approval",
  "message": "Registration successful. KYC verification in progress."
}

```
## API Endpoints

| Sl.No | Endpoint | Method |
|---|---------|--------|
| 1 | `http://localhost:8000/api/customers/register` | POST |
| 2 | `http://localhost:8000/api/customers/1001/` | GET |



## Features
* **User Registration**
  * Register with email, password, name, date of birth, phone number, address, and KYC documents.
  * Automatically generates JWT tokens after registration (email-based login).

* **JWT Authentication**
  * Login using email and password.
  * JWT payload includes `email`, `kyc_status`, and `kyc_verified` fields.

* **Bank Account Management**
  * Create savings or current accounts.
  * Validate minimum initial deposits (Savings: 500, Current: 1000).
  * View all accounts of a customer.

* **Money Transfer**
  * Transfer money between accounts.
  * Validates sender balance and daily transfer limits.
  * Logs transactions.
  * Edge cases: insufficient funds, exceeding daily limit.

* **Loan Application**
  * Submit loan application with type, amount, and tenure.
  * System calculates EMI:  
    ```
    EMI = (P * R * (1+R)^N) / ((1+R)^N - 1)
    ```
    *P*: principal, *R*: monthly interest rate, *N*: number of months
  * Admin reviews and approves/rejects loan.
  * Loan status updated accordingly.

## Models
* **CustomUser**
  * Fields: email, username, password, first_name, last_name, date_of_birth, phone_number, address, kyc_status, kyc_uploaded_at, id_proof_document, address_proof_document
* **BankAccount**
  * Fields: account_number, customer (FK), account_type, balance, created_at
* **LoanApplication**
  * Fields: customer (FK), loan_type, principal_amount, tenure_months, interest_rate, emi, status, applied_at, approved_at

## Serializers
* **UserRegistrationSerializer**
  * Handles user creation and validation.
  * Provides helper method to generate JWT tokens.
* **CustomTokenObtainPairSerializer**
  * Email-based login.
  * Adds `kyc_status` and `kyc_verified` to JWT payload.
* **BankAccountSerializer**
  * Validates minimum balance for account types.
* **LoanApplicationSerializer**
  * Calculates EMI and validates input.

## Views / Endpoints
* **User Registration**
  * URL: `/auth/register/`
  * Method: POST
  * Payload example:
    ```json
    {
      "username": "o@gmail.com",
      "email": "o@gmail.com",
      "password": "Password123!",
      "password2": "Password123!",
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1990-01-01",
      "phone_number": "9876543210",
      "address": "123 Main St",
      "id_proof_document": "id_doc_path",
      "address_proof_document": "address_doc_path"
    }
    ```
  * Response: JWT access & refresh tokens, KYC status.

* **Login (JWT Email)**
  * URL: `/auth/login/`
  * Method: POST
  * Payload:
    ```json
    {
      "email": "o@gmail.com",
      "password": "Password123!"
    }
    ```
  * Response: JWT access & refresh tokens with KYC info.

* **Bank Account Creation**
  * URL: `/accounts/create/`
  * Method: POST
  * Requires authenticated user
  * Payload:
    ```json
    {
      "account_type": "SAVINGS",
      "balance": 500
    }
    ```

* **Bank Account List**
  * URL: `/accounts/`
  * Method: GET
  * Returns all accounts for the authenticated user.

* **Money Transfer**
  * URL: `/transfer/`
  * Method: POST
  * Payload example:
    ```json
    {
      "sender_account": "123456789012",
      "receiver_account": "987654321098",
      "amount": 2000
    }
    ```
  * Handles validation: sufficient funds, daily limit, transaction logging.

* **Loan Application**
  * URL: `/loans/apply/`
  * Method: POST
  * Payload example:
    ```json
    {
      "loan_type": "HOME",
      "principal_amount": 500000,
      "tenure_months": 60,
      "interest_rate": 0.08
    }
    ```
  * Response: EMI calculation and loan status.

## Utilities
* `generate_account_number()` – Generates unique 12-digit account numbers.
* `calculate_emi(principal, rate, tenure)` – Calculates monthly EMI.

## Notes
* JWT is required only for email-based login and protected endpoints.
* KYC status defaults to `PENDING` upon registration.
* Admin review required for loan approval.
