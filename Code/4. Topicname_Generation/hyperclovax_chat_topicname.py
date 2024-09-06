import sys
import requests
import json
import pandas as pd
import time
from tqdm import tqdm
import re
import numpy as np

##### 1. Chat Completions API Load
def chatbot_api(prompt,query):
  # API 엔드포인트 URL 및 키 설정
  api_url = "https://clovastudio.apigw.ntruss.com/testapp/v1/chat-completions/HCX-003"

  headers = {
          "X-NCP-CLOVASTUDIO-API-KEY": "",
          "X-NCP-APIGW-API-KEY": "",
          "X-NCP-CLOVASTUDIO-REQUEST-ID": "",
          "Content-Type": "application/json"
      }

  # 대화 메시지 설정
  messages = [
      {
          "role": "system",
          "content": prompt
      },
      {
          "role": "user",
          "content": query
      }
  ]

  # 요청 바디 설정
  data = {
      "messages": messages,
      "temperature": 0.3,
      "maxTokens": 500
  }

  # API 호출
  response = requests.post(api_url, headers=headers, data=json.dumps(data))

  # 응답 처리
  if response.status_code == 200:
      result = response.json()
      return result['result']['message']['content']
  else:
      print(f"Error {response.status_code}: {response.text}")

##### 2. Prompt 생성
def generate_prompt(stock,cross):
  
  template = """
    # 절대 유의사항 (반드시 준수해야 함)
    0. (반드시 준수, 안할 시 처벌) **Topic1 : tsmc 관련 삼성전자 소식, Topic9 : 삼성전자 97년도 시총 돌파 과 같이 존재하지 않는 단어를 활용하여 키워드 생성을 하면 안됩니다.**
    1. **당신이 알고 있는 지식을 사용하지 않습니다. **개별 토픽에 대한 설명 내에 있는 단어들로만** 키워드를 구성해야 합니다. 사전 지식은 필요없습니다. 임의로 키워드 생성 하면 안됩니다.**
    2. 전체 토픽의 개수는 반드시 10개입니다. 각 토픽마다 제목을 반드시 제시해야 합니다.
    3. 10개의 개별 토픽마다 제목을 제시하지 않을 경우 강력한 처벌이 주어집니다. 
    4. 'Topic10: 삼성전자-KAIST 로보틱스 인재양성 협약'과 같이 한 개의 토픽에 대해 답변하는 것이 아니라, 개별 토픽(Topic1, Topic2, ...)에 대해 각각 답변해야 합니다.
    5. 개별 토픽에 대한 제목을 제시할 때, **반드시 개별 토픽의 설명만을 기반으로** 답변해야 합니다. 다른 토픽의 설명을 참고하거나 혼합하여 답변하면 절대 안 됩니다.
    6. 반드시 outline에 있는 항목에만 답해야 합니다. 그 외 항목들에 대해 임의로 생성한 답변은 절대 허용되지 않습니다.
    7. **개별 토픽에 대한 설명 내에 있는 단어들로만** 키워드를 구성해야 합니다. **설명 외의 단어를 사용하면 절대 안 됩니다.** 이는 엄격히 강조됩니다.
    8. **예시를 참고하여 비슷하게 생성해야 합니다.**
    9. **연준이라는 단어는 연방준비위원회를 의미합니다. 단어의 줄임말을 사용하지 않아야 합니다.**
    
    # 배경 
    골든 크로스는 단기 이동평균선(50일)이 장기 이동평균선(200일)을 아래에서 위로 교차할 때 발생하는 신호입니다. 이는 주식 시장에서 강한 매수 신호로 간주되며, 주가 상승의 시작을 나타낼 수 있습니다.
    데드 크로스는 단기 이동평균선(50일)이 장기 이동평균선(200일)을 위에서 아래로 교차할 때 발생하는 신호입니다. 이는 주식 시장에서 강한 매도 신호로 간주되며, 주가 하락의 시작을 나타낼 수 있습니다. 

    # 역할/목적
    당신은 뉴스 기사에서 도출된 10개의 토픽들에 대한 설명을 보고, 각 토픽을 대표할 수 있는 이름(키워드 형태)를 제시해야 합니다.
    제시한 토픽의 이름은 {stock} 종목의 뉴스를 토픽 형태로 확인하고 싶은 사람들에게 제공될 것입니다.
  """
  return template.format(stock=stock, cross=cross)


