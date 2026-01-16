import os
import glob
import pickle
import folium
import matplotlib
import numpy as np
import pandas as pd
from folium import Element
import matplotlib.pyplot as plt
from html2image import Html2Image
from datetime import datetime, date
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

files = glob.glob('static/data/subway_data/*.csv')
dfs = []

colors = {
    1: '#0052a4',
    2: '#00a84d',
    3: '#ef7c1c',
    4: '#00a5de',
    5: '#996cac',
    6: '#cd7c2f',
    7: '#747f00',
    8: '#e6186c',
    9: '#bdb092'
}

# 지하철 데이터 가져와서 전처리
for file in files:
    # 날짜 추출
    basename = file.replace('.csv', '')
    date_str = basename[40:]
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    df = pd.read_csv(file, encoding='EUC-KR')

    # 년도마다 컬럼 이름이 조금씩 달라서 조정 + 필요없는 컬럼 제거
    if '연번' in df.columns:
        df = df.drop(columns=['연번'])
    if '조사일자' in df.columns:
        df = df.rename(columns={'조사일자': '요일구분'})
    if '구분' in df.columns:
        df = df.rename(columns={'구분': '상하구분'})

    # 호선 컬럼에 있는 데이터 정수화
    df['호선'] = df['호선'].astype(str).str.extract('(\d+)').astype(int)

    # 공백 제거
    df['요일구분'] = df['요일구분'].str.strip()

    # 날짜 컬럼 추가
    df["년도"] = year
    df["월"] = month
    df["일"] = day

    dfs.append(df)


df_all = pd.concat(dfs, ignore_index=True)

# 시간을 입력값으로 만들기 위해 melt
time_cols = [c for c in df_all.columns if '시' in c]
df_melted = df_all.melt(
    id_vars=['요일구분','역번호','상하구분','년도','월','일'],
    value_vars=time_cols,
    var_name='시간',
    value_name='혼잡도'
)

# 그래프 등에서 "n시 n분" 형태로 사용하기 위해 전처리 전 str형식으로 저장
timeStr = df_melted['시간'].unique()

# rf 입력값으로 쓰기 위해 시간 정수화
df_melted['시간'] = df_melted['시간'].str.replace('시','').str.replace('분','').astype(int)

df_melted = df_melted.dropna(subset=['혼잡도'])

# 요일, 상하 구분 원핫인코딩
subway_df = pd.get_dummies(df_melted, columns=['요일구분','상하구분'])

# 입력값 타깃값 나누고 훈련,테스트 세트 만들기
X = subway_df.drop(columns=['혼잡도'])
y = subway_df['혼잡도']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# 모델 훈련 
file_path = "./static/data/subway_rf.pkl"

if os.path.exists(file_path): # 이미 모델을 훈련시켰으면
    #저장해뒀던 모델 불러옴
    with open("static/data/subway_rf.pkl", "rb") as f:
            loaded_subway_rf = pickle.load(f)
else: # 모델 훈련 처음이면
    # 모델 훈련
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    with open("static/data/subway_rf.pkl", "wb") as f:
        pickle.dump(model, f)




''' <혼잡도 예측 함수>
subName: str = 역 이름 ex)'개봉역'
subLine: int = 호선 ex) 1
DateTime: object(datetime) = "%Y-%m-%d %H:%M" 형태의 datetime 객체 ex) 2025-12-31 03:30
direction: str = 상하선 또는 내외선 ex) '상선'
'''
def pred_subway(subName, subLine, DateTime, direction): 
    # ['역번호', '년도', '월', '일', '시간', '요일구분_일요일', '요일구분_토요일', '요일구분_평일', '상하구분_내선',
    #  '상하구분_상선', '상하구분_외선', '상하구분_하선']
    
    # 역번호 추출
    subNum = df_all.loc[(df_all["호선"] == subLine) & (df_all["출발역"] == subName), "역번호"].unique()[0]

    # 데이터에 존재하지 않는 역이면 -1 반환
    if subNum not in subway_df['역번호']:
        return -1

    # DateTime의 날짜/시간 정보 정수형으로 바꿈
    year = DateTime.year
    month = DateTime.month
    day = DateTime.day

    time = DateTime.hour * 100 + DateTime.minute

    # 요일 / 상하선 구분
    sun, sat, wday, inner, up, outer, down = 0, 0, 0, 0, 0, 0, 0

    if direction == '상선':
        up = 1
    elif direction == '하선':
        down = 1
    if direction == '내선':
        inner = 1
    elif direction =='외선':
        outer = 1

    if 0 <= DateTime.weekday() < 4:
        wday = 1
    elif DateTime.weekday() == 5:
        sat = 1
    elif DateTime.weekday() == 6:
        sun = 1
    
    # 예측
    pred_res = loaded_subway_rf.predict([[subNum, year, month, day, time, sun, sat, wday, inner, up, outer, down]])[0]

    return pred_res


