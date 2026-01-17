import pandas as pd
import numpy as np

bus_info_df = pd.read_excel('static/data/bus_data/서울시버스정류소위치정보(20260108).xlsx')

def get_busStationID(api_response):
    bus_stops = []

    # BUS 구간 찾기
    for itinerary in api_response["metaData"]["plan"]["itineraries"]:
        for leg in itinerary["legs"]:
            if leg.get("mode") == "BUS":
                for s in leg["passStopList"]["stations"]:
                    bus_stops.append({
                        "stationName": s["stationName"],
                        "lat": float(s["lat"]),
                        "lon": float(s["lon"])
                    })


    res = {}

    for stop in bus_stops:
        name = stop['stationName']
        x = stop['lon']
        y = stop['lat']

    
        filtered = bus_info_df[bus_info_df['정류소명'].str.contains(name, na=False)]

        # 거리 계산 
        filtered['오차'] = np.sqrt((filtered['X좌표'] - x)**2 + (filtered['Y좌표'] - y)**2)

        # 오차가 가장 작은 ARS_ID 추출
        best_match = filtered.loc[filtered['오차'].idxmin(), 'ARS_ID']

        res[name] = int(best_match)
        
    return res

