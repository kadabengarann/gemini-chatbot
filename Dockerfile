FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Adjust permissions
RUN chmod -R u+w /app/app/datasource

# Expose the application port
EXPOSE 7860

# Start the application with Gunicorn and Gevent
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--worker-class=gevent", "--worker-connections=1000", "--workers=3", "wsgi:app"]
