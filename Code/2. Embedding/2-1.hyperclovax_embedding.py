import time
import pandas as pd
import json
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm
import re
from datetime import datetime

def get_embedding(news_title):
    url = "https://clovastudio.apigw.ntruss.com/testapp/v1/api-tools/embedding/clir-emb-dolphin/38dcf11f53da401a9f85da7c74eb66f4"

    headers = {
        "X-NCP-CLOVASTUDIO-API-KEY": "",
        "X-NCP-APIGW-API-KEY": "",
        "X-NCP-CLOVASTUDIO-REQUEST-ID": "",
        "Content-Type": ""
    }

    data = {
        "text": news_title
    }

    response = requests.post(url, headers=headers, json=data)
    
    time.sleep(1)
    
    # 임베딩 결과 반환
    if response.status_code == 200:
        return response.json()['result']['embedding']
    else:
        return [None] * 1024  # 에러 발생 시 None 값으로 채운 리스트 반환

def apply_embeddings(df):
    # tqdm을 사용하여 진행 상황 표시
    tqdm.pandas()
    
    # 각 뉴스 제목에 대해 임베딩 계산
    embeddings = df['title'].progress_apply(get_embedding)
    
    # 임베딩을 DataFrame으로 변환
    embeddings_df = pd.DataFrame(embeddings.tolist(), columns=[f'Embedding_{i}' for i in range(1024)])
    
    # 원래 DataFrame과 결합
    df = pd.concat([df, embeddings_df], axis=1)
    
    return df

# 날짜를 기준으로 정렬하는 함수
def extract_date(filename):
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    if match:
        return datetime.strptime(match.group(), '%Y-%m-%d')
    return None

# 우선순위와 날짜에 따른 정렬 함수
def sort_key(filename):
    if '삼성전자' in filename:
        priority = 2
    elif 'SK하이닉스' in filename:
        priority = 1
    else:
        priority = 0
    date = extract_date(filename)
    return (priority, date)

# dead cross 시점에 해당하는 csv data path 가져오기
dead_open_path = '../data/news/stock/dead'
dead_save_path = '../data/news/stock/dead_embedding'
dead_csv_files = [f for f in os.listdir(dead_open_path) if f.endswith('.csv')]
dead_csv_files = sorted(dead_csv_files, key=sort_key, reverse=True)
dead_open_file_path = [os.path.join(dead_open_path,path) for path in dead_csv_files]
dead_save_file_path = [os.path.join(dead_save_path, f"embedded_{csv_name}") for csv_name in dead_csv_files]

# golden cross 시점에 해당하는 csv data path 가져오기
golden_open_path = '../data/news/stock/golden'
golden_save_path = '../data/news/stock/golden_embedding'
golden_csv_files = [f for f in os.listdir(golden_open_path) if f.endswith('.csv')]
golden_csv_files = sorted(golden_csv_files, key=sort_key, reverse=True)
golden_open_file_path = [os.path.join(golden_open_path,path) for path in golden_csv_files]
golden_save_file_path = [os.path.join(golden_save_path, f"embedded_{csv_name}") for csv_name in golden_csv_files]

# dead,golden cross 시점에 해당하는 sector csv data path 가져오기
sector_open_path = '../data/news/sector'
sector_save_path = '../data/news/sector/sector_embedding'
sector_dead_csv_files = []; sector_golden_csv_files = []
for filename in dead_csv_files:
    sector_dead_csv_files.append(unicodedata.normalize('NFC', filename).replace('삼성전자_dead', '반도체').replace('SK하이닉스_dead', '반도체'))
for filename in golden_csv_files:
    modified_filename = unicodedata.normalize('NFC', filename).replace('삼성전자_golden', '반도체').replace('SK하이닉스_golden', '반도체')
    sector_golden_csv_files.append(modified_filename)
    
sector_dead_open_file_path = [os.path.join(sector_open_path,path) for path in sector_dead_csv_files]
sector_dead_save_file_path = [os.path.join(sector_save_path, f"embedded_{csv_name}") for csv_name in sector_dead_csv_files]

sector_golden_open_file_path = [os.path.join(sector_open_path,path) for path in sector_golden_csv_files]
sector_golden_save_file_path = [os.path.join(sector_save_path, f"embedded_{csv_name}") for csv_name in sector_golden_csv_files]

# 최근순으로 golden cross 1번 sector 1번, dead_cross 1번 sector 1번 진행
all_open_file_path = []
all_save_file_path = []

