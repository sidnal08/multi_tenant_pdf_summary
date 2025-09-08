FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
