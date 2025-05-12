FROM python:3.11-slim

WORKDIR /app

# copy just what the executor needs
COPY utils    ./utils
COPY executor ./executor

# expose everything on the module path
ENV PYTHONPATH=/app:/app/utils:/app/utils/pb

RUN pip install --no-cache-dir -r executor/requirements.txt \
    && pip install --no-cache-dir "grpcio>=1.71.0" "grpcio-tools>=1.71.0" \
    && pip install --no-cache-dir --upgrade protobuf

CMD ["python", "utils/other/hotreload.py", "executor/src/app.py"]
