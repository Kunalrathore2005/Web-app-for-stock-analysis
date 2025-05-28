from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# MySQL Configuration (using your root/root credentials)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'stock_app_db'
}

# Ticker Mapping
ALL_TICKERS = {
    'apple': 'AAPL', 'aapl': 'AAPL',
    'microsoft': 'MSFT', 'msft': 'MSFT',
    'tesla': 'TSLA', 'tsla': 'TSLA',
    'amazon': 'AMZN', 'amzn': 'AMZN',
    'google': 'GOOG', 'goog': 'GOOG',
    'meta': 'META', 'facebook': 'META',
    'netflix': 'NFLX', 'nflx': 'NFLX',
    'spotify': 'SPOT', 'spot': 'SPOT',
    'nvidia': 'NVDA', 'nvda': 'NVDA',
    'paypal': 'PYPL', 'pypl': 'PYPL',
    'bp': 'BP', 'britishpetroleum': 'BP',
    'jpmorgan': 'JPM', 'jpm': 'JPM',
    'johnsonandjohnson': 'JNJ', 'jnj': 'JNJ',
    'visa': 'V', 'v': 'V',
    'procterandgamble': 'PG', 'pg': 'PG',
    'unitedhealth': 'UNH', 'unh': 'UNH',
    'mastercard': 'MA', 'ma': 'MA',
    'homedepot': 'HD', 'hd': 'HD',
    'disney': 'DIS', 'dis': 'DIS',
    'intel': 'INTC', 'intc': 'INTC',
    'comcast': 'CMCSA', 'cmcsa': 'CMCSA',
    'adobe': 'ADBE', 'adbe': 'ADBE',
    'abbott': 'ABT', 'abt': 'ABT',
    'pfizer': 'PFE', 'pfe': 'PFE',
    'merck': 'MRK', 'mrk': 'MRK',
    'exxonmobil': 'XOM', 'xom': 'XOM',
    'chevron': 'CVX', 'cvx': 'CVX',
    'coca-cola': 'KO', 'ko': 'KO',
    'pepsico': 'PEP', 'pep': 'PEP',
    'walmart': 'WMT', 'wmt': 'WMT',
    'cisco': 'CSCO', 'csco': 'CSCO',
    'mcdonalds': 'MCD', 'mcd': 'MCD',
    'nike': 'NKE', 'nke': 'NKE',
    'ibm': 'IBM', 'ibm': 'IBM',
    'oracle': 'ORCL', 'orcl': 'ORCL',
    'att': 'T', 't': 'T',
    'qualcomm': 'QCOM', 'qcom': 'QCOM',
    'thermofisher': 'TMO', 'tmo': 'TMO',
    'broadcom': 'AVGO', 'avgo': 'AVGO',
    'honeywell': 'HON', 'hon': 'HON',
    'medtronic': 'MDT', 'mdt': 'MDT',
    'eli-lilly': 'LLY', 'lly': 'LLY',
    'unitedparcel': 'UPS', 'ups': 'UPS',
    'starbucks': 'SBUX', 'sbu': 'SBUX',
    'texasinst': 'TXN', 'txn': 'TXN',
    'lowes': 'LOW', 'low': 'LOW',
    'spglobal': 'SPGI', 'spgi': 'SPGI',
    'bristolmyers': 'BMY', 'bmy': 'BMY',
    'amgen': 'AMGN', 'amgn': 'AMGN',
    'philipmorris': 'PM', 'pm': 'PM',
    'altria': 'MO', 'mo': 'MO',
    'caterpillar': 'CAT', 'cat': 'CAT',
    '3m': 'MMM', 'mmm': 'MMM',
    'boeing': 'BA', 'ba': 'BA',
    'goldmansachs': 'GS', 'gs': 'GS',
    'americanexpress': 'AXP', 'axp': 'AXP',
    'schwab': 'SCHW', 'schw': 'SCHW',
    'blackrock': 'BLK', 'blk': 'BLK',
    'raytheon': 'RTX', 'rtx': 'RTX',
    'conocophillips': 'COP', 'cop': 'COP',
    'prologis': 'PLD', 'pld': 'PLD',
    'linde': 'LIN', 'lin': 'LIN',
    'estee': 'EL', 'el': 'EL',
    'danaher': 'DHR', 'dhr': 'DHR',
    'colgate': 'CL', 'cl': 'CL',
    'generaldynamics': 'GD', 'gd': 'GD',
    'emerson': 'EMR', 'emr': 'EMR',
    'ford': 'F', 'f': 'F',
    'humana': 'HUM', 'hum': 'HUM',
    'aig': 'AIG', 'aig': 'AIG',
    'metlife': 'MET', 'met': 'MET',
    'prudential': 'PRU', 'pru': 'PRU',
    'paccar': 'PCAR', 'pcar': 'PCAR',
    'walgreens': 'WBA', 'wba': 'WBA',
    'halliburton': 'HAL', 'hal': 'HAL',
    'schlumberger': 'SLB', 'slb': 'SLB',
    'occidental': 'OXY', 'oxy': 'OXY',
    'eogresources': 'EOG', 'eog': 'EOG',
    'devonenergy': 'DVN', 'dvn': 'DVN',
    'apache': 'APA', 'apa': 'APA',
    'marathonpetro': 'MPC', 'mpc': 'MPC',
    'valero': 'VLO', 'vlo': 'VLO',
    'phillips66': 'PSX', 'psx': 'PSX',
    'hess': 'HES', 'hes': 'HES',
    'marathonoil': 'MRO', 'mro': 'MRO',
    'energyselect': 'XLE', 'xle': 'XLE',
    'target': 'TGT', 'tgt': 'TGT',
    'costco': 'COST', 'cost': 'COST',
    'kraftheinz': 'KHC', 'khc': 'KHC',
    'kimberlyclark': 'KMB', 'kmb': 'KMB',
    'clorox': 'CLX', 'clx': 'CLX',
    'generalmills': 'GIS', 'gis': 'GIS',
    'kellogg': 'K', 'k': 'K',
    'keurig': 'KDP', 'kdp': 'KDP',
    'sysco': 'SYY', 'syy': 'SYY',
    'archerdaniels': 'ADM', 'adm': 'ADM',
    'mondelez': 'MDLZ', 'mdlz': 'MDLZ',
    'kroger': 'KR', 'kr': 'KR'
}

