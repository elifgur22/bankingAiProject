from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    """Outcome of the risk / fraud assessment of a single transaction.

    risk_level:         LOW | MEDIUM | HIGH
    risk_score:         0.0 - 1.0 expected risk, NOT the model's confidence
    fraud_score:        0.0 - 1.0 probability of the fraud class
    is_fraud_suspected: fraud_score above the decision threshold
    source:             "model" when the trained pipeline answered,
                        "rules" when the deterministic fallback did
    """

    risk_level: str
    risk_score: float
    fraud_score: float = 0.0
    is_fraud_suspected: bool = False
    source: str = "model"
