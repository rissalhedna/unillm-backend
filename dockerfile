# Stage 1: Build
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# # Stage 2: Runtime
# FROM python:3.11-slim

# WORKDIR /app

# COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
# COPY --from=build /usr/local/bin/ /usr/local/bin/
# COPY --from=build /app /app

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
