# app/api/fire/routes.py
from flask import jsonify, request, current_app
from app.api.fire import bp
import requests
import csv
from io import StringIO
from datetime import datetime, timedelta

# EONET API for Wildfires category (ID: 8)
EONET_EVENTS_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"

# NASA FIRMS API base for archive data by date
FIRMS_ARCHIVE_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/c1181b338621213c631c3c5f59e1c4a2/VIIRS_SNPP_NRT/USA"


@bp.route('/events', methods=['GET'])
def get_wildfire_events():
    """API: 获取过去一年内的官方野火事件"""
    current_app.logger.info("API request: /api/fire/events")
    
    # 获取过去365天的事件
    params = {
        'category': 'wildfires',
        'limit': 200, # 获取最近的200个事件
        'days': 365,
        'status': 'all' # 包括开放和已关闭的事件
    }
    
    try:
        response = requests.get(EONET_EVENTS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data.get('events', []):
            # EONET的坐标格式是 [lon, lat]
            geometry = event['geometry'][0]
            events.append({
                'id': event['id'],
                'title': event['title'],
                'date': geometry['date'],
                'lat': geometry['coordinates'][1],
                'lon': geometry['coordinates'][0]
            })
            
        return jsonify({"events": events})

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch data from EONET: {e}")
        return jsonify({"error": "Failed to retrieve event data from EONET."}), 503


@bp.route('/usa_by_date', methods=['GET'])
def get_usa_fires_by_date():
    """API: 获取美国指定日期的活跃火点"""
    # 获取日期参数，如果没有，则默认为当天 (最近24小时)
    date_str = request.args.get('date')
    
    if date_str:
        # 如果提供了日期，构建历史数据URL
        # URL格式: /api/country/csv/MAP_KEY/VIIRS_SNPP_NRT/USA/1/YYYY-MM-DD
        url = f"{FIRMS_ARCHIVE_BASE_URL}/1/{date_str}"
        current_app.logger.info(f"API request: /api/fire/usa_by_date?date={date_str}")
    else:
        # 否则，使用近24小时的URL
        url = f"{FIRMS_ARCHIVE_BASE_URL}/1" # 最后的 '1' 代表 1 day (24h)
        current_app.logger.info("API request: /api/fire/usa_by_date (for last 24h)")

    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_file = StringIO(response.text)
        reader = csv.DictReader(csv_file)
        
        fires = []
        for row in reader:
            try:
                fires.append({
                    "lat": float(row['latitude']),
                    "lon": float(row['longitude']),
                    "frp": float(row['frp']),
                    "acq_date": row['acq_date'],
                    "acq_time": row['acq_time'],
                })
            except (ValueError, KeyError):
                continue # 跳过格式错误的行

        return jsonify({"fires": fires})

    except requests.exceptions.RequestException as e:
        # FIRMS对于没有数据的日期可能会返回404，这不应该被视为服务器错误
        if e.response and e.response.status_code == 404:
            current_app.logger.info(f"No fire data found for date: {date_str}")
            return jsonify({"fires": []}) # 返回空列表表示当天无火点
            
        current_app.logger.error(f"Failed to fetch data from NASA FIRMS for date {date_str}: {e}")
        return jsonify({"error": "Failed to retrieve fire point data from NASA FIRMS."}), 503