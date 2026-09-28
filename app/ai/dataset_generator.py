"""Synthetic transaction dataset generator.

No real customer data is used anywhere in this project. Rows are drawn from
a seeded generator so training runs are reproducible.
"""

import numpy as np
import pandas as pd

from app.ai.transaction_feature_builder import (
    FEATURE_COLUMNS,
    FRAUD_TARGET_COLUMN,
    RISK_TARGET_COLUMN,
    TransactionFeatureBuilder
)

DEFAULT_ROW_COUNT = 8_000

DEFAULT_SEED = 42

ACCOUNT_TYPES = [
    "CURRENT",
    "SAVING_ACCOUNT",
    "SALARY_ACCOUNT",
    "FOREIGN_CURRENCY_ACCOUNT",
    "INVESTMENT_ACCOUNT",
    "CREDIT_CARD_ACCOUNT"
]

TRANSACTION_TYPES = ["DEPOSIT", "WITHDRAW", "TRANSFER", "SUNDRY"]

CURRENCIES = ["TRY", "USD", "EUR", "GBP"]

# Latent-score cut points that turn a continuous risk signal into labels.
# Calibrated so the generated set lands near 60/30/10 LOW/MEDIUM/HIGH
# instead of a degenerate all-LOW distribution.
MEDIUM_RISK_THRESHOLD = 0.28

HIGH_RISK_THRESHOLD = 0.52


def generate_transaction_dataset(
        row_count: int = DEFAULT_ROW_COUNT,
        seed: int = DEFAULT_SEED
) -> pd.DataFrame:

    rng = np.random.default_rng(seed)

    current_balance = np.round(
        rng.lognormal(mean=8.6, sigma=1.15, size=row_count),
        2
    )

    overdraft_limit = np.where(
        rng.random(row_count) < 0.45,
        np.round(rng.uniform(0, 20_000, size=row_count), 2),
        0.0
    )

    blocked_balance = np.where(
        rng.random(row_count) < 0.25,
        np.round(rng.uniform(0, 0.4, size=row_count) * current_balance, 2),
        0.0
    )

    debit_blocked = (rng.random(row_count) < 0.07).astype(int)
    credit_blocked = (rng.random(row_count) < 0.04).astype(int)
    is_primary = (rng.random(row_count) < 0.55).astype(int)

    available_balance = np.maximum(
        current_balance + overdraft_limit - blocked_balance,
        0.0
    )

    # Most transactions are small relative to the balance, a tail is not.
    amount_ratio = rng.lognormal(mean=-1.9, sigma=1.25, size=row_count)

    transaction_amount = np.round(
        np.maximum(available_balance, 1_000.0) * amount_ratio + 25.0,
        2
    )

    ratio = transaction_amount / np.maximum(available_balance, 1.0)

    account_type = rng.choice(ACCOUNT_TYPES, size=row_count)
    transaction_type = rng.choice(
        TRANSACTION_TYPES,
        size=row_count,
        p=[0.30, 0.35, 0.28, 0.07]
    )
    currency = rng.choice(
        CURRENCIES,
        size=row_count,
        p=[0.70, 0.15, 0.10, 0.05]
    )

    frame = pd.DataFrame({
        "transaction_amount": transaction_amount,
        "available_balance": available_balance,
        "current_balance": current_balance,
        "overdraft_limit": overdraft_limit,
        "blocked_balance": blocked_balance,
        "amount_to_available_ratio": ratio,
        "debit_transaction_blocked": debit_blocked,
        "credit_transaction_blocked": credit_blocked,
        "is_primary_account": is_primary,
        "account_type": account_type,
        "transaction_type": transaction_type,
        "currency": currency
    })

    risk_signal = _risk_signal(frame, rng)

    frame[RISK_TARGET_COLUMN] = np.select(
        [
            risk_signal >= HIGH_RISK_THRESHOLD,
            risk_signal >= MEDIUM_RISK_THRESHOLD
        ],
        ["HIGH", "MEDIUM"],
        default="LOW"
    )

    frame[FRAUD_TARGET_COLUMN] = _fraud_labels(frame, risk_signal, rng)

    return frame[
        FEATURE_COLUMNS + [RISK_TARGET_COLUMN, FRAUD_TARGET_COLUMN]
    ]


def _risk_signal(frame: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """Continuous 0-1 risk driver behind the categorical risk label."""

    ratio = frame["amount_to_available_ratio"].to_numpy()

    # Saturating response: the jump from 5% to 50% of the available balance
    # matters far more than the jump from 150% to 200%.
    ratio_component = 1.0 - np.exp(-2.5 * ratio)

    signal = (
        0.50 * ratio_component
        + 0.28 * frame["debit_transaction_blocked"].to_numpy()
        + 0.10 * (frame["blocked_balance"].to_numpy() > 0)
        + 0.12 * np.clip(
            frame["transaction_amount"].to_numpy() / 100_000.0,
            0.0,
            1.0
        )
        + 0.04 * (1 - frame["is_primary_account"].to_numpy())
    )

    # Label noise keeps the model from learning a trivially perfect rule.
    signal = signal + rng.normal(loc=0.0, scale=0.04, size=len(frame))

    return np.clip(signal, 0.0, 1.0)


def _fraud_labels(
        frame: pd.DataFrame,
        risk_signal: np.ndarray,
        rng: np.random.Generator
) -> np.ndarray:
    """Rare positive class driven by risk plus a few fraud-specific cues."""

    ratio = frame["amount_to_available_ratio"].to_numpy()

    probability = (
        0.004
        + 0.300 * (ratio > 1.2)
        + 0.220 * frame["debit_transaction_blocked"].to_numpy()
        + 0.120 * (
            (frame["transaction_amount"].to_numpy() > 75_000)
            & (frame["is_primary_account"].to_numpy() == 0)
        )
        + 0.060 * (
            (frame["currency"].to_numpy() != "TRY")
            & (frame["transaction_type"].to_numpy() == "TRANSFER")
        )
        + 0.040 * (risk_signal > HIGH_RISK_THRESHOLD)
    )

    return (rng.random(len(frame)) < probability).astype(int)


def build_feature_frame(features: dict) -> pd.DataFrame:
    """Wrap a single feature dict into the exact training column order."""

    return pd.DataFrame([features])[FEATURE_COLUMNS]


__all__ = [
    "DEFAULT_ROW_COUNT",
    "DEFAULT_SEED",
    "TransactionFeatureBuilder",
    "build_feature_frame",
    "generate_transaction_dataset"
]
