import requests
import time

# 정류장 ID와 이름 매핑
stop_info = {
    "7061038700": "메트로팔레스1",
    "7011004900": "수성도서관건너",
    "7011006800": "동대구역건너",
    "7011006700": "동대구역"
}

# 각 정류장에서 필터링할 버스 번호 설정
bus_filters = {
    "메트로팔레스1": ["425", "937"],
    "수성도서관건너": ["708"],
    "동대구역건너": ["북구3"],
    "동대구역": ["708"]
}

api_url_template = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_=" + str(int(time.time() * 1000))

# Safari에서 사용하는 User-Agent 헤더를 추가
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 특정 필터 기준 (예: 10분 이내 도착 버스)
FILTER_TIME = 30

def get_bus_data(stop_id):
    # API 호출
    url = api_url_template.format(stop_id)
    print(f"Calling API: {url}")
    response = requests.get(url, headers=headers)
    
    # 응답 상태 확인
    if response.status_code == 200:
        try:
            # JSON 응답 처리
            data = response.json()
            #print(f"Response data: {data}")  # 응답 데이터 출력 (디버깅용)
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
            return []
        
        buses = []
        
        # JSON 데이터에서 추출
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

def filter_buses(buses, stop_name):
    # 각 정류장별로 필터링할 버스 번호 리스트
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
                    continue  # 만약 숫자로 변환할 수 없는 값이 있으면 무시
            if arr_state_minutes <= FILTER_TIME:
                bus["stopName"] = stop_name  # 정류장 이름 추가
                filtered_buses.append(bus)
    return filtered_buses

# 각 정류장에 대해 데이터 수집
all_buses = []
for stop_id, stop_name in stop_info.items():
    buses = get_bus_data(stop_id)
    filtered_buses = filter_buses(buses, stop_name)
    all_buses.extend(filtered_buses)

# 결과 출력
if all_buses:
    print("필터링된 버스 정보:")
    for bus in all_buses:
        print(f"정류장: {bus['stopName']}, 버스 번호: {bus['routeNo']}, 남은 시간: {bus['arrState']}, 현재 위치: {bus['bsNm']}, 남은 정류장 간격: {bus['bsGap']}")
else:
    print("필터링된 버스 정보가 없습니다.")