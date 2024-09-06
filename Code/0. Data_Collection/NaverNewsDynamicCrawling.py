from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

## 크롤링 함수 
# 크롤링할 url 생성하는 함수: 검색어, 시작 날짜, 종료 날짜 입력 
    # sort=0 : 관련도 순
    # pd = 3: 날짜로 검색
    # ds: 시작 날짜, de: 종료 날짜
    # office_category=3: 경제&IT
def makeUrl(search, start_date, end_date):
    url = "https://search.naver.com/search.naver?where=news&query=" + search + "&sm=tab_opt&sort=0&pd=3&ds=" + str(start_date) + "&de=" + str(end_date) +"&office_category=3"
    print("뉴스 검색 결과 url: ", url)
    return url  

# html에서 원하는 속성을 추출하는 함수: 크롤링할 기사의 원본 링크 
def news_attrs_crawler(articles, attrs):
    attrs_content = []
    for article in articles:
        attrs_content.append(article.attrs[attrs])
    return attrs_content

# 크롤링할 기사의 원본 링크 반환 함수: 검색 결과 url 입력
def articles_crawler(url):
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
    driver.get(url)
    # 아래로 자동 스크롤
    actions = driver.find_element(By.CSS_SELECTOR, 'body')
    start = time.time()
    for i in range(400): 
        actions.send_keys(Keys.END)
        time.sleep(0.1)
    print("스크롤 시간: ", round(time.time() - start, 3))
    # html 파싱하기
    start = time.time()
    original_html = driver.page_source
    html = BeautifulSoup(original_html, "html.parser")
    url_naver = html.select("div.group_news > ul.list_news._infinite_list > li div.news_wrap.api_ani_send > div.news_area > div.news_info > div.info_group> a.info")
    urls = news_attrs_crawler(url_naver, 'href')
    print("검색된 모든 기사 수: ", len(urls))
    print("url 파싱에 걸린 시간: ", round(time.time() - start, 2))
    return urls

# HTML 태그를 제거하는 함수
def remove_html_tags(text):
    if not isinstance(text, str):
        text = str(text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# 불필요한 공백을 제거하는 함수
def remove_unnecessary_whitespace(text):
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()  # 양쪽 끝의 공백 제거
    text = re.sub(r'\s+', ' ', text)  # 여러 개의 공백을 하나의 공백으로 변경
    return text

def make_news_df(urls): 
    # 필요한 내용 담기
    news_titles = []
    news_urls =[]
    news_contents =[]
    news_dates = []

    # NAVER 뉴스만 남기기
    for i in tqdm(range(len(urls))):
        if "news.naver.com" in urls[i]:
            news_urls.append(urls[i])
        else:
            pass
    print("네이버 뉴스 기사 수: ", len(news_urls))

    # 기사 내용 크롤링
    start = time.time()
    for url in tqdm(news_urls):
        #각 기사 html get하기
        news = requests.get(url,headers=headers)
        news_html = BeautifulSoup(news.text,"html.parser")

        # 뉴스 제목 가져오기
        title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
        if title == None:
            title = news_html.select_one("#content > div.end_ct > div > h2")
        
        # 뉴스 본문 가져오기
        content = news_html.select("article#dic_area")
        if content == []:
            content = news_html.select("#articeBody")
        content = ''.join(str(content))

        # html태그제거 및 텍스트 다듬기
        title = remove_html_tags(title)
        content = remove_html_tags(content)
        content = remove_unnecessary_whitespace(content)

        news_titles.append(title)
        news_contents.append(content)

        # 날짜 가져오기
        try:
            html_date = news_html.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
            news_date = html_date.attrs['data-date-time']
        except AttributeError:
            news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
            news_date = remove_html_tags(news_date)
        news_dates.append(news_date)
    print("기사 크롤링에 걸린 시간: ", round(time.time() - start, 2))

    #데이터 프레임 만들기
    news_df = pd.DataFrame({'date':news_dates,'title':news_titles,'link':news_urls,'content':news_contents})

    return news_df
