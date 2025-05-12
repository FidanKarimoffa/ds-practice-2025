# books_db/Dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY src   ./src
COPY proto ./proto
# utils is still mounted via volumes in docker-compose
ENV PYTHONPATH=/app/src:/app/utils:/app/utils/pb  

RUN pip install --no-cache-dir grpcio grpcio-tools protobuf
CMD ["python", "-m", "src.app"]
