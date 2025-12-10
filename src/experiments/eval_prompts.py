# experiments/eval_prompts.py
import json
import os
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import mlflow

# -------------------------
# Config / Load API Key
# -------------------------
load_dotenv()

def get_client():
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

client = get_client()

# -------------------------
# Models
# -------------------------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Paths
# -------------------------
PROMPT_DIR = "src/experiments/prompts"
EVAL_FILE = "data/eval.jsonl"
RESULT_DIR = "src/experiments/results"
os.makedirs(RESULT_DIR, exist_ok=True)

PROMPTS = {
    "baseline": os.path.join(PROMPT_DIR, "baseline_zeroshot.txt"),
    "few_shot": os.path.join(PROMPT_DIR, "few_shot.txt"),
    "advanced": os.path.join(PROMPT_DIR, "advanced_cot.txt"),
}


# -------------------------
# Load prompts
# -------------------------
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


prompt_templates = {name: load_prompt(p) for name, p in PROMPTS.items()}

# -------------------------
# Load evaluation dataset
# -------------------------
eval_samples = []
with open(EVAL_FILE, "r", encoding="utf-8") as f:
    for line in f:
        eval_samples.append(json.loads(line.strip()))


# -------------------------
# LLM Call Helper
# -------------------------
def call_llm(prompt):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.3,
    )
    return completion.choices[0].message.content


# -------------------------
# MLflow experiment
# -------------------------
mlflow.set_tracking_uri("http://13.60.180.47:5000")
mlflow.set_experiment("prompt_comparison")

# -------------------------
# Evaluation Loop
# -------------------------
overall_summary = {}

for prompt_name, template in prompt_templates.items():
    print(f"\n=== Running prompt: {prompt_name} ===")

    # Start an MLflow run for this prompt strategy
    with mlflow.start_run(run_name=prompt_name):
        per_example_results = []
        sim_scores = []

        # For reproducibility, log prompt text as artifact
        mlflow.log_text(template, artifact_file=f"prompt_{prompt_name}.txt")

        for sample in eval_samples:
            sample_id = sample["sample_id"]
            ground_truth = sample["ground_truth"]

            # Merge features into readable text (human-friendly)
            features_text = (
                f"Sample ID: {sample_id}\n"
                f"skin_L: {sample.get('skin_L')}\n"
                f"skin_a: {sample.get('skin_a')}\n"
                f"skin_b: {sample.get('skin_b')}\n"
                f"mst_level: {sample.get('mst_level')}\n"
                f"tone_group: {sample.get('tone_group')}\n"
                f"descriptor: {sample.get('descriptor')}\n"
                f"undertone: {sample.get('undertone')}\n"
                f"eye_color_left: {sample.get('eye_color_left')}\n"
                f"eye_color_right: {sample.get('eye_color_right')}\n"
                f"hair_color: {sample.get('hair_color')}\n"
            )

            # Fill template – we support {FEATURES} placeholder (case-insensitive)
            final_prompt = template.replace("{FEATURES}", features_text).replace(
                "{features}", features_text
            )

            # Call LLM
            output = call_llm(final_prompt)

            # Metrics
            emb_pred = embed_model.encode([output])[0]
            emb_true = embed_model.encode([ground_truth])[0]
            sim = float(cosine_similarity([emb_pred], [emb_true])[0][0])

            sim_scores.append(sim)

            per_example_results.append(
                {
                    "sample_id": sample_id,
                    "prediction": output,
                    "ground_truth": ground_truth,
                    "similarity": sim,
                }
            )

            print(f"  {sample_id}: sim={sim:.3f}")

        # Aggregates
        avg_sim = sum(sim_scores) / len(sim_scores)

        # Log aggregated metrics to MLflow
        mlflow.log_metric("avg_cosine_similarity", avg_sim)
        mlflow.log_metric("n_examples", len(per_example_results))

        # Save per-example results file and log as artifact
        out_file = os.path.join(RESULT_DIR, f"{prompt_name}_results.jsonl")
        with open(out_file, "w", encoding="utf-8") as fw:
            for r in per_example_results:
                fw.write(json.dumps(r) + "\n")

        mlflow.log_artifact(out_file, artifact_path="results")

        overall_summary[prompt_name] = {
            "avg_cosine_similarity": avg_sim,
            "n": len(per_example_results),
            "results_file": out_file,
        }

# -------------------------
# Print summary
# -------------------------
print("\n=== Summary (Average Metrics) ===")
for name, v in overall_summary.items():
    print(f"{name}: sim={v['avg_cosine_similarity']:.3f}")
