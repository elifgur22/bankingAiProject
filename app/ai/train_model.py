"""Train the transaction risk and fraud models on synthetic data.

Run with:  python -m app.ai.train_model
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.ai.dataset_generator import (
    DEFAULT_ROW_COUNT,
    DEFAULT_SEED,
    generate_transaction_dataset
)
from app.ai.model_evaluation import (
    evaluate_classifier,
    feature_importances,
    render_confusion_matrix
)
from app.ai.transaction_feature_builder import (
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    FRAUD_TARGET_COLUMN,
    NUMERIC_FEATURES,
    RISK_TARGET_COLUMN
)

AI_DIR = Path(__file__).parent

RISK_MODEL_PATH = AI_DIR / "transaction_risk_model.joblib"

FRAUD_MODEL_PATH = AI_DIR / "transaction_fraud_model.joblib"

ARTIFACTS_DIR = AI_DIR / "artifacts"

TEST_SIZE = 0.25


def build_pipeline(class_weight: str | None = None) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES + BINARY_FEATURES
            )
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        class_weight=class_weight,
        random_state=DEFAULT_SEED,
        n_jobs=-1
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])


def train_model(
        row_count: int = DEFAULT_ROW_COUNT,
        seed: int = DEFAULT_SEED,
        write_artifacts: bool = True
) -> dict:
    """Train both models and return their evaluation report."""

    dataset = generate_transaction_dataset(row_count=row_count, seed=seed)

    features = dataset[FEATURE_COLUMNS]

    risk_report = _train_single(
        features,
        dataset[RISK_TARGET_COLUMN],
        model_path=RISK_MODEL_PATH,
        name="risk",
        class_weight=None,
        positive_label=None,
        seed=seed,
        write_model=write_artifacts
    )

    fraud_report = _train_single(
        features,
        dataset[FRAUD_TARGET_COLUMN],
        model_path=FRAUD_MODEL_PATH,
        name="fraud",
        class_weight="balanced",
        positive_label=1,
        seed=seed,
        write_model=write_artifacts
    )

    report = {
        "dataset": {
            "rows": int(len(dataset)),
            "seed": seed,
            "source": "synthetic (app.ai.dataset_generator)",
            "risk_level_distribution": _distribution(
                dataset[RISK_TARGET_COLUMN]
            ),
            "fraud_rate": float(dataset[FRAUD_TARGET_COLUMN].mean())
        },
        "risk_model": risk_report,
        "fraud_model": fraud_report
    }

    if write_artifacts:
        _write_reports(report)

    return report


def _train_single(
        features: pd.DataFrame,
        target: pd.Series,
        model_path: Path,
        name: str,
        class_weight: str | None,
        positive_label,
        seed: int,
        write_model: bool
) -> dict:

    train_features, test_features, train_target, test_target = (
        train_test_split(
            features,
            target,
            test_size=TEST_SIZE,
            random_state=seed,
            stratify=target
        )
    )

    pipeline = build_pipeline(class_weight=class_weight)
    pipeline.fit(train_features, train_target)

    metrics = evaluate_classifier(
        pipeline,
        test_features,
        test_target,
        positive_label=positive_label
    )

    if write_model:
        joblib.dump(pipeline, model_path)

    return {
        "name": name,
        "model_path": str(model_path),
        "train_rows": int(len(train_features)),
        "test_rows": int(len(test_features)),
        "metrics": metrics,
        "feature_importances": feature_importances(pipeline, top_n=15)
    }


def _distribution(series: pd.Series) -> dict:
    counts = series.value_counts(normalize=True).to_dict()

    return {str(key): float(value) for key, value in counts.items()}


def _write_reports(report: dict) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    (ARTIFACTS_DIR / "training_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    lines = ["# Model training report", ""]

    lines.append(
        f"Dataset: {report['dataset']['rows']} synthetic rows "
        f"(seed {report['dataset']['seed']})"
    )
    lines.append(
        f"Fraud rate: {report['dataset']['fraud_rate']:.4f}"
    )
    lines.append("")

    for key in ("risk_model", "fraud_model"):
        section = report[key]
        metrics = section["metrics"]

        lines.append(f"## {section['name']} model")
        lines.append("")
        lines.append(f"- accuracy: {metrics['accuracy']:.4f}")
        lines.append(f"- precision: {metrics['precision']:.4f}")
        lines.append(f"- recall: {metrics['recall']:.4f}")
        lines.append(f"- f1: {metrics['f1']:.4f}")

        if metrics.get("roc_auc") is not None:
            lines.append(f"- roc_auc: {metrics['roc_auc']:.4f}")

        lines.append("")
        lines.append("### Confusion matrix")
        lines.append("")
        lines.append("```")
        lines.append(render_confusion_matrix(metrics["confusion_matrix"]))
        lines.append("```")
        lines.append("")
        lines.append("### Top feature importances")
        lines.append("")

        for item in section["feature_importances"][:10]:
            lines.append(
                f"- {item['feature']}: {item['importance']:.4f}"
            )

        lines.append("")

    (ARTIFACTS_DIR / "training_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    for key in ("risk_model", "fraud_model"):
        pd.DataFrame(report[key]["feature_importances"]).to_csv(
            ARTIFACTS_DIR / f"{report[key]['name']}_feature_importance.csv",
            index=False
        )

        confusion = report[key]["metrics"]["confusion_matrix"]

        pd.DataFrame(
            confusion["matrix"],
            index=confusion["labels"],
            columns=confusion["labels"]
        ).to_csv(
            ARTIFACTS_DIR / f"{report[key]['name']}_confusion_matrix.csv"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the synthetic transaction risk/fraud models."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROW_COUNT
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED
    )

    arguments = parser.parse_args()

    report = train_model(row_count=arguments.rows, seed=arguments.seed)

    print("Risk model :", RISK_MODEL_PATH)
    print("Fraud model:", FRAUD_MODEL_PATH)
    print(
        "Risk accuracy : "
        f"{report['risk_model']['metrics']['accuracy']:.4f}"
    )
    print(
        "Fraud recall  : "
        f"{report['fraud_model']['metrics']['recall']:.4f}"
    )
    print("Artifacts  :", ARTIFACTS_DIR)


if __name__ == "__main__":
    main()
