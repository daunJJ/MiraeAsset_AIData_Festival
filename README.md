<h1 align="center"> 🚀 군집화를 통한 주요 뉴스 토픽 추출 및 <br> 뉴스 지식 베이스 기반 주가 흐름 분석  AI 서비스 </h1>

## Introduction
**대회 소개**
- 대회명: 제 8회 2024 미래에셋증권 AI•DATA FESTIVAL
- 대회 기간: 2023.07.02~ 2023.07.31
- 주관: 미래에셋증권 X NAVER CLOUD
- 참가자:전국 대학(원)생 300여개 팀

**프로젝트 소개**
- 공모주제: HyperCLOVA X와 함께, AI로 만드는 금융투자의 새로운 경험
- 목적: AI를 활용하여 주식투자의 어려움을 해소하고, 주가 흐름을 정성적으로 분석하기 위한 뉴스 기반 주가 흐름 해석 기능을 제공하고자 함
- 데이터 출처 및 제공
    - 종목별 주가 데이터 (FinanceDataReader)
    - 기업 및 산업 보고서 (미래에셋증권)
    - 네이버 뉴스 기사 (네이버) 
- 참여자
    - [이준희](https://github.com/Ijhee)
    - [정다운](https://github.com/daunJJ)

## Content 
<img src="https://github.com/user-attachments/assets/35e70725-2808-42d2-9161-51ec8ac66ada" width="900"/>

**0. 데이터 수집**
- [종목별 주가 데이터 수집](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/0.%20Data_Collection/indicator_price.py)
- [기업 보고서 크롤링](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/0.%20Data_Collection/corporation_report_crawling.py)
- [산업 보고서 크롤링](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/0.%20Data_Collection/industrial_report_crawling.py)

**1. 골든크로스•데드크로스 판단**
- [크로스 시점 추출](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/1.%20Golden_Death_Cross/golden_cross_death_cross.py)
  
**2. 네이버 뉴스 스크래핑** 
- [네이버 뉴스 동적 크롤링](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/0.%20Data_Collection/NaverNewsDynamicCrawling.py)
- [크로스 시점 뉴스 다운로드](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/0.%20Data_Collection/CrossNewsDownload.py)

**3. 주요 토픽 추출**
- [뉴스 제목 텍스트 임베딩](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/2.%20Embedding/2-1.hyperclovax_embedding.py)
- [BerTopic을 활용한 주요 토픽 추출](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/2.%20Embedding/2-2.BertTopic.ipynb)
- [생성형 AI를 활용한 주요 토픽 네임 생성](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/4.%20Topicname_Generation/hyperclovax_chat_topicname.py)

**4. 뉴스 지식 베이스 생성**
- [주요 토픽 뉴스 요약을 통한 뉴스 지식 베이스 생성](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/3.%20Summary/hyperclovax_summary.py)

**5. 주가 흐름 분석**
- [Knowledge-Intensive LLM을 통한 주가 흐름 분석](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Code/5.%20Knowledge-Intesive-LLM/Knowledge_intensive_LLM.py)

## Presentation
[<img src="https://github.com/user-attachments/assets/91cb05f7-8aa6-4974-a4ee-57e6b411e86b" width="700"/>](https://github.com/daunJJ/MiraeAsset_AIData_Festival/blob/main/Presentation/%EB%AF%B8%EB%9E%98%EC%97%90%EB%8F%84_%EB%B3%B8%EC%84%A0%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf)
