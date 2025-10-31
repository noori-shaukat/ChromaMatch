# ChromaMatch – Contribution Report

## Team Members

| Name | ERP ID |
|------|---------|------|
| **Hamna Usman** | 26990 |
| **Noor-un-Nisa Shaukat** |
| **Anushe Ali** | 26418 |

---

## Task Distribution & Responsibilities

| Area | Description | Responsible Member |
|------|--------------|--------------------|
| **Data Preparation & Ingestion** | Collected and preprocessed facial image data; implemented image augmentation and dataset splitting for training and validation. | Anushe Ali |
| **Model Development & Training** | Trained the ChromaMatch v1 model; integrated MLflow tracking for experiments and model registry. | Hamna Usman |
| **API Development (FastAPI)** | Built RESTful API for inference including `/health` and `/analyze` endpoints; added Swagger and ReDoc documentation. | Anushe Ali |
| **MLflow Integration** | Configured MLflow for experiment tracking, model registry, and version control. | Hamna Usman |
| **CI/CD Pipeline & Pre-commit Hooks** | Configured GitHub Actions for testing, linting, and deployment; implemented pre-commit hooks (`black`, `ruff`, `detect-secrets`). | Noor-un-Nisa Shaukat |
| **Monitoring – Prometheus & Grafana** | Set up Prometheus for metrics scraping (CPU, memory, disk); configured Grafana dashboard using Windows Exporter data source. | Hamna Usman |
| **Evidently Data Drift Reports** | Created Evidently reports for model drift and performance tracking using dummy data. | Hamna Usman |
| **Dockerization** | Created Dockerfile and Makefile targets for building and running the app. | Noor-un-Nisa Shaukat |
| **Testing** | Wrote unit tests (`pytest`) for API endpoints and integrated them in CI/CD workflow. | Noor-un-Nisa Shaukat |
**Security Compliance:** | Added MIT License, `.gitignore`, and pre-commit configurations to ensure repository and codebase security compliance. | Noor-un-Nisa Shaukat
| **Documentation** | Prepared README.md, CONTRIBUTION.md, and architectural diagrams. | Anushe Ali |
---

## Summary

Each team member contributed collaboratively across the pipeline — from **data preparation**, **model tracking**, **deployment**, to **monitoring** — ensuring a complete **MLOps lifecycle** implementation.
