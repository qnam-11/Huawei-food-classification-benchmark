FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# torch needs libgomp at runtime; slim images do not ship it
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch; versions match requirements.txt so pip does not reinstall CUDA wheels
RUN pip install --no-cache-dir \
    torch==2.8.0 torchvision==0.23.0 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects port 7860
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