''' 상위 10개의 역 그래프 이미지로 저장하는 함수
lineNum: int = 호선 ex) 7
'''

# def draw_graph_top10(lineNum):
#     # 입력받은 호선의 인기순 10개의 역 가져와서 전처리
#     subway_rank = pd.read_csv('static/data/subway_data/rank/서울교통공사_승하차순위_20241231.csv', encoding='EUC-KR')

#     subway_rank = subway_rank.sort_values(by=["호선", "순위"])

#     grouped = dict(tuple(subway_rank.groupby("호선")))

#     line_group = grouped[lineNum].head(10)

#     line_group['역명'] = line_group['역명'].apply(lambda x: x.split("(")[0])


#     line = line_group[['역코드', '역명']]

#     for i, l in enumerate(line['역명']):
#         res = []
#         names = []
#         for t in timeStr:
#             time_tmp = t
#             formatted = time_tmp.replace("시", ":").replace("분", "")  # "5:30"

#             # today_str = date.today().strftime("%Y-%m-%d")  # "2026-01-15"
#             dt = datetime.strptime("2026-01-16 " + formatted, "%Y-%m-%d %H:%M")
  

#             direction = '내선' if lineNum == 2 else '상선'
#             res.append(pred_subway(l, lineNum, dt, direction))
#             names.append(l)

#         plt.rc('font', family='Malgun Gothic')
#         plt.rcParams['axes.unicode_minus'] = False
#         plt.figure(figsize=(12, 6))
#         plt.plot(timeStr, res, marker = 'o', linestyle = '-', color = colors[lineNum])
#         plt.title(str(lineNum)+'호선 '+names[i] + " (평일/상선)")
#         plt.xlabel('시간대')
#         plt.ylabel('혼잡도', rotation = 0, labelpad=30)
#         plt.xticks(timeStr, rotation=45)
#         plt.grid(True)
#         plt.legend(loc="best")  
#         plt.savefig(str(lineNum)+'호선_'+names[i]+'_평일_상선.jpg', bbox_inches="tight")
#         # plt.show()


