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