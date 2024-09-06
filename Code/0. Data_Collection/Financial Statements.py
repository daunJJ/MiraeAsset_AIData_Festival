import pandas as pd
from tqdm import tqdm
import OpenDartReader
from collections import defaultdict
import glob

###### 1. 반도체 분야 종목에 대해 재무제표 다운로드
# CSV 파일 읽기
df = pd.read_csv('stock_name.csv', encoding='cp949')

# OpenDartReader API 설정
my_api = "0f429235d11ce8816af3d06d8dd400016feb0251"
dart = OpenDartReader(my_api)

# 연도와 분기 설정
year_todo = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
quarter_todo = ['11013', '11012', '11014', '11011']

year_list = [year for year in year_todo for _ in range(4)]
quarter_list = [quarter for _ in range(11) for quarter in quarter_todo]

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

semiconductor_stock_code_dict = defaultdict(str)
for i in range(len(df['종목명'])):
    if df['종목명'][i] in semiconductor_list:
        semiconductor_stock_code_dict[df['종목코드'][i]] = df['종목명'][i]

save_path = r'C:\Users\leejunhee\OneDrive\바탕 화면\miraeasset\data'

for stock in tqdm(list(semiconductor_stock_code_dict.keys())):
    final_df = pd.DataFrame() # 한 종목의 데이터프레임을 저장할 변수
    for i in range(len(year_list)):
        try:
            stock_df = dart.finstate(stock, year_list[i], reprt_code=quarter_list[i])
            stock_df['stock_code'] = stock
            final_df = pd.concat([final_df, stock_df], axis=0)
        except Exception as e:
            stock_df = [stock,None,year_list[i],quarter_list[i]]
            stock_df.extend([None for _ in range(19)])
            final_df.loc[len(final_df)] = stock_df
            print(f"Error with stock {stock}, year {year_list[i]}, quarter {quarter_list[i]}: {e}")
            continue
        
    # 매 루프마다 CSV 파일로 저장
    final_df['종목명'] = semiconductor_stock_code_dict[stock]
    final_df.to_excel(f'{save_path}/financial_data_{stock}.xlsx', index=False)

###### 2. 개별 종목의 재무제표 하나의 데이터프레임으로 합치기
# 폴더 경로 설정
folder_path = r'C:\Users\leejunhee\OneDrive\바탕 화면\miraeasset\data'

# 폴더 내의 모든 .xlsx 파일을 리스트로 불러오기
xlsx_files = glob.glob(os.path.join(folder_path, '*.xlsx'))

jaemu_df = pd.DataFrame()
for _file in xlsx_files:
    jaemu_df = pd.concat([jaemu_df, pd.read_excel(_file)], axis=0)
    
final_df.to_excel(f'{save_path}/financial_data_{stock}.xlsx', index=False)