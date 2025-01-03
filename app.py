from flask import Flask, render_template
from am7 import bus_stops as a_bus_stops, get_bus_data as a_get_bus_data, filter_buses as a_filter_buses
from pm6 import bus_stops as p_bus_stops, get_bus_data as p_get_bus_data, filter_buses as p_filter_buses

app = Flask(__name__)


@app.route('/am7', methods=['GET'])
def am7():
    all_buses = []
    for stop_id, stop_data in a_bus_stops.items():
        stop_name = stop_data["name"]
        filters = stop_data["filters"]
        buses = a_get_bus_data(stop_id)
        filtered_buses = a_filter_buses(buses, stop_name, filters)
        all_buses.extend(filtered_buses)
    if all_buses:
        return render_template('bus.html', buses=all_buses)#, bus_locations=bus_locations)
    else:
        return render_template('bus.html', message="필터링된 버스 정보가 없습니다.")

@app.route('/pm6', methods=['GET'])
def pm6():
    all_buses = []
    for stop_id, stop_data in p_bus_stops.items():
        stop_name = stop_data["name"]
        filters = stop_data["filters"]
        buses = p_get_bus_data(stop_id)
        filtered_buses = p_filter_buses(buses, stop_name, filters)
        all_buses.extend(filtered_buses)
    if all_buses:
        return render_template('bus.html', buses=all_buses)#, bus_locations=bus_locations)
    else:
        return render_template('bus.html', message="필터링된 버스 정보가 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)