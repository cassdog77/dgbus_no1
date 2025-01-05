import requests
import time
from flask import Flask, render_template, request
import os

app = Flask(__name__)

bus_stops_am = {
    "7061038700": {
        "name": "메트로팔레스1",
        "filters": ["425","937"]
    },
    "7011006700": {
        "name": "동대구역",
        "filters": ["708"]
    },
    "7011003900": {
        "name": "아이위시앞",
        "filters": ["북구3"]
    }
}

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

bus_id = {
    "북구3": "4060003000",
    "425": "3000425000",
}

station_name_map = {}

# 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 버스 도착 정보 가져오기
def get_bus_data(stop_id):
    # API URL 
    url = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_={}".format(stop_id,str(int(time.time() * 1000)))
    response = requests.get(url, headers=headers)
    data = response.json()
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


# 버스번호 -> 위치 정보 가져오기
def get_bus_location(bus,dir):
    # 정류장
    url = "https://businfo.daegu.go.kr:8095/dbms_web_api/bs/route?routeId={}".format(bus_id[bus])
    response = requests.get(url, headers=headers)
    data = response.json()
    bus_stops = []
    for i in data.get('body', []):
        bs_id = i.get("bsId")
        bs_name = i.get("bsNm")
        station_name_map[bs_id] = bs_name
        bus_stop = {
            "lat": i.get("lat"),
            "lng": i.get("lng"),
            "stationName": bs_name
        }
        bus_stops.append(bus_stop)
    
    # 버스위치
    url = "https://businfo.daegu.go.kr:8095/dbms_web_api/bs/position?routeId={}".format(bus_id[bus])
    #print(url)
    response = requests.get(url, headers=headers)
    data = response.json()
    bus_locations = []
    for i in data.get('body', []):
        if i.get("moveDir") == dir:
            bus_location = {
                "moveDir": i.get("moveDir"), 
                "lat": i.get("lat"),
                "lng": i.get("lng"),
                "stationName": station_name_map[i.get("bsId")] 
            }
            bus_locations.append(bus_location)
    return bus_stops, bus_locations

# Flask 라우트
@app.route('/bus', methods=['GET'])
def bus_route():
    item = request.args.get('item', 'am') 
    if item == 'am':
        bus_stops = bus_stops_am
    elif item == 'pm':
        bus_stops = bus_stops_pm
    else:
        bus = item 
        dir = request.args.get('dir', '1') 
        bus_stops, bus_locations = get_bus_location(bus,dir)
        return render_template('bus_location.html', bus_locations=bus_locations, bus_stops=bus_stops, 
                               item=item, api_key=os.getenv('KAKAO_MAPS_API_KEY'))

    all_buses = process_bus_data(bus_stops)
    return render_template('busstop.html', buses=all_buses, item=item)

if __name__ == '__main__':
    app.run(debug=True)