def draw_graph_top10(lineNum):
    # 입력받은 호선의 인기순 10개의 역 가져와서 전처리
    subway_rank = pd.read_csv('static/data/subway_data/rank/서울교통공사_승하차순위_20241231.csv', encoding='EUC-KR')

    subway_rank = subway_rank.sort_values(by=["호선", "순위"])

    grouped = dict(tuple(subway_rank.groupby("호선")))

    line_group = grouped[lineNum].head(10)

    line_group['역명'] = line_group['역명'].apply(lambda x: x.split("(")[0])


    line = line_group[['역코드', '역명']]

    for i, l in enumerate(line['역명']):
        res1 = []
        res2 = []
        names = []
        for t in timeStr:
            time_tmp = t
            formatted = time_tmp.replace("시", ":").replace("분", "")  # "5:30"

            # today_str = date.today().strftime("%Y-%m-%d")  # "2026-01-15"
            dt = datetime.strptime("2026-01-17 " + formatted, "%Y-%m-%d %H:%M")
  

            direction = ('내선', '외선') if lineNum==2 else ('상선','하선')
            res1.append(pred_subway(l, lineNum, dt, direction[0]))
            res2.append(pred_subway(l, lineNum, dt, direction[1]))

            names.append(l)

        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
        fig, axes = plt.subplots(1, 2, figsize=(10,4))
        # 첫 번째 그래프
        axes[0].plot(timeStr, res1, marker='o', linestyle='-', color=colors[lineNum])
        axes[0].set_title(str(lineNum)+'호선 '+names[i] + " (주말/"+direction[0]+")")
        axes[0].tick_params(axis='x', labelsize=7)  # x축 눈금 글자 크기를 8로
        axes[0].set_xlabel('시간대')
        axes[0].set_ylabel('혼잡도', rotation=0, labelpad=30)
        axes[0].set_xticks(timeStr)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True)
        axes[0].legend(loc="best")

        # 두 번째 그래프
        axes[1].plot(timeStr, res2, marker='o', linestyle='-', color=colors[lineNum])
        axes[1].set_title(str(lineNum)+'호선 '+names[i] + " (주말/"+direction[1]+")")
        axes[1].tick_params(axis='x', labelsize=7)
        axes[1].set_xlabel('시간대')
        axes[1].set_ylabel('혼잡도', rotation=0, labelpad=30)
        axes[1].set_xticks(timeStr)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True)
        axes[1].legend(loc="best")

        plt.tight_layout()
        plt.savefig(str(lineNum)+'호선_'+names[i]+'_주말.jpg', bbox_inches="tight")
        # plt.show()



''' 지도에 원 그리는 함수
path: list(tuple) = [(역명1, 호선1), (역명2, 호선2), ... (역명n, 호선n)] 
                    
                    ex) [('중곡', 7), ('군자',7), ('어린이대공원', 7), ('건대입구', 7), ('구의', 2), ('강변', 2)]
'''
def draw_circles(path):
    sl = pd.read_csv('static/data/subway_data/subway_loc/지하철역위치좌표.csv')
    center_lat = sl[sl['지하철역'].isin([n+'역' for n, _ in path])]['x좌표'].mean()
    center_lon = sl[sl['지하철역'].isin([n+'역' for n, _ in path])]['y좌표'].mean()
    map_osm = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # 특정 위도, 경도 중심으로 하는 OpenStreetMap을 출력

    for name, line in path:
        pred = pred_subway(name, line, datetime.now(), '상선')

        # 서울의 중심에 위치하는 명동역의 위도와 경도를 중심으로 지도 출력
        latitude = sl[sl['지하철역']== name+'역']['x좌표'].iloc[0]
        longitude = sl[sl['지하철역']==name+'역']['y좌표'].iloc[0]
        
        color = colors.get(line)

        # 각 지하철 역의 위치별로 원형마커를 지도에 추가
        
        marker = folium.CircleMarker([latitude, longitude],
                            radius = pred / 5,
                            popup = [name,float(pred)],
                            color = color,
                            fill = True,
                            fill_color = color)
        marker.add_to(map_osm)
        
        # 역 정보 텍스트 추가 (역이름, 혼잡도)
        folium.Marker(
            location = [latitude, longitude],
            icon = folium.DivIcon(html='<br><div style="display:flex;flex-direction:column;align-items:center;font-size:12px;color:black; white-space:nowrap; text-align:center;">''<div style="background-color:rgba(255,255,255,0.8);padding:3px 6px;border-radius:4px;border:1px solid gray;margin-top:2px;">'+name+'역<br>혼잡도: '+str(round(pred))+'</div>''</div>')
        ).add_to(map_osm)

    map_osm.save("map.html")
    hti = Html2Image()
    hti.screenshot(html_file="map.html", save_as="map.png")



###  테스트용

# Path = [('중곡', 7), ('군자',7), ('어린이대공원', 7), ('건대입구', 7), ('구의', 2), ('강변', 2)]

# draw_circles(Path)


# for i in range(1,9):
#     draw_graph_top10(i)

# # 결정 계수
# print(loaded_subway_rf.score(X_test, y_test))
# # 평균 제곱근 오차
# y_pred = loaded_subway_rf.predict(X_test)
# rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# print("RMSE:", rmse)

