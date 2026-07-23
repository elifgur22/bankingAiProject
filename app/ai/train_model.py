from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def train_model() -> None:
    training_data = pd.DataFrame([
        {
            "transaction_amount": 500,
            "available_balance": 10_000,
            "blocked_balance": 0,
            "debit_blocked": 0,
            "risk_level": "LOW"
        },
        {
            "transaction_amount": 2_000,
            "available_balance": 20_000,
            "blocked_balance": 0,
            "debit_blocked": 0,
            "risk_level": "LOW"
        },
        {
            "transaction_amount": 30_000,
            "available_balance": 35_000,
            "blocked_balance": 5_000,
            "debit_blocked": 0,
            "risk_level": "MEDIUM"
        },
        {
            "transaction_amount": 50_000,
            "available_balance": 40_000,
            "blocked_balance": 0,
            "debit_blocked": 0,
            "risk_level": "MEDIUM"
        },
        {
            "transaction_amount": 100_000,
            "available_balance": 50_000,
            "blocked_balance": 10_000,
            "debit_blocked": 0,
            "risk_level": "HIGH"
        },
        {
            "transaction_amount": 5_000,
            "available_balance": 20_000,
            "blocked_balance": 0,
            "debit_blocked": 1,
            "risk_level": "HIGH"
        }
    ])

    features = training_data[[
        "transaction_amount",
        "available_balance",
        "blocked_balance",
        "debit_blocked"
    ]]

    target = training_data["risk_level"]

    model = RandomForestClassifier(
        n_estimators=50,
        random_state=42
    )

    model.fit(features, target)

    model_path = Path(__file__).parent / "transaction_risk_model.joblib"

    joblib.dump(model, model_path)

    print("Model oluşturuldu:", model_path)


if __name__ == "__main__":
    train_model()