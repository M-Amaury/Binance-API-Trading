import requests
import json
import sqlite3

# Get a list of all available cryptocurrencies
def get_cryptocurrencies():
  response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
  data = response.json()
  cryptocurrencies = []
  for symbol in data['symbols']:
      cryptocurrencies.append(symbol['symbol'])
  return cryptocurrencies

print(get_cryptocurrencies())

# Display the 'ask' or 'bid' price of an asset
def get_depth(direction='ask', pair='BTCUSDT'):
  response = requests.get(f'https://api.binance.com/api/v3/ticker/bookTicker?symbol={pair}')
  data = response.json()
  if direction == 'ask':
    price = data['askPrice']
  elif direction == 'bid':
    price = data['bidPrice']
  else:
    raise ValueError("Invalid value for 'direction'. Must be 'ask' or 'bid'.")
  return price

print(get_depth())  # Display the 'ask' price for BTCUSDT
print(get_depth(pair='ETHUSDT', direction='bid'))  # Display the 'bid' price for ETHUSDT

# Get the order book for an asset
def get_order_book(pair='BTCUSDT'):
  response = requests.get(f'https://api.binance.com/api/v3/depth?symbol={pair}&limit=100')
  data = response.json()
  order_book = data['bids'], data['asks']
  return order_book

print(get_order_book())  # Get the order book for BTCUSDT
print(get_order_book('ETHUSDT'))  # Get the order book for ETHUSDT

# Create a function to read aggregated trading data (candles)
def refresh_data_candle(pair='BTCUSDT', duration='5m'):
  response = requests.get(f'https://api.binance.com/api/v3/klines?symbol={pair}&interval={duration}')
  data = response.json()
  candles = []
  for candle in data:
    candles.append({
      'date': candle[0],
      'high': candle[2],
      'open': candle[1],
      'close': candle[4],
      'volume': candle[5],
      })
  return candles

print(refresh_data_candle())  # Get the candle data for BTCUSDT, 5-minute duration
print(refresh_data_candle(pair='ETHUSDT', duration='15m'))  # Get the candle data for ETHUSDT, 15-minute duration

# Create a SQLite table to store the candle data
def create_table_candles(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE candles (
                    Id INTEGER PRIMARY KEY,
                    date INT,
                    high REAL,
                    open REAL,
                    close REAL,
                    volume REAL
                )''')
    conn.commit()


# Store the candle data in the database
def store_candles(conn, candles):
    c = conn.cursor()
    for candle in candles:
        c.execute('''INSERT INTO candles (date, high, open, close, volume)
                      VALUES (?,?,?,?,?)''',
                  (candle['date'], candle['high'], candle['open'], candle['close'], candle['volume']))
    conn.commit()

# Modify refresh_data_candle() to update when new candle data is available
def refresh_and_store_candles(conn, pair='BTCUSDT', duration='5m'):
    # Get the latest candle data
    candles = refresh_data_candle(pair, duration)
    # Store the candle data in the database
    store_candles(conn, candles)

# Create a function to extract all available trade data
def refresh_data(pair='BTCUSDT'):
    response = requests.get(f'https://api.binance.com/api/v3/trades?symbol={pair}&limit=100')
    data = response.json()
    trades = []
    for trade in data:
        trades.append({
            'uuid': trade['id'],
            'traded_crypto': trade['qty'],
            'price': trade['price'],
            'created_at_int': trade['time'],
            'side': trade['isBuyerMaker']
        })
    return trades

print(refresh_data())  # Get the trade data for BTCUSDT
print(refresh_data(pair='ETHUSDT'))  # Get the trade data for ETHUSDT

# Store the trade data in the database
def store_trades(conn, trades):
    c = conn.cursor()
    for trade in trades:
        c.execute('''INSERT INTO trades (uuid, traded_crypto, price, created_at_int, side)
                      VALUES (?,?,?,?,?)''',
                  (trade['uuid'], trade['traded_crypto'], trade['price'], trade['created_at_int'], trade['side']))
    conn.commit()

# Create an order
def create_order(api_key, secret_key, direction, price, amount, pair='BTCUSDT', order_type='LimitOrder'):
    # Set the API endpoint and headers
    endpoint = 'https://api.binance.com/api/v3/order'
    headers = {'X-MBX-APIKEY': api_key}
    # Set the request payload
    payload = {
        'symbol': pair,
        'side': direction,
        'type': order_type,
        'price': price,
        'quantity': amount
    }
    # Make a POST request to the API endpoint
    response = requests.post(endpoint, headers=headers, json=payload)
    # Return the response data
    return response.json()

# Cancel an order
def cancel_order(api_key, secret_key, uuid):
    # Set the API endpoint and headers
    endpoint = f'https://api.binance.com/api/v3/order?symbol=BTCUSDT&orderId={uuid}'
    headers = {'X-MBX-APIKEY': api_key}
    # Make a DELETE request to the API endpoint
    response = requests.delete(endpoint, headers=headers)
    # Return the response data
    return response.json()

# Set up the SQLite database
conn = sqlite3.connect('my_database.db')
create_table_candles(conn)
create_table_trades(conn)
create_table_last_checks(conn)

# Example usage: refresh and store the candle data for BTCUSDT, 5-minute duration
refresh_and_store_candles(conn, pair='BTCUSDT', duration='5m')

# Example usage: get the trade data for BTCUSDT and store it in the database
trades = refresh_data(pair='BTCUSDT')
store_trades(conn, trades)

# Example usage: create a limit order to buy 1 BTC at a price of 10000 USDT
api_key = 'your_api_key'
secret_key = 'your_secret_key'
response = create_order(api_key, secret_key, 'BUY', '10000', '1')
print(response)

# Example usage: cancel the order with the specified UUID
uuid = 'your_order_uuid'
response = cancel_order(api_key, secret_key, uuid)
print(response)

# Close the connection to the database
conn.close()