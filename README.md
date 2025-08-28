# CA Energy Data Platform

这是一个使用 Flask 和 GridStatus 构建的加州能源数据可视化平台。项目经过重构，采用了应用工厂和蓝图模式，具有良好的可扩展性。

## 项目结构

   /ca-energy-refactored/
   |-- app/
   |   |-- init.py             # 应用工厂
   |   |-- static/
   |   |-- templates/
   |   |-- main/                   # 主模块 (UI路由)
   |   -- api/                    # API模块 |       -- ca/                 # 加州API蓝图
   |
   |-- logs/                       # 日志文件夹
   |-- run.py                      # 应用启动脚本
   |-- config.py                   # 配置文件
   |-- requirements.txt
   |-- Dockerfile
   |-- README.md

## 安装与启动

1.  **克隆仓库**
    ```bash
    git clone <your-repo-url>
    cd ca-energy-refactored
    ```

2.  **创建虚拟环境并安装依赖**
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **运行应用 (开发模式)**
    ```bash
    python run.py
    ```
    应用将在 `http://127.0.0.1:5000` 上运行。

4.  **使用 Docker 运行 (生产模式)**
    ```bash
    # 构建 Docker 镜像
    docker build -t ca-energy-app .

    # 运行 Docker 容器
    docker run -p 5000:5000 ca-energy-app
    ```

## API 概览

所有与加州数据相关的 API 都在 `/api/ca/` 前缀下。

* `/api/ca/load/latest`: 获取最新负荷数据
* `/api/ca/load/today`: 获取今日负荷数据
* `/api/ca/load/history?date=YYYY-MM-DD`: 获取历史负荷数据
* ... 更多请参见 `app/api/ca/routes.py`