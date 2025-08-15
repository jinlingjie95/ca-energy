# ca-energy/README.md

# CA Energy Load Forecasting

This project provides a web application for visualizing real-time and historical load data from the California Independent System Operator (CAISO). It includes features for fetching and displaying load forecasts for different time intervals and regions.

## Project Structure

- **templates/load.html**: Contains the HTML structure for the front-end interface. It includes sections for displaying real-time load data, historical load data, and a new section for "全区域历史负荷预测数据" (All-Region Historical Load Forecast Data). This section allows users to select a date and fetch forecast data for different intervals (5 minutes, 15 minutes, hourly).

- **load_api.py**: Implements the Flask API endpoints for fetching load data and forecasts from CAISO. It handles requests for the latest load data, historical load data, and load forecasts, including the new functionality for all-region historical load forecast data.

- **app.py**: The main entry point for the Flask application. It initializes the app and registers the blueprint for the load API. This file may include new routes or configurations related to the forecasting functionality.

- **requirements.txt**: Lists the dependencies required for the project, including Flask and any other libraries needed for data handling and visualization.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ca-energy
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your web browser and navigate to `http://127.0.0.1:5000` to access the application.

## Usage

- **Real-time Load Data**: Click the "刷新" (Refresh) button to fetch the latest load data from CAISO.

- **Historical Load Data**: Select a date using the date input and click the "查看" (View) button to fetch historical load data.

- **全区域历史负荷预测数据**: In the new section, select a date and click one of the forecast buttons (5分钟预测, 15分钟预测, 每小时预测) to fetch historical load forecast data for all regions. The data will be displayed in a chart with different colors representing different data sources.

## API Endpoints

- `/api/load/get_latest_date`: Fetches the latest load data.
- `/api/load/get_history_date`: Fetches historical load data for a specified date.
- `/api/load/get_load_forecast`: Fetches load forecast data for a specified date and interval.
- `/api/load/get_all_load_forecast`: Fetches all-region historical load forecast data for a specified date and interval.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.