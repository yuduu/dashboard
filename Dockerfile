# Stage 1: Install dependencies using uv
FROM python:3.11-slim as builder

# Install uv
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app
COPY requirements.txt .

# Use uv to install into a custom directory
RUN /root/.cargo/bin/uv pip install --system -r requirements.txt --target /install

# Stage 2: Final image
FROM python:3.11-slim

# Set Python path to include /install
ENV PYTHONPATH="/install:$PYTHONPATH"

COPY --from=builder /install /install
COPY app/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
