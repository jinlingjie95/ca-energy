from flask import render_template
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    """渲染主导航页面"""
    return render_template('index.html')

@bp.route('/ca')
def ca_page():
    """渲染加州电力数据可视化页面"""
    return render_template('ca.html')

@bp.route('/weather')
def weather_page():
    """渲染美国天气数据查看平台页面"""
    return render_template('weather.html', title='天气查询')

@bp.route('/fire')
def fire_page():
    """渲染山火信息地图页面"""
    return render_template('fire.html', title='山火信息')