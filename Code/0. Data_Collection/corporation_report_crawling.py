from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import re
import pandas as pd

# 저장할 디렉토리 경로
save_directory = r"..\data\corporation_report_pdf"

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

semiconductor_list = [
    '삼성전자', 'SK하이닉스', 'SK스퀘어', '한미반도체', '리노공업', '테크윙', 'DB하이텍', '이오테크닉스', '동진쎄미켐', 
    '주성엔지니어링', '원익IPS', '솔브레인', '피에스케이홀딩스', '하나마이크론', 'HPSP', 'ISC', '피에스케이', '유진테크', 
    '파두', '하나머티리얼즈', '케이씨텍', '티씨케이', '원익QnC', '에스앤에스텍', '코미코', '제주반도체', '두산테스나', 
    '에프에스티', '덕산테코피아', '해성디에스', '넥스틴', '미코', 'SFA반도체', '에스티아이', '디아이', '젬백스', 
    '오픈엣지테크놀로지', '와이씨', '테스', '제우스', '예스티', '신성이엔지', '칩스앤미디어', '에이디테크놀로지', '동운아나텍', 
    '가온칩스', 'GST', '이엔에프테크놀로지', '에이직랜드', '월덱스', '네패스', '유니셈', '텔레칩스', '인텍플러스', 
    '유니테스트', '브이엠', '티에스이', '어보브반도체', '에이팩트', '네오셈', '티이엠씨', '한솔아이원스', '엘오티베큠', 
    '프로텍', 'KEC', '윈팩', 'LB세미콘', '엑시콘', '디엔에프', 'HLB이노베이션', '케이씨', '기가비스', '케이알엠', 
    '뉴파워프라즈마', '엠케이전자', '한양디지텍', '와이씨켐', '원익홀딩스', '아이텍', '로체시스템즈', '코세스', '퀄리타스반도체', 
    '케이엔제이', '지앤비에스 에코', '넥스트칩', '싸이맥스', '오킨스전자', '자람테크놀로지', '라온텍', '덕산하이메탈', 
    '매커스', '샘씨엔에스', '유니트론텍', '사피엔반도체', '오로스테크놀로지', '에이엘티', '아이엠티', '워트', '씨앤지하이테크', 
    '그린리소스', '비씨엔씨', '하이딥', '엘티씨', '티에프이', '티이엠씨씨엔에스', '미래산업', '라온테크', '타이거일렉', 
    '유니퀘스트', '시그네틱스', '레이저쎌', '아진엑스텍', '케이엔더블유', '네패스아크', '마이크로컨텍솔', '코스텍시스', 
    '미래반도체', '큐알티', '티엘비', '큐에스아이', '제이티', '제너셈', '제이아이테크', '저스템', '엔투텍', 
    '퓨릿', '램테크놀러지', '서플러스글로벌', 'KX하이텍', '지니틱스', '피엠티', '마이크로투나노', '픽셀플러스', 'LB루셈', 
    '다원넥스뷰', '피델릭스', '시지트로닉스', '지오엘리먼트', '메카로', '오디텍', '러셀', '아이앤씨', '네온테크', 
    '더코디', '엔시트론', '한국전자홀딩스', '엑사이엔씨', '성우테크론', '제이엔비', '테크엘'
]

base_url = 'https://securities.miraeasset.com/bbs/board/message/list.do'

encoded_codes = [custom_quote(code) for code in semiconductor_list]

final_df = pd.DataFrame()

decode_code_list = [];text_filename_list = []; report_title_list=[]; 
report_abstract_list=[]; date_time_list = []
for i, code in tqdm(enumerate(encoded_codes), total=len(encoded_codes)):
    decoded_code = semiconductor_list[i]
    # for category in [1800, 1525]:
    for category in [1800]:
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
                text_filename_list.append(str(year)+'년에는 기업분석 보고서가 존재하지 않습니다')
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
df.to_csv(os.path.join(save_directory, 'corporation_report_data.csv'), index=False, encoding='utf-8')
print("Data saved to report_data.csv")