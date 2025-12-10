import pandas as pd
from evidently.report import Report
from evidently.metric_preset.data_drift import DataDriftPreset
from evidently import ColumnMapping
import os

def generate_drift_report():
    reference_path = "data/reference.jsonl"
    current_path = "data/current.jsonl"

    reference = pd.read_json(reference_path, lines=True)
    current = pd.read_json(current_path, lines=True)

    column_mapping = ColumnMapping()

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)

    os.makedirs("monitoring", exist_ok=True)

    output_path = "monitoring/data_drift_report.html"
    report.save_html(output_path)

    return output_path
