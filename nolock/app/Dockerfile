# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY app.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables (these will be overridden in OpenShift)
ENV SERVICE_URL=""
ENV DB_PASSWORD=""
ENV REDIS_HOST="localhost"
ENV REDIS_PORT=6379
ENV REDIS_DB=0

# Run the application
CMD ["python", "app.py"]
