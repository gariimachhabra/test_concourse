import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(f'postgresql+psycopg2://concourse_user:concourse_pass@172.24.0.2:5432/concourse')
select_query = "SELECT * FROM yfinance_data;"
df = pd.read_sql(select_query, engine)

print(df.head())
print(df.info())
print(df.describe())