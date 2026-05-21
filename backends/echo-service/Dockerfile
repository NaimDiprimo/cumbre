FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.32.0
RUN groupadd -r app && useradd -r -g app app
COPY main.py /app/main.py
RUN chown -R app:app /app
USER app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
