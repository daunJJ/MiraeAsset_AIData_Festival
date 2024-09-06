import sys
import requests
import json
import pandas as pd
import time
from tqdm import tqdm
import re
import numpy as np

def summary_api(news_content,summarycount):
  client_id = ''
  client_secret = ''
  url = 'https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize'

  headers = {
              'Accept': 'application/json;UTF-8',
              'Content-Type': 'application/json;UTF-8',
              'X-NCP-APIGW-API-KEY-ID': client_id,
              'X-NCP-APIGW-API-KEY': client_secret
          }

  data = {
    "document": {
      "content": news_content
    },
    "option": {
      "language": "ko",
      "model": "news",
      "tone": 2,
      "summaryCount": summarycount
    }
  }

  response = requests.post(url, headers=headers, data=json.dumps(data).encode('UTF-8'))
  rescode = response.status_code
  
  # time.sleep(1)
  
  if(rescode == 200):
      response_json = response.json()  # JSON으로 변환
      return response_json['summary']  # 'summary' 키에 접근
  else:
      print("Error : " + response.text)
      return ''

       
def data_processing(path):

  df = pd.read_excel(path)
  df['content_summary'] = ''
  df['content'] = df['content'].apply(lambda x: x.replace('[', '').replace(']', '').replace('이데일리','').replace('기자',''))
  df['content'] = df['content'].apply(lambda x: x.strip())
  
  return df


def extract_topic5(df):
  df = df
  topic_df = pd.DataFrame()
  for topic in df['topic'].unique():
    topic_temp = df[df['topic']==topic]
    topic_temp.reset_index(drop=True,inplace=True)
    idx_list = []
    for i in range(len(topic_temp)):
      if (len(topic_temp.loc[i,'content'])>100)&(len(topic_temp.loc[i,'content'])<2000):
        idx_list.append(i)
      else:
        pass
    topic_temp = topic_temp.loc[idx_list,:]
    
    topic_temp.sort_values(by=['distance_to_center'],inplace=True)
    topic_df = pd.concat([topic_df,topic_temp.iloc[:5,:]])
    
  return topic_df
  
def summary_topic(df):
  topic_summary_df = pd.DataFrame()
  topic_summary_df['topic'] = np.nan
  topic_summary_df['topic_name'] = np.nan
  topic_summary_df['topic_content_summary'] = np.nan
  topic_summary_df['TargetDate'] = np.nan
  topic_summary_df['CrossType'] = np.nan

  for idx,topic in enumerate(df['topic'].unique()):
    topic_df = df[df['topic']==topic]

    topic_df.reset_index(drop=True,inplace=True)
    topic_summary_df.loc[idx,'topic'] = topic_df.loc[0,'topic']
    topic_summary_df.loc[idx,'topic_name'] = topic_df.loc[0,'topic_name']
    topic_summary_df.loc[idx,'TargetDate'] = topic_df.loc[0,'TargetDate']
    topic_summary_df.loc[idx,'CrossType'] = topic_df.loc[0,'CrossType']
    
    topic_summary = ''
    for _content in topic_df['content_summary']:
      topic_summary += _content
      topic_summary += '\n'
    if len(topic_summary) >= 2000:
      topic_summary = topic_summary[:1980]
    topic_summary_df.loc[idx,'topic_content_summary'] = summary_api(topic_summary,2)
    
  return topic_summary_df
#################### stock ####################
######## 1. 데이터 전처리
path = '../data/BERTopic_10docs/embedded_news_df_삼성전자_golden_2023-02-16_BERTopic_10.xlsx'
df = data_processing(path)
######## 2. 각 토픽 -> 5개의 기사만 추출
topic_df = extract_topic5(df)
# 2-1. topic 2,11 제거(text가 특수문자를 기준으로 클러스터링 되었으며, 클러스터 내 내용이 많지 않음)
df = topic_df[topic_df['topic']!=2]
df = df[df['topic']!=11]
df.reset_index(inplace=True,drop=True)

######### 3. 각 기사 -> 3문장으로 요약
for i in tqdm(range(len(df))):
  df.loc[i,'content_summary'] = summary_api(df.loc[i,'content'],3)

######### 4. 토픽별로 5개의 기사 요약본 -> 1개의 기사 요약본(300자 이내)로 요약
stock_summary_df = summary_topic(df)
stock_summary_df.to_excel('../data/Topic_per_summary/news_df_삼성전자_2023-02-16_summary_3sen.xlsx',index=False)

#################### Sector #################### 
######## 1. 데이터 전처리
path = '../data/BERTopic_10docs/embedded_news_df_반도체_2023-02-16_BERTopic_10.xlsx'
df = data_processing(path)

######## 2. 각 토픽 -> 5개의 기사만 추출
topic_df = extract_topic5(df)
# 2-1. topic 10개만 선정(text가 특수문자를 기준으로 클러스터링 되었으며, 클러스터 내 내용이 많지 않음)
df = topic_df[topic_df['topic']<=9]
df.reset_index(inplace=True,drop=True)

######### 3. 각 기사 -> 3문장으로 요약
for i in tqdm(range(len(df))):
  df.loc[i,'content_summary'] = summary_api(df.loc[i,'content'],3)

######### 4. 토픽별로 5개의 기사 요약본 -> 1개의 기사 요약본(300자 이내)로 요약
sector_summary_df = summary_topic(df)
sector_summary_df.to_excel('../data/Topic_per_summary/news_df_반도체_2023-02-16_summary_3sen.xlsx',index=False)

