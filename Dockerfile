# Dockerfile

# --- 阶段 1: 基础环境 ---
# 使用官方的 Python 3.10 精简版作为基础镜像
# slim 版本体积更小，适合部署
FROM python:3.10-slim

# --- 阶段 2: 配置环境 ---
# 在容器内创建一个工作目录
WORKDIR /app

# 设置环境变量
# FLASK_APP: 告诉 Flask 哪个文件是主应用
# FLASK_ENV: 设置为 production, 这会关闭调试模式，并触发我们代码中的文件日志记录
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
# 确保 Python 输出是无缓冲的，这对于日志记录很重要
ENV PYTHONUNBUFFERED=1

# --- 阶段 3: 安装依赖 ---
# 为了利用 Docker 的层缓存机制，先只复制依赖文件
# 这样如果只有代码变动，就不需要重新安装所有库，构建会更快
COPY requirements.txt .

# 在容器内运行 pip 命令，安装所有依赖
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# --- 阶段 4: 复制代码和设置 ---
# 将项目中的所有文件 (app.py, templates/ 文件夹等) 复制到容器的工作目录 /app 中
COPY . .

# --- 阶段 5: 暴露端口 ---
# 声明容器将会在 5000 端口上监听请求
# 这需要和 Gunicorn 启动时绑定的端口保持一致
EXPOSE 5000

# --- 阶段 6: 启动命令 ---
# 容器启动时要执行的命令
# 使用 Gunicorn 来启动应用
# --workers 3: 启动3个工作进程处理请求 (可根据服务器CPU核心数调整)
# --bind 0.0.0.0:5000: 监听所有网络接口的 5000 端口
# app:app: 第一个 app 指的是 app.py 文件，第二个 app 指的是 Flask 的实例对象 (app = Flask(__name__))
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]