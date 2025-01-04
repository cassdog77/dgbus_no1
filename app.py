import requests
import time
from flask import Flask, render_template, request

app = Flask(__name__)

# 정류장 정보와 필터링할 버스 번호를 함께 저장 (AM7용)
bus_stops_am = {
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

# 정류장 정보와 필터링할 버스 번호를 함께 저장 (PM6용)
bus_stops_pm = {
    "7021012500": {
        "name": "고성지구대",
        "filters": ["708"]
    },
    "7021013400": {
        "name": "북구청건너",
        "filters": ["708"]
    },
    "7021013700": {
        "name": "kt북대구건너",
        "filters": ["234"]
    },      
    "7061038700": {
        "name": "고성아파트건너",
        "filters": ["북구3"]
    },
    "7011002100": {
        "name": "신천LH건너",
        "filters": ["425"]
    }
}


# 버스 도착 정보 가져오기
def get_bus_data(stop_id):
    # API URL 및 헤더 설정
    api_url_template = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_=" + str(int(time.time() * 1000))

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
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

# 필터링된 버스 정보
def filter_buses(buses, stop_name, filters):
    filtered_buses = []
    for bus in buses:
        if bus["routeNo"] in filters:
            bus["stopName"] = stop_name
            filtered_buses.append(bus)
    return filtered_buses

# 공통된 버스 데이터를 처리하는 함수
def process_bus_data(bus_stops):
    all_buses = []
    for stop_id, stop_data in bus_stops.items():
        stop_name = stop_data["name"]
        filters = stop_data["filters"]
        buses = get_bus_data(stop_id)
        filtered_buses = filter_buses(buses, stop_name, filters)
        all_buses.extend(filtered_buses)
    return all_buses

# Flask 라우트
@app.route('/bus', methods=['GET'])
def bus_route():
    item = request.args.get('item')
    if item == 'am':
        bus_stops = bus_stops_am
    elif item == 'pm':
        bus_stops = bus_stops_pm
    all_buses = process_bus_data(bus_stops)
    return render_template('busstop.html', buses=all_buses, item=item)

if __name__ == '__main__':
    app.run(debug=True)

