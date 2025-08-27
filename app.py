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
# 获取电力负荷数据的函数
# --------------------------------------------------------------------------

def get_realtime_load():
    """从 CAISO 获取当天至今的实时电力负荷数据序列。"""
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
        app.logger.error(f"获取实时数据时发生错误: {e}", exc_info=True)
        return {"error": "服务器在获取实时数据时发生内部错误。"}
    
def get_realtime_load_latest_data():
    """从 CAISO 获取最新的一个实时电力负荷数据点。"""
    try:
        app.logger.debug("正在尝试获取实时电力负荷...")
        load_df = caiso.get_load(date='latest')
        
        if load_df is None or load_df.empty:
            app.logger.warning("未获取到实时电力负荷数据，API 可能暂无数据。")
            return {"error": "未获取到电力负荷数据，可能是API暂无数据。"}
            
        # 从数据表中提取最后一行，即最新的数据点
        latest_record = load_df.iloc[-1]
        
        # 将时间转换为 datetime 对象
        latest_time = pd.to_datetime(latest_record['Time'])
        # 获取负荷值
        latest_load = latest_record['Load']

        data_to_return = {
            "time": latest_time.strftime('%H:%M'),
            "value": float(latest_load) # 转换为 float 类型以确保 JSON 兼容性
        }
        
        app.logger.info(f"成功获取最新的实时数据点: 时间 {data_to_return['time']}, 负荷 {data_to_return['value']}")
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
# 获取储能数据的函数
# --------------------------------------------------------------------------

def get_latest_storage_point():
    """获取最新的单个储能数据点。"""
    try:
        app.logger.debug("正在获取最新的单个储能数据点...")
        # 'latest' 参数返回一个包含最新数据的字典
        storage_dict = caiso.get_storage(date='latest')
        
        if not isinstance(storage_dict, dict) or not storage_dict:
            app.logger.warning("未获取到最新的单个储能数据点。")
            return {"error": "无可用储能数据"}
        
        # 从字典中提取时间和供应值
        dt = pd.to_datetime(storage_dict['time']).strftime('%H:%M')
        value = storage_dict['supply']
        data_to_return = {
            "time": dt,
            "value": value
        }
        app.logger.info(f"成功获取最新储能数据点: 时间 {dt}, 供应 {value}")
        return data_to_return
    except Exception as e:
        app.logger.error(f"获取最新储能数据点时出错: {e}", exc_info=True)
        return {"error": str(e)}

def get_realtime_storage():
    """获取当天至今的储能数据序列，用于实时图表。"""
    try:
        app.logger.debug("正在获取今日储能数据序列...")
        # 获取当天的数据需要传入一个日期对象
        storage_df  = caiso.get_storage(date=pd.Timestamp.now(tz=gridstatus.CAISO.default_timezone).date())
        if storage_df is None or storage_df.empty:
            app.logger.warning("未获取到今日储能数据序列。")
            return {"error": "无可用储能数据"}
        
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        data_to_return = {
            "time": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": storage_df['Supply'].tolist()
        }
        app.logger.info("成功获取今日储能数据序列。")
        return data_to_return
    except Exception as e:
        app.logger.error(f"获取今日储能数据序列时出错: {e}", exc_info=True)
        return {"error": str(e)}

def get_history_storage(date=None):
    """根据指定日期获取历史储能数据。"""
    try:
        if date is None:
            app.logger.warning("get_history_storage 缺少日期参数。")
            return {"error": "必须提供日期参数"}
        
        app.logger.debug(f"正在获取 {date} 的历史储能数据...")
        storage_df = caiso.get_storage(date)
        if storage_df is None or storage_df.empty:
            app.logger.warning(f"未找到 {date} 的储能数据。")
            return {"error": "该日期无可用储能数据"}
        
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        data_to_return = {
            "time": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": storage_df['Supply'].tolist()
        }
        app.logger.info(f"成功获取 {date} 的历史储能数据。")
        return data_to_return
    except Exception as e:
        app.logger.error(f"获取历史储能数据 ({date}) 时出错: {e}", exc_info=True)
        return {"error": str(e)}
    
