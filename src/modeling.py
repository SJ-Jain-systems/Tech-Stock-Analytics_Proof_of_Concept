"""Train baseline models for next-day stock movement prediction."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_INPUT_PATH = Path("data/processed/stock_features.csv")
MODEL_COMPARISON_OUTPUT_PATH = Path("data/processed/model_comparison.csv")
FEATURE_IMPORTANCE_OUTPUT_PATH = Path("data/processed/feature_importance.csv")
MODEL_OUTPUT_DIR = Path("models")
TARGET_COLUMN = "target_next_day_up"
DATE_COLUMN = "date"
RANDOM_STATE = 42
TRAIN_DATE_FRACTION = 0.8


def get_feature_columns():
    """Return the feature columns used by the modeling workflow."""
    return [
        "lag_1_return",
        "lag_2_return",
        "lag_3_return",
        "lag_5_return",
        "return_5d",
        "return_10d",
        "return_20d",
        "rolling_volatility_10",
        "rolling_volatility_20",
        "rolling_volatility_50",
        "volume_change",
        "volume_to_ma20_ratio",
        "close_to_ma20_ratio",
        "price_range_pct",
        "intraday_return",
    ]


def load_modeling_data(input_path=FEATURE_INPUT_PATH):
    """Load feature data and drop rows missing selected features or target."""
    input_file = Path(input_path)
    feature_columns = get_feature_columns()
    required_columns = [DATE_COLUMN, TARGET_COLUMN, *feature_columns]

    df = pd.read_csv(input_file)
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    modeling_data = df.copy()
    modeling_data[DATE_COLUMN] = pd.to_datetime(modeling_data[DATE_COLUMN], errors="coerce")
    for column in [TARGET_COLUMN, *feature_columns]:
        modeling_data[column] = pd.to_numeric(modeling_data[column], errors="coerce")

    modeling_data = modeling_data.replace([np.inf, -np.inf], np.nan)
    modeling_data = modeling_data.dropna(subset=required_columns).reset_index(drop=True)
    modeling_data[TARGET_COLUMN] = modeling_data[TARGET_COLUMN].astype(int)

    if modeling_data.empty:
        raise ValueError("No modeling rows remain after dropping missing values.")

    return modeling_data


def chronological_train_test_split(df, train_fraction=TRAIN_DATE_FRACTION):
    """Split data by date, training on earliest dates and testing on latest dates."""
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    sorted_dates = np.array(sorted(df[DATE_COLUMN].dropna().unique()))
    if len(sorted_dates) < 2:
        raise ValueError("At least two unique dates are required for a train-test split.")

    split_index = int(len(sorted_dates) * train_fraction)
    split_index = min(max(split_index, 1), len(sorted_dates) - 1)
    train_dates = set(sorted_dates[:split_index])

    train_df = df[df[DATE_COLUMN].isin(train_dates)].sort_values(DATE_COLUMN).copy()
    test_df = df[~df[DATE_COLUMN].isin(train_dates)].sort_values(DATE_COLUMN).copy()

    feature_columns = get_feature_columns()
    X_train = train_df[feature_columns]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[feature_columns]
    y_test = test_df[TARGET_COLUMN]

    return X_train, X_test, y_train, y_test


def train_models(X_train, y_train):
    """Fit baseline and supervised classification models."""
    models = {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

    for model in models.values():
        model.fit(X_train, y_train)

    return models


def _positive_class_scores(model, X_test):
    """Return positive-class prediction scores for ROC-AUC evaluation."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X_test)[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X_test)
    return None


def evaluate_models(models, X_test, y_test):
    """Evaluate fitted models and return a comparison table."""
    results = []

    for model_name, model in models.items():
        y_pred = model.predict(X_test)
        y_score = _positive_class_scores(model, X_test)

        if y_score is not None and y_test.nunique() == 2:
            roc_auc = roc_auc_score(y_test, y_score)
        else:
            roc_auc = np.nan

        results.append(
            {
                "model": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": roc_auc,
            }
        )

    return pd.DataFrame(results).sort_values("f1", ascending=False).reset_index(drop=True)


def _build_feature_importance(models):
    """Create feature-importance rows for tree-based models."""
    feature_columns = get_feature_columns()
    importance_rows = []

    for model_name in ["random_forest", "gradient_boosting"]:
        model = models[model_name]
        for feature, importance in zip(feature_columns, model.feature_importances_):
            importance_rows.append(
                {
                    "model": model_name,
                    "feature": feature,
                    "importance": importance,
                }
            )

    return pd.DataFrame(importance_rows).sort_values(
        ["model", "importance"], ascending=[True, False]
    )


def save_outputs(
    models,
    model_comparison,
    model_comparison_path=MODEL_COMPARISON_OUTPUT_PATH,
    feature_importance_path=FEATURE_IMPORTANCE_OUTPUT_PATH,
    model_output_dir=MODEL_OUTPUT_DIR,
):
    """Save evaluation tables, feature importance, and fitted model artifacts."""
    model_comparison_file = Path(model_comparison_path)
    feature_importance_file = Path(feature_importance_path)
    output_dir = Path(model_output_dir)

    model_comparison_file.parent.mkdir(parents=True, exist_ok=True)
    feature_importance_file.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_comparison.to_csv(model_comparison_file, index=False)

    feature_importance = _build_feature_importance(models)
    feature_importance.to_csv(feature_importance_file, index=False)

    for model_name, model in models.items():
        joblib.dump(model, output_dir / f"{model_name}.joblib")

    return feature_importance


def main():
    """Run the end-to-end predictive modeling workflow."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / FEATURE_INPUT_PATH
    model_comparison_path = project_root / MODEL_COMPARISON_OUTPUT_PATH
    feature_importance_path = project_root / FEATURE_IMPORTANCE_OUTPUT_PATH
    model_output_dir = project_root / MODEL_OUTPUT_DIR

    modeling_data = load_modeling_data(input_path)
    X_train, X_test, y_train, y_test = chronological_train_test_split(modeling_data)
    models = train_models(X_train, y_train)
    model_comparison = evaluate_models(models, X_test, y_test)
    save_outputs(
        models,
        model_comparison,
        model_comparison_path,
        feature_importance_path,
        model_output_dir,
    )

    print(model_comparison.to_string(index=False))


if __name__ == "__main__":
    main()