##### 3. Query 생성
def generate_query(stock, cross, query, summary,example):
    template = """
    # 절대 유의사항 (반드시 준수해야 함)
    1. 전체 토픽의 개수는 반드시 10개이며, 각 토픽마다 제목을 반드시 제시해야 합니다. 따라서 총 10개의 키워드를 반드시 제시해야 합니다.
    2. 10개의 개별 토픽마다 제목을 제시하지 않을 경우 강력한 처벌이 주어집니다. 
    3. 'Topic10: 삼성전자-KAIST 로보틱스 인재양성 협약'과 같이 한 개의 토픽에 대해 답변하는 것이 아니라, 개별 토픽에 대해 각각 답변해야 합니다.
    4. 개별 토픽에 대한 제목을 제시할 때, **반드시 개별 토픽의 설명만을 기반으로** 답변해야 합니다. 다른 토픽의 설명을 참고하거나 혼합하여 답변하면 절대 안 됩니다.
    5. 개별 토픽에 대한 설명은 참고 데이터 목차에 제시되어 있습니다.
    6. 해당 뉴스 기사를 기반으로 outline에 대해 대답해야 합니다. 단, outline 중 아는 것에만 대답하고 모르는 내용에 대해서는 절대 대답하지 마십시오. 절대 뉴스 기사에 없는 내용을 생성해서는 안 됩니다.
    7. **개별 토픽에 대한 설명 내에 있는 단어들로만** 키워드를 구성해야 합니다. **설명 외의 단어를 사용하면 절대 안 됩니다.** 이는 엄격히 강조됩니다.
    8. 예시를 참고하여 비슷하게 생성해야 합니다. 예시와 동일한 형식을 유지해야 합니다.

    # 절차/참고 데이터
    1. 나는 {stock} 종목의 {cross} 시점 이전 한 달 동안의 뉴스 기사에 대해 토픽 모델링을 진행했을 때 도출된 토픽에 대한 뉴스 기사 요약본(토픽에 대한 설명)을 제공할 것입니다.
    2. 개별 토픽에 대한 설명 글은 Topic1, 그리고 Topic1에 대한 설명, 그리고 Topic2, 그리고 Topic2에 대한 설명.. 과 같이 데이터가 구성되어 있습니다.
    3. 따라서 Topic1에 대한 키워드를 제시할 때 **반드시 Topic1에 대한 설명을 기반으로** 키워드를 제시해야 합니다. **다른 키워드의 설명을 기반으로 답변하면 절대 안 됩니다.**
    4. **개별 토픽에 대한 설명 내에 있는 단어들로만** 키워드를 구성해야 합니다. **설명 외의 단어를 사용하면 절대 안 됩니다.** 이는 엄격히 강조됩니다.
    5. 예시를 참고하여 비슷하게 생성해야 합니다. 예시와 동일한 형식을 유지해야 합니다.
    
    
    # 개별 토픽에 대한 설명
    {summarys}

    # outline
    {query}

    # 예시
    {example}
    """
    return template.format(stock=stock, cross=cross, query=query, summarys=summary,example=example)

##### 4. 삼성전자 관련 뉴스 내 토픽 이름 생성
# News data load
stock_df = pd.read_excel('/Users/ljhee/Desktop/MiraeAsset_AI_Festival/data/Topic_per_summary/news_df_삼성전자_2023-02-16_summary_3sen.xlsx')

# 변수 설정
stock = "삼성전자"
cross = "골든 크로스"
# outline
query = """"
Topic1: 
Topic2:
Topic3:
Topic4:
Topic5:
Topic6:
Topic7:
Topic8:
Topic9:
Topic10:
"""
# Few-shot
example = """
Topic1:삼성전자 반도체 중장기 투자 계획
Topic2:삼성전자, 갤럭시 S23 시리즈 흥행에 사활
Topic3:이재용 회장의 혁신과 투자 주문

"""
prompt = generate_prompt(stock,cross)

# News Summary Data 
news_summary = ''
for i in range(len(stock_df)):
    news_summary += 'Topic'
    news_summary += str(i+1)
    news_summary += ':'
    news_summary += stock_df.loc[i,'topic_content_summary']
    news_summary += '\n'

# 텍스트 생성
query = generate_query(stock, cross, query, news_summary, example)
samsung_answer = chatbot_api(prompt,query)
print(samsung_answer)

##### 5. 섹터(반도체) 관련 뉴스 내 토픽 이름 생성
# News data load
sector_df = pd.read_excel('..data/Topic_per_summary/news_df_반도체_2023-02-16_summary_3sen.xlsx')

# 변수 설정
stock = "반도체"
cross = "골든 크로스"

# outline
query = """"
Topic1: 
Topic2:
Topic3:
Topic4:
Topic5:
Topic6:
Topic7:
Topic8:
Topic9:
Topic10:
"""

# Few-shot
example ="""
Topic1: 반도체 수출액 감소와 무역적자 우려
Topic2: 뉴욕증시 주요지수 하락과 코스피 상승
Topic3: 중국 진출 제한 규제 및 반도체 투자 세액공제 확대안
"""
prompt = generate_prompt(stock,cross)

# News Summary Data 
news_summary = ''
for i in range(len(sector_df)):
    news_summary += 'Topic'
    news_summary += str(i+1)
    news_summary += ':'
    news_summary += sector_df.loc[i,'topic_content_summary']
    news_summary += '\n'

# 텍스트 생성
query = generate_query(stock, cross, query, news_summary, example)
sector_answer = chatbot_api(prompt,query)
print(sector_answer)