import pandas as pd
import numpy as np
import glob
import re
import os
import math
import pickle
import datetime
import calendar
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 버스 배차간격 전처리
interval_file = pd.read_excel("static/data/bus_data/배차간격(20260108).xlsx")

interval = interval_file[['노선번호', '배차간격']]
interval = interval.rename(columns = {"노선번호": "노선명"})

def convert_to_int_or_str(x):
    try:
        return int(x)  
    except ValueError:
        return str(x) 

# interval["노선명"] = interval["노선명"].apply(convert_to_int_or_str)
interval['시간별버스수'] = round(60 / interval['배차간격'])



# 버스 승하차 총 승객수 전처리
files = glob.glob('static/data/bus_data/*.csv')
dfs = []
#2025년_버스노선별_정류장별_시간대별_승하차_인원_정보(12월)
for file in files:
    df = pd.read_csv(file, encoding='EUC-KR')

    df = df.drop(columns = ['노선번호', '표준버스정류장ID', '역명', '교통수단타입코드', '교통수단타입명', '등록일자'])

    dfs.append(df)


df_all = pd.concat(dfs, ignore_index=True)

df_all["노선명"] = df_all["노선명"].str.replace(r"번\(.*\)", "",  regex=True)
df_all["노선명"] = df_all["노선명"].str.replace(r"\(.*\)", "",  regex=True)
df_all = df_all[~df_all['버스정류장ARS번호'].str.contains('~', na=False)]



# df_all["노선명"] = df_all["노선명"].apply(convert_to_int_or_str)
df_all["노선명"] = df_all["노선명"].astype(str)


for h in range(24):  
    in1 = f"{h:d}시승차총승객수"   # 1시, 2시...
    in2 = f"{h:02d}시승차총승객수" # 00시, 01시...
    out1 = f"{h:d}시하차총승객수"
    out2 = f"{h:02d}시하차총승객수"
    sum_ = f"{h:02d}시승하차순증감승객수"

    for in_bus, out_bus in [(in1, out1), (in2, out2)]:
        if in_bus in df_all.columns and out_bus in df_all.columns:
            df_all[sum_] = df_all[in_bus] - df_all[out_bus]
            df_all.drop(columns=[in_bus, out_bus], inplace=True)



target_cols = df_all.filter(regex="승하차순증감승객수").columns

merged = df_all.merge(interval[["노선명", "시간별버스수"]],
                            on="노선명", how="left")

# 연도와 월 추출
merged["연도"] = merged["사용년월"].astype(str).str[:4].astype(int)
merged["월"] = merged["사용년월"].astype(str).str[-2:].astype(int)
merged = merged.drop(columns = ['사용년월'])

# 월별 일수 계산 (윤년 포함)
merged["일수"] = merged.apply(lambda row: calendar.monthrange(row["연도"], row["월"])[1], axis=1)

merged = merged.dropna()

# 각 승차컬럼을 일수로 나누기
for col in target_cols:
    merged[col] = (merged[col] / merged["일수"]).apply(math.ceil)

# # 노선명를 숫자로 변환, 변환 불가능한 값은 NaN 처리
# merged["노선명_num"] = pd.to_numeric(merged["노선명"], errors="coerce")

# # NaN이 된 행(즉, str 형식 노선명)을 제거
# merged = merged.dropna(subset=["노선명_num"])

# 필요하다면 원래 노선명 대신 숫자형으로 덮어쓰기
# merged["노선명"] = merged["노선명_num"].astype(int)
# merged = merged.drop(columns=["노선명_num"])

# 혼잡도 구하기: 시간별 버스 수로 나누고 해당 버스의 정원으로 나눔

for col in target_cols:
    merged[col] = (merged[col] / merged["시간별버스수"]).apply(math.ceil)

bus_df = merged.sort_values(by="노선명")




