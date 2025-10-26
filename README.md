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
## Objective
This module handles **customer registration** and triggers **KYC (Know Your Customer)** verification automatically.  
It ensures that user accounts are created securely and KYC documents are stored for validation.

---

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
