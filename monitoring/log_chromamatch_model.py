# monitoring/log_chromamatch_model.py
import mlflow
import mlflow.pyfunc
from src.models.pyfunc_wrapper import ChromaMatchPyFunc

# MLflow tracking (local)
mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)  # change if your MLflow server runs elsewhere
mlflow.set_experiment("ChromaMatch")


def log_and_register_model():
    with mlflow.start_run(run_name="ChromaMatch_pyfunc_v1"):
        # Log an example parameter/metric (optional)
        mlflow.log_param("model_type", "chroma_pyfunc")
        # define conda env or requirements for reproducibility
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
                        "scikit-learn",
                    ]
                },
            ],
        }

        # Use mlflow.pyfunc.log_model to save the PythonModel
        mlflow.pyfunc.log_model(
            artifact_path="chromamatch_model",
            python_model=ChromaMatchPyFunc(),
            conda_env=conda_env,
            registered_model_name="ChromaMatch_Model",
        )
        print(
            "Model logged and registered as 'ChromaMatch_Model' (may create version v1)"
        )


if __name__ == "__main__":
    log_and_register_model()
