from flask import Flask, render_template, jsonify
import pandas as pd
import gdown
import os
import time
from config import routes, choose_route, calculate_position
import folium
from folium.plugins import AntPath

app = Flask(__name__)
# URLs of the Google Drive files
vessel_details_url = 'https://drive.google.com/uc?id=1FCi6rRsbqCopaSaioLluuZA_CIk8m6KF'
vessel_contents_url = 'https://drive.google.com/uc?id=1FDnSbruHxMycEkNtNDFn0KM1pCjDrJj8'
# Local file paths after downloading
vessel_details_file = 'vessel_details.xlsx'
vessel_contents_file = 'vessel_contents.xlsx'
# Global variables to store the last download time
last_download_time_details = 0
last_download_time_contents = 0

def download_files():
    global last_download_time_details, last_download_time_contents
    current_time = time.time()
    
    # Check if the files were downloaded less than two minutes ago
    if current_time - last_download_time_details < 120 and current_time - last_download_time_contents < 120:
        print("Files were downloaded less than two minutes ago. Skipping download.")
        return
    
    if os.path.exists(vessel_details_file):
        os.remove(vessel_details_file)
    if os.path.exists(vessel_contents_file):
        os.remove(vessel_contents_file)
    
    # Download the files from Google Drive
    gdown.download(vessel_details_url, vessel_details_file, quiet=False)
    gdown.download(vessel_contents_url, vessel_contents_file, quiet=False)
    
    # Update the last download time
    last_download_time_details = current_time
    last_download_time_contents = current_time

def load_data():
    # Download the files
    download_files()
    
    # Read vessel details
    vessel_details = pd.read_excel(vessel_details_file)
    # Read vessel contents
    vessel_contents = pd.read_excel(vessel_contents_file)
    
    # Calculate "Delhi Date" by adding 8 days to "Destination Date"
    vessel_details['Delhi Date'] = vessel_details['Dest. Date'] + pd.Timedelta(days=8)
    
    # Calculate total travel time
    vessel_details['Total Days'] = (vessel_details['Dest. Date'] - vessel_details['Start Date']).dt.days

    # Calculate elapsed Days based on the current date
    vessel_details['Elapsed Days'] = (pd.to_datetime('today') - vessel_details['Start Date']).dt.days

    # Organize data into the required format for the main table
    main_data = []
    for _, row in vessel_details.iterrows():
        main_data.append((
            row['Vessel Name'],
            row['Start Date'].strftime('%Y-%m-%d'),
            row['Dest. Date'].strftime('%Y-%m-%d'),
            row['Delhi Date'].strftime('%Y-%m-%d'),
            row['Vessel ID']  # Assuming there is a Vessel ID column in vessel_details.xlsx
        ))

    # Create a dictionary for vessel contents
    contents_dict = {}
    for _, row in vessel_contents.iterrows():
        if row['Vessel ID'] not in contents_dict:
            contents_dict[row['Vessel ID']] = []
        contents_dict[row['Vessel ID']].append({
            'Item Name': row['Item Name'],
            'Quantity': row['Quantity']
        })

    return main_data, contents_dict, vessel_details

headings = ("Vessel", "Start Date", "Dest. Date", "Delhi Date")

def positions():
    _, _, vessel_details = load_data()
    vessels_positions = []
    for _, row in vessel_details.iterrows():
        initial_port = row['Initial Port']
        total_days = row['Total Days']
        elapsed_days = row['Elapsed Days']
        vessel_name = row['Vessel Name']
        route_name = choose_route(initial_port)
        fraction  =  elapsed_days/total_days
        if row['Start Date'] > pd.to_datetime('today'):
            if initial_port.lower() == 'ningbo':
                current_position = (30.051067, 121.717758)
            elif initial_port.lower() == 'shenzhen':
                current_position = (22.552016, 113.836183)
        else:
            fraction = elapsed_days / total_days
            if route_name:
                route = routes[route_name]
                current_position = calculate_position(route, fraction)
            else:
                current_position = (None, None)
        
        vessels_positions.append({
            'vessel_name': vessel_name,
            'current_position': current_position
        })
    return vessels_positions, vessel_details
    
def draw_map():
    mapObj = folium.Map(location=[13.944599, 99.791178], zoom_start=4)
    
    route1 = routes["orange"]
    route2 = routes["blue"]
    vessel_positions, vessel_details = positions()  # Return vessel_details as well
    icon_path = 'static/ship.png'  # Ensure this path is correct

    for vessel in vessel_positions:
        # Retrieve vessel details for the current vessel
        current_vessel_details = vessel_details.loc[vessel_details['Vessel Name'] == vessel['vessel_name']].iloc[0]

        # Format dates to display only the date portion without the time
        starting_date = current_vessel_details['Start Date'].strftime('%Y-%m-%d')
        destination_date = current_vessel_details['Dest. Date'].strftime('%Y-%m-%d')
        delhi_date = current_vessel_details['Delhi Date'].strftime('%Y-%m-%d')

        # Create popup content for the current vessel
        popup_content = f"<b>Vessel Name:</b> {current_vessel_details['Vessel Name']}<br>"
        popup_content += f"<b>Initial Port:</b> {current_vessel_details['Initial Port']}<br>"
        popup_content += f"<b>Start Date:</b> {starting_date}<br>"
        popup_content += f"<b>Dest. Date:</b> {destination_date}<br>"
        popup_content += f"<b>Delhi Date:</b> {delhi_date}<br>"

        # Create marker with unique popup for each vessel
        folium.Marker(
            vessel['current_position'],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.CustomIcon(icon_path, icon_size=(30, 30))  # Adjust icon_size as needed
        ).add_to(mapObj)

    AntPath(route1, delay=1000, dash_array=[30, 15], color='orange', weight=3).add_to(mapObj)
    AntPath(route2, delay=1000, dash_array=[30, 15], color='blue', weight=3).add_to(mapObj)
    
    return mapObj._repr_html_()


@app.route('/')
def table():
    data, _, _ = load_data()
    map_html = draw_map()
    return render_template("index.html", headings=headings, data=data, vessels_positions=positions(), map_html = map_html)

@app.route('/vessel/<vessel_id>')
def vessel_details(vessel_id):
    _, contents_dict, _ = load_data()
    return jsonify(contents_dict.get(vessel_id, []))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == '__main__':
    app.run(debug=True)
