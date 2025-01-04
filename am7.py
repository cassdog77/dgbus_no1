import requests
import time

# 정류장 정보와 필터링할 버스 번호를 함께 저장
bus_stops = {
    "7061038700": {
        "name": "메트로팔레스1",
        "filters": ["425"]
    },
    "7011006700": {
        "name": "동대구역",
        "filters": ["708"]
    },
    "7011003900": {
        "name": "동대구동화아이위시아파트앞",
        "filters": ["북구3"]
    }

}

api_url_template = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_=" + str(int(time.time() * 1000))

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 전역 변수로 정류장 ID-이름 매핑을 위한 딕셔너리
station_name_map = {}

# 버스 도착 정보 가져오기
def get_bus_data(stop_id):
    url = api_url_template.format(stop_id)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
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
            #print(bus_info)
        return buses
    else:
        print(f"API 응답 오류: {response.status_code}")
        return []

# 필터링된 버스 정보
def filter_buses(buses, stop_name, filters):
    filtered_buses = []
    for bus in buses:
        if bus["routeNo"] in filters:
            bus["stopName"] = stop_name
            filtered_buses.append(bus)
    return filtered_buses


# 전체 프로세스를 실행
def process_bus_data():
    all_buses = []
    for stop_id, stop_data in bus_stops.items():
        stop_name = stop_data["name"]
        filters = stop_data["filters"]
        buses = get_bus_data(stop_id)
        print(buses)
        filtered_buses = filter_buses(buses, stop_name, filters)
        all_buses.extend(filtered_buses)
    
    return all_buses