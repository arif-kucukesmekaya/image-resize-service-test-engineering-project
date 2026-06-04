# Bu dosya: Prometheus metriklerinin tanımlanması ve FastAPI entegrasyonu
from fastapi import FastAPI
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
RESIZE_TOTAL = Counter(
    "resize_operations_total",
    "Total number of image resize operations",
    ["status", "format"]
)

RESIZE_DURATION = Histogram(
    "resize_duration_seconds",
    "Time taken to resize images in seconds",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

S3_UPLOAD_DURATION = Histogram(
    "s3_upload_duration_seconds",
    "Time taken to upload resized images to S3 in seconds"
)

def setup_metrics(app: FastAPI) -> None:
    """Sets up Prometheus HTTP instrumentation and registers custom application metrics.

    Args:
        app: The FastAPI application instance to instrument.
    """
    # Instruments standard HTTP request metrics and exposes the '/metrics' endpoint
    Instrumentator().instrument(app).expose(app)