# 버스 종류 반환
def classify_bus_type(bus_number: str) -> str:
    if bus_number.startswith('N'):
        return '심야'

    # 마을버스
    if re.search(r'[가-힣A-Za-z]', bus_number) and re.search(r'\d', bus_number):
        return '마을'

    # 숫자만 추출 (앞자리 0 유지)
    match = re.match(r"\d+", bus_number)
    tmp_bus_number = match.group() if match else bus_number

    # 광역버스
    if len(tmp_bus_number) == 4 and tmp_bus_number.startswith('9'):
        return '광역'

    # 지선버스
    if len(tmp_bus_number) == 4:
        return '지선'

    # 간선버스
    if len(tmp_bus_number) == 3:
        return '간선'

    # 순환버스
    if len(tmp_bus_number) == 2:
        return '순환'

    return '알수없음'



# 버스 정원 반환
def classify_bus_capacity(busType: str) -> int:
    if busType == '심야' or busType == '광역' or busType == '간선' or busType == '순환' or busType == '지선':
        return 50
    elif busType == '마을':
        return 35
    elif busType == '광역':
        return 45
    
    return -1

bus_df['버스종류'] = bus_df["노선명"].apply(classify_bus_type)
bus_df['정원'] = bus_df['버스종류'].apply(classify_bus_capacity)

# 혼잡도
for col in target_cols:
    bus_df[col] = (bus_df[col] / bus_df['정원']) * 100
    bus_df[col] = bus_df[col].apply(math.ceil)

bus_df = bus_df[bus_df['노선명'].str.match(r'^\d+$')]

# bus_df.to_csv("bus_data.csv", index=False, encoding="utf-8-sig")

time_cols = [c for c in bus_df.columns if '승하차순증감승객수' in c]
bus_df_melted = bus_df.melt(
    id_vars = ['노선명', '버스정류장ARS번호', '연도', '월'],
    value_vars = time_cols,
    var_name = '시간',
    value_name = '혼잡도'
)

bus_df_melted['시간'] = bus_df_melted['시간'].str.extract(r'(\d+)')

bus_df_melted['노선명'] = bus_df_melted['노선명'].astype(int)

X = bus_df_melted.drop(columns=['혼잡도'])
y = bus_df_melted['혼잡도']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# 모델 훈련 
file_path = "./static/data/bus_rf.pkl"

if os.path.exists(file_path): # 이미 모델을 훈련시켰으면
    # 저장해뒀던 모델 불러옴
    with open("static/data/bus_rf.pkl", "rb") as f:
        loaded_bus_rf = pickle.load(f)
else: # 모델 훈련 처음이면
    # 모델 훈련
    loaded_bus_rf = RandomForestRegressor(n_estimators=50, random_state=42)
    loaded_bus_rf.fit(X_train, y_train)
    with open("static/data/bus_rf.pkl", "wb") as f:
        pickle.dump(loaded_bus_rf, f)

# model = RandomForestRegressor(n_estimators=50, random_state=42)
# model.fit(X_train, y_train)
# with open("bus_rf.pkl", "wb") as f:
#     pickle.dump(model, f)

# with open("data/bus_rf.pkl", "rb") as f:
#         loaded_bus_rf = pickle.load(f)

def pred_bus(busNum, stationNum, DateTime): 

    # 데이터에 존재하지 않는 벗 이면 -1 반환
    if busNum not in bus_df_melted['노선명']:
        return -1

    # DateTime의 날짜/시간 정보 정수형으로 바꿈
    year = DateTime.year
    month = DateTime.month

    time = DateTime.hour * 100 + DateTime.minute 

    # 예측
    pred_res = loaded_bus_rf.predict([[busNum, stationNum, year, month, time]])[0]

    return float(pred_res)


# # 결정 계수
# print(loaded_bus_rf.score(X_test, y_test))
# # 평균 제곱근 오차
# y_pred = loaded_bus_rf.predict(X_test)
# rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# print("RMSE:", rmse)
