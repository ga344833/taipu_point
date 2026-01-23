FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 修正 entrypoint.sh 的行尾符號（Windows CRLF -> Linux LF）
RUN dos2unix entrypoint.sh || true

# 設定 entrypoint 執行權限
RUN chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8000

# 使用 entrypoint.sh 作為入口點
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
