# Stage 1: Install dependencies using uv
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY requirements.txt .

# Use uv to install into a custom directory
RUN /bin/uv pip install --system -r requirements.txt --target /install

# Stage 2: Final image
FROM python:3.11-slim

# Add /install/bin to PATH so CLI tools like uvicorn are found
ENV PATH="/install/bin:$PATH"
ENV PYTHONPATH="/install:$PYTHONPATH"

COPY --from=builder /install /install
COPY app/ /app/

WORKDIR /app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]