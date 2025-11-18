# Docker 部署指南

## 🐳 快速部署

### 方式1: 使用 docker-compose（推荐）

```bash
# 1. 确保数据库已准备好
python scripts/migrate_to_sqlite.py

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 访问API
# http://localhost:8000/docs
```

### 方式2: 国内用户加速部署（推荐）⚡

```bash
# 使用国内优化版（构建速度提升5-10倍）
docker-compose -f docker-compose.cn.yml up -d
```

**优势**:
- ✅ 使用阿里云Debian镜像源（apt-get加速）
- ✅ 使用清华pip镜像源（Python包加速）
- ✅ 构建速度提升5-10倍

### 方式3: 直接使用 Docker

```bash
# 1. 构建镜像
docker build -t chinese-medical-kg:latest .

# 2. 运行容器
docker run -d \
  --name chinese-medical-kg-api \
  -p 8000:8000 \
  -v $(pwd)/ontology/data:/app/ontology/data \
  chinese-medical-kg:latest

# 3. 查看日志
docker logs -f chinese-medical-kg-api
```

### 方式4: 生产环境部署

```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

---

## ⚡ 国内加速配置

### 方案1: 使用国内优化版Dockerfile（推荐）⭐⭐⭐

```bash
# 使用国内优化版构建
docker build -f Dockerfile.cn -t chinese-medical-kg:latest .

# 或使用docker-compose
docker-compose -f docker-compose.cn.yml up -d
```

**优势**:
- ✅ 使用阿里云Debian镜像源（apt-get加速）
- ✅ 使用清华pip镜像源（Python包加速）
- ✅ 构建速度提升5-10倍

### 方案2: 配置Docker镜像加速器

#### 配置Docker daemon（推荐）

编辑 `/etc/docker/daemon.json`（Linux）或 Docker Desktop 设置：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

然后重启Docker：
```bash
sudo systemctl restart docker  # Linux
# 或重启Docker Desktop
```

#### 国内Docker镜像源列表

| 镜像源 | 地址 | 说明 |
|--------|------|------|
| 中科大 | https://docker.mirrors.ustc.edu.cn | 推荐 |
| 网易 | https://hub-mirror.c.163.com | 稳定 |
| 百度云 | https://mirror.baidubce.com | 速度快 |
| 阿里云 | 需要登录获取 | 个人专属 |

### 方案3: 使用国内pip镜像源

#### 方法1: 在Dockerfile中配置（已配置）

Dockerfile中已自动配置清华源：
```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 方法2: 构建时指定

```bash
docker build \
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
  -t chinese-medical-kg .
```

#### 国内pip镜像源列表

| 镜像源 | 地址 | 速度 |
|--------|------|------|
| 清华 | https://pypi.tuna.tsinghua.edu.cn/simple | ⭐⭐⭐⭐⭐ |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ | ⭐⭐⭐⭐ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ | ⭐⭐⭐⭐ |
| 豆瓣 | https://pypi.douban.com/simple/ | ⭐⭐⭐ |

### 方案4: 使用国内apt-get镜像源

Dockerfile中已自动配置阿里云Debian镜像源。

如果需要手动配置，编辑Dockerfile：
```dockerfile
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
```

### 📊 速度对比

| 操作 | 国外源 | 国内源 | 提升 |
|------|--------|--------|------|
| 拉取基础镜像 | 2-5分钟 | 10-30秒 | **5-10x** |
| apt-get更新 | 1-2分钟 | 5-10秒 | **10-20x** |
| pip安装依赖 | 3-10分钟 | 30秒-2分钟 | **5-10x** |
| **总构建时间** | **10-20分钟** | **2-5分钟** | **5-10x** |

### 🔧 完整配置示例

#### 1. 配置Docker镜像加速器

```bash
# Linux
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
sudo systemctl restart docker

# macOS/Windows: Docker Desktop -> Settings -> Docker Engine
```

#### 2. 使用国内优化版构建

```bash
# 方式1: 使用docker-compose（推荐）
docker-compose -f docker-compose.cn.yml build
docker-compose -f docker-compose.cn.yml up -d

# 方式2: 直接构建
docker build -f Dockerfile.cn -t chinese-medical-kg .
docker run -d -p 8000:8000 \
  -v $(pwd)/ontology/data:/app/ontology/data \
  chinese-medical-kg
```

#### 3. 验证加速效果

```bash
# 查看构建时间
time docker build -f Dockerfile.cn -t chinese-medical-kg .

# 查看镜像源配置
docker info | grep -A 10 "Registry Mirrors"
```

---

## 📋 前置条件

### 1. 准备数据库文件

在构建镜像前，需要先创建SQLite数据库：

```bash
# 迁移数据到SQLite
python scripts/migrate_to_sqlite.py
```

这会生成 `ontology/data/medical_kg.db` 文件。

### 2. 检查文件

```bash
# 确认数据库文件存在
ls -lh ontology/data/medical_kg.db

# 应该看到类似输出：
# -rw-r--r-- 1 user user 41M Nov 18 15:47 ontology/data/medical_kg.db
```

---

## 🚀 部署步骤

### 步骤1: 克隆项目

```bash
git clone <your-repo-url>
cd chinese-medical-kg
```

### 步骤2: 准备数据

```bash
# 安装依赖（本地）
pip install -r requirements.txt

# 迁移数据到SQLite
python scripts/migrate_to_sqlite.py
```

### 步骤3: 构建和启动

