import pandas as pd
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab

# Load datasets
reference = pd.read_json("reference.jsonl", lines=True)
current = pd.read_json("current.jsonl", lines=True)

# Build drift dashboard
dashboard = Dashboard(tabs=[DataDriftTab()])

dashboard.calculate(reference, current)

dashboard.save("data_drift_report.html")

print("Saved: data_drift_report.html")
