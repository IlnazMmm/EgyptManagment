import json
import logging
import os
import socket
import time
import uuid
from datetime import datetime, timezone
from urllib import request

from fastapi import Request


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "egypt-backend",
            "environment": os.getenv("APP_ENV", "local"),
            "host": socket.gethostname(),
        }

        if hasattr(record, "event_type"):
            payload["event_type"] = record.event_type
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "method"):
            payload["method"] = record.method
        if hasattr(record, "path"):
            payload["path"] = record.path
        if hasattr(record, "status_code"):
            payload["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            payload["client_ip"] = record.client_ip
        if hasattr(record, "frontend"):
            payload["frontend"] = record.frontend

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


class ElasticsearchHandler(logging.Handler):
    def __init__(self, base_url: str, index_prefix: str = "egypt-logs"):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.index_prefix = index_prefix

    def emit(self, record: logging.LogRecord) -> None:
        try:
            data = self.format(record)
            day = datetime.now(timezone.utc).strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{day}"
            req = request.Request(
                url=f"{self.base_url}/{index_name}/_doc",
                data=data.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            request.urlopen(req, timeout=0.5).read()
        except Exception:
            # Elasticsearch transport is best-effort: do not break request flow
            # and do not spam stderr with Python logging internal tracebacks.
            return


def setup_logging() -> None:
    logger = logging.getLogger("egypt")
    if logger.handlers:
        return

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = JsonFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    elastic_url = os.getenv("ELASTICSEARCH_URL")
    if elastic_url:
        elastic_handler = ElasticsearchHandler(elastic_url)
        elastic_handler.setLevel(logging.INFO)
        elastic_handler.setFormatter(formatter)
        logger.addHandler(elastic_handler)


def get_logger() -> logging.Logger:
    return logging.getLogger("egypt")


async def log_request(request: Request, call_next):
    logger = get_logger()
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "HTTP request",
            extra={
                "event_type": "backend.http",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "HTTP request failed",
            extra={
                "event_type": "backend.http.error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )
        raise
