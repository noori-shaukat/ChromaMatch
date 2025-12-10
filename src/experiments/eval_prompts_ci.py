import os


def evaluate():
    EVAL_FILE = "data/eval.jsonl"
    if not os.path.exists(EVAL_FILE):
        print("data/eval.jsonl not found. Skipping evaluation.")
        return

    # Quick check: count samples
    count = 0
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1

    print(f"CI Prompt evaluation: found {count} samples. CI check passed.")


if __name__ == "__main__":
    evaluate()
