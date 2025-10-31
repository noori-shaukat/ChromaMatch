from prometheus_client import start_http_server, Gauge
import random
import time

# Define metrics
gpu_utilization = Gauge(
    "gpu_utilization_percent", "Simulated GPU utilization percentage"
)
gpu_memory_usage = Gauge("gpu_memory_usage_mb", "Simulated GPU memory usage (MB)")
gpu_temperature = Gauge(
    "gpu_temperature_celsius", "Simulated GPU temperature (Celsius)"
)


def generate_fake_gpu_metrics():
    """Simulate GPU metrics with random values."""
    gpu_utilization.set(random.uniform(10, 95))  # %
    gpu_memory_usage.set(random.uniform(500, 8000))  # MB
    gpu_temperature.set(random.uniform(40, 85))  # °C


if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(9101)
    print("GPU Metrics Exporter running on http://localhost:9101/metrics")

    while True:
        generate_fake_gpu_metrics()
        time.sleep(5)
