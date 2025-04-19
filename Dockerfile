FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
EXPOSE 8000
RUN chmod +x ./scripts/run.sh
ENTRYPOINT ["./scripts/run.sh"]
