from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import re
import pandas as pd

# 저장할 디렉토리 경로
save_directory = r"..\data\industrial_report_pdf"

# PDF 파일을 다운로드하여 저장하는 함수
def download_pdf(url, filename):
    response = requests.get(url)
    file_path = os.path.join(save_directory, filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    # print(f"{filename} has been downloaded.")

# 파일 이름에서 허용되지 않는 문자를 제거하는 함수
def clean_filename(filename):
    return "".join(c for c in filename if c not in r'\/:*?"<>|')

# URL 인코딩 함수
def custom_quote(s):
    return urllib.parse.quote(s.encode('euc-kr'))

def save_text(content, filename):
    file_path = os.path.join(save_directory, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"{filename} has been saved.")

# 웹 페이지에서 텍스트를 추출하는 함수
def extract_text_from_url(url):
    response = requests.get(url)
    response.encoding = 'euc-kr'
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('td', {'class': 'bbs_detail_view'})
    if content_div:
        message_content = content_div.find('div', {'id': 'messageContentsDiv'}).get_text(strip=True)
        return message_content
    return None
def get_title_from_bbs_layer_icon(url):
    response = requests.get(url)
    response.encoding = 'euc-kr'
    soup = BeautifulSoup(response.text, 'html.parser')
    bbs_layer_icon = soup.find('p', class_='bbs_layer_icon')
    if bbs_layer_icon:
        a_tag = bbs_layer_icon.find('a', {'href': True, 'title': True})
        if a_tag:
            title_text = a_tag['title']
            return title_text
    return None

semiconductor = [
    '반도체'
]

base_url = 'https://securities.miraeasset.com/bbs/board/message/list.do'

encoded_codes = [custom_quote(code) for code in semiconductor]

final_df = pd.DataFrame()

decode_code_list = [];text_filename_list = []; report_title_list=[]; 
report_abstract_list=[]; date_time_list = []
for i, code in tqdm(enumerate(encoded_codes), total=len(encoded_codes)):
    decoded_code = semiconductor[i]
    # for category in [1800, 1525]:
    for category in [1525]:
        for year in range(2014, 2025):
            params = {
                'categoryId': category,
                'selectedId': category,
                'searchType': 2,
                'searchStartYear': year,
                'searchStartMonth': '01',
                'searchStartDay': '01',
                'searchEndYear': year,
                'searchEndMonth': '12',
                'searchEndDay': '31'
            }
            url = (f"{base_url}?categoryId={params['categoryId']}&selectedId={params['selectedId']}"
                   f"&searchType={params['searchType']}&searchStartYear={params['searchStartYear']}"
                   f"&searchStartMonth={params['searchStartMonth']}&searchStartDay={params['searchStartDay']}"
                   f"&searchEndYear={params['searchEndYear']}&searchEndMonth={params['searchEndMonth']}"
                   f"&searchEndDay={params['searchEndDay']}&searchText={code}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tbody_tags = soup.find_all('tbody')
            for i in range(0,len(tbody_tags[1].find_all('td')),4):
                date_time_list.append(tbody_tags[1].find_all('td')[i].get_text(strip=True))
            
            # 모든 subject 태그를 찾기
            subject_tags = soup.find_all('div', class_='subject')
            if len(subject_tags)==0:
                decode_code_list.append(decoded_code)
                text_filename_list.append(str(year)+'년에는 산업분석 보고서가 존재하지 않습니다')
                report_title_list.append('')
                report_abstract_list.append('')
            else:
                for subject_tag in subject_tags:
                    a_tag = subject_tag.find('a', href=True)
                    if not a_tag:
                        continue

                    title_tag = subject_tag.find_previous('td')
                    report_title = title_tag.get_text(strip=True)
                    
                    if 'javascript:view' in a_tag['href']:
                        match = re.search(r"javascript:view\('(\d+)','(\d+)'\)", a_tag['href'])
                        if match:
                            article_id, category_id = match.groups()
                            article_url = (f"https://securities.miraeasset.com/bbs/board/message/view.do?"
                                        f"messageId={article_id}&messageNumber=0&messageCategoryId=0&startId=zzzzz%7E"
                                        f"&startPage=1&curPage=1&searchType=2&searchText={code}&searchStartYear={year}"
                                        f"&searchStartMonth=01&searchStartDay=01&searchEndYear={year}&searchEndMonth=12"
                                        f"&searchEndDay=31&lastPageFlag=&vf_headerTitle=&categoryId={category}&selectedId={category}")
                            
                            text_content = extract_text_from_url(article_url)
                            # if text_content:
                            text_filename = get_title_from_bbs_layer_icon(article_url)
                            # text_filename = clean_filename(f"{decoded_code}]_{article_id}.txt")
                            # save_text(text_content, text_filename)
                            
                            decode_code_list.append(decoded_code)
                            text_filename_list.append(text_filename)
                            report_title_list.append(report_title)
                            report_abstract_list.append(text_content)

            df = pd.DataFrame({"code": decode_code_list, "datetime":date_time_list,
                    "filename": text_filename_list, "report_title": report_title_list,
                        "report_abstract": report_abstract_list})
            final_df = pd.concat([final_df,df],axis=0)

                    
                # if 'javascript:downConfirm' in a_tag['href']:
                #     pdf_url = a_tag['href'].split("'")[1]
                #     title = a_tag['title']
                #     filename = clean_filename(f"{decoded_code}]_{title}")
                #     data.append({"code": decoded_code, "filename": filename,
                #                  "report_title": date_text, "report_abstract": title})
                    
            # PDF 다운로드 링크 추출
            a_tags = soup.find_all('a', href=True)
            for a_tag in a_tags:
                if 'javascript:downConfirm' in a_tag['href']:
                    pdf_url = a_tag['href'].split("'")[1]
                    title = a_tag['title']
                    filename = clean_filename(f"{decoded_code}]_{title}.pdf")
                    download_pdf(pdf_url, filename)


# 데이터프레임 생성 및 저장
df = pd.DataFrame({"code": decode_code_list, "datetime":date_time_list,
                   "filename": text_filename_list, "report_title": report_title_list,
                     "report_abstract": report_abstract_list})
df.to_csv(os.path.join(save_directory, 'industrial_report_data.csv'), index=False, encoding='utf-8')
print("Data saved to report_data.csv")
