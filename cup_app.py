from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
from sklearn.metrics import mutual_info_score

app = Flask(__name__)

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

    # Return the result as JSON or render it in a template
    return jsonify({
        'stock1': stock1,
        'stock2': stock2,
        'mutual_information': mi_score
    })

if __name__ == '__main__':
    app.run(debug=True)
