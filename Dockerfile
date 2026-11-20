# Focus Log v1 — lean container image (stdlib only, no dependencies).
FROM python:3.12-slim
WORKDIR /app
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
