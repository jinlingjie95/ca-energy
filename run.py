from app import create_app

app = create_app()

if __name__ == '__main__':
    # 使用 Flask 自带的服务器运行，仅用于开发环境
    # 生产环境请使用 Gunicorn
    app.run(port=5000, debug=True)