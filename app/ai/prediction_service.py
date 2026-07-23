from pathlib import Path

import joblib
import pandas as pd


class PredictionService:

    def __init__(self):
        model_path = (
            Path(__file__).parent
            / "transaction_risk_model.joblib"
        )

        self.model = joblib.load(model_path)

    def predict_risk(
            self,
            transaction_amount: float,
            available_balance: float,
            blocked_balance: float,
            debit_blocked: bool
    ) -> str:

        features = pd.DataFrame([
            {
                "transaction_amount": transaction_amount,
                "available_balance": available_balance,
                "blocked_balance": blocked_balance,
                "debit_blocked": int(debit_blocked)
            }
        ])

        prediction = self.model.predict(features)

        return prediction[0]