# --------------------------------------------------------------------------
# 获取实时电价的函数
# --------------------------------------------------------------------------

def get_main_traiding_hub_locations():
    """获取主要交易中心的地点列表。"""
    try:
        app.logger.debug("正在获取主要交易中心地点列表...")
        locations = caiso.trading_hub_locations
        if not locations:
            app.logger.warning("未获取到任何交易中心地点。")
            return {"error": "No trading hub locations available"}
        
        app.logger.info(f"成功获取了 {len(locations)} 个交易中心地点。")
        return {"locations": locations}
    except Exception as e:
        app.logger.error(f"获取交易中心地点时出错: {e}", exc_info=True)
        return {"error": str(e)}

def get_main_traiding_hub_latest_lmp_point(market=None, location=None):
    """
    获取指定市场和地点的最新电价数据点。
    locations: e.g. ['TH_NP15_GEN-APND']
    market : gridstatus.Markets.DAY_AHEAD_HOURLY or gridstatus.Markets.REAL_TIME_5_MIN
    """
    try:
        if market is None or location is None:
            app.logger.warning("get_main_traiding_hub_latest_lmp_point 缺少必要参数: market 或 location")
            return {"error": "必须提供 market 和 location 参数"}
        
        lmp_df = caiso.get_lmp(date='latest', market=market, locations=[location])
        if lmp_df is None or lmp_df.empty:
            app.logger.warning("未获取到最新的单个电价数据点。")
            return {"error": "No LMP data available"}
        
        # 获取最后一条记录，即最新的数据点
        latest_record = lmp_df.iloc[-1]
        dt = pd.to_datetime(latest_record['Time']).strftime('%H:%M')
        value = latest_record['LMP']
        
        app.logger.info(f"成功获取最新电价数据点: 时间 {dt}, 电价 {value}")
        return { "time": dt, "value": float(value) }
    except Exception as e:
        app.logger.error(f"获取最新电价数据点时出错: {e}", exc_info=True)
        return {"error": str(e)}
    
def get_main_traiding_hub_history_lmp(date=None, market=None, location=None):
    """
    根据指定日期和市场获取指定主干电网的历史电价数据。
    market : gridstatus.Markets.DAY_AHEAD_HOURLY or gridstatus.Markets.REAL_TIME_5_MIN
    """
    try:
        if date is None or market is None:
            app.logger.warning("get_main_traiding_hub_history_lmp 缺少必要参数: date 或 market")
            return {"error": "必须提供日期和市场参数"}
        
        if location not in caiso.trading_hub_locations:
            app.logger.warning(f"无效的地点参数: {location} 不在交易中心列表中。")
            return {"error": "无效的地点参数"}
        
        app.logger.debug(f"正在获取 {date} 的 {location} 电价数据, market: {market}...")
        lmp_df = caiso.get_lmp(date, market=market, locations=[location])
        
        if lmp_df is None or lmp_df.empty:
            app.logger.warning(f"在 {date} 未找到 {location} 的电价数据。")
            return {"error": "No LMP data available"}
        
        # 转换时间格式
        lmp_df['Time'] = pd.to_datetime(lmp_df['Time'])
        lmp_df['time_str'] = lmp_df['Time'].dt.strftime('%H:%M')

        data_to_return = {
            location: {
                "time": lmp_df['time_str'].tolist(),
                "value": lmp_df['LMP'].tolist()
            }
        }
            
        app.logger.info(f"成功获取了 {location} 的历史电价数据。")
        return data_to_return
        
    except Exception as e:
        app.logger.error(f"获取历史电价数据 ({date}, {location}) 时出错: {e}", exc_info=True)
        return {"error": str(e)}


