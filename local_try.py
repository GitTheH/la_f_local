import os
import requests
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    filename='data_retrieval.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Alpha Vantage API configuration
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY') or 'YOUR_ALPHA_VANTAGE_API_KEY'
BASE_URL = 'https://www.alphavantage.co/query'

# Rate limiting configuration
REQUESTS_PER_MINUTE = 70
SLEEP_INTERVAL = 60 / REQUESTS_PER_MINUTE

SYMBOLS = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS",
    "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO",
    "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH",
    "V", "VZ", "WBA", "WMT"
]


# List of S&P 500 symbols
"""SYMBOLS = [
    "MMM", "ACE", "ABT", "ANF", "ACN", "ADBE", "AMD", "AES", "AET", "AFL", "A", "GAS", "APD",
    "ARG", "AKAM", "AA", "ALXN", "ATI", "AGN", "ALL", "ANR", "ALTR", "MO", "AMZN", "AEE",
    "AEP", "AXP", "AIG", "AMT", "AMP", "ABC", "AMGN", "APH", "APC", "ADI", "AON", "APA",
    "AIV", "APOL", "AAPL", "AMAT", "ADM", "AIZ", "T", "ADSK", "ADP", "AN", "AZO", "AVB",
    "AVY", "AVP", "BHI", "BLL", "BAC", "BK", "BCR", "BAX", "BBT", "BEAM", "BDX", "BBBY",
    "BMS", "BRK.B", "BBY", "BIG", "BIIB", "BLK", "HRB", "BMC", "BA", "BWA", "BXP", "BSX",
    "BMY", "BRCM", "BF.B", "CHRW", "CA", "CVC", "COG", "CAM", "CPB", "COF", "CAH", "CFN",
    "KMX", "CCL", "CAT", "CBG", "CBS", "CELG", "CNP", "CTL", "CERN", "CF", "SCHW", "CHK",
    "CVX", "CMG", "CB", "CI", "CINF", "CTAS", "CSCO", "C", "CTXS", "CLF", "CLX", "CME",
    "CMS", "COH", "KO", "CCE", "CTSH", "CL", "CMCSA", "CMA", "CSC", "CAG", "COP", "CNX",
    "ED", "STZ", "CBE", "GLW", "COST", "CVH", "COV", "CCI", "CSX", "CMI", "CVS", "DHI",
    "DHR", "DRI", "DVA", "DF", "DE", "DELL", "DNR", "XRAY", "DVN", "DV", "DO", "DTV",
    "DFS", "DISCA", "DLTR", "D", "RRD", "DOV", "DOW", "DPS", "DTE", "DD", "DUK", "DNB",
    "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "EMC", "EMR", "ESV", "ETR",
    "EOG", "EQT", "EFX", "EQR", "EL", "EXC", "EXPE", "EXPD", "ESRX", "XOM", "FFIV", "FDO",
    "FAST", "FII", "FDX", "FIS", "FITB", "FHN", "FSLR", "FE", "FISV", "FLIR", "FLS",
    "FLR", "FMC", "FTI", "F", "FRX", "FOSL", "BEN", "FCX", "FTR", "GME", "GCI", "GPS",
    "GD", "GE", "GIS", "GPC", "GNW", "GILD", "GS", "GT", "GOOG", "GWW", "HAL", "HOG",
    "HAR", "HRS", "HIG", "HAS", "HCP", "HCN", "HNZ", "HP", "HES", "HPQ", "HD", "HON",
    "HRL", "HSP", "HST", "HCBK", "HUM", "HBAN", "ITW", "IR", "TEG", "INTC", "ICE", "IBM",
    "IFF", "IGT", "IP", "IPG", "INTU", "ISRG", "IVZ", "IRM", "JBL", "JEC", "JDSU", "JNJ",
    "JCI", "JOY", "JPM", "JNPR", "K", "KEY", "KMB", "KIM", "KMI", "KLAC", "KSS", "KFT",
    "KR", "LLL", "LH", "LRCX", "LM", "LEG", "LEN", "LUK", "LXK", "LIFE", "LLY", "LTD",
    "LNC", "LLTC", "LMT", "L", "LO", "LOW", "LSI", "MTB", "M", "MRO", "MPC", "MAR",
    "MMC", "MAS", "MA", "MAT", "MKC", "MCD", "MHP", "MCK", "MJN", "MWV", "MDT", "MRK",
    "MET", "PCS", "MCHP", "MU", "MSFT", "MOLX", "TAP", "MON", "MNST", "MCO", "MS",
    "MOS", "MSI", "MUR", "MYL", "NBR", "NDAQ", "NOV", "NTAP", "NFLX", "NWL", "NFX",
    "NEM", "NWSA", "NEE", "NKE", "NI", "NE", "NBL", "JWN", "NSC", "NTRS", "NOC", "NU",
    "NRG", "NUE", "NVDA", "NYX", "ORLY", "OXY", "OMC", "OKE", "ORCL", "OI", "PCAR",
    "PLL", "PH", "PDCO", "PAYX", "BTU", "JCP", "PBCT", "POM", "PEP", "PKI", "PRGO",
    "PFE", "PCG", "PM", "PSX", "PNW", "PXD", "PBI", "PCL", "PNC", "RL", "PPG", "PPL",
    "PX", "PCP", "PCLN", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "QEP",
    "PWR", "QCOM", "DGX", "RRC", "RTN", "RHT", "RF", "RSG", "RAI", "RHI", "ROK", "COL",
    "ROP", "ROST", "RDC", "R", "SWY", "SAI", "CRM", "SNDK", "SCG", "SLB", "SNI", "STX",
    "SEE", "SHLD", "SRE", "SHW", "SIAL", "SPG", "SLM", "SJM", "SNA", "SO", "LUV", "SWN",
    "SE", "S", "STJ", "SWK", "SPLS", "SBUX", "HOT", "STT", "SRCL", "SYK", "SUN", "STI",
    "SYMC", "SYY", "TROW", "TGT", "TEL", "TE", "THC", "TDC", "TER", "TSO", "TXN", "TXT",
    "HSY", "TRV", "TMO", "TIF", "TWX", "TWC", "TIE", "TJX", "TMK", "TSS", "TRIP", "TSN",
    "TYC", "USB", "UNP", "UNH", "UPS", "X", "UTX", "UNM", "URBN", "VFC", "VLO", "VAR",
    "VTR", "VRSN", "VZ", "VIAB", "V", "VNO", "VMC", "WMT", "WAG", "DIS", "WPO", "WM",
    "WAT", "WPI", "WLP", "WFC", "WDC", "WU", "WY", "WHR", "WFM", "WMB", "WIN", "WEC",
    "WPX", "WYN", "WYNN", "XEL", "XRX", "XLNX", "XL", "XYL", "YHOO", "YUM", "ZMH", "ZION"
]"""


