# 使用官方 Python 輕量版映像檔
FROM python:3.9-slim

# 禁止產生 .pyc 檔
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 設定工作目錄
WORKDIR /app

# 複製相依檔案並安裝相依套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製程式碼至容器中
COPY . .

# 暴露應用程式所使用的埠號
EXPOSE 5000

# 啟動應用程式
CMD ["python", "main.py"]
