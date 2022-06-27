import pandas as pd
import numpy as np
from io import BytesIO
from matplotlib import pyplot as plt
from sqlalchemy import create_engine


db_conn_str = 'mysql://root:''@localhost/db2'
db_conn = create_engine(db_conn_str)
df = pd.read_sql('SELECT * FROM data', con=db_conn)

df_tail = df.tail()

made = df_tail['ft_made'].sum()
total = df_tail['ft_attempted'].sum()
last5 = round(made/total, 2) * 100

total_made = df['ft_made'].sum()
total_total = df['ft_attempted'].sum()
total_percent = round(total_made/total_total, 2) * 100

print(last5)
print(total_percent)
