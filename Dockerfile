FROM python:3.9-slim

# 安裝 psycopg2 建置所需的系統依賴
RUN apt-get update && apt-get install -y gcc libpq-dev

WORKDIR /app

# 複製需求檔案並安裝 Python 相依套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製應用程式碼
COPY . .

CMD ["python", "main.py"]
