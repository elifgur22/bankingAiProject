"""Evaluation helpers shared by training and the AI tests."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score
)
from sklearn.pipeline import Pipeline


def evaluate_classifier(
        pipeline: Pipeline,
        features,
        expected_labels,
        positive_label=None
) -> dict:

    predictions = pipeline.predict(features)

    binary = positive_label is not None
    average = "binary" if binary else "macro"
    pos_label = positive_label if binary else 1

    metrics = {
        "accuracy": float(accuracy_score(expected_labels, predictions)),
        "precision": float(
            precision_score(
                expected_labels,
                predictions,
                average=average,
                pos_label=pos_label,
                zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                expected_labels,
                predictions,
                average=average,
                pos_label=pos_label,
                zero_division=0
            )
        ),
        "f1": float(
            f1_score(
                expected_labels,
                predictions,
                average=average,
                pos_label=pos_label,
                zero_division=0
            )
        ),
        "support": int(len(expected_labels)),
        "classification_report": classification_report(
            expected_labels,
            predictions,
            zero_division=0,
            output_dict=True
        ),
        "confusion_matrix": build_confusion_matrix(
            pipeline,
            expected_labels,
            predictions
        )
    }

    if binary:
        metrics["roc_auc"] = _safe_roc_auc(
            pipeline,
            features,
            expected_labels,
            positive_label
        )

    return metrics


def build_confusion_matrix(
        pipeline: Pipeline,
        expected_labels,
        predictions
) -> dict:

    labels = list(pipeline.classes_)

    matrix = confusion_matrix(
        expected_labels,
        predictions,
        labels=labels
    )

    return {
        "labels": [str(label) for label in labels],
        "matrix": matrix.tolist()
    }


def render_confusion_matrix(confusion: dict) -> str:
    """Plain text confusion matrix; keeps the project free of plotting deps."""

    labels = confusion["labels"]
    matrix = confusion["matrix"]

    width = max(
        [len("actual \\ predicted")]
        + [len(label) for label in labels]
        + [len(str(cell)) for row in matrix for cell in row]
    ) + 2

    header = "actual \\ predicted".ljust(width)
    header += "".join(label.rjust(width) for label in labels)

    lines = [header]

    for label, row in zip(labels, matrix, strict=True):
        line = label.ljust(width)
        line += "".join(str(cell).rjust(width) for cell in row)
        lines.append(line)

    return "\n".join(lines)


def feature_importances(pipeline: Pipeline, top_n: int | None = None) -> list:
    """Importance per expanded (post one-hot) feature, highest first."""

    classifier = pipeline.named_steps["classifier"]
    preprocessor = pipeline.named_steps["preprocessor"]

    names = list(preprocessor.get_feature_names_out())
    importances = np.asarray(classifier.feature_importances_, dtype=float)

    ranked = sorted(
        (
            {"feature": name, "importance": float(importance)}
            for name, importance in zip(names, importances, strict=True)
        ),
        key=lambda item: item["importance"],
        reverse=True
    )

    return ranked[:top_n] if top_n else ranked


def _safe_roc_auc(
        pipeline: Pipeline,
        features,
        expected_labels,
        positive_label
) -> float | None:

    try:
        classes = list(pipeline.classes_)
        positive_index = classes.index(positive_label)

        probabilities = pipeline.predict_proba(features)[:, positive_index]

        return float(roc_auc_score(expected_labels, probabilities))
    except (ValueError, IndexError):
        # Single-class split: ROC AUC is undefined.
        return None
