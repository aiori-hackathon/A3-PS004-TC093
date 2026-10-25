# Use an official lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer outputs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory inside container
WORKDIR /app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy gateway proxy script
COPY gateway_proxy.py .

# Expose custom TLS gateway port
EXPOSE 8530

# Command to run the validating DNSSEC proxy daemon
CMD ["python", "gateway_proxy.py"]