latest_data = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def fetch_stock_data(symbols, start_date=None, end_date=None):
    global latest_data
    try:
        stock_data = yf.download(symbols, start=start_date, end=end_date)['Close']
        if stock_data.empty:
            return None

        stock_data.dropna(inplace=True)
        
        if isinstance(stock_data, pd.Series):
            stock_data = stock_data.to_frame()
            
        data = {
            'dates': stock_data.index.strftime('%Y-%m-%d').tolist(),
            'datasets': [
                {
                    'label': symbol,
                    'data': stock_data[symbol].tolist()
                } for symbol in stock_data.columns
            ]
        }
        
        latest_data = data
        return True
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def fetch_news():
    try:
        url = f'https://newsapi.org/v2/everything?q=stocks&language=en&sortBy=publishedAt&apiKey={'bb678b73f77e411f8e36a887f073dc38'}'
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        return [
            {
                'title': article.get('title', 'No title'),
                'description': article.get('description', 'No description') or 'No description',
                'url': article.get('url', '#'),
                'image': article.get('urlToImage', None)
            } for article in articles[:10]
        ]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return [
            {"title": "News Unavailable", "description": "Could not fetch news. Please try again later.", "url": "#", "image": None}
        ]

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = request.form.get('username')
    password = hashlib.sha256(request.form.get('password').encode()).hexdigest()
    cursor.execute("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        session['user'] = username
        return redirect(url_for('home'))
    return render_template('login.html', message='Invalid credentials, try again.')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        username = request.form.get('username').strip()
        password = hashlib.sha256(request.form.get('password').encode()).hexdigest()
        email = request.form.get('email').strip()
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', message="Username already exists, choose another.")
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                       (username, password, email))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        email = request.form.get('email')
        cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return render_template('reset.html', message='Password reset link sent to your email.')
        conn.close()
        return render_template('reset.html', message='Email not found!')
    return render_template('reset.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    global latest_data
    if 'user' not in session:
        return redirect(url_for('home'))
    
    message = None
    show_graph = False

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        companies_input = request.form.get('companies').strip().lower()
        date_range = request.form.get('date_range').strip()
        companies = [ALL_TICKERS.get(part) for part in companies_input.split() if part in ALL_TICKERS]

        if not companies:
            message = "No valid company names found."
        else:
            try:
                if date_range:
                    start_date, end_date = date_range.split(' - ')
                else:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                success = fetch_stock_data(companies, start_date, end_date)
                if success:
                    show_graph = True
                    for company in companies:
                        cursor.execute("INSERT INTO stock_data (username, company_name, ticker, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                                       (session['user'], company, company, start_date, end_date))
                    conn.commit()
                else:
                    message = "No data available for the selected period."
            except ValueError:
                message = "Invalid date range format. Use YYYY-MM-DD - YYYY-MM-DD."
            finally:
                conn.close()

    news_articles = fetch_news()
    return render_template('index.html', message=message, show_graph=show_graph, username=session['user'], news=news_articles)

@app.route('/data')
def data():
    global latest_data
    if latest_data:
        return jsonify(latest_data)
    return jsonify({'error': 'No data available'}), 404

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, created_at FROM users WHERE username = %s", (session['user'],))
    user_data = cursor.fetchone()  # Fetch once
    conn.close()
    if user_data:
        email = user_data[0]
        created_at = user_data[1]
    else:
        email = 'No email set'
        created_at = 'N/A'
    return render_template('profile.html', username=session['user'], email=email, created_at=created_at)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = session['user']
    cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()  # Fetch once
    email = result[0] if result else ''  # Use the result directly
    if request.method == 'POST':
        new_username = request.form.get('username').strip()
        new_email = request.form.get('email').strip()
        new_password = request.form.get('password').strip()
        if not new_username or not new_email:
            conn.close()
            return render_template('edit_profile.html', message='Username and email required.', username=username, email=email)
        cursor.execute("SELECT username FROM users WHERE username = %s", (new_username,))
        if cursor.fetchone() and new_username != username:
            conn.close()
            return render_template('edit_profile.html', message='Username exists.', username=username, email=email)
        password_hash = hashlib.sha256(new_password.encode()).hexdigest() if new_password else None
        cursor.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE username = %s",
                       (new_username, new_email, password_hash, username))
        conn.commit()
        if new_username != username:
            session['user'] = new_username
        conn.close()
        return redirect(url_for('profile', message='Profile updated.'))
    conn.close()
    return render_template('edit_profile.html', username=username, email=email)

@app.route('/news')
def news():
    if 'user' not in session:
        return redirect(url_for('login'))
    news_articles = fetch_news()
    return render_template('news.html', news=news_articles, username=session['user'])

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/manifest.json')
def manifest():
    return send_file('static/manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_file('static/sw.js')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')