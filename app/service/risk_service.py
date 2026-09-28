from app.ai.prediction_result import PredictionResult

# Weights of the deterministic fallback. They intentionally mirror the
# drivers used by the synthetic data generator, so a transaction scored
# without the model lands in a comparable band.
DEBIT_BLOCKED_WEIGHT = 0.35

OVER_AVAILABLE_WEIGHT = 0.30

LARGE_AMOUNT_WEIGHT = 0.20

BLOCKED_BALANCE_WEIGHT = 0.10

NON_PRIMARY_WEIGHT = 0.05

LARGE_AMOUNT_THRESHOLD = 100_000.0

HIGH_RISK_THRESHOLD = 0.70

MEDIUM_RISK_THRESHOLD = 0.35

FRAUD_SUSPICION_THRESHOLD = 0.80


class RiskService:
    """Deterministic rule engine used when the trained model is unavailable.

    Payments must not fail because a model file is missing, so this is the
    documented fallback path rather than dead code.
    """

    def calculate_transaction_risk(self, features: dict) -> PredictionResult:
        risk_score = 0.0

        if features.get("debit_transaction_blocked"):
            risk_score += DEBIT_BLOCKED_WEIGHT

        ratio = float(features.get("amount_to_available_ratio", 0.0))

        if ratio > 1.0:
            risk_score += OVER_AVAILABLE_WEIGHT
        elif ratio > 0.5:
            risk_score += OVER_AVAILABLE_WEIGHT / 2

        if float(features.get("transaction_amount", 0.0)) >= (
            LARGE_AMOUNT_THRESHOLD
        ):
            risk_score += LARGE_AMOUNT_WEIGHT

        if float(features.get("blocked_balance", 0.0)) > 0:
            risk_score += BLOCKED_BALANCE_WEIGHT

        if not features.get("is_primary_account"):
            risk_score += NON_PRIMARY_WEIGHT

        risk_score = round(min(risk_score, 1.0), 4)

        return PredictionResult(
            risk_level=self._to_risk_level(risk_score),
            risk_score=risk_score,
            fraud_score=risk_score,
            is_fraud_suspected=risk_score >= FRAUD_SUSPICION_THRESHOLD,
            source="rules"
        )

    @staticmethod
    def _to_risk_level(risk_score: float) -> str:
        if risk_score >= HIGH_RISK_THRESHOLD:
            return "HIGH"

        if risk_score >= MEDIUM_RISK_THRESHOLD:
            return "MEDIUM"

        return "LOW"
