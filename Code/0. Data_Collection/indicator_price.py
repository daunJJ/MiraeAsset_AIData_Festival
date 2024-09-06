# %%
# !pip install finance-datareader
import pandas as pd
from collections import defaultdict
import FinanceDataReader as fdr
from tqdm import tqdm

######### 1. 반도체 분야 주식들의 주가 데이터 구축
df = pd.read_csv('semiconductor_stock_list.csv')
df['stock_code'] = df['stock_code'].astype(str).str.zfill(6)

final_df = pd.DataFrame()
for stock in tqdm(df['종목코드']):
    stock_df = fdr.DataReader(stock)
    min_date = stock_df.index.min()
    if min_date< pd.Timestamp('2014-01-01'):
        try:
            stock_df = pd.DataFrame(fdr.DataReader(stock, start='2014-01-01', end='2024-06-30')).reset_index()
            stock_df['stock_code'] = [stock for i in range(len(stock_df))]
            final_df = pd.concat([final_df, stock_df],axis=0)
        except:
            pass
    else:
        try:
            stock_df = pd.DataFrame(fdr.DataReader(stock, start=min_date, end='2024-06-30')).reset_index()
            stock_df['stock_code'] = [stock for i in range(len(stock_df))]
            final_df = pd.concat([final_df, stock_df],axis=0)
        except:
            pass

name = pd.read_csv('semiconductor_stock_list.csv')
name['stock_code'] = name['stock_code'].astype(str).str.zfill(6)
merged_df = pd.merge(final_df, name, how='inner', on='stock_code')

final_df.to_csv('semiconductor_stock_price.csv',index=False)