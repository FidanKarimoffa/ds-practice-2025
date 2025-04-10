# executor/Dockerfile

FROM python:3.9

# Set working directory in container
WORKDIR /app

# Copy the entire project into the container so that the directory structure is maintained
COPY . /app/

# Set PYTHONPATH so Python can find the 'bookstore' package under /app/utils/pb
ENV PYTHONPATH=/app/utils/pb

# Install dependencies (Assuming you have executor/requirements.txt)
RUN pip install --no-cache-dir -r executor/requirements.txt
RUN pip install --no-cache-dir "grpcio>=1.71.0" "grpcio-tools>=1.71.0"
RUN pip install --upgrade protobuf

# Run the executor service; if you use a hotreload script you can adjust accordingly
CMD python utils/other/hotreload.py "executor/src/app.py"
