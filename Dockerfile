# Stage 1: Build image
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim

ENV PATH="/install/bin:$PATH"
COPY --from=builder /install /install
COPY app/ /app/

WORKDIR /app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
