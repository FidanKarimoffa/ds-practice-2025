# payment_service/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir grpcio grpcio-tools protobuf
CMD ["python", "server.py"]