# Alpha Vantage functions
FUNCTIONS = {
    'TIME_SERIES_DAILY_ADJUSTED': 'TIME_SERIES_DAILY_ADJUSTED',
    'OVERVIEW': 'OVERVIEW',
    'INCOME_STATEMENT': 'INCOME_STATEMENT',
    'BALANCE_SHEET': 'BALANCE_SHEET',
    'CASH_FLOW': 'CASH_FLOW',
    'EARNINGS': 'EARNINGS',
    'NEWS_SENTIMENT': 'NEWS_SENTIMENT'
}

# Database connection
try:
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    print(f"Database connection failed: {e}")
    exit(1)

# Create tables
def create_tables():
    try:
        # Symbols table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT,
                industry TEXT,
                exchange TEXT,
                currency TEXT,
                country TEXT,
                market_cap INTEGER,
                pe_ratio REAL,
                eps REAL,
                dividend_yield REAL,
                fifty_two_week_high REAL,
                fifty_two_week_low REAL
            );
        ''')

        # Time series data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_series_daily (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adjusted_close REAL,
                volume INTEGER,
                dividend_amount REAL,
                split_coefficient REAL,
                PRIMARY KEY (symbol, date)
            );
        ''')

        # Fundamental data tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_statements (
                symbol TEXT,
                fiscal_date_ending TEXT,
                reported_currency TEXT,
                total_revenue INTEGER,
                gross_profit INTEGER,
                net_income INTEGER,
                operating_income INTEGER,
                operating_expense INTEGER,
                interest_expense INTEGER,
                income_before_tax INTEGER,
                PRIMARY KEY (symbol, fiscal_date_ending)
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_sheets (
                symbol TEXT,
                fiscal_date_ending TEXT,
                reported_currency TEXT,
                total_assets INTEGER,
                total_liabilities INTEGER,
                total_shareholder_equity INTEGER,
                cash_and_cash_equivalents INTEGER,
                short_term_debt INTEGER,
                long_term_debt INTEGER,
                PRIMARY KEY (symbol, fiscal_date_ending)
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_flows (
                symbol TEXT,
                fiscal_date_ending TEXT,
                reported_currency TEXT,
                operating_cash_flow INTEGER,
                investing_cash_flow INTEGER,
                financing_cash_flow INTEGER,
                capital_expenditures INTEGER,
                free_cash_flow INTEGER,
                PRIMARY KEY (symbol, fiscal_date_ending)
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earnings (
                symbol TEXT,
                fiscal_date_ending TEXT,
                reported_date TEXT,
                reported_eps REAL,
                estimated_eps REAL,
                surprise REAL,
                surprise_percentage REAL,
                PRIMARY KEY (symbol, fiscal_date_ending)
            );
        ''')

        # Sentiment data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_sentiment (
                symbol TEXT,
                time_published TEXT,
                title TEXT,
                url TEXT,
                source TEXT,
                overall_sentiment_score REAL,
                overall_sentiment_label TEXT,
                PRIMARY KEY (symbol, time_published)
            );
        ''')

        print("Tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        print(f"Error creating tables: {e}")
        conn.close()
        exit(1)


# Helper function to safely convert to float
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# Fetch and store company overview
def fetch_company_overview(symbol):
    params = {
        'function': FUNCTIONS['OVERVIEW'],
        'symbol': symbol,
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if 'Symbol' not in data:
            raise Exception(f"No data for symbol {symbol}")
        cursor.execute('''
            INSERT OR REPLACE INTO symbols (symbol, name, sector, industry, exchange, currency, country, market_cap, pe_ratio, eps, dividend_yield, fifty_two_week_high, fifty_two_week_low)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            data.get('Symbol'),
            data.get('Name'),
            data.get('Sector'),
            data.get('Industry'),
            data.get('Exchange'),
            data.get('Currency'),
            data.get('Country'),
            int(data.get('MarketCapitalization') or 0),
            safe_float(data.get('PERatio')),  # Use safe_float here
            safe_float(data.get('EPS')),      # Use safe_float here
            safe_float(data.get('DividendYield')),  # Use safe_float here
            safe_float(data.get('52WeekHigh')),  # Use safe_float here
            safe_float(data.get('52WeekLow'))    # Use safe_float here
        ))
        conn.commit()
        print(f"Company overview for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching company overview for {symbol}: {e}")
        print(f"Error fetching company overview for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)


# Fetch and store time series data
def fetch_time_series_daily(symbol):
    params = {
        'function': FUNCTIONS['TIME_SERIES_DAILY_ADJUSTED'],
        'symbol': symbol,
        'outputsize': 'full',
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        time_series = data.get('Time Series (Daily)', {})
        if not time_series:
            raise Exception(f"No time series data for symbol {symbol}")
        records = []
        for date_str, daily_data in time_series.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if date < datetime.now().date() - timedelta(days=365*10):
                continue  # Skip data older than 10 years
            records.append((
                symbol,
                date_str,
                float(daily_data.get('1. open', 0)),
                float(daily_data.get('2. high', 0)),
                float(daily_data.get('3. low', 0)),
                float(daily_data.get('4. close', 0)),
                float(daily_data.get('5. adjusted close', 0)),
                int(daily_data.get('6. volume', 0)),
                float(daily_data.get('7. dividend amount', 0)),
                float(daily_data.get('8. split coefficient', 0))
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO time_series_daily (symbol, date, open, high, low, close, adjusted_close, volume, dividend_amount, split_coefficient)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"Time series data for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching time series data for {symbol}: {e}")
        print(f"Error fetching time series data for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)


# Fetch and store income statements
def fetch_income_statement(symbol):
    params = {
        'function': FUNCTIONS['INCOME_STATEMENT'],
        'symbol': symbol,
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        reports = data.get('annualReports', [])
        if not reports:
            raise Exception(f"No income statement data for symbol {symbol}")
        records = []
        for report in reports:
            fiscal_date_ending = report.get('fiscalDateEnding')
            date = datetime.strptime(fiscal_date_ending, '%Y-%m-%d').date()
            if date < datetime.now().date() - timedelta(days=365 * 10):
                continue  # Skip data older than 10 years

            # Use safe_int to handle 'None' or invalid values
            records.append((
                symbol,
                fiscal_date_ending,
                report.get('reportedCurrency'),
                safe_int(report.get('totalRevenue')),  # Use safe_int
                safe_int(report.get('grossProfit')),  # Use safe_int
                safe_int(report.get('netIncome')),  # Use safe_int
                safe_int(report.get('operatingIncome')),  # Use safe_int
                safe_int(report.get('operatingExpenses')),  # Use safe_int
                safe_int(report.get('interestExpense')),  # Use safe_int
                safe_int(report.get('incomeBeforeTax'))  # Use safe_int
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO income_statements (symbol, fiscal_date_ending, reported_currency, total_revenue, gross_profit, net_income, operating_income, operating_expense, interest_expense, income_before_tax)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"Income statements for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching income statements for {symbol}: {e}")
        print(f"Error fetching income statements for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)


# Fetch and store balance sheets
def fetch_balance_sheet(symbol):
    params = {
        'function': FUNCTIONS['BALANCE_SHEET'],
        'symbol': symbol,
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        reports = data.get('annualReports', [])
        if not reports:
            raise Exception(f"No balance sheet data for symbol {symbol}")
        records = []
        for report in reports:
            fiscal_date_ending = report.get('fiscalDateEnding')
            date = datetime.strptime(fiscal_date_ending, '%Y-%m-%d').date()
            if date < datetime.now().date() - timedelta(days=365*10):
                continue  # Skip data older than 10 years
            records.append((
                symbol,
                fiscal_date_ending,
                report.get('reportedCurrency'),
                int(report.get('totalAssets') or 0),
                int(report.get('totalLiabilities') or 0),
                int(report.get('totalShareholderEquity') or 0),
                int(report.get('cashAndCashEquivalentsAtCarryingValue') or 0),
                int(report.get('shortTermDebt') or 0),
                int(report.get('longTermDebt') or 0)
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO balance_sheets (symbol, fiscal_date_ending, reported_currency, total_assets, total_liabilities, total_shareholder_equity, cash_and_cash_equivalents, short_term_debt, long_term_debt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"Balance sheets for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching balance sheet for {symbol}: {e}")
        print(f"Error fetching balance sheet for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)

# Helper function to safely convert to integer
def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

# Fetch and store cash flow statements
def fetch_cash_flow(symbol):
    params = {
        'function': FUNCTIONS['CASH_FLOW'],
        'symbol': symbol,
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        reports = data.get('annualReports', [])
        if not reports:
            raise Exception(f"No cash flow data for symbol {symbol}")
        records = []
        for report in reports:
            fiscal_date_ending = report.get('fiscalDateEnding')
            date = datetime.strptime(fiscal_date_ending, '%Y-%m-%d').date()
            if date < datetime.now().date() - timedelta(days=365*10):
                continue  # Skip data older than 10 years
            records.append((
                symbol,
                fiscal_date_ending,
                report.get('reportedCurrency'),
                safe_int(report.get('operatingCashflow')),         # Use safe_int
                safe_int(report.get('cashflowFromInvestment')),    # Use safe_int
                safe_int(report.get('cashflowFromFinancing')),     # Use safe_int
                safe_int(report.get('capitalExpenditures')),       # Use safe_int
                safe_int(report.get('freeCashFlow'))               # Use safe_int
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO cash_flows (symbol, fiscal_date_ending, reported_currency, operating_cash_flow, investing_cash_flow, financing_cash_flow, capital_expenditures, free_cash_flow)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"Cash flow statements for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching cash flow statements for {symbol}: {e}")
        print(f"Error fetching cash flow statements for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)


# Fetch and store earnings
def fetch_earnings(symbol):
    params = {
        'function': FUNCTIONS['EARNINGS'],
        'symbol': symbol,
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        reports = data.get('annualEarnings', [])
        if not reports:
            raise Exception(f"No earnings data for symbol {symbol}")
        records = []
        for report in reports:
            fiscal_date_ending = report.get('fiscalDateEnding')
            reported_eps = float(report.get('reportedEPS') or 0)
            date = datetime.strptime(fiscal_date_ending, '%Y-%m-%d').date()
            if date < datetime.now().date() - timedelta(days=365*10):
                continue  # Skip data older than 10 years
            records.append((
                symbol,
                fiscal_date_ending,
                None,  # Reported date not available in annual earnings
                reported_eps,
                None,  # Estimated EPS not available in annual earnings
                None,  # Surprise not available in annual earnings
                None   # Surprise percentage not available in annual earnings
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO earnings (symbol, fiscal_date_ending, reported_date, reported_eps, estimated_eps, surprise, surprise_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"Earnings data for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching earnings data for {symbol}: {e}")
        print(f"Error fetching earnings data for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)

# Fetch and store news sentiment
# Fetch and store news sentiment
def fetch_news_sentiment(symbol):
    params = {
        'function': FUNCTIONS['NEWS_SENTIMENT'],
        'tickers': symbol,
        'time_from': (datetime.now() - timedelta(days=365 * 10)).strftime('%Y%m%dT%H%M'),
        'sort': 'LATEST',
        'apikey': API_KEY,
        'limit': 200
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        feed = data.get('feed', [])

        # Check if there is no news sentiment data
        if not feed:
            # Insert a default value if no data is available
            cursor.execute('''
                INSERT OR REPLACE INTO news_sentiment (symbol, time_published, title, url, source, overall_sentiment_score, overall_sentiment_label)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            ''', (symbol, '', '', '', '', 0, ''))
            conn.commit()
            logging.warning(f"No news sentiment data for symbol {symbol}, inserted empty values.")
            print(f"No news sentiment data for symbol {symbol}, inserted empty values.")
            return


        records = []
        for item in feed:
            time_published = item.get('time_published')
            records.append((
                symbol,
                time_published,
                item.get('title'),
                item.get('url'),
                item.get('source'),
                float(item.get('overall_sentiment_score') or 0),
                item.get('overall_sentiment_label')
            ))
        cursor.executemany('''
            INSERT OR REPLACE INTO news_sentiment (symbol, time_published, title, url, source, overall_sentiment_score, overall_sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        ''', records)
        conn.commit()
        print(f"News sentiment data for {symbol} stored.")
    except Exception as e:
        logging.error(f"Error fetching news sentiment for {symbol}: {e}")
        print(f"Error fetching news sentiment for {symbol}: {e}")
        conn.close()
        exit(1)
    time.sleep(SLEEP_INTERVAL)


# Main function to orchestrate data fetching
def main():
    create_tables()
    total_symbols = len(SYMBOLS)
    for idx, symbol in enumerate(SYMBOLS):
        print(f"Processing {symbol} ({idx+1}/{total_symbols})")
        fetch_company_overview(symbol)
        fetch_time_series_daily(symbol)
        fetch_income_statement(symbol)
        fetch_balance_sheet(symbol)
        fetch_cash_flow(symbol)
        fetch_earnings(symbol)
        fetch_news_sentiment(symbol)
        # Implement rate limiting after each symbol
        time.sleep(SLEEP_INTERVAL)

    print("Data retrieval complete.")

if __name__ == '__main__':
    main()
    conn.close()
