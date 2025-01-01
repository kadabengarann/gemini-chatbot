FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Create and set permissions for the application directory
RUN mkdir -p $APP_HOME && \
    chown -R 1000:1000 $APP_HOME

# Set the working directory
WORKDIR $APP_HOME

# Switch to root user for system dependencies installation
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        gcc && \
    pip install --upgrade pip

# Copy requirements.txt and install Python dependencies
COPY --chown=1000:1000 requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY --chown=1000:1000 . .

# Switch back to non-root user
USER 1000:1000

# Expose the application port
EXPOSE 80

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--worker-class=gevent", "--worker-connections=1000", "--workers=3", "wsgi:app"]