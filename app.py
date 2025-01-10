import requests
import time
from flask import Flask, render_template, request
import os

app = Flask(__name__)

bus_stops_am = {
    "7061038700": {
        "name": "메트로팔레스1",
        "filters": ["425","937"]
    }
}

bus_stops_pm = {
    "7021013700": {
        "name": "kt북대구건너",
        "filters": ["234"]
    },      
    "7021030400": {
        "name": "고성아파트건너",
        "filters": ["북구3"]
    },
    "7021012500": {
        "name": "고성지구대",
        "filters": ["708"]
    }
}

bus_stops_amc = {
    "7011002200": {
        "name": "신천LH",
        "filters": ["북구3","101"]
    },
    "7011006700": {
        "name": "동대구역",
        "filters": ["708"]
    },
    "7001005900": {
        "name": "섬유회관건너",
        "filters": ["동구2","939"]
    } 
}

bus_stops_pmc = {
    "7011002400": {
        "name": "역전시장앞",
        "filters": ["425","651","909"]
    },
    "7001006800": {
        "name": "228중앙공원",
        "filters": ["425","651","518"]
    } 
}

# https://apis.map.kakao.com/web/sample/addMapClickEventWithMarker/
bus_id = {
    "북구3": ["4060003000"],
    "425": ["3000425000"],
    "101": ["3000101000","3000101007","3000101009"],
    "234": ["3000234000"],
    "708": ["3000708000","3000708001"]  
}

station_name_map = {}

# 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 버스 도착 정보 가져오기
def get_bus_data(stop_id):
    url = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/{}?_={}".format(stop_id, str(int(time.time() * 1000)))
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
def get_bus_location(bus, dir):
    bus_routes = bus_id[bus]
    bus_stops = []
    bus_locations = []
    
    # 각 버스에 대해 정류장과 버스 위치 정보 가져오기
    for route in bus_routes:
        # 정류장 정보
        url = "https://businfo.daegu.go.kr:8095/dbms_web_api/bs/route?routeId={}".format(route)
        response = requests.get(url, headers=headers)
        data = response.json()
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
        
        # 버스 위치 정보
        url = "https://businfo.daegu.go.kr:8095/dbms_web_api/bs/position?routeId={}".format(route)
        response = requests.get(url, headers=headers)
        data = response.json()
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
    elif item == 'amc':
        bus_stops = bus_stops_amc
    elif item == 'pm':
        bus_stops = bus_stops_pm
    elif item == 'pmc':
        bus_stops = bus_stops_pmc

    else:
        bus = item
        dir = request.args.get('dir', '1')
        bus_stops, bus_locations = get_bus_location(bus, dir)
        return render_template('bus_location.html', bus_locations=bus_locations, bus_stops=bus_stops, 
                               item=item, api_key=os.getenv('GOOGLE_MAPS_API_KEY'))

    all_buses = process_bus_data(bus_stops)
    return render_template('busstop.html', buses=all_buses, item=item)

if __name__ == '__main__':
    app.run(debug=True)