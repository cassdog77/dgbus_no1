from flask import Flask, render_template
import requests
import time

app = Flask(__name__)

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

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

FILTER_TIME = 10

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
        return buses
    else:
        print(f"API 응답 오류: {response.status_code}")
        return []

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

@app.route('/bus_info', methods=['GET'])
def bus_info():
    all_buses = []
    for stop_id, stop_name in stop_info.items():
        buses = get_bus_data(stop_id)
        filtered_buses = filter_buses(buses, stop_name)
        all_buses.extend(filtered_buses)

    if all_buses:
        return render_template('bus_info.html', buses=all_buses)
    else:
        return render_template('bus_info.html', message="필터링된 버스 정보가 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)