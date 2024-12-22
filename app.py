from flask import Flask, render_template
from morning import load_station_names as m_load_station_names, get_bus_data as m_get_bus_data, filter_buses as m_filter_buses, stop_info as m_stop_info, get_bus_location as m_get_bus_location
from evening import load_station_names as e_load_station_names, get_bus_data as e_get_bus_data, filter_buses as e_filter_buses, stop_info as e_stop_info, get_bus_location as e_get_bus_location

app = Flask(__name__)

@app.route('/morning', methods=['GET'])
def morning():
    # 첫 요청 시 정류장 이름을 미리 불러옴 (모닝용)
    m_load_station_names()
    all_buses = []
    for stop_id, stop_name in m_stop_info.items():
        buses = m_get_bus_data(stop_id)
        filtered_buses = m_filter_buses(buses, stop_name)
        all_buses.extend(filtered_buses)
    
    bus_locations = m_get_bus_location()  # 북구3 버스 위치 정보 가져오기

    if all_buses:
        return render_template('morning.html', buses=all_buses, bus_locations=bus_locations)
    else:
        return render_template('morning.html', message="필터링된 버스 정보가 없습니다.")

@app.route('/evening', methods=['GET'])
def evening():
    # 첫 요청 시 정류장 이름을 미리 불러옴 (이브닝용)
    e_load_station_names()
    all_buses = []
    for stop_id, stop_name in e_stop_info.items():
        buses = e_get_bus_data(stop_id)
        filtered_buses = e_filter_buses(buses, stop_name)
        all_buses.extend(filtered_buses)
    
    bus_locations = e_get_bus_location()  # 북구3 버스 위치 정보 가져오기

    if all_buses:
        return render_template('evening.html', buses=all_buses, bus_locations=bus_locations)
    else:
        return render_template('evening.html', message="필터링된 버스 정보가 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)