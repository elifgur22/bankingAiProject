# AI Banking Backend

An AI-powered banking backend developed with **Python**, **FastAPI**, and **Machine Learning**.  
This project follows enterprise backend architecture inspired by Java Spring Boot applications and aims to integrate AI-based risk analysis into banking transactions.

---

# Technologies

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Pandas
- Scikit-learn
- Joblib

---

# Project Architecture

```
Frontend
        │
        ▼
FastAPI Controllers
        │
        ▼
Service Layer
        │
        ▼
Repository Layer
        │
        ▼
SQLite Database

                │
                ▼
          AI Feature Builder
                │
                ▼
          Machine Learning
                │
                ▼
          Risk Prediction
```

---

# Current Features

## Account Management

- Create Account
- Account Types
- Primary Account Support

---

## Account Balance

- Current Balance
- Available Balance
- Overdraft Limit
- Blocked Balance
- Debit Transaction Block
- Credit Transaction Block

---

## Monetary Transactions

Current transaction entity supports:

- Deposit (planned)
- Withdraw (planned)
- Transfer (planned)
- Sundry (planned)

Each transaction stores:

- Amount
- Currency
- Branch
- Transaction Type
- Risk Score
- Risk Level

---

## Risk Engine

A rule-based risk engine has been implemented.

Current rules include:

- Debit transaction blocked
- Transaction amount exceeds available balance
- High amount transactions
- Blocked balance exists

Risk Levels:

- LOW
- MEDIUM
- HIGH

---

## AI Module

Current AI components:

- Transaction Feature Builder
- Training Pipeline
- Prediction Service
- Random Forest Model

Current training dataset is manually generated for learning purposes.

Future versions will use larger transaction datasets.

---

# Current Project Structure

```
app/

├── api/
├── service/
├── repository/
├── domain/
├── schemas/
├── ai/

│   ├── train_model.py
│   ├── prediction_service.py
│   ├── transaction_feature_builder.py
│   └── transaction_risk_model.joblib

├── database.py
└── main.py
```

---

# Roadmap

## Backend

- [x] Account
- [x] Account Balance
- [x] Monetary Transaction
- [x] Repository Layer
- [x] Service Layer
- [x] Rule Based Risk Engine

---

## AI

- [x] Feature Builder
- [x] First ML Model
- [x] Prediction Service
- [ ] Fraud Detection
- [ ] Model Retraining
- [ ] Explainable AI
- [ ] Real Banking Dataset

---

## Banking Operations

- [ ] Deposit
- [ ] Withdraw
- [ ] Transfer
- [ ] Sundry Batch
- [ ] Interest Calculation
- [ ] Scheduled Jobs

---

# Future Goals

- AI-powered fraud detection
- Intelligent transaction risk scoring
- Banking analytics dashboard
- REST API
- PostgreSQL
- Docker
- JWT Authentication
- Redis
- CI/CD Pipeline
