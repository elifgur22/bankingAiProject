from app.ai.prediction_service import PredictionService


prediction_service = PredictionService()

risk_level = prediction_service.predict_risk(
    transaction_amount=120_000,
    available_balance=50_000,
    blocked_balance=10_000,
    debit_blocked=False
)

print("Tahmin edilen risk:", risk_level)