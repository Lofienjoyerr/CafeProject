FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
RUN chmod +x ./scripts/run.sh
CMD ["./scripts/run.sh"]
