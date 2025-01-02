FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Create and set permissions for the application directory
RUN mkdir -p $APP_HOME && \
    chown -R 1000:1000 $APP_HOME

# Switch to root user for system dependencies installation
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        gcc \
        git && \
    pip install --upgrade pip

# Switch to app directory
WORKDIR $APP_HOME

# Clone the application repository
RUN git clone https://github.com/kadabengarann/gemini-chatbot.git $APP_HOME
RUN ls $APP_HOME

# Adjust ownership of cloned files
RUN chown -R 1000:1000 $APP_HOME

# Switch to non-root user
USER 1000:1000

# Install Python dependencies with user flag
RUN pip install --no-cache-dir --prefix=$APP_HOME/.local -r requirements.txt

# Add ~/.local/bin to the PATH
ENV PATH=$PATH:$APP_HOME/.local/bin
ENV PYTHONPATH=$PYTHONPATH:$APP_HOME/.local/lib/python3.11/site-packages

# Verify Gunicorn installation
RUN which gunicorn
RUN python -c "import gunicorn; print('Gunicorn module found!')"

# Expose the application port
EXPOSE 7860

# Pull the latest changes on container start
CMD cd $APP_HOME && git pull origin master && \
    gunicorn --bind 0.0.0.0:7860 --worker-class=gevent --worker-connections=1000 --workers=3 wsgi:app