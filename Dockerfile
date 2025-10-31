# ---- build stage ----
FROM python:3.11-slim AS build
WORKDIR /app
# system deps if needed (e.g., libgl1 for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential gcc curl ca-certificates \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---- runtime stage ----
FROM python:3.11-slim
WORKDIR /app
# create non-root user
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY src/ ./src
# COPY .env ./

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
