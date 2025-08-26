from flask import Flask, render_template, jsonify, request
import logging
from logging.handlers import RotatingFileHandler
import gridstatus
import pandas as pd

app = Flask(__name__)

caiso = gridstatus.CAISO()


if not app.debug:
    # 创建一个日志格式化器，定义日志信息的格式
    #    格式包含: 时间戳、日志等级、信息内容、以及发生错误的路径和行号
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # 创建一个 RotatingFileHandler
    #    - 'app.log': 日志文件的名称
    #    - maxBytes: 每个日志文件的最大大小 (这里是 1MB)
    #    - backupCount: 最多保留的备份文件数量
    file_handler = RotatingFileHandler(
        'app.log', maxBytes=1024 * 1024, backupCount=10
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用程序已在运行环境中启动')

else:
    # 设置等级为 DEBUG，以获得最详细的日志信息
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('应用程序已在测试环境中启动 (Debug Mode)')


# --------------------------------------------------------------------------

def get_realtime_load():
    """从 CAISO 获取最新的实时电力负荷数据。"""
    try:
        app.logger.debug("正在尝试获取实时电力负荷...")
        load_df = caiso.get_load(date='latest')
        
        if load_df is None or load_df.empty:
            app.logger.warning("未获取到实时电力负荷数据，API 可能暂无数据。")
            return {"error": "未获取到电力负荷数据，可能是API暂无数据。"}
            
        load_df['Time'] = pd.to_datetime(load_df['Time'])

        data_to_return = {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
        app.logger.info("成功获取并处理了实时电力负荷数据。")
        return data_to_return
        
    except Exception as e:
        # 使用 app.logger.error 来记录错误，exc_info=True 会自动附上完整的错误堆栈追踪
        app.logger.error(f"获取实时数据时发生错误: {e}", exc_info=True)
        return {"error": "服务器在获取实时数据时发生内部错误。"}

    
def get_history_load(date=None):
    """根据指定日期从 CAISO 获取历史电力负荷数据。"""
    try:
        if date is None:
            app.logger.warning("get_history_load 函数被调用，但缺少日期参数。")
            return {"error": "必须提供日期参数"}
        
        app.logger.debug(f"正在尝试获取日期为 {date} 的历史负荷数据...")
        load_df = caiso.get_load(date)
        
        if load_df is None or load_df.empty:
            app.logger.warning(f"无法获取日期为 {date} 的历史负荷数据。")
            return {"error": f"无法获取 {date} 的可用负荷数据"}
            
        load_df['Time'] = pd.to_datetime(load_df['Time'])
        data_to_return = {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
        app.logger.info(f"成功获取并处理了 {date} 的历史负荷数据。")
        return data_to_return
        
    except Exception as e:
        app.logger.error(f"获取历史数据 ({date}) 时发生错误: {e}", exc_info=True)
        return {"error": "服务器在获取历史数据时发生内部错误。"}

    
def get_load_forecast(date=None, option=None, area=None):
    """从 CAISO 获取电力负荷预测数据。"""
    try:
        if date is None or option is None:
            app.logger.warning(f"get_load_forecast 缺少必要参数: date={date}, option={option}")
            return {"error": "必须提供日期和预测选项参数"}
        
        app.logger.debug(f"正在获取预测数据: date={date}, option={option}...")
        
        if option == 'hourly':
            load_forecast_df = caiso.get_load_forecast_day_ahead(date)
        elif option == '5min':
            load_forecast_df = caiso.get_load_forecast_5_min(date)
        elif option == '15min':
            load_forecast_df = caiso.get_load_forecast_15_min(date)
        else:
            app.logger.error(f"无效的预测选项参数: {option}")
            return {"error": "无效的预测选项参数"}

        if load_forecast_df is None or load_forecast_df.empty:
            app.logger.warning(f"无可用的负荷预测数据: date={date}, option={option}")
            return {"error": "无可用的负荷预测数据"} 
        
        load_forecast_df["Time"] = load_forecast_df["Interval Start"]

        if area is None:
            load_forecast_df = load_forecast_df[load_forecast_df["TAC Area Name"] == "CA ISO-TAC"]
            load_forecast_df['Time'] = pd.to_datetime(load_forecast_df['Time'])
            data_to_return = {
                "time": load_forecast_df['Time'].dt.strftime('%H:%M').tolist(),
                "value": load_forecast_df['Load Forecast'].tolist()
            }
        
        app.logger.info(f"成功获取并处理了预测数据: date={date}, option={option}")
        return data_to_return
        
    except Exception as e:
        app.logger.error(f"获取预测数据 ({date}, {option}) 时发生错误: {e}", exc_info=True)
        return {"error": "服务器在获取预测数据时发生内部错误。"}


# --------------------------------------------------------------------------
# 路由 和 API 端点
# --------------------------------------------------------------------------

@app.route('/')
def index():
    """渲染主导航页面"""
    app.logger.info("访问了主页 (/)")
    return render_template('index.html')

@app.route('/power')
def power_page():
    """渲染电力数据可视化页面"""
    app.logger.info("访问了电力数据页面 (/power)")
    return render_template('power.html', title="CAISO 实时电力负荷")

@app.route('/api/realtime_load')
def api_realtime_load():
    """提供实时电力数据的API端点"""
    app.logger.info("API请求: /api/realtime_load")
    data = get_realtime_load()
    return jsonify(data)

@app.route('/api/history_load')
def api_history_load():
    """提供历史电力负荷数据的API端点"""
    date_param = request.args.get('date')
    app.logger.info(f"API请求: /api/history_load, 日期: {date_param}")
    if not date_param:
        return jsonify({"error": "必须提供日期参数"}), 400
    data = get_history_load(date_param)
    return jsonify(data)

@app.route('/api/load_forecast')
def api_load_forecast():
    """提供电力负荷预测数据的API端点"""
    date_param = request.args.get('date')
    option_param = request.args.get('option')
    app.logger.info(f"API请求: /api/load_forecast, 日期: {date_param}, 选项: {option_param}")
    data = get_load_forecast(date=date_param, option=option_param, area=None)
    return jsonify(data)

# --------------------------------------------------------------------------
# 应用程序执行入口
# --------------------------------------------------------------------------
if __name__ == '__main__':
    # 运行 Flask 应用
    # port=5000: 指定服务运行的端口
    # debug=True: 开启调试模式，这会让服务器在代码变更后自动重载，并提供更详细的错误页面
    app.run(port=5000, debug=True)