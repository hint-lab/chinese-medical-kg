FROM python:3.11-slim

LABEL maintainer="wang-hao@shu.edu.cn"
LABEL description="Chinese Medical KG API Service"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/ontology/data

# 暴露端口（FastAPI默认8000）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令（使用uvicorn）
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

