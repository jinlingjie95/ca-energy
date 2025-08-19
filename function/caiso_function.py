import gridstatus
import pandas as pd

caiso = gridstatus.CAISO()


def get_realtime_load():
    """Fetch the latest load data from CAISO."""
    try:
        load_df = caiso.get_load(date='latest')
        if load_df is None or load_df.empty:
            return {"error": "No load data available"}
        load_df['Time'] = pd.to_datetime(load_df['Time'])

        data_to_return = {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
        return data_to_return
    except Exception as e:
        return {"error": str(e)}

def get_history_load(date=None):
    """Fetch historical load data from CAISO."""
    try:
        if date is None:
            return {"error": "Date parameter is required"}
        
        load_df = caiso.get_load(date)
        if load_df is None or load_df.empty:
            return {"error": "No load data available"}
        load_df['Time'] = pd.to_datetime(load_df['Time'])
        data_to_return = {
            "time": load_df['Time'].dt.strftime('%H:%M').tolist(),
            "value": load_df['Load'].tolist()
        }
        return data_to_return
    except Exception as e:
        return {"error": str(e)}
    
def get_load_forecast(date=None, option=None, area=None):
    """Fetch load forecast data from CAISO."""
    try:
        if date is None:
            return {"error": "Date parameter is required"}
        if option is None:
            return {"error": "Option parameter is required"}
        
        if option == 'hourly':
            load_forecast_df = caiso.get_load_forecast_day_ahead(date)
        elif option == '5min':
            load_forecast_df = caiso.get_load_forecast_5_min(date)
        elif option == '15min':
            load_forecast_df = caiso.get_load_forecast_15_min(date)
        else:
            return {"error": "Invalid option parameter"}

        if load_forecast_df is None or load_forecast_df.empty:
            return {"error": "No load forecast data available"} 
        
        # 
        load_forecast_df["Time"] = load_forecast_df["Interval Start"]

        # filter by area if specified
        if area is None:
            # Filter for CA ISO-TAC area
            load_forecast_df = load_forecast_df[load_forecast_df["TAC Area Name"] == "CA ISO-TAC"]
            load_forecast_df = load_forecast_df.drop(columns=["TAC Area Name"])

            load_forecast_df['Time'] = pd.to_datetime(load_forecast_df['Time'])
            data_to_return = {
                "time": load_forecast_df['Time'].dt.strftime('%H:%M').tolist(),
                "value": load_forecast_df['Load'].tolist()
            }
        elif area == 'ALL':
            # Return all areas without filtering
            result = {}
            for area_name, group in load_forecast_df.groupby("TAC Area Name"):
                group = group.copy()

                result[area_name] = {
                    "time": group['Time'].dt.strftime('%H:%M').tolist(),
                    "value": group['Load Forecast'].tolist()
                }
        else:
            # Filter for specific area
            load_forecast_df = load_forecast_df[load_forecast_df["TAC Area Name"] == area]
            if load_forecast_df.empty:
                return {"error": f"No data available for area: {area}"}
            
            load_forecast_df['Time'] = pd.to_datetime(load_forecast_df['Time'])
            data_to_return = {
                "time": load_forecast_df['Time'].dt.strftime('%H:%M').tolist(),
                "value": load_forecast_df['Load'].tolist()
            }
            
        return data_to_return
    except Exception as e:
        return {"error": str(e)}


