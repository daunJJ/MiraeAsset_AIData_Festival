import sys
import requests
import json
import pandas as pd
import time
from tqdm import tqdm
import re
import numpy as np

def chatbot_api(prompt,query,temperature):
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
      "temperature": temperature,
      "maxTokens": 300
  }

  # API 호출
  response = requests.post(api_url, headers=headers, data=json.dumps(data))

  time.sleep(20)
  
  # 응답 처리
  if response.status_code == 200:
      result = response.json()
      return result['result']['message']['content']
  else:
      print(f"Error {response.status_code}: {response.text}")

def generate_prompt(stock,cross,start_date,end_date):
  
  template = """
    # 주의사항
    **현재 {stock}의 골든크로스만 분석할거야. 다른 종목들의 골든크로스는 언급하지마** 
    반드시 outline에 있는 항목에만 답해야해. 그 외 항목들, 특히 골든 크로스 발생 이유를 너가 생성해서 말한다면 반드시 처벌할거야.
    해당 뉴스 기사를 기반으로 outline에 대해 대답해. 단, outline 중 아는 것에만 대답하고 모르는 내용에 대해서는 절대 대답하지 마.
    절대 뉴스 기사에 없는 내용을 생성해서는 안돼. 특히 매출액과 같은 숫자는 반드시 뉴스에 있는 숫자를 그대로 사용해. 너가 마음대로 숫자를 생성할 경우 제일 강한 처벌이 주어져.
    **만약 내가 제공한 뉴스 데이터가 아닌, 너가 학습했던 뉴스 기사 내용을 활용하여 답변을 생성한다면, 반드시 {start_date}부터, {end_date} 사이에 있던 {stock}과 관련된 사건에 관련해서 생성해야 해. 없는 사실을 생성하지 마.**
    ** outline 내 5. 산업 및 시장 동향에서 말하는 경쟁사 상황에서의 경쟁사는 {stock}을 제외한 다른 모든 기업이야.” **
    
    # 배경 
    골든 크로스는 단기 이동평균선(50일)이 장기 이동평균선(200일)을 아래에서 위로 교차할 때 발생하는 신호야. 이는 주식 시장에서 강한 매수 신호로 간주되며, 주가 상승의 시작을 나타낼 수 있어.
    골든 크로스는 시장 참여자들에게 긍정적인 신호를 주어 매수 심리를 자극하기 때문에, 이러한 매수 압력은 주가를 상승시키는 경향이 있어. 
    데드 크로스는 단기 이동평균선(50일)이 장기 이동평균선(200일)을 위에서 아래로 교차할 때 발생하는 신호야. 이는 주식 시장에서 강한 매도 신호로 간주되며, 주가 하락의 시작을 나타낼 수 있어. 
    데드 크로스는 시장 참여자들에게 부정적인 신호를 주어 매도 심리를 자극하기 때문에, 이러한 매도 압력은 주가를 하락시키는 경향이 있어.  

    # 역할/목적
    너는 뉴스 기사를 기반으로 {stock} 종목 주가에 {cross}가 발생한 이유를 분석할거야.
    너가 분석한 내용은 {stock} 종목의 주가 흐름과 원인을 분석하고 싶은 사람들에게 제공될거야. 
  """
  return template.format(stock=stock, cross=cross, start_date=start_date, end_date=end_date)

