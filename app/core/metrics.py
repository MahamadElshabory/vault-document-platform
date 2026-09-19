from prometheus_client import (Counter,Histogram,make_asgi_app,)


ingestion_duration = Histogram(
    "vault_ingestion_duration_seconds",
    "Time spent processing document ingestion jobs"
)

ingestion_failures = Counter(
    "vault_ingestion_failures_total",
    "Number of failed document ingestion jobs"
)

query_latency = Histogram(
    "vault_query_latency_seconds",
    "Time spent processing RAG queries"
)


metrics_app = make_asgi_app()