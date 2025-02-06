FROM python:3.9-slim

WORKDIR /app

# 建立非 root 用戶
RUN useradd -m myuser && \
    chown -R myuser /app

# 複製 requirements 檔案
COPY app/requirements.txt .

# 建立並啟用虛擬環境
RUN python -m venv /app/venv && \
    chown -R myuser /app/venv
ENV PATH="/app/venv/bin:$PATH"

# 切換到非 root 用戶
USER myuser

# 更新 pip 並安裝相依套件
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY --chown=myuser app/ .

# 設定環境變數
ENV PORT=8080

# 使用 JSON 格式的 CMD
CMD ["gunicorn", "--bind", ":8080", "main:app"]