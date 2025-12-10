# experiments/qualitative_score.py
import json
import os
import mlflow

RESULT_DIR = "experiments/results"
files = [f for f in os.listdir(RESULT_DIR) if f.endswith("_results.jsonl")]

print("Found result files:", files)

for fname in files:
    path = os.path.join(RESULT_DIR, fname)
    prompt_name = fname.replace("_results.jsonl", "")
    print(f"\nScoring predictions for: {prompt_name}")

    # Start MLflow run
    mlflow.set_experiment("prompt_comparison")
    with mlflow.start_run(run_name=f"qualitative_{prompt_name}"):
        scores = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line.strip())
                print("\n---------------------------")
                print("SAMPLE ID:", obj["sample_id"])
                print("GROUND TRUTH:\n", obj["ground_truth"])
                print("\nPREDICTION:\n", obj["prediction"])
                print("---------------------------")
                # Input ratings
                while True:
                    try:
                        factual = int(input("Factuality (1-5): "))
                        helpful = int(input("Helpfulness (1-5): "))
                        break
                    except ValueError:
                        print("Enter integers 1-5.")

                scores.append({"sample_id": obj["sample_id"], "factuality": factual, "helpfulness": helpful})

        # Save qualitative scores
        qpath = os.path.join(RESULT_DIR, f"{prompt_name}_qualitative.json")
        with open(qpath, "w", encoding="utf-8") as fw:
            json.dump(scores, fw, indent=2)

        # Log artifact and aggregated metrics
        mlflow.log_artifact(qpath, artifact_path="qualitative")
        avg_fact = sum([s["factuality"] for s in scores]) / len(scores)
        avg_help = sum([s["helpfulness"] for s in scores]) / len(scores)
        mlflow.log_metric("avg_factuality", avg_fact)
        mlflow.log_metric("avg_helpfulness", avg_help)
        print(f"Logged qualitative metrics for {prompt_name}: factual={avg_fact:.2f}, helpful={avg_help:.2f}")
