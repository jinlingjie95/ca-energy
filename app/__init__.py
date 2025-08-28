import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config
import os

def create_app(config_class=Config):
    """
    应用工厂函数，用于创建和配置 Flask 应用实例。
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 注册蓝图
    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api.ca.routes import bp as ca_api_bp
    app.register_blueprint(ca_api_bp, url_prefix='/api/ca')
    
    # 在这里可以继续注册其他地区的蓝图，例如:
    # from app.api.tx.routes import bp as tx_api_bp
    # app.register_blueprint(tx_api_bp, url_prefix='/api/tx')

    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 创建 RotatingFileHandler
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=1024 * 1024, backupCount=10
        )
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # 清除默认处理器并添加新的处理器
        app.logger.handlers.clear()
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用程序启动')
    
    # 如果在调试模式，使用默认的 Flask 日志记录器
    else:
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('应用程序在调试模式下启动')

    return app