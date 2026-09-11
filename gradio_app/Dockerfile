FROM python:3.13-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy main requirements (includes gradio via requirements-gradio.txt merge or separate install)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gradio separately to avoid polluting main requirements.txt
COPY gradio_app/requirements-gradio.txt ./gradio_app/
RUN pip install --no-cache-dir -r gradio_app/requirements-gradio.txt

# Copy Gradio app code
COPY gradio_app/ ./gradio_app/

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

CMD ["python", "gradio_app/app.py"]