for i in range(len(golden_open_file_path)):
    if i <= len(dead_open_file_path)-1:
        all_open_file_path.append(golden_open_file_path[i])
        all_open_file_path.append(sector_golden_open_file_path[i])
        all_open_file_path.append(dead_open_file_path[i])
        all_open_file_path.append(sector_dead_open_file_path[i])
        
        all_save_file_path.append(golden_save_file_path[i])
        all_save_file_path.append(sector_golden_save_file_path[i])
        all_save_file_path.append(dead_save_file_path[i])
        all_save_file_path.append(sector_dead_save_file_path[i])
    else:
        all_open_file_path.append(golden_open_file_path[i])
        all_open_file_path.append(sector_golden_open_file_path[i])
        all_save_file_path.append(golden_save_file_path[i])
        all_save_file_path.append(sector_golden_save_file_path[i])

for idx,file_path in enumerate(all_open_file_path):
    # 최근순으로 golden cross 1번 sector 1번, dead_cross 1번 sector 1번 과 같이 데이터 불러오기
    df = pd.read_csv(file_path)
    df.drop(['Unnamed: 0'],axis=1,inplace=True)
    
    print(file_path)
    if 'golden' in file_path:
        
        previous_df = df[df['TargetDate'] == 'P'].copy()
        # Golden -> G / Death -> D
        previous_df.loc[:, 'CrossType'] = 'G'
        
        previous_df = previous_df.drop_duplicates()
        previous_df = previous_df.dropna()
        previous_df.reset_index(drop=True,inplace=True)
        
        if '삼성전자' in file_path:
            # [], ()와 안에 들어가있는 문자 제거, 삼성전자 제거, 특수 기호 제거
            previous_df['title'] = previous_df['title'].apply(lambda x: re.sub(r'\[.*?\]|\(.*?\)|삼성전자|[^가-힣a-zA-Z0-9\s.%↑↓]', '', x))
            print(previous_df['title'])
            previous_df_with_embeddings = apply_embeddings(previous_df)
            
            output_path = all_save_file_path[idx]
            previous_df_with_embeddings.to_csv(output_path, index=False) 
        elif 'SK하이닉스' in file_path:
            previous_df['title'] = previous_df['title'].apply(lambda x: re.sub(r'\[.*?\]|\(.*?\)|SK하이닉스|[^가-힣a-zA-Z0-9\s.%↑↓]', '', x))
            print(previous_df['title'])
            previous_df_with_embeddings = apply_embeddings(previous_df)
            
            output_path = all_save_file_path[idx]
            previous_df_with_embeddings.to_csv(output_path, index=False) 
    
    elif 'dead' in file_path:
        
        previous_df = df[df['TargetDate'] == 'P'].copy()
        # Golden -> G / Death -> D
        previous_df.loc[:, 'CrossType'] = 'D'
        
        previous_df = previous_df.drop_duplicates()
        previous_df = previous_df.dropna()
        previous_df.reset_index(drop=True,inplace=True)
    
        if '삼성전자' in file_path:
            # [], ()와 안에 들어가있는 문자 제거, 삼성전자 제거, 특수 기호 제거
            previous_df['title'] = previous_df['title'].apply(lambda x: re.sub(r'\[.*?\]|\(.*?\)|삼성전자|[^가-힣a-zA-Z0-9\s.%↑↓]', '', x))
            print(previous_df['title'])
            previous_df_with_embeddings = apply_embeddings(previous_df)
            
            output_path = all_save_file_path[idx]
            previous_df_with_embeddings.to_csv(output_path, index=False) 
        elif 'SK하이닉스' in file_path:
            previous_df['title'] = previous_df['title'].apply(lambda x: re.sub(r'\[.*?\]|\(.*?\)|SK하이닉스|[^가-힣a-zA-Z0-9\s.%↑↓]', '', x))
            print(previous_df['title'])
            previous_df_with_embeddings = apply_embeddings(previous_df)
            
            output_path = all_save_file_path[idx]
            previous_df_with_embeddings.to_csv(output_path, index=False)
    
    else:
        previous_df = df[df['TargetDate'] == 'P'].copy()
        # Golden -> G / Death -> D
        previous_df.loc[:, 'CrossType'] = 'N'
        
        previous_df = previous_df.drop_duplicates()
        previous_df = previous_df.dropna()
        previous_df.reset_index(drop=True,inplace=True)

        previous_df['title'] = previous_df['title'].apply(lambda x: re.sub(r'\[.*?\]|\(.*?\)|[^가-힣a-zA-Z0-9\s.%↑↓]', '', x))
        print(previous_df['title'])
        previous_df_with_embeddings = apply_embeddings(previous_df)
        
        output_path = all_save_file_path[idx]
        previous_df_with_embeddings.to_csv(output_path, index=False) 
        
    print(output_path)


