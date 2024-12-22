from flask import Flask, render_template
from morning import load_station_names as load_morning_station_names, get_bus_data as get_morning_bus_data, filter_buses as filter_morning_buses, stop_info, get_bus_location as get_morning_bus_location
from evening import load_station_names as load_evening_station_names, get_bus_data as get_evening_bus_data, filter_buses as filter_evening_buses, get_bus_location as get_evening_bus_location

app = Flask(__name__)

@app.route('/morning', methods=['GET'])
def morning():
    # 첫 요청 시 정류장 이름을 미리 불러옴 (모닝용)
    load_morning_station_names()

    all_buses = []
    for stop_id, stop_name in stop_info.items():
        buses = get_morning_bus_data(stop_id)
        filtered_buses = filter_morning_buses(buses, stop_name)
        all_buses.extend(filtered_buses)
    
    bus_locations = get_morning_bus_location()  # 북구3 버스 위치 정보 가져오기

    if all_buses:
        return render_template('morning.html', buses=all_buses, bus_locations=bus_locations)
    else:
        return render_template('morning.html', message="필터링된 버스 정보가 없습니다.")

@app.route('/evening', methods=['GET'])
def evening():
    # 첫 요청 시 정류장 이름을 미리 불러옴 (이브닝용)
    load_evening_station_names()

    all_buses = []
    for stop_id, stop_name in stop_info.items():
        buses = get_evening_bus_data(stop_id)
        filtered_buses = filter_evening_buses(buses, stop_name)
        all_buses.extend(filtered_buses)
    
    bus_locations = get_evening_bus_location()  # 북구3 버스 위치 정보 가져오기

    if all_buses:
        return render_template('evening.html', buses=all_buses, bus_locations=bus_locations)
    else:
        return render_template('evening.html', message="필터링된 버스 정보가 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)