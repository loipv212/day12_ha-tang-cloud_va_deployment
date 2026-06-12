# Base image
FROM python:3.11

# Thư mục làm việc trong container
WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY 02-docker/develop/requirements.txt .

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY 02-docker/develop/app.py .

# Copy utils
COPY utils ./utils

# Expose port
EXPOSE 8000

# Run app
CMD ["python", "app.py"]