from flask import Flask, send_file
from evidently.report import Report
from evidently.metrics import DataDriftTable
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

DATA_DIR = "data"
REFERENCE_PATH = os.path.join(DATA_DIR, "reference_embeddings.csv")
CURRENT_PATH = os.path.join(DATA_DIR, "current_embeddings.csv")


def generate_sample_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REFERENCE_PATH):
        reference = pd.DataFrame(
            {
                "avg_R": np.random.normal(120, 25, 200),
                "avg_G": np.random.normal(130, 25, 200),
                "avg_B": np.random.normal(140, 25, 200),
                "brightness": np.random.uniform(0.3, 0.9, 200),
                "predicted_color": np.random.choice(
                    ["red", "blue", "green", "beige"], 200
                ),
            }
        )
        reference.to_csv(REFERENCE_PATH, index=False)

    current = pd.DataFrame(
        {
            "avg_R": np.random.normal(150, 25, 200),
            "avg_G": np.random.normal(110, 25, 200),
            "avg_B": np.random.normal(120, 25, 200),
            "brightness": np.random.uniform(0.2, 0.8, 200),
            "predicted_color": np.random.choice(["red", "blue", "green", "beige"], 200),
        }
    )
    current.to_csv(CURRENT_PATH, index=False)


generate_sample_data()


@app.route("/")
def generate_report():
    reference = pd.read_csv(REFERENCE_PATH)
    current = pd.read_csv(CURRENT_PATH)

    report = Report(metrics=[DataDriftTable()])
    report.run(reference_data=reference, current_data=current)

    report_path = os.path.join(DATA_DIR, "data_drift_report.html")
    report.save_html(report_path)

    return send_file(report_path, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
