import pandas as pd
from datetime import datetime
import yfinance as yf
from sqlalchemy import create_engine


def fetch_stock_data():
    symbol = "SBIN.NS"
    stock = yf.Ticker(symbol)
    stock_data = stock.history(period="1y")
    
    engine = create_engine(f'postgresql+psycopg2://myuser:mypassword@192.168.56.1:5432/raw_stock_data')
    stock_data.to_sql(name="yfinance_data", con=engine, if_exists='replace', index=False)
    print("data inserted")

fetch_stock_data()
