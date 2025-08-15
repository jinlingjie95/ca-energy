from flask import Flask, render_template
import logging

# 导入蓝图
from lmp_api import lmp_api
from load_api import load_api
from storage_api import storage_api

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(lmp_api)
app.register_blueprint(load_api)
app.register_blueprint(storage_api)

logging.basicConfig(level=logging.INFO)

@app.route('/storage')
def storage_page():
    return render_template('storage.html')

@app.route('/load')
def load_page():
    return render_template('load.html')

@app.route('/lmp')
def lmp_page():
    return render_template('lmp.html')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)