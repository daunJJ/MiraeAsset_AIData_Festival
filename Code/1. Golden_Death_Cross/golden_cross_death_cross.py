# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager, rc
import os
from tqdm import tqdm

stock_price_data_path = r'..p/data/semiconductor_stock_price.csv'

# 이동평균선을 계산하는 함수
def calculate_moving_averages(df, short_window, long_window):
    df['Short_MA'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['Long_MA'] = df['Close'].rolling(window=long_window, min_periods=1).mean()
    return df

# 골든크로스와 데드크로스를 파악하는 함수
def identify_crosses(df):
    df['Signal'] = 0.0
    df['Signal'][short_window:] = np.where(df['Short_MA'][short_window:] > df['Long_MA'][short_window:], 1.0, 0.0)   
    df['Position'] = df['Signal'].diff()
    return df

# 골든크로스와 데드크로스를 시각화하는 함수
def plot_crosses(df, ticker):
    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'], label='Close Price', color='k', alpha=0.6)
    plt.plot(df['Short_MA'], label=f'Short {short_window}-day MA', color='b', alpha=0.6)
    plt.plot(df['Long_MA'], label=f'Long {long_window}-day MA', color='r', alpha=0.6)

    # 골든크로스와 데드크로스 지점 표시
    golden_crosses = df[df['Position'] == 1]
    dead_crosses = df[df['Position'] == -1]

    plt.plot(golden_crosses.index, df['Short_MA'][df['Position'] == 1], '^', markersize=10, color='b', lw=0, label='Golden Cross')
    plt.plot(dead_crosses.index, df['Short_MA'][df['Position'] == -1], 'v', markersize=10, color='r', lw=0, label='Dead Cross')

    plt.title(f'{ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    
    # 골든크로스와 데드크로스 지점을 강조
    for xc in golden_crosses.index:
        plt.axvline(x=xc, color='b', linestyle='--', lw=0.8)
    for xc in dead_crosses.index:
        plt.axvline(x=xc, color='r', linestyle='--', lw=0.8)

    # 골든크로스와 데드크로스 날짜를 주요 틱으로 추가
    xticks = sorted(golden_crosses.index.tolist() + dead_crosses.index.tolist())
    ax = plt.gca()
    ax.set_xticks(xticks)

    # 기본 단위의 x축 레이블 폰트 크기 줄이기 및 90도 회전
    for label in ax.get_xticklabels():
        label.set_fontsize(8)  # 기본 폰트 크기 줄이기
        label.set_rotation(90)  # 90도 회전

    # 골든크로스와 데드크로스 시점의 x축 레이블 포맷 설정
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # xticks 텍스트 색상 설정
    for xtick in ax.get_xticklabels():
        if xtick.get_text() in golden_crosses.index.strftime('%Y-%m-%d').tolist():
            xtick.set_color('b')
        elif xtick.get_text() in dead_crosses.index.strftime('%Y-%m-%d').tolist():
            xtick.set_color('r')

    plt.gcf().autofmt_xdate()  # x축 레이블 자동 포맷팅
    
    # 그래프 저장
    filename = f"{ticker}_cross_figure.png"
    plt.savefig(filename, dpi=300)
    plt.show()
    
cross_point_df = pd.DataFrame()

# 메인 함수
if __name__ == "__main__":
    df = pd.read_csv(stock_price_data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)  # 일자를 인덱스로 설정
    
    for stock_code in tqdm(df['stock_code'].unique()):
        stock_df = df[df['stock_code'] == stock_code]
        
        if stock_df.empty:
            print(f"No data for stock_code {stock_code}")
            continue
        
        stock_name = stock_df['stock_name'].iloc[0]
        
        short_window = 50
        long_window = 200

        stock_df = calculate_moving_averages(stock_df, short_window, long_window)
        stock_df = identify_crosses(stock_df)
        plot_crosses(stock_df, stock_name)

        dead_cross_df = stock_df[stock_df['Position'] == -1]
        golden_cross_df = stock_df[stock_df['Position'] == 1]
        
        cross_point_df = pd.concat([cross_point_df, dead_cross_df, golden_cross_df], axis=0)

# 결과를 csv로 저장
cross_point_df.to_csv('cross_points.csv', index=True)
