from flask import Blueprint, jsonify, request
import gridstatus
import pandas as pd
from datetime import datetime
import logging

lmp_api = Blueprint('lmp_api', __name__)
caiso = gridstatus.CAISO()

@lmp_api.route('/api/lmp')
def get_lmp_data():
    try:
        logging.info("Fetching latest LMP data from CAISO...")
        lmp_df = caiso.get_lmp(date='latest', market=gridstatus.Markets.DAY_AHEAD_HOURLY, locations=['TH_NP15_GEN-APND'])
        if lmp_df is None or lmp_df.empty:
            logging.warning("No LMP data available.")
            return jsonify({"error": "No LMP data available"}), 503
        lmp_df['Time'] = pd.to_datetime(lmp_df['Time'])
        data_to_return = {
            "timestamps": lmp_df['Time'].dt.strftime('%H:%M').tolist(),
            "lmp_values": lmp_df['LMP'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching LMP data: {e}")
        return jsonify({"error": str(e)}), 500

@lmp_api.route('/api/get_history_lmp')
def get_history_lmp():
    try:
        logging.info("Fetching historical LMP data from CAISO...")
        date = request.args.get('date')
        location = request.args.get('location')
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if not location:
            return jsonify({"error": "Location parameter is required"}), 400
        lmp_df = caiso.get_lmp(date, market=gridstatus.Markets.DAY_AHEAD_HOURLY)
        if lmp_df is None or lmp_df.empty:
            logging.warning("No LMP data available.")
            return jsonify({"error": "No LMP data available"}), 503
        lmp_df['Time'] = pd.to_datetime(lmp_df['Time'])
        data_to_return = {
            "timestamps": lmp_df['Time'].dt.strftime('%H:%M').tolist(),
            "lmp_values": lmp_df['LMP'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching LMP data: {e}")
        return jsonify({"error": str(e)}), 500

@lmp_api.route('/api/locations')
def get_lmp_locations():
    return jsonify({"locations": caiso.trading_hub_locations})