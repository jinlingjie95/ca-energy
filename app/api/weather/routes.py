# app/api/weather/routes.py
from flask import jsonify, request, current_app
from app.api.weather import bp
import requests
import asyncio

# 美国各州首府列表
STATE_CAPITALS = [
    "Montgomery, AL", "Juneau, AK", "Phoenix, AZ", "Little Rock, AR", "Sacramento, CA",
    "Denver, CO", "Hartford, CT", "Dover, DE", "Tallahassee, FL", "Atlanta, GA",
    "Honolulu, HI", "Boise, ID", "Springfield, IL", "Indianapolis, IN", "Des Moines, IA",
    "Topeka, KS", "Frankfort, KY", "Baton Rouge, LA", "Augusta, ME", "Annapolis, MD",
    "Boston, MA", "Lansing, MI", "Saint Paul, MN", "Jackson, MS", "Jefferson City, MO",
    "Helena, MT", "Lincoln, NE", "Carson City, NV", "Concord, NH", "Trenton, NJ",
    "Santa Fe, NM", "Albany, NY", "Raleigh, NC", "Bismarck, ND", "Columbus, OH",
    "Oklahoma City, OK", "Salem, OR", "Harrisburg, PA", "Providence, RI", "Columbia, SC",
    "Pierre, SD", "Nashville, TN", "Austin, TX", "Salt Lake City, UT", "Montpelier, VT",
    "Richmond, VA", "Olympia, WA", "Charleston, WV", "Madison, WI", "Cheyenne, WY"
]

def fetch_weather_for_city(session, url):
    """在一个 aiohttp session 中异步获取单个城市的天气"""
    try:
        with session.get(url) as response:
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": data["name"],
                    "temp": round(data["main"]["temp"]),
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"]
                }
            else:
                return None # 如果请求失败则返回 None
    except Exception:
        return None


@bp.route('/state_capitals', methods=['GET'])
def get_weather_for_state_capitals():
    """API: 获取所有州首府的天气数据"""
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key :
        return jsonify({"error": "Weather API key is not configured."}), 500

    weather_data = []
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # 使用 requests.Session 来复用 TCP 连接，提高效率
    with requests.Session() as session:
        for city_state in STATE_CAPITALS:
            city = city_state.split(',')[0]
            params = {
                'q': f"{city_state},us",
                'appid': api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            try:
                response = session.get(base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    weather_data.append({
                        "city": data["name"],
                        "temp": round(data["main"]["temp"]),
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"]
                    })
                else:
                    # 如果某个城市查询失败，记录日志但继续
                    current_app.logger.warning(f"Could not fetch weather for {city_state}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Request failed for {city_state}: {e}")

    return jsonify({"capitals": weather_data})


@bp.route('/city', methods=['GET'])
def get_weather_by_city():
    """API: 根据城市名获取天气数据"""
    city = request.args.get('q')
    if not city:
        return jsonify({"error": "City parameter 'q' is required"}), 400

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key :
        return jsonify({"error": "Weather API key is not configured."}), 500

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},us&appid={api_key}&units=metric&lang=zh_cn"

    try:
        response = requests.get(url)
        if response.status_code == 404:
            return jsonify({"error": f"City '{city}' not found"}), 404
        
        response.raise_for_status()
        data = response.json()

        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }
        return jsonify(weather_info)

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Could not fetch weather for {city}: {e}")
        return jsonify({"error": "Failed to retrieve data from weather service."}), 503
    
@bp.route('/forecast/hourly', methods=['GET'])
def get_hourly_forecast():
    """API: 获取某个城市未来24小时的3小时天气预报"""
    city = request.args.get('q')
    if not city:
        return jsonify({"error": "City parameter 'q' is required"}), 400

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return jsonify({"error": "Weather API key is not configured."}), 500

    # 使用 5 day / 3 hour forecast API
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},us&appid={api_key}&units=metric&lang=zh_cn"

    try:
        response = requests.get(url)
        if response.status_code == 404:
            return jsonify({"error": f"Forecast data for city '{city}' not found"}), 404
        
        response.raise_for_status()
        data = response.json()

        # 提取接下来8个时间点的数据 (3小时 * 8 = 24小时)
        forecasts = []
        for item in data.get('list', [])[:8]:
            forecasts.append({
                # dt 是 unix timestamp, dt_txt 是文本时间
                "time": item['dt_txt'], 
                "temp": item['main']['temp'],
                "humidity": item['main']['humidity'],
                "wind_speed": item['wind']['speed'],
                "description": item['weather'][0]['description']
            })
        
        return jsonify({"city": data['city']['name'], "forecasts": forecasts})

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Could not fetch hourly forecast for {city}: {e}")
        return jsonify({"error": "Failed to retrieve forecast data from weather service."}), 503