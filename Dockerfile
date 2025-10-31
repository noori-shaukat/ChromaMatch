# ---- build stage ----
FROM python:3.11-slim AS build
WORKDIR /app
# system deps if needed (e.g., libgl1 for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential gcc curl ca-certificates \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- runtime stage ----
FROM python:3.11-slim
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

# create non-root user
RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=build /usr/local /usr/local

COPY src/ ./src
# COPY .env ./

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
