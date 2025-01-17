# evening.py

import requests
import time

# 정류장 ID와 이름 매핑 (저녁용으로 수정 가능)
stop_info = { #https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/7021013700?_=1734858175998
    "7021030400": "고성아파트건너",
    "7021013700": "kt북대구건너",
    "7021013400": "북구청건너",
    "7021012500": "고성지구대",
    "7011002100": "신천LH건너"
}

# 각 정류장에서 필터링할 버스 번호 설정 (저녁용으로 수정 가능)
bus_filters = {
    "고성아파트건너": ["북구3"],
    "kt북대구건너": ["234"],
    "북구청건너": ["708"],
    "고성지구대": ["708"],
    "신천LH건너": ["425"]
}

api_url_template = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_=" + str(int(time.time() * 1000))

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

FILTER_TIME = 30

# 전역 변수로 정류장 ID-이름 매핑을 위한 딕셔너리
station_name_map = {}

# 정류장 정보를 API에서 한 번만 받아오는 함수
def load_station_names():
    global station_name_map
    route_url = "https://businfo.daegu.go.kr:8095/dbms_web_api/bs/route?routeId=3000425000"
    response = requests.get(route_url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            for body in data.get('body', []):
                bs_id = body.get("bsId")
                bs_name = body.get("bsNm")
                station_name_map[bs_id] = bs_name
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
    else:
        print(f"API 응답 오류: {response.status_code}")

# 특정 정류장 ID로 이름을 가져오는 함수
def get_station_name(bs_id):
    return station_name_map.get(bs_id, "알 수 없음")

# 버스 도착 정보 가져오기
def get_bus_data(stop_id):
    url = api_url_template.format(stop_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            #print(data)
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
            return []
        
        buses = []
        for bus in data.get('body', {}).get('list', []):
            bus_info = {
                "routeNo": bus.get("routeNo"),
                "arrState": bus.get("arrState"),
                "bsNm": bus.get("bsNm"),
                "bsGap": bus.get("bsGap")
            }
            buses.append(bus_info)
        return buses
    else:
        print(f"API 응답 오류: {response.status_code}")
        return []

# 필터링된 버스 정보
def filter_buses(buses, stop_name):
    filtered_buses = []
    for bus in buses:
        if bus["routeNo"] in bus_filters.get(stop_name, []):
            arr_state = bus["arrState"]
            if arr_state == "전":  
                arr_state_minutes = 1
            elif arr_state == "전전": 
                arr_state_minutes = 3
            else:
                try:
                    arr_state_minutes = int(arr_state.replace("분", ""))
                except ValueError:
                    continue
            if arr_state_minutes <= FILTER_TIME:
                bus["stopName"] = stop_name
                filtered_buses.append(bus)
    return filtered_buses

# 425 버스 위치 정보 가져오기
def get_bus_location():
    bus_location_url = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/pos/3000425000?routeTCd=&_=" + str(int(time.time() * 1000))
    response = requests.get(bus_location_url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
            return []
        
        bus_locations = []
        for bus in data.get('body', []):
            if bus.get("moveDir") == "0":

                bus_location = {
                    "vehicleNo": bus.get("vhcNo"),
                    "bsGap": 49 - bus.get("seq"),
                    "stationName": get_station_name(bus.get("bsId"))   # 이름으로 표기
                }
                if bus_location["bsGap"] > 0:
                    bus_locations.append(bus_location)
        return sorted(bus_locations, key=lambda x: x['bsGap'], reverse=False)
    else:
        print(f"API 응답 오류: {response.status_code}")
        return []