def generate_query(stock, cross, query, summary,example,start_date,end_date):
    template = """
    # 주의사항
    반드시 outline 에 있는 항목만 답변.
    
    # 절차/참고 데이터
    나는 {stock} 종목의 {cross} 시점 이전 한 달 동안의 뉴스 기사를 너에게 제공할거야. 
    해당 뉴스 기사를 기반으로 outline에 대해 대답해. 단, outline 중 아는 것에만 대답하고 모르는 내용에 대해서는 절대 대답하지 마.
    절대 뉴스 기사에 없는 내용을 생성해서는 안돼. 특히 매출액과 같은 숫자는 반드시 뉴스에 있는 숫자를 그대로 사용해. 너가 마음대로 숫자를 생성할 경우 제일 강한 처벌이 주어져.
    **만약 내가 제공한 뉴스 데이터가 아닌, 너가 학습했던 뉴스 기사 내용을 활용하여 답변을 생성한다면, 반드시 {start_date}일부터, {end_date} 사이에 있던 {stock}과 관련된 사건에 관련해서 생성해야 해. 없는 사실을 생성하지 마.**
    
    뉴스 기사: {summarys}

    outline: {query}

    # 예시
    {example}
    "
    """
    return template.format(stock=stock, cross=cross, query=query, summarys=summary,example=example,start_date=start_date,end_date=end_date)

# 파일 로드
stock_df = pd.read_excel('../data/Topic_per_summary/news_df_삼성전자_2023-02-16_summary_3sen.xlsx')
sector_df = pd.read_excel('../data/Topic_per_summary/news_df_반도체_2023-02-16_summary_3sen.xlsx')

# 변수 설정
stock = "삼성전자"
sector= "반도체"
cross = "골든 크로스"

start_date  = '2023년 1월 16일'
end_date = '2023년 2월 16일'

queries = [
    """
    1. 기업 실적 
        - 매출 증가/감소
        - 분기/연간 실적
    """,
    """
    2. 기업 운영
        - 신제품 출시/개발
        - 사업 확장
        - M&A
    """,
    """
    3. 기업 내부 이슈
        - 경영진 활동
        - 법적 문제
    """,
    """
    4. 투자
        - 기술 투자
        - 해외 투자
        - 연구 개발(R&D) 투자
        - 환경,사회,지배구조(ESG) 투자
    """,
    """
    5. 산업 및 시장 동향
        - 산업 트렌드
        - 경쟁사 상황 
    """,
    """
    6. 외부 환경
        - 경제 지표 (경제 성장률, 금리 인상/인하, 물가 상승, 실업률)
        - 글로벌 이슈
        - 정치적 상황 
    """,
    """
    7. 향후 전망
    """
]

