import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from NaverNewsDynamicCrawling import makeUrl
from NaverNewsDynamicCrawling import articles_crawler
from NaverNewsDynamicCrawling import make_news_df

## 크로스 시점 추출 
# 종목별 크로스 시점 데이터 불러오기 
df = pd.read_csv('../data/cross/sector/cross_points.csv')
# 삼성전자만 추출
stock_df = df[df['stock_code']==5930]

## 뉴스 기사 저장 
def cross_news_data(row):
    # 골든, 데드 판단
    if row['Position'] == -1:
        cross = 'dead'
    elif row['Position'] == 1:
        cross = 'golden'
    # 검색 키워드: 종목명
    stock = row['stock_name']
    # 검색 키워드: 섹터명 -> 원본 데이터에 추가하기 
    sector = '반도체'
    # 기준 시점: 크로스 시점
    standard_date = row['Date']
    print("크로스: ", cross, ", 시점: ", standard_date)
    # 기준, 이전, 이후 시점 생성 
    original_date = datetime.strptime(standard_date, '%Y-%m-%d')
    previous_date = original_date - relativedelta(months=1)
    #next_date = original_date + relativedelta(months=1)
    # '%Y.%m.%d' 형식으로 변경 
    original_date = original_date.strftime('%Y.%m.%d')
    previous_date = previous_date.strftime('%Y.%m.%d')
    #next_date = next_date.strftime('%Y.%m.%d')
    # [종목]
    # 크로스 이전 종목 뉴스 데이터 저장 
    url = makeUrl(stock, previous_date, original_date)
    urls = articles_crawler(url)
    news_df_previous = make_news_df(urls)
    news_df_previous['TargetDate'] = 'P'
    # 크로스 이후 종목 뉴스 데이터 저장 -> 이후 제외 
    #url = makeUrl(stock, original_date, next_date)
    #urls = articles_crawler(url)
    #news_df_next = make_news_df(urls)
    #news_df_next['TargetDate'] = 'N'
    # 이전, 이후를 합쳐서 저장
    #news_df = pd.concat([news_df_previous, news_df_next], ignore_index=True)
    news_df_previous.to_csv('../data/news/stock/{}/news_df_{}_{}_{}.csv'.format(cross, stock, cross, standard_date))
    # [섹터]
    # 크로스 이전 섹터 뉴스 데이터 저장 
    url = makeUrl(sector, previous_date, original_date)
    urls = articles_crawler(url)
    news_df_previous = make_news_df(urls)
    news_df_previous['TargetDate'] = 'P'
    # 크로스 이후 섹터 뉴스 데이터 저장 -> 이후 제외 
    #url = makeUrl(sector, original_date, next_date)
    #urls = articles_crawler(url)
    #news_df_next = make_news_df(urls)
    #news_df_next['TargetDate'] = 'N'
    # 이전, 이후를 합쳐서 저장
    #news_df = pd.concat([news_df_previous, news_df_next], ignore_index=True)
    news_df_previous.to_csv('../data/news/sector/news_df_{}_{}.csv'.format(sector, standard_date))

# 뉴스 기사 추출을 원하는 [종목]의 크로스 데이터를 넣기 
stock_df.apply(cross_news_data, axis=1)
