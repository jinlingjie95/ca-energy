# Dockerfile

# --- 阶段 1: 基础环境 ---
# 使用官方的 Python 3.10 精简版作为基础镜像
FROM python:3.10-slim

# --- 阶段 2: 配置环境 ---
WORKDIR /app

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
# 确保 Python 输出是无缓冲的，这对于日志记录很重要
ENV PYTHONUNBUFFERED=1

# --- 阶段 3: 安装依赖 ---
# 为了利用 Docker 的层缓存机制，先只复制依赖文件
COPY requirements.txt .
# 在容器内运行 pip 命令，安装所有依赖
RUN pip install --no-cache-dir -r requirements.txt

# --- 阶段 4: 复制代码 ---
# 将项目中的所有文件复制到容器的工作目录 /app 中
COPY . .

# --- 阶段 5: 暴露端口 ---
# 声明容器将会在 5000 端口上监听请求
EXPOSE 5000

# --- 阶段 6: 启动命令 ---
# 使用 Gunicorn 启动应用
# --workers 3: 启动3个工作进程
# --bind 0.0.0.0:5000: 监听所有网络接口的 5000 端口
# "run:app": 指的是 run.py 文件中的 app 实例
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "run:app"]