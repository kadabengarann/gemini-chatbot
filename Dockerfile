FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Create and set permissions for the application directory
RUN mkdir -p $APP_HOME && \
    chown -R 1000:1000 $APP_HOME

# Switch to a non-root user for security
USER 1000:1000

# Set the working directory
WORKDIR $APP_HOME

# Copy only requirements.txt to leverage Docker cache
COPY --chown=1000:1000 requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        gcc && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY --chown=1000:1000 . .

# Expose the application port
EXPOSE 7860

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--worker-class=gevent", "--worker-connections=1000", "--workers=3", "wsgi:app"]