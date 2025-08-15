from flask import Blueprint, jsonify, request
import gridstatus
import pandas as pd
from datetime import datetime
import logging

storage_api = Blueprint('storage_api', __name__)
caiso = gridstatus.CAISO()

@storage_api.route('/api/storage/get_realtime_storage')
def get_realtime_storage():
    try:
        logging.info("Fetching latest storage data from CAISO...")
        storage_df  = caiso.get_storage(date='latest')
        # 实时数据是一个dict结构
        if not isinstance(storage_df, dict) or storage_df is None:
            logging.warning("No storage data available.")
            return jsonify({"error": "No storage data available"}), 503
        
        dt = pd.to_datetime(storage_df['time']).strftime('%H:%M')
        value = storage_df['supply']
        data_to_return = {
            "timestamps": dt,
            "storage_values": value
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching storage data: {e}")
        return jsonify({"error": str(e)}), 500

@storage_api.route('/api/storage/get_latest_storage')
def get_latest_storage():
    """Fetch the latest storage data from CAISO."""
    try:
        logging.info("Fetching latest storage data from CAISO...")
        storage_df  = caiso.get_storage(date=pd.Timestamp.now().date())
        if storage_df is None or storage_df.empty:
            logging.warning("No storage data available.")
            return jsonify({"error": "No storage data available"}), 503
        
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        data_to_return = {
            "timestamps": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "storage_values": storage_df['Supply'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching storage data: {e}")
        return jsonify({"error": str(e)}), 500

@storage_api.route('/api/storage/get_history_storage')
def get_history_storage():
    """Fetch historical storage data from CAISO."""
    try:
        logging.info("Fetching historical storage data from CAISO...")
        date = request.args.get('date')
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        storage_df = caiso.get_storage(date)
        if storage_df is None or storage_df.empty:
            logging.warning("No storage data available.")
            return jsonify({"error": "No storage data available"}), 503
        storage_df['Time'] = pd.to_datetime(storage_df['Time'])
        data_to_return = {
            "timestamps": storage_df['Time'].dt.strftime('%H:%M').tolist(),
            "storage_values": storage_df['Supply'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching storage data: {e}")
        return jsonify({"error": str(e)}), 500
