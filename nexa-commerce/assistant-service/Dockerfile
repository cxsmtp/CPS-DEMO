# Nexa Commerce - shopping assistant (Python).
FROM python:3.12-slim

WORKDIR /srv/assistant
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src

RUN useradd --uid 10001 --create-home nexa
USER nexa

EXPOSE 8083
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8083/healthz')"
CMD ["python", "src/server.py"]