def get_all_apnode_history_lmp(date=None, market=None):
    """
    根据指定日期和市场获取所有 AP Nodes 的历史电价数据，并按节点分类。
    market : gridstatus.Markets.DAY_AHEAD_HOURLY or gridstatus.Markets.REAL_TIME_5_MIN
    """
    try:
        if date is None or market is None:
            app.logger.warning("get_all_apnode_history_lmp 缺少必要参数: date 或 market")
            return {"error": "必须提供日期和市场参数"}
        
        app.logger.debug(f"正在获取 {date} 的所有 AP Nodes 电价数据, market: {market}...")
        lmp_df = caiso.get_lmp(date, market=market, locations="ALL_AP_NODES")
        
        if lmp_df is None or lmp_df.empty:
            app.logger.warning(f"在 {date} 未找到任何 AP Node 的电价数据。")
            return {"error": "No LMP data available"}
        
        # 转换时间格式
        lmp_df['Time'] = pd.to_datetime(lmp_df['Time'])
        lmp_df['time_str'] = lmp_df['Time'].dt.strftime('%H:%M')
        
        # 使用 pandas 的 groupby 方法按 'Location' 分组并构建所需的字典结构
        grouped = lmp_df.groupby('Location')
        data_to_return = {}
        
        for location_name, group_df in grouped:
            # 对每个分组的数据进行排序，确保时间序列是正确的
            sorted_group = group_df.sort_values(by='Time')
            data_to_return[location_name] = {
                "time": sorted_group['time_str'].tolist(),
                "value": sorted_group['LMP'].tolist()
            }
            
        app.logger.info(f"成功处理了 {len(data_to_return)} 个节点的历史电价数据。")
        return data_to_return
        
    except Exception as e:
        app.logger.error(f"获取所有 AP Nodes 历史电价时出错: {e}", exc_info=True)
        return {"error": str(e)}

# --------------------------------------------------------------------------
# 太阳能和风能
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# 功能函数
# --------------------------------------------------------------------------

def get_market_enum(market_str):
    if market_str == 'day_ahead_hourly': return gridstatus.Markets.DAY_AHEAD_HOURLY
    if market_str == 'real_time_5_min': return gridstatus.Markets.REAL_TIME_5_MIN
    return None


# --------------------------------------------------------------------------
# 路由 和 API 端点
# --------------------------------------------------------------------------

@app.route('/')
def index():
    """渲染主导航页面"""
    app.logger.info("访问了主页 (/)")
    return render_template('index.html')

@app.route('/ca')
def ca_page():
    """渲染加州电力数据可视化页面"""
    app.logger.info("访问了加州电力数据页面 (/ca)")
    return render_template('ca.html')

# --------------------------------------------------------------------------
# 负荷数据 API
# --------------------------------------------------------------------------
@app.route('/api/load/realtime')
def api_realtime_load():
    """提供当天至今的实时电力负荷数据序列的API端点"""
    app.logger.info("API请求: /api/load/realtime")
    data = get_realtime_load()
    return jsonify(data)

@app.route('/api/load/latest_point')
def api_realtime_load_latest():
    """提供最新的单个电力负荷数据点的API端点"""
    app.logger.info("API请求: /api/load/latest_point")
    data = get_realtime_load_latest_data()
    return jsonify(data)

@app.route('/api/load/history')
def api_history_load():
    """提供历史电力负荷数据的API端点"""
    date_param = request.args.get('date')
    app.logger.info(f"API请求: /api/load/history, 日期: {date_param}")
    if not date_param:
        return jsonify({"error": "必须提供日期参数"}), 400
    data = get_history_load(date_param)
    return jsonify(data)

@app.route('/api/load/forecast')
def api_load_forecast():
    """提供电力负荷预测数据的API端点"""
    date_param = request.args.get('date')
    option_param = request.args.get('option')
    app.logger.info(f"API请求: /api/load/forecast, 日期: {date_param}, 选项: {option_param}")
    data = get_load_forecast(date=date_param, option=option_param, area=None)
    return jsonify(data)

# --------------------------------------------------------------------------
# 储能数据 API
# --------------------------------------------------------------------------
@app.route('/api/storage/realtime')
def api_realtime_storage():
    """提供当天至今的储能数据序列的API端点"""
    app.logger.info("API请求: /api/storage/realtime")
    data = get_realtime_storage()
    return jsonify(data)