examples = [
    """
    1.기업 실적
    - 매출 증가/감소:
    SK 하이닉스는 매출은 16조4천233억원으로 작년 동기 대비 124.8% 증가했습니다. 매출은 분기 기준 역대 최대 실적으로, 기존 기록인 2022년 2분기 13조8천110억원을 크게 뛰어넘었습니다.
    반면, 4분기 영업이익은 4조 3061억원으로 크게 감소했으며, 특히 반도체 부문은 2000억원대 영업이익을 기록해 부진한 실적을 보였습니다.
    - 분기/연간 실적:
    2022년 4분기 실적에서 매출은 증가했지만 영업이익은 약 70% 급감하여 수익성 개선이 시급한 상황이었습니다.
    """,
    """
    2. 기업 운영
    - 신제품 출시/개발:
    SK 하이닉스는 2021년 LPDDR5X DRAM을 출시하여 모바일 기기에서의 성능과 전력 효율성을 크게 향상시켰습니다. 또한, 176단 3D NAND 플래시를 개발하여 데이터 저장 용량과 처리 속도를 극대화했습니다.
    - 사업 확장:
    SK 하이닉스는 유럽 시장에서의 입지를 강화하기 위해 독일에 새로운 연구개발(R&D) 센터를 설립했습니다. 이 센터는 차세대 메모리 기술 개발과 현지 고객 지원을 목표로 하고 있습니다.
    - M&A:
    SK 하이닉스는 일본 도시바(Toshiba)의 메모리 사업 일부를 인수하여 NAND 플래시 메모리 시장에서의 경쟁력을 높였습니다.
    """,
    """
    3. 기업 내부 이슈
    - 경영진 활동:
    이석희 SK 하이닉스 CEO는 글로벌 반도체 시장에서의 리더십 강화를 위해 미국 실리콘밸리의 주요 기술 기업들과 협력 관계를 강화했습니다. 이를 통해 기술 혁신과 새로운 비즈니스 기회를 모색하고 있습니다.
    - 기술 및 인프라 투자:
    SK 하이닉스는 2021년 청주에 새로운 반도체 제조 공장을 건설하기 시작했으며, 이는 차세대 메모리 제품의 생산 능력을 확대하기 위한 전략의 일환입니다. 이 공장은 2024년 완공을 목표로 하고 있습니다.
    SK 하이닉스는 또한 포항공대(POSTECH)와 협력하여 '스마트 팩토리' 프로젝트를 진행하고 있으며, 이를 통해 생산 공정의 자동화와 효율성을 극대화하고 있습니다.
    - 법적 문제:
    기간 내 SK 하이닉스는 미국에서의 특허 침해 소송에서 승소하여 법적 리스크를 최소화했습니다. 이는 회사의 기술적 우위와 법적 대응 능력을 보여줍니다.
    """,
    """
    4. 투자
    - 기술 투자:
    SK 하이닉스는 2022년부터 2026년까지 5년간 120조 원을 투자하여 메모리 반도체 연구개발(R&D)과 생산 능력을 확장할 계획입니다. 이는 차세대 메모리 기술 개발과 시장 점유율 확대를 위한 전략적 투자입니다.
    - 해외 투자:
    SK 하이닉스는 중국 우시에 위치한 공장을 최신 기술로 업그레이드하고 생산 라인을 확장하여 중국 시장에서의 경쟁력을 강화하고 있습니다.
    - 연구 개발(R&D) 투자:
    SK 하이닉스는 AI 및 머신러닝 기반의 반도체 설계 기술을 개발하기 위해 글로벌 AI 연구기관들과 협력하고 있습니다. 이를 통해 차세대 반도체 제품의 성능을 획기적으로 개선할 계획입니다.
    - 환경,사회,지배구조(ESG) 투자:
    SK 하이닉스는 탄소 중립 목표 달성을 위해 재생 에너지 사용을 확대하고 있으며, 2025년까지 모든 사업장에서 재생 에너지를 100% 사용하기로 약속했습니다. 또한, 지역 사회와의 협력을 통해 사회적 책임을 다하고 있습니다.
    """
    ,
    """
    5. 산업 및 시장 동향
    - 산업 트렌드:
    2021년 말, 반도체 산업은 전 세계적인 칩 부족 현상으로 인해 큰 변화를 겪고 있습니다. SK 하이닉스는 이를 기회로 삼아 D램과 NAND 플래시 메모리의 생산을 대폭 확대하고 있습니다. 특히, 자율주행차와 5G 스마트폰의 수요 증가로 인해 고성능 메모리 제품의 시장이 급성장하고 있습니다.
    - 경쟁사 상황:
    SK 하이닉스는 삼성전자와의 경쟁에서 기술 혁신과 생산 효율성 면에서 두각을 나타내고 있습니다. 또한, 마이크론과의 경쟁에서도 품질과 가격 경쟁력을 통해 시장 점유율을 확대하고 있습니다. SK 하이닉스는 특히 고부가가치 제품에서 강세를 보이며, 경쟁사 대비 높은 이익률을 유지하고 있습니다.
    - 정부 규제, 환경 정책:
    한국 정부는 반도체 산업의 경쟁력 강화를 위해 연구개발(R&D) 지원과 세제 혜택을 확대하고 있습니다. 또한, SK 하이닉스는 정부의 친환경 정책에 발맞춰 탄소 배출을 줄이기 위한 다양한 환경 프로젝트를 진행 중입니다. 미국과 유럽의 새로운 규제에도 유연하게 대응하고 있습니다.
    """,
    """
    6. 외부 환경
    - 경제 지표:
        - 경제 성장률: 2021년 한국의 경제 성장률은 4.2%로, 코로나19 팬데믹 이후 회복세를 보이고 있습니다.
        - 금리 인상/인하: 한국은행은 기준금리를 1.0%로 인상하며, 인플레이션 압력을 완화하고 경제 성장을 지속적으로 지원하고 있습니다.
    - 글로벌 이슈:
    미-중 기술 패권 경쟁: 미국과 중국 간의 기술 패권 경쟁이 심화되면서, 반도체 공급망의 지역화와 자국 중심의 생산이 중요해지고 있습니다. SK 하이닉스는 이 변화에 대응하기 위해 글로벌 생산 기지를 다변화하고 있습니다.
    - 정치적 상황:
    한국 정부의 지원: 한국 정부는 반도체 인재 양성을 위해 대규모 장학금 프로그램과 산학 협력 프로젝트를 추진하고 있습니다. 이를 통해 미래 기술 인재를 확보하고, 산업의 지속적인 성장을 도모하고 있습니다.
    """,
    """
    7. 향후 전망
    반도체 수출 전망:
    수출 회복 기대: 반도체 수출은 2022년 상반기 동안 다소 부진할 것으로 예상되지만, 하반기 이후 글로벌 경제 회복과 함께 수요가 증가할 것으로 기대되고 있습니다. 특히, 전기차와 데이터 센터의 확대로 인해 메모리 반도체의 수요가 급증할 전망입니다.
    기술 발전 및 시장 변화:
    AI 반도체 시장 성장: 인공지능(AI) 기술 발전에 따라 AI 반도체의 수요가 급격히 증가하고 있습니다. SK 하이닉스는 이러한 시장 변화에 발맞춰 고성능 AI 반도체 개발에 집중하고 있습니다.
    차세대 D램 DDR5: DDR5의 보급 속도가 예상보다 빠르게 진행되고 있으며, 이는 메모리 반도체 업계에 긍정적인 영향을 미칠 것입니다. SK 하이닉스는 이를 통해 고부가가치 제품군을 강화할 계획입니다.
    정부 및 정책적 지원:
    정부의 반도체 인재 양성: 한국 정부는 반도체 인재 양성을 위해 전국 대학과 협력하여 맞춤형 교육 프로그램을 운영하고 있으며, 향후 5년간 4,000명 이상의 전문 인력을 양성할 계획입니다. 이는 반도체 산업의 경쟁력 강화를 위한 중요한 기반이 될 것입니다.
    글로벌 반도체 규제 변화: 미국, 유럽, 아시아 지역의 반도체 규제 변화에 대응하여 SK 하이닉스는 글로벌 생산 체인의 안정성을 확보하고, 각국의 규제에 신속히 대응할 수 있는 체제를 구축하고 있습니다.
    """
]

