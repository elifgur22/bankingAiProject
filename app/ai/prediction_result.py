from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    risk_level: str
    risk_score: float