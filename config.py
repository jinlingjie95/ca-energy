import os

class Config:
    """基本配置类"""
    # 可以在这里添加更多配置，例如数据库URI等
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or "8f89d9738ad762c4a9bd1f30359ab8e5"
