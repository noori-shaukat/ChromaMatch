import json
import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable
from evidently.metrics import DatasetDriftMetric
from evidently.metrics import ColumnDriftMetric
from evidently.ui.workspace import Workspace


# -------------------------------
# Paths
# -------------------------------
reference_path = "evidently/reference/reference.jsonl"
current_path = "evidently/current/current.jsonl"
workspace_path = "evidently"

# -------------------------------
# Load JSONL into pandas
# -------------------------------
def load_jsonl(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


reference_df = load_jsonl(reference_path)
current_df = load_jsonl(current_path)

# -------------------------------
# Create Evidently Report
# -------------------------------
report = Report(
    metrics=[
        DatasetDriftMetric(),
        DataDriftTable(),
    ]
)

report.run(
    reference_data=reference_df,
    current_data=current_df
)

# Save results
report.save_html("evidently/metrics/data_drift_report.html")

print("Drift report saved → evidently/metrics/data_drift_report.html")
