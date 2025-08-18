from flask import Blueprint, jsonify, request
import gridstatus
import pandas as pd
from datetime import datetime
import logging

other_api = Blueprint('other_api', __name__)
caiso = gridstatus.CAISO()

@other_api.route('/api/other/get_curtailment')
def get_curtailment():
    """Fetch curtailment data from CAISO."""
    try:
        logging.info("Fetching curtailment data from CAISO...")
        date = request.args.get('date')
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        curtailment_df = caiso.get_curtailment(date)
        if curtailment_df is None or curtailment_df.empty:
            logging.warning("No curtailment data available.")
            return jsonify({"error": "No curtailment data available"}), 503
        curtailment_df['Time'] = pd.to_datetime(curtailment_df['Time'])
        data_to_return = {
            "timestamps": curtailment_df['Time'].dt.strftime('%H:%M').tolist(),
            "curtailment_values": curtailment_df['Curtailment'].tolist()
        }
        return jsonify(data_to_return)
    except Exception as e:
        logging.error(f"Error fetching curtailment data: {e}")
        return jsonify({"error": str(e)}), 500