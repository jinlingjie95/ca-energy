from flask import Blueprint, jsonify, request
import gridstatus
import pandas as pd
from datetime import datetime
import logging

load_api = Blueprint('load_api', __name__)
caiso = gridstatus.CAISO()

@load_api.route('/api/load/get_latest_date')
def get_latest_load():
    """Fetch the latest load data from CAISO."""
    try:
        logging.info("Fetching latest load data from CAISO...")
        load_df = caiso.get_load(date='latest')
        if load_df is None or load_df.empty:
            logging.warning("No load data available.")
            return jsonify({"error": "No load data available"}), 503
        load_df['Time'] = pd.to_datetime(load_df['Time'])
        data_to_return = {
            "timestamps": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "load_values": load_df['Load'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching load data: {e}")
        return jsonify({"error": str(e)}), 500

@load_api.route('/api/load/get_history_date')
def get_history_load():
    """Fetch historical load data from CAISO."""
    try:
        logging.info("Fetching historical load data from CAISO...")
        date = request.args.get('date')
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        load_df = caiso.get_load(date)
        if load_df is None or load_df.empty:
            logging.warning("No load data available.")
            return jsonify({"error": "No load data available"}), 503
        load_df['Time'] = pd.to_datetime(load_df['Time'])
        data_to_return = {
            "timestamps": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "load_values": load_df['Load'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching load data: {e}")
        return jsonify({"error": str(e)}), 500
    
@load_api.route('/api/load/get_load_forecast')
def get_load_forecast():
    """Fetch load forecast data from CAISO."""
    try:
        logging.info("Fetching load forecast data from CAISO...")
        date = request.args.get('date')
        option = request.args.get('option')  # 'latest' or specific date
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if option == 'hourly':
            load_forecast_df = caiso.get_load_forecast(date)
        elif option == '5min':
            load_forecast_df = caiso.get_load_forecast_5_min(date)
        elif option == '15min':
            load_forecast_df = caiso.get_load_forecast_15_min(date)
        else:
            load_forecast_df = caiso.get_load_forecast(date)
          
        if load_forecast_df is None or load_forecast_df.empty:
            logging.warning("No load forecast data available.")
            return jsonify({"error": "No load forecast data available"}), 503
        
        if 'Time' not in load_forecast_df.columns:
            # 如果没有'Time'列，则用'Interval Start'列重命名为'Time'
            if 'Interval Start' in load_forecast_df.columns:
                load_forecast_df['Time'] = load_forecast_df['Interval Start']
            else:
                logging.warning("No 'Time' or 'Interval Start' column in forecast data.")
                return jsonify({"error": "No valid time column in forecast data"}), 500

        load_forecast_df['Time'] = pd.to_datetime(load_forecast_df['Time'])
        data_to_return = {
            "timestamps": load_forecast_df['Time'].dt.strftime('%H:%M').tolist(),
            "load_forecast_values": load_forecast_df['Load Forecast'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching load forecast data: {e}")
        return jsonify({"error": str(e)}), 500
    