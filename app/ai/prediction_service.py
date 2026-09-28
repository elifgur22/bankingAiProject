from pathlib import Path

import joblib

from app.ai.dataset_generator import build_feature_frame
from app.ai.prediction_result import PredictionResult
from app.core.logging_config import get_logger

logger = get_logger(__name__)

AI_DIR = Path(__file__).parent

RISK_MODEL_PATH = AI_DIR / "transaction_risk_model.joblib"

FRAUD_MODEL_PATH = AI_DIR / "transaction_fraud_model.joblib"

# Expected-risk weights. risk_score is a severity estimate, not the model's
# confidence in whichever label it happened to pick.
RISK_LEVEL_WEIGHTS = {
    "LOW": 0.0,
    "MEDIUM": 0.5,
    "HIGH": 1.0
}

FRAUD_DECISION_THRESHOLD = 0.5


class PredictionService:
    """Thin inference wrapper around the trained scikit-learn pipelines.

    Models are loaded once, lazily, on first use. When a model file is
    missing the service reports ``available == False`` and the caller falls
    back to the deterministic rule engine instead of failing the payment.
    """

    def __init__(
            self,
            risk_model_path: Path | None = None,
            fraud_model_path: Path | None = None
    ):
        self.risk_model_path = risk_model_path or RISK_MODEL_PATH
        self.fraud_model_path = fraud_model_path or FRAUD_MODEL_PATH

        self._risk_model = None
        self._fraud_model = None
        self._loaded = False

    def _load_models(self) -> None:
        if self._loaded:
            return

        self._risk_model = self._load(self.risk_model_path, "risk")
        self._fraud_model = self._load(self.fraud_model_path, "fraud")
        self._loaded = True

    @staticmethod
    def _load(path: Path, name: str):
        if not path.exists():
            logger.warning(
                "%s model not found at %s; run python -m app.ai.train_model",
                name,
                path
            )

            return None

        try:
            return joblib.load(path)
        except Exception as error:
            logger.error("Failed to load %s model: %s", name, error)

            return None

    @property
    def available(self) -> bool:
        self._load_models()

        return self._risk_model is not None

    def predict(self, features: dict) -> PredictionResult | None:
        """Score one transaction. Returns None when no model is loaded."""

        if not self.available:
            return None

        frame = build_feature_frame(features)

        risk_level, risk_score = self._predict_risk(frame)
        fraud_score = self._predict_fraud(frame)

        return PredictionResult(
            risk_level=risk_level,
            risk_score=risk_score,
            fraud_score=fraud_score,
            is_fraud_suspected=fraud_score >= FRAUD_DECISION_THRESHOLD,
            source="model"
        )

    def _predict_risk(self, frame) -> tuple[str, float]:
        probabilities = self._risk_model.predict_proba(frame)[0]
        classes = [str(label) for label in self._risk_model.classes_]

        risk_score = sum(
            RISK_LEVEL_WEIGHTS.get(label, 0.0) * float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        )

        predicted_index = int(probabilities.argmax())

        return classes[predicted_index], round(float(risk_score), 4)

    def _predict_fraud(self, frame) -> float:
        if self._fraud_model is None:
            return 0.0

        classes = list(self._fraud_model.classes_)

        if 1 not in classes:
            return 0.0

        probabilities = self._fraud_model.predict_proba(frame)[0]

        return round(float(probabilities[classes.index(1)]), 4)
