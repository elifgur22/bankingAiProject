from app.ai.prediction_result import PredictionResult
from app.ai.prediction_service import PredictionService
from app.ai.transaction_feature_builder import TransactionFeatureBuilder
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.domain.account import Account
from app.domain.account_balance import AccountBalance
from app.service.risk_service import RiskService

logger = get_logger(__name__)


class TransactionRiskService:
    """Turns an account plus a proposed movement into a risk assessment.

    Order of preference: trained model -> deterministic rules. Scoring never
    raises; a failure downgrades to rules and the transaction still settles.
    """

    def __init__(
            self,
            prediction_service: PredictionService | None = None,
            risk_service: RiskService | None = None,
            feature_builder: TransactionFeatureBuilder | None = None
    ):
        self.prediction_service = prediction_service or PredictionService()
        self.risk_service = risk_service or RiskService()
        self.feature_builder = feature_builder or TransactionFeatureBuilder()

    def assess(
            self,
            account: Account | None,
            account_balance: AccountBalance,
            transaction_type: str,
            amount: float,
            currency: str,
            available_balance: float
    ) -> PredictionResult:

        features = self.feature_builder.build_features(
            account=account,
            account_balance=account_balance,
            transaction_type=transaction_type,
            amount=amount,
            currency=currency,
            available_balance=available_balance
        )

        if not get_settings().risk_prediction_enabled:
            return self.risk_service.calculate_transaction_risk(features)

        try:
            prediction = self.prediction_service.predict(features)

            if prediction is not None:
                return prediction
        except Exception as error:
            logger.error(
                "Risk model scoring failed, falling back to rules: %s",
                error
            )

        return self.risk_service.calculate_transaction_risk(features)
