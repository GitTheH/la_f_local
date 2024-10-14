
from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics import mutual_info_score
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from flask_cors import CORS
from datetime import date



app = Flask(__name__)
CORS(app)
# Connect to SQLite Database
def get_db_connection():
    conn = sqlite3.connect('financial_data.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Homepage with Stock Selection
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM symbols")
    stocks = cursor.fetchall()
    conn.close()
    return render_template('index.html', stocks=stocks)

# Endpoint to Fetch Stock Data and Perform Analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    stock1 = request.form['stock1']
    stock2 = request.form['stock2']

    # Fetch time series data for both stocks
    conn = get_db_connection()
    stock1_data = pd.read_sql_query(f"SELECT * FROM time_series_daily WHERE symbol = '{stock1}'", conn)
    stock2_data = pd.read_sql_query(f"SELECT * FROM time_series_daily WHERE symbol = '{stock2}'", conn)
    conn.close()

    # Join the two dataframes on the 'date' column
    merged_data = pd.merge(stock1_data, stock2_data, on='date', suffixes=(f'_{stock1}', f'_{stock2}'))

    # Calculate Mutual Information between the closing prices of the two stocks
    mi_score = mutual_info_score(merged_data[f'close_{stock1}'], merged_data[f'close_{stock2}'])

    # Return the result as JSON
    return jsonify({
        'stock1': stock1,
        'stock2': stock2,
        'mutual_information': mi_score
    })

# Standalone Stock Dashboard
@app.route('/standalone', methods=['GET', 'POST'])
def standalone():
    conn = get_db_connection()

    # Fetch list of available stocks
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM symbols")
    stocks = cursor.fetchall()

    # Default stock: AAPL
    stock_symbol = 'AAPL'
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol')

    # Fetch stock info from 'symbols' table
    stock_info = pd.read_sql_query(f"SELECT * FROM symbols WHERE symbol = '{stock_symbol}'", conn).to_dict('records')[0]

    # Fetch recent prices from 'time_series_daily' table (latest day before today)
    recent_prices = pd.read_sql_query(f"SELECT * FROM time_series_daily WHERE symbol = '{stock_symbol}' ORDER BY date DESC LIMIT 1", conn)

    conn.close()

    return render_template('standalone.html', stock_info=stock_info, recent_prices=recent_prices, stocks=stocks)

# Price-Volume Relationship Calculation
@app.route('/price_volume_relationship', methods=['POST'])
def price_volume_relationship():
    stock_symbol = request.form['stock_symbol']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Fetch relevant data for the selected timeframe
    conn = get_db_connection()
    query = f"SELECT date, close, volume FROM time_series_daily WHERE symbol = '{stock_symbol}' AND date BETWEEN '{start_date}' AND '{end_date}'"
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Check if data is available
    if data.empty:
        return jsonify({
            'error': 'No data available for the selected date range'
        })

    # Calculate price-volume relationship (correlation)
    correlation = data['close'].pct_change().corr(data['volume'])

    return jsonify({
        'stock': stock_symbol,
        'start_date': start_date,
        'end_date': end_date,
        'correlation': correlation
    })

# Time-to-Revert Analysis
@app.route('/time_to_revert', methods=['POST'])
def time_to_revert():
    stock_symbol = request.form['stock_symbol']
    period = int(request.form['period'])

    # Fetch stock price data
    conn = get_db_connection()
    query = f"SELECT date, close FROM time_series_daily WHERE symbol = '{stock_symbol}' ORDER BY date"
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate rolling mean
    data['rolling_mean'] = data['close'].rolling(window=period).mean()

    # Calculate time-to-revert (time to revert to the rolling mean)
    data['deviation'] = data['close'] - data['rolling_mean']
    data.dropna(inplace=True)

    # Time to revert when the deviation is close to zero
    data['time_to_revert'] = (data['deviation'].abs() < 0.01).cumsum()

    time_to_revert = data['time_to_revert'].max()

    return jsonify({
        'stock': stock_symbol,
        'time_to_revert': int(time_to_revert)
    })

# Sharpe ratio
@app.route('/sharpe_ratio', methods=['POST'])
def sharpe_ratio():
    stock_symbol = request.form['stock_symbol']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    risk_free_rate = float(request.form['risk_free_rate'])  # Risk-free rate input from the user

    # Fetch stock price data
    conn = get_db_connection()
    query = f"SELECT date, close FROM time_series_daily WHERE symbol = '{stock_symbol}' AND date BETWEEN '{start_date}' AND '{end_date}'"
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate daily returns
    data['returns'] = data['close'].pct_change().dropna()

    # Calculate average return and standard deviation of returns (volatility)
    mean_return = data['returns'].mean()
    std_dev_return = data['returns'].std()

    # Calculate Sharpe Ratio
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev_return

    return jsonify({
        'stock': stock_symbol,
        'start_date': start_date,
        'end_date': end_date,
        'sharpe_ratio': sharpe_ratio
    })

# YTD data endpoint
# YTD data endpoint
@app.route('/get_ytd_data/<stock_symbol>', methods=['GET'])
def get_ytd_data(stock_symbol):
    conn = get_db_connection()
    # Fetch YTD data including open, close, and volume
    query = f"""
        SELECT date, open, close, volume 
        FROM time_series_daily 
        WHERE symbol = '{stock_symbol}' 
        AND strftime('%Y', date) = strftime('%Y', 'now')
        ORDER BY date ASC
    """
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate daily returns (percentage)
    data['returns'] = data['close'].pct_change().fillna(0) * 100

    # Calculate average price and volume in dollars (volume * average price)
    data['avg_price'] = (data['open'] + data['close']) / 2
    data['volume_in_dollars'] = data['volume'] * data['avg_price']

    return jsonify({
        'dates': data['date'].tolist(),
        'prices': data['close'].tolist(),  # YTD prices for the chart
        'returns': data['returns'].tolist(),  # Daily returns for the returns chart
        'volumes_in_dollars': data['volume_in_dollars'].tolist()  # Volume in dollars
    })

# Multiple Stock Analysis Page
@app.route('/multiple', methods=['GET', 'POST'])
def multiple_stocks():
    conn = get_db_connection()

    # Fetch list of available stocks
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM symbols")
    stocks = cursor.fetchall()
    conn.close()

    return render_template('multiple.html', stocks=stocks)

# Correlation Matrix Calculation
# Correlation Matrix Calculation
@app.route('/correlation_matrix', methods=['POST'])
def correlation_matrix():
    stock_symbols = request.form.get('stock_symbols').split(',')
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    if len(stock_symbols) < 2:
        return jsonify({'error': 'Please select at least two stocks.'}), 400

    conn = get_db_connection()
    data_frames = []
    for symbol in stock_symbols:
        query = """
            SELECT date, close FROM time_series_daily 
            WHERE symbol = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """
        data = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        data.set_index('date', inplace=True)
        data.rename(columns={'close': symbol}, inplace=True)
        data_frames.append(data)
    conn.close()

    # Combine data and drop rows with missing values
    combined_data = pd.concat(data_frames, axis=1).dropna()
    if combined_data.empty:
        return jsonify({'error': 'No overlapping data between selected stocks in the specified date range.'}), 400

    # Calculate correlation matrix
    correlation_matrix = combined_data.corr()

    # Convert correlation matrix to JSON serializable format
    corr_matrix_dict = correlation_matrix.to_dict()

    # Prepare CSV data
    csv_data = correlation_matrix.to_csv()

    # Generate heatmap image
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()

    plt.close()

    # Return the result
    return jsonify({
        'correlation_matrix': corr_matrix_dict,
        'csv': csv_data,
        'heatmap': img_base64
    })



# Cross-Stock Volatility Calculation with CSV export
@app.route('/cross_volatility', methods=['POST'])
def cross_volatility():
    stock_symbols = request.form.get('stock_symbols').split(',')
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    if len(stock_symbols) < 2:
        return jsonify({'error': 'Please select at least two stocks.'}), 400

    conn = get_db_connection()
    data_frames = []
    for symbol in stock_symbols:
        query = """
            SELECT date, close FROM time_series_daily 
            WHERE symbol = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """
        data = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        data.set_index('date', inplace=True)
        data.rename(columns={'close': symbol}, inplace=True)
        data_frames.append(data)
    conn.close()

    # Combine data and calculate rolling volatility
    combined_data = pd.concat(data_frames, axis=1).dropna()
    if combined_data.empty:
        return jsonify({'error': 'No overlapping data between selected stocks in the specified date range.'}), 400

    volatilities = combined_data.pct_change().rolling(window=30).std().dropna()

    # Prepare data for Chart.js
    datasets = []
    colors = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#9966ff']

    for i, symbol in enumerate(stock_symbols):
        datasets.append({
            'label': symbol,
            'data': volatilities[symbol].tolist(),
            'borderColor': colors[i % len(colors)],
            'borderWidth': 2,
            'fill': False,
            'pointRadius': 0,
            'lineTension': 0
        })

    # Prepare CSV data
    volatilities_csv = volatilities.reset_index().to_csv(index=False)

    return jsonify({
        'dates': volatilities.index.tolist(),
        'volatility_datasets': datasets,
        'volatilities_csv': volatilities_csv
    })





# Example: Sharpe Ratio for Apple (AAPL) from 2019 to today
@app.route('/standalone_example')
def standalone_example():
    conn = get_db_connection()
    start_date = '2019-01-01'
    end_date = date.today().strftime('%Y-%m-%d')

    # Fetch Apple's stock price data
    query = f"SELECT date, close FROM time_series_daily WHERE symbol = 'AAPL' AND date BETWEEN '{start_date}' AND '{end_date}'"
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Calculate daily returns
    data['returns'] = data['close'].pct_change().dropna()

    # Assume a risk-free rate of 1%
    risk_free_rate = 0.01
    mean_return = data['returns'].mean()
    std_dev_return = data['returns'].std()

    # Calculate Sharpe Ratio
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev_return

    return jsonify({
        'sharpe_ratio': round(sharpe_ratio, 2)  # Return a nicely rounded Sharpe Ratio
    })



# Example: Cross-Stock Volatility for six selected stocks
@app.route('/multiple_example')
def multiple_example():
    conn = get_db_connection()
    stock_symbols = ['AAPL', 'BA', 'MSFT', 'KO', 'IBM', 'INTC']
    start_date = '2022-01-01'
    end_date = date.today().strftime('%Y-%m-%d')

    data_frames = []
    for symbol in stock_symbols:
        query = f"SELECT date, close FROM time_series_daily WHERE symbol = '{symbol}' AND date BETWEEN '{start_date}' AND '{end_date}'"
        data = pd.read_sql_query(query, conn)
        data.set_index('date', inplace=True)
        data.rename(columns={'close': symbol}, inplace=True)
        data_frames.append(data)

    combined_data = pd.concat(data_frames, axis=1).dropna()

    volatilities = combined_data.pct_change().rolling(window=30).std().dropna()
    conn.close()

    # Prepare data for Chart.js
    datasets = []
    colors = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#9966ff']

    for i, symbol in enumerate(stock_symbols):
        datasets.append({
            'label': symbol,
            'data': volatilities[symbol].tolist(),
            'borderColor': colors[i],
            'borderWidth': 2,  # Slightly thicker lines for better visibility
            'fill': False,
            'pointRadius': 0,  # Remove points for decluttering
            'lineTension': 0  # Keep straight lines
        })

    return jsonify({
        'dates': volatilities.index.tolist(),
        'volatility_datasets': datasets
    })




if __name__ == '__main__':
    app.run(debug=True)