```bash
# 使用docker-compose（国内用户推荐使用.cn版本）
docker-compose -f docker-compose.cn.yml up -d

# 或标准版本
docker-compose up -d

# 或手动构建
docker build -f Dockerfile.cn -t chinese-medical-kg .
docker run -d -p 8000:8000 \
  -v $(pwd)/ontology/data:/app/ontology/data \
  chinese-medical-kg
```

### 步骤4: 验证部署

```bash
# 检查容器状态
docker ps

# 测试API
curl http://localhost:8000/

# 访问API文档
# 浏览器打开: http://localhost:8000/docs
```

---

## 🔧 配置说明

### 端口配置

- **默认端口**: 8000
- **修改端口**: 编辑 `docker-compose.yml` 中的端口映射

```yaml
ports:
  - "9000:8000"  # 外部端口:容器端口
```

### 数据持久化

数据库文件通过 volume 挂载，确保数据持久化：

```yaml
volumes:
  - ./ontology/data:/app/ontology/data
```

### 环境变量

可以通过环境变量配置：

```yaml
environment:
  - PYTHONUNBUFFERED=1
  # 可以添加其他环境变量
```

---

## 📊 健康检查

容器包含健康检查，可以通过以下命令查看：

```bash
# 查看健康状态
docker ps

# 查看详细健康信息
docker inspect chinese-medical-kg-api | grep -A 10 Health
```

---

## 🛠️ 常用命令

### 启动和停止

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

### 更新服务

```bash
# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d --force-recreate
```

### 进入容器

```bash
# 进入运行中的容器
docker exec -it chinese-medical-kg-api bash

# 在容器内测试
python -c "from ontology.db_loader import MedicalKnowledgeGraphDB; db = MedicalKnowledgeGraphDB(); print(db.get_statistics())"
```

---

## 🐛 故障排除

### 问题1: 数据库文件不存在

**错误**: `FileNotFoundError: 数据库不存在`

**解决**:
```bash
# 在本地先迁移数据
python scripts/migrate_to_sqlite.py

# 确认文件存在
ls -lh ontology/data/medical_kg.db
```

### 问题2: 端口被占用

**错误**: `port is already allocated`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 或修改docker-compose.yml中的端口
ports:
  - "8001:8000"  # 使用其他端口
```

### 问题3: 容器无法启动

**检查日志**:
```bash
docker-compose logs api
```

**常见原因**:
- 数据库文件路径错误
- 依赖安装失败
- 端口冲突

### 问题4: API返回404

**检查**:
```bash
# 进入容器检查数据库
docker exec -it chinese-medical-kg-api bash
ls -lh /app/ontology/data/medical_kg.db

# 测试数据库连接
python -c "from ontology.db_loader import MedicalKnowledgeGraphDB; db = MedicalKnowledgeGraphDB(); print('OK')"
```

### 问题5: 构建速度慢（国内用户）

**解决**: 
1. 使用国内优化版：`docker-compose -f docker-compose.cn.yml build`
2. 配置Docker镜像加速器（见上方"国内加速配置"章节）
3. 检查网络连接

### 问题6: 镜像源不可用

**解决**: 切换到备用镜像源

```dockerfile
# 在Dockerfile.cn中切换pip源
# 从清华源切换到阿里云源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com
```

### 问题7: 构建时pip安装失败

**解决**: 
1. 检查网络连接
2. 切换到备用镜像源
3. 使用代理（如果可用）

---

## 📦 生产环境建议

### 1. 使用生产配置

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 使用反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 使用 HTTPS

配置SSL证书，通过Nginx或Traefik等反向代理。

### 4. 监控和日志

```bash
# 使用docker logs
docker-compose logs -f --tail=100

# 或集成到日志系统（如ELK、Loki等）
```

---

## 🔐 安全建议

1. **只读挂载数据库**（生产环境）:
   ```yaml
   volumes:
     - ./ontology/data:/app/ontology/data:ro
   ```

2. **限制资源使用**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

3. **使用非root用户**（可选）:
   在Dockerfile中添加：
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

---

## 📝 示例：完整部署流程

### 标准部署

```bash
# 1. 克隆项目
git clone <repo-url>
cd chinese-medical-kg

# 2. 准备数据（本地）
pip install -r requirements.txt
python scripts/migrate_to_sqlite.py

# 3. 构建和启动
docker-compose up -d

# 4. 等待服务启动（约10-20秒）
sleep 20

# 5. 测试API
curl http://localhost:8000/api/statistics

# 6. 访问文档
# 浏览器: http://localhost:8000/docs
```

### 国内用户快速部署（推荐）⚡

```bash
# 1. 配置Docker镜像加速器（一次性）
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
sudo systemctl restart docker

# 2. 克隆项目
git clone <repo-url>
cd chinese-medical-kg

# 3. 准备数据
pip install -r requirements.txt
python scripts/migrate_to_sqlite.py

# 4. 使用国内优化版构建（速度快5-10倍）
docker-compose -f docker-compose.cn.yml build
docker-compose -f docker-compose.cn.yml up -d

# 5. 查看日志
docker-compose -f docker-compose.cn.yml logs -f
```

---

## 💡 最佳实践

1. **国内用户**: 使用 `docker-compose.cn.yml` 和 `Dockerfile.cn`，构建速度提升5-10倍
2. **配置Docker镜像加速器**: 加速基础镜像拉取
3. **生产环境**: 使用 `docker-compose.prod.yml` 配置
4. **定期更新镜像源**: 确保使用最新最快的源
5. **数据备份**: 定期备份 `ontology/data/medical_kg.db` 文件

---

## 🔗 相关文档

- [README.md](../README.md) - 项目主文档
- [docs/API.md](../docs/API.md) - API使用文档
