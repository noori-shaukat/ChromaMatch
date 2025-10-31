# monitoring/log_chromamatch_model.py
import mlflow
import mlflow.pyfunc
from src.models.pyfunc_wrapper import ChromaMatchPyFunc
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

# MLflow tracking (local or remote)
mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)  # change if your MLflow server runs elsewhere
mlflow.set_experiment("ChromaMatch")


def log_and_register_model():
    with mlflow.start_run(run_name="ChromaMatch_pyfunc_v1"):
        # Log parameters
        mlflow.log_param("model_type", "chroma_pyfunc")
        mlflow.log_param("python_version", "3.11")

        # Dummy metrics for demonstration (replace with actual test data + predictions)
        y_true = np.array([1, 0, 1, 1, 0])
        y_pred = np.array([1, 0, 0, 1, 0])

        # Compute metrics
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        # Log metrics
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision", prec)
        mlflow.log_metric("recall", rec)
        mlflow.log_metric("f1_score", f1)

        # Define conda environment for reproducibility
        conda_env = {
            "name": "chromamatch-env",
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                "python=3.11",
                {
                    "pip": [
                        "torch",
                        "transformers",
                        "pillow",
                        "numpy",
                        "scikit-learn",
                        "mlflow",
                    ]
                },
            ],
        }

        # Log model to MLflow
        mlflow.pyfunc.log_model(
            artifact_path="chromamatch_model",
            python_model=ChromaMatchPyFunc(),
            conda_env=conda_env,
            registered_model_name="ChromaMatch_Model",
        )

        print(
            "Model logged and registered as 'ChromaMatch_Model' with metrics and versioning."
        )


if __name__ == "__main__":
    log_and_register_model()
