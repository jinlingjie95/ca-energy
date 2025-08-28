import pandas as pd
import gridstatus
from flask import current_app

# 初始化 CAISO 实例
caiso = gridstatus.CAISO()

def get_market_enum(market_str):
    """根据字符串返回对应的 gridstatus 市场枚举值"""
    if market_str == 'day_ahead_hourly':
        return gridstatus.Markets.DAY_AHEAD_HOURLY
    if market_str == 'real_time_5_min':
        return gridstatus.Markets.REAL_TIME_5_MIN
    return None

# --- 电力负荷数据 (Load) ---

def get_latest_load():
    """获取最新的实时电力负荷数据点"""
    try:
        current_app.logger.debug("Fetching latest load data...")
        load_df = caiso.get_load(date='latest')
        if load_df is None or load_df.empty:
            return {"error": "No load data available from API."}
        
        latest = load_df.iloc[-1]
        latest_time = pd.to_datetime(latest['Time'])
        
        return {
            "time": latest_time.strftime('%H:%M'),
            "value": float(latest['Load'])
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching latest load: {e}", exc_info=True)
        return {"error": "Server error while fetching latest load data."}

def get_today_load():
    """获取当天至今的实时电力负荷数据序列"""
    try:
        current_app.logger.debug("Fetching today's load data...")
        load_df = caiso.get_load(date='today')
        if load_df is None or load_df.empty:
            return {"error": "No load data available for today."}
        
        load_df['Time'] = pd.to_datetime(load_df['Time'])
        return {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching today's load: {e}", exc_info=True)
        return {"error": "Server error while fetching today's load data."}

def get_history_load(date):
    """获取指定日期的历史电力负荷数据"""
    try:
        current_app.logger.debug(f"Fetching historical load for date: {date}...")
        load_df = caiso.get_load(date)
        if load_df is None or load_df.empty:
            return {"error": f"No load data available for {date}"}

        load_df['Time'] = pd.to_datetime(load_df['Time'])
        return {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching history load for {date}: {e}", exc_info=True)
        return {"error": "Server error while fetching historical load data."}

def get_load_forecast(date, option):
    """获取电力负荷预测数据"""
    try:
        current_app.logger.debug(f"Fetching load forecast for date: {date}, option: {option}...")
        forecast_map = {
            'hourly': caiso.get_load_forecast_day_ahead,
            '5min': caiso.get_load_forecast_5_min,
            '15min': caiso.get_load_forecast_15_min
        }
        fetch_func = forecast_map.get(option)
        if not fetch_func:
            return {"error": "Invalid forecast option"}

        forecast_df = fetch_func(date)
        if forecast_df is None or forecast_df.empty:
            return {"error": f"No forecast data available for {date} with option {option}"}
        
        forecast_df = forecast_df[forecast_df["TAC Area Name"] == "CA ISO-TAC"]
        forecast_df['Time'] = pd.to_datetime(forecast_df["Interval Start"])
        
        return {
            "time": forecast_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": forecast_df['Load Forecast'].tolist()
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching load forecast for {date}, {option}: {e}", exc_info=True)
        return {"error": "Server error while fetching forecast data."}

# --- 储能数据 (Storage) ---

def get_latest_storage():
    """获取最新的储能数据点"""
    try:
        storage_dict = caiso.get_storage(date='latest')
        if not isinstance(storage_dict, dict) or not storage_dict:
            return {"error": "No storage data available"}
        
        return {
            "time": pd.to_datetime(storage_dict['time']).strftime('%H:%M'),
            "value": storage_dict['supply']
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching latest storage: {e}", exc_info=True)
        return {"error": "Server error while fetching latest storage data."}

def get_today_storage():
    """获取当天的储能数据序列"""
    try:
        today = pd.Timestamp.now(tz=gridstatus.CAISO.default_timezone).date()
        storage_df = caiso.get_storage(date=today)
        if storage_df is None or storage_df.empty:
            return {"error": "No storage data available for today"}
        
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        return {
            "time": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": storage_df['Supply'].tolist()
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching today's storage: {e}", exc_info=True)
        return {"error": "Server error while fetching today's storage data."}

def get_history_storage(date):
    """获取指定日期的历史储能数据"""
    try:
        storage_df = caiso.get_storage(date)
        if storage_df is None or storage_df.empty:
            return {"error": f"No storage data available for {date}"}
        
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        return {
            "time": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": storage_df['Supply'].tolist()
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching history storage for {date}: {e}", exc_info=True)
        return {"error": "Server error while fetching historical storage data."}


# --- 电价数据 (LMP) ---

def get_trading_hub_locations():
    """获取所有交易中心的地点列表"""
    try:
        return {"locations": caiso.trading_hub_locations}
    except Exception as e:
        current_app.logger.error(f"Error fetching trading hub locations: {e}", exc_info=True)
        return {"error": "Could not retrieve trading hub locations."}

def get_trading_hub_latest_lmp():
    """获取所有主干电网的最新实时电价"""
    locations_data = get_trading_hub_locations()
    if "error" in locations_data:
        return locations_data

    all_latest_data = {}
    for loc in locations_data.get("locations", []):
        day_ahead = caiso.get_lmp(date='latest', market=gridstatus.Markets.DAY_AHEAD_HOURLY, locations=[loc])
        real_time = caiso.get_lmp(date='latest', market=gridstatus.Markets.REAL_TIME_5_MIN, locations=[loc])
        
        all_latest_data[loc] = {
            "day_ahead_hourly": format_lmp_latest(day_ahead),
            "real_time_5_min": format_lmp_latest(real_time)
        }
    return {"locations": all_latest_data}
    
def get_trading_hub_today_lmp():
    """获取所有主干电网的今日实时电价"""
    locations_data = get_trading_hub_locations()
    if "error" in locations_data:
        return locations_data

    all_today_data = {}
    for loc in locations_data.get("locations", []):
        day_ahead = caiso.get_lmp(date='today', market=gridstatus.Markets.DAY_AHEAD_HOURLY, locations=[loc])
        real_time = caiso.get_lmp(date='today', market=gridstatus.Markets.REAL_TIME_5_MIN, locations=[loc])
        
        all_today_data[loc] = {
            "day_ahead_hourly": format_lmp_timeseries(day_ahead),
            "real_time_5_min": format_lmp_timeseries(real_time)
        }
    return {"hubs": all_today_data}

def get_trading_hub_history_lmp(date, market, locations):
    """获取指定主干电网的历史电价数据"""
    all_data = {}
    market_enum = get_market_enum(market)
    if not market_enum: return {"error": "Invalid market parameter"}

    for loc in locations:
        try:
            lmp_df = caiso.get_lmp(date, market=market_enum, locations=[loc])
            all_data[loc] = format_lmp_timeseries(lmp_df)
        except Exception as e:
            current_app.logger.error(f"Error fetching history LMP for {loc} on {date}: {e}", exc_info=True)
            all_data[loc] = {"error": f"Failed to fetch data for {loc}"}
    return all_data

def get_all_nodes_history_lmp(date, market):
    """获取所有地区节点(AP Nodes)的历史电价数据"""
    market_enum = get_market_enum(market)
    if not market_enum: return {"error": "Invalid market parameter"}

    try:
        lmp_df = caiso.get_lmp(date, market=market_enum, locations="ALL_AP_NODES")
        if lmp_df is None or lmp_df.empty:
            return {"error": f"No AP node LMP data available for {date}"}

        lmp_df['Time'] = pd.to_datetime(lmp_df['Time'])
        lmp_df['time_str'] = lmp_df['Time'].dt.strftime('%H:%M')
        
        grouped = lmp_df.groupby('Location')
        data_to_return = {}
        for name, group in grouped:
            sorted_group = group.sort_values(by='Time')
            data_to_return[name] = {
                "time": sorted_group['time_str'].tolist(),
                "value": sorted_group['LMP'].tolist()
            }
        return data_to_return
    except Exception as e:
        current_app.logger.error(f"Error fetching all nodes LMP for {date}: {e}", exc_info=True)
        return {"error": "Server error fetching all nodes LMP data."}


# --- 燃料组合数据 (Fuel Mix) ---

def get_fuel_mix_data(date):
    """获取指定日期的燃料组合数据并格式化"""
    try:
        fuel_mix_df = caiso.get_fuel_mix(date)
        if fuel_mix_df is None or fuel_mix_df.empty:
            return {"error": f"No fuel mix data available for {date}"}

        fuel_mix_df['Time'] = pd.to_datetime(fuel_mix_df['Time'])
        time_list = fuel_mix_df['Time'].dt.strftime('%H:%M').tolist()
        
        energy_types = [
            "Solar", "Wind", "Geothermal", "Biomass", "Biogas", "Small Hydro",
            "Coal", "Nuclear", "Natural Gas", "Large Hydro", "Batteries", "Imports", "Other"
        ]
        
        data_to_return = {}
        for energy in energy_types:
            if energy in fuel_mix_df.columns:
                data_to_return[energy] = {
                    "time": time_list,
                    "value": fuel_mix_df[energy].tolist()
                }
        return data_to_return
    except Exception as e:
        current_app.logger.error(f"Error fetching fuel mix for {date}: {e}", exc_info=True)
        return {"error": "Server error while fetching fuel mix data."}


# --- 辅助格式化函数 ---

def format_lmp_latest(df):
    """格式化最新的LMP数据点"""
    if df is None or df.empty:
        return {"error": "No data available"}
    latest = df.iloc[-1]
    return {
        "time": pd.to_datetime(latest['Time']).strftime('%H:%M'),
        "value": float(latest['LMP'])
    }

def format_lmp_timeseries(df):
    """格式化LMP时间序列数据"""
    if df is None or df.empty:
        return {"error": "No data available"}
    df['Time'] = pd.to_datetime(df['Time'])
    return {
        "time": df['Time'].dt.strftime('%H:%M').tolist(),
        "value": df['LMP'].tolist()
    }