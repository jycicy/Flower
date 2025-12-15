# 基础镜像：Python 3.12-slim（和你服务器Python版本一致，兼容所有依赖）
# slim 镜像体积小，适合生产环境，避免冗余
FROM python:3.12-slim

# 设置工作目录（容器内项目根目录，统一路径）
WORKDIR /app

# 安装系统依赖（适配 Ubuntu 24.04，解决 MySQL 客户端、编译依赖问题）
# 新增 libssl-dev：适配 Python 3.12 对 SSL 的依赖要求

RUN apt update && \
    apt install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖列表到容器（优先复制 requirements.txt，利用 Docker 缓存机制）
# 后续仅修改代码时，无需重新安装依赖，加速构建
COPY requirements.txt .

# 安装 Python 依赖（--no-cache-dir 避免缓存，--upgrade 确保 pip 是最新版）
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制整个项目到容器（.dockerignore 已排除无关文件，无需担心冗余）
COPY . .

# 收集静态资源（--noinput 自动确认，无需交互，适合容器构建）
# 静态资源会生成到 /app/static_collected（和 settings.py 中 STATIC_ROOT 一致）
RUN python manage.py collectstatic --noinput

# 暴露容器内部端口（和 Gunicorn 绑定端口一致，仅容器内通信）
EXPOSE 8000

# 容器启动命令（用 Gunicorn 启动 Django，适配 Python 3.12，添加性能优化参数）
# --workers 4：启动 4 个工作进程（建议 = 服务器 CPU 核心数 * 2 + 1，适配大部分云服务器）
# --timeout 60：超时时间 60 秒，避免长请求断开
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "flower.wsgi:application"]