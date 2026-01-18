import bus_service as bs
import subway_service as ss
import datetime
from datetime import datetime



''' CEI(혼잡 경험 지수) 구하는 함수
path: List(tuple) -> 경로 데이터 지하철은 튜플 길이가 4
                     버스는 튜플 길이가 3.
                     지하철: (역명, 호선, 시간, 상하선 or 내외선)
                     버스: (버스번호, 정류장명, 시간)
times: tuple -> (지하철 총 소요시간, 버스 총 소요시간)
'''
def pred_intergrate(path, times):
    slist = [] # 지하철 혼잡도 저장
    blist = [] # 버스 혼잡도 저장
    for p in path:
        if len(p) == 4:
            formatted = f"{str(p[2])[:2]}시{str(p[2])[2:]}분"
            
            today = datetime.today().date()
            hour = int(formatted[:2])   
            minute = int(formatted[3:5])

            dt = datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)
    

            pred_res = ss.pred_subway(p[0], p[1], dt, p[3])

            slist.append(pred_res)

        elif len(p) == 3:
            today = datetime.today().date() 
            hour = p[2]  
            minute = 0

            dt = datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)
            

            pred_res = bs.pred_bus(p[0], p[1], dt)
            blist.append(pred_res)



    return ((sum(slist) / len(slist)) * times[0] + (sum(blist) / len(blist)) * times[1]) / (sum(times))


# # 테스트용
# Path = [('중곡', 7, 1200, '하선'), ('군자', 7, 1200, '하선'), ('어린이대공원', 7, 1200, '하선'),
#          ('건대입구', 7, 1200, '하선'), ('구의', 2, 1230, '내선'), ('강변', 2, 1230, '내선'),
#          (3216, 5147, 12), (3216, 5142, 12), (3216, 5143, 12), (3216, 5170, 12),
#          (3216, 5140, 12), (721, 5141, 13), (721, 5001, 13), (721, 6003, 13)
#     ]

# print(pred_intergrate(Path, (6, 8)))