def generate_news_summary(df):
    news_summary = ''
    for i in range(len(df)):
        news_summary += '뉴스' + str(i+1) + '.' + df.loc[i, 'topic_content_summary']
    return news_summary

def generate_queries(stock, cross, queries, news_summary, examples,start_date,end_date):
    return [generate_query(stock, cross, q, news_summary, e,start_date,end_date) for q, e in zip(queries, examples)]

# 주식별 텍스트 생성
stock_prompt = generate_prompt(stock, cross,start_date,end_date)
sector_prompt = generate_prompt(sector, cross,start_date,end_date)

stock_summary = generate_news_summary(stock_df)
sector_summary = generate_news_summary(sector_df)

stock_query = generate_queries(stock, cross, queries[:4], stock_summary, examples[:4],start_date,end_date)
sector_query = generate_queries(sector, cross, queries[4:], sector_summary, examples[4:],start_date,end_date)

# 챗봇 응답
temperature_list = [0.2,0.2,0.2,0.4,0.15,0.15,0.15]
stock_answer = [chatbot_api(stock_prompt, q, temperature_list[i]) for i, q in enumerate(stock_query)]
sector_answer = [chatbot_api(sector_prompt, q, temperature_list[i]) for i, q in enumerate(sector_query)]

# 출력
for answer in stock_answer + sector_answer:
    print(answer)