@app.route('/api/storage/latest_point')
def api_latest_storage_point():
    """提供最新的单个储能数据点的API端点"""
    app.logger.info("API请求: /api/storage/latest_point")
    data = get_latest_storage_point()
    return jsonify(data)

@app.route('/api/storage/history')
def api_history_storage():
    """提供历史储能数据的API端点"""
    date_param = request.args.get('date')
    app.logger.info(f"API请求: /api/storage/history, 日期: {date_param}")
    if not date_param:
        return jsonify({"error": "必须提供日期参数"}), 400
    data = get_history_storage(date_param)
    return jsonify(data)

# --------------------------------------------------------------------------
# 电价数据 API
# --------------------------------------------------------------------------
@app.route('/api/locations/trading_hubs')
def api_get_trading_hub_locations():
    return jsonify(get_main_traiding_hub_locations())

# --- 主干电网最新电价 API ---
@app.route('/api/lmp/latest/trading_hubs')
def api_latest_trading_hubs_lmp():
    """获取所有主干电网的最新实时电价。"""
    locations_data = get_main_traiding_hub_locations()

    if "error" in locations_data:
        return jsonify(locations_data), 500

    all_latest_data = {}
    for loc in locations_data.get("locations", []):
        all_latest_data[loc] = {
            "day_ahead_hourly": get_main_traiding_hub_latest_lmp_point(market=gridstatus.Markets.DAY_AHEAD_HOURLY, location=loc),
            "real_time_5_min": get_main_traiding_hub_latest_lmp_point(market=gridstatus.Markets.REAL_TIME_5_MIN, location=loc)
        }
    return jsonify({"locations": all_latest_data})

# --- 主干电网历史电价 API ---
@app.route('/api/lmp/history/trading_hubs')
def api_history_trading_hubs_lmp():
    date_param = request.args.get('date')
    market_str = request.args.get('market')
    locations_str = request.args.get('locations') # locations=HUB1,HUB2,HUB3
    if not all([date_param, market_str, locations_str]):
        return jsonify({"error": "必须提供 date, market 和 locations 参数"}), 400
    
    market_enum = get_market_enum(market_str)
    if market_enum is None: return jsonify({"error": "无效的 market 参数"}), 400
    
    if locations_str is not None:
        locations = locations_str.split(',')

    all_data = {}
    for loc in locations:
        data = get_main_traiding_hub_history_lmp(date=date_param, market=market_enum, location=loc)
        if "error" in data:
            # 如果单个查询失败，可以记录日志并继续
            app.logger.error(f"查询主干电网数据失败: {loc}, 错误: {data['error']}")
            continue
        all_data.update(data)
        
    return jsonify(all_data)

# --- 地区历史电价数据 API ---
@app.route('/api/lmp/history/all_nodes')
def api_history_all_nodes_lmp():
    """提供所有节点历史电价数据的API端点"""
    date_param = request.args.get('date')
    market_str = request.args.get('market')
    app.logger.info(f"API请求: /api/lmp/history/all_nodes, date: {date_param}, market: {market_str}")
    if not date_param or not market_str:
        return jsonify({"error": "必须提供 date 和 market 参数"}), 400
    
    market_enum = None
    if market_str == 'day_ahead_hourly': market_enum = gridstatus.Markets.DAY_AHEAD_HOURLY
    elif market_str == 'real_time_5_min': market_enum = gridstatus.Markets.REAL_TIME_5_MIN
    else: return jsonify({"error": "无效的 market 参数"}), 400

    data = get_all_apnode_history_lmp(date=date_param, market=market_enum)
    return jsonify(data)

# --------------------------------------------------------------------------
# 应用程序执行入口
# --------------------------------------------------------------------------
if __name__ == '__main__':
    # 运行 Flask 应用
    # port=5000: 指定服务运行的端口
    # debug=True: 开启调试模式，这会让服务器在代码变更后自动重载，并提供更详细的错误页面
    app.run(port=5000, debug=True)