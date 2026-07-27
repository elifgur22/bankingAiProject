from pathlib import Path

import joblib
import pandas as pd

from app.ai.prediction_result import PredictionResult


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
    ) -> PredictionResult:

        features = pd.DataFrame([
            {
                "transaction_amount": transaction_amount,
                "available_balance": available_balance,
                "blocked_balance": blocked_balance,
                "debit_blocked": int(debit_blocked)
            }
        ])

        risk_level = self.model.predict(features)[0]

        probabilities = self.model.predict_proba(features)[0]
        risk_score = float(max(probabilities))

        return PredictionResult(
            risk_level=risk_level,
            risk_score=risk_score
        )