from flask import jsonify, request, current_app
from app.api.ca import bp
from app.api.ca import data_fetcher

# --- 负荷数据 API (Load API) ---

@bp.route('/load/latest', methods=['GET'])
def api_latest_load():
    """API: 获取最新的电力负荷数据点"""
    current_app.logger.info("API request: /api/ca/load/latest")
    data = data_fetcher.get_latest_load()
    return jsonify(data)

@bp.route('/load/today', methods=['GET'])
def api_today_load():
    """API: 获取当日至今的电力负荷数据序列"""
    current_app.logger.info("API request: /api/ca/load/today")
    data = data_fetcher.get_today_load()
    return jsonify(data)

@bp.route('/load/history', methods=['GET'])
def api_history_load():
    """API: 获取历史电力负荷数据"""
    date = request.args.get('date')
    current_app.logger.info(f"API request: /api/ca/load/history?date={date}")
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    data = data_fetcher.get_history_load(date)
    return jsonify(data)

@bp.route('/load/forecast', methods=['GET'])
def api_load_forecast():
    """API: 获取电力负aho预测数据"""
    date = request.args.get('date')
    option = request.args.get('option')
    current_app.logger.info(f"API request: /api/ca/load/forecast?date={date}&option={option}")
    if not date or not option:
        return jsonify({"error": "Date and option parameters are required"}), 400
    data = data_fetcher.get_load_forecast(date, option)
    return jsonify(data)

@bp.route('/load/forecast/today', methods=['GET'])
def api_load_forecast_today():
    """API: 获取今日日前负荷预测数据"""
    current_app.logger.info(f"API request: /api/ca/load/forecast/today")
    # 直接调用 data_fetcher 获取今天的 'hourly' 预测
    data = data_fetcher.get_load_forecast('today', 'hourly')
    return jsonify(data)

# --- 储能数据 API (Storage API) ---

@bp.route('/storage/latest', methods=['GET'])
def api_latest_storage():
    """API: 获取最新的储能数据点"""
    current_app.logger.info("API request: /api/ca/storage/latest")
    data = data_fetcher.get_latest_storage()
    return jsonify(data)

@bp.route('/storage/today', methods=['GET'])
def api_today_storage():
    """API: 获取当天的储能数据序列"""
    current_app.logger.info("API request: /api/ca/storage/today")
    data = data_fetcher.get_today_storage()
    return jsonify(data)

@bp.route('/storage/history', methods=['GET'])
def api_history_storage():
    """API: 获取历史储能数据"""
    date = request.args.get('date')
    current_app.logger.info(f"API request: /api/ca/storage/history?date={date}")
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    data = data_fetcher.get_history_storage(date)
    return jsonify(data)

# --- 电价数据 API (LMP API) ---

@bp.route('/locations/trading_hubs', methods=['GET'])
def api_get_trading_hub_locations():
    """API: 获取交易中心地点列表"""
    current_app.logger.info("API request: /api/ca/locations/trading_hubs")
    data = data_fetcher.get_trading_hub_locations()
    return jsonify(data)

@bp.route('/lmp/trading_hubs/latest', methods=['GET'])
def api_latest_trading_hubs_lmp():
    """API: 获取所有主干电网的最新电价"""
    current_app.logger.info("API request: /api/ca/lmp/trading_hubs/latest")
    data = data_fetcher.get_trading_hub_latest_lmp()
    return jsonify(data)

@bp.route('/lmp/trading_hubs/today', methods=['GET'])
def api_today_trading_hubs_lmp():
    """API: 获取所有主干电网的今日电价"""
    current_app.logger.info("API request: /api/ca/lmp/trading_hubs/today")
    data = data_fetcher.get_trading_hub_today_lmp()
    return jsonify(data)

@bp.route('/lmp/trading_hubs/history', methods=['GET'])
def api_history_trading_hubs_lmp():
    """API: 获取主干电网的历史电价"""
    date = request.args.get('date')
    market = request.args.get('market')
    locations_str = request.args.get('locations')
    current_app.logger.info(f"API request: /api/ca/lmp/trading_hubs/history?date={date}&market={market}&locations={locations_str}")
    
    if not all([date, market, locations_str]):
        return jsonify({"error": "date, market, and locations parameters are required"}), 400
    
    locations = locations_str.split(',')
    data = data_fetcher.get_trading_hub_history_lmp(date, market, locations)
    return jsonify(data)

@bp.route('/lmp/history/all_nodes', methods=['GET'])
def api_history_all_nodes_lmp():
    """API: 获取所有地区节点的历史电价"""
    date = request.args.get('date')
    market = request.args.get('market')
    current_app.logger.info(f"API request: /api/ca/lmp/history/all_nodes?date={date}&market={market}")

    if not date or not market:
        return jsonify({"error": "date and market parameters are required"}), 400

    data = data_fetcher.get_all_nodes_history_lmp(date, market)
    return jsonify(data)


# --- 燃料组合数据 API (Fuel Mix API) ---

@bp.route('/fuel_mix/today', methods=['GET'])
def api_get_fuel_mix_today():
    """API: 获取今日燃料组合数据"""
    current_app.logger.info("API request: /api/ca/fuel_mix/today")
    data = data_fetcher.get_fuel_mix_data("today")
    return jsonify(data)

@bp.route('/fuel_mix/history', methods=['GET'])
def api_get_fuel_mix_history():
    """API: 获取历史燃料组合数据"""
    date = request.args.get('date')
    current_app.logger.info(f"API request: /api/ca/fuel_mix/history?date={date}")
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    data = data_fetcher.get_fuel_mix_data(date)
    return jsonify(data)

# --- 太阳能和风能预测 API (Solar and Wind Forecast API) ---

@bp.route('/forecast/solar_and_wind', methods=['GET'])
def api_solar_and_wind_forecast():
    """API: 获取太阳能和风能的日前预测数据"""
    date = request.args.get('date')
    current_app.logger.info(f"API request: /api/ca/forecast/solar_and_wind?date={date}")
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    data = data_fetcher.get_solar_and_wind_forecast(date)
    return jsonify(data)