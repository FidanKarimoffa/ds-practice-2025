# # order_queue/Dockerfile

# # Start from a base Python image
# FROM python:3.9

# # Create a working directory
# WORKDIR /app
# COPY . /app/
# ENV PYTHONPATH=/app

# # Copy the requi rements if you have them (or just install grpc)
# # COPY requirements.txt /app/requirements.txt
# COPY ./order_queue/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt



# RUN pip install --no-cache-dir "grpcio>=1.71.0" "grpcio-tools>=1.71.0"

# # # Copy the proto files and app code
# # COPY order_queue.proto /app/
# # COPY order_queue_pb2.py /app/
# # COPY order_queue_pb2_grpc.py /app/
# # COPY app.py /app/

# RUN pip install --upgrade protobuf

# # Set the command to run the container
# CMD python utils/other/hotreload.py "order_queue/src/app.py"







# order_queue/Dockerfile
FROM python:3.9

WORKDIR /app

# Copy the entire ds-practice-2025-master repo into /app
COPY . /app/

# So Python can see /app/utils
ENV PYTHONPATH=/app/utils/pb

# Install dependencies
RUN pip install --no-cache-dir -r order_queue/requirements.txt
RUN pip install --no-cache-dir "grpcio>=1.71.0" "grpcio-tools>=1.71.0" protobuf

# Run the queue service
CMD ["python", "order_queue/src/app.py"]

