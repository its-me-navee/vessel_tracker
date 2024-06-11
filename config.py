import math

# Define sea waypoints for each route from China to India
routes = {
    'orange': [
        (30.051067, 121.717758),
        (30.205605, 121.729410),
        (30.353196, 121.814864),
        (30.413510, 122.009077),
        (30.326378, 122.506261),
        (30.205605, 122.704358),
        (29.916491, 122.708242),
        (27.506761, 121.556963),
        (25.211292, 119.987135),
        (22.564612, 116.735799),
        (0.493844, 105.043057),
        (0.576235, 103.731079),
        (1.250578, 103.434563),
        (2.527718, 101.521743),
        (8.221385, 95.614676),
        (8.38248, 94.056513),
        (8.129301, 88.707595),
        (5.473798, 81.428414),
        (5.473798, 79.986532),
        (7.230413, 76.730669),
        (11.223999, 75.172506),
        (15.634113, 73.428293),
        (18.250901, 72.916657),
        (18.5994, 72.849443),
        (18.807269, 72.871027),
        (18.96275, 72.8741945)
    ],
    'blue': [
        (22.552016, 113.836183),
        (22.463271, 113.745458),
        (22.034602, 113.680255),
        (19.434803, 113.168067),
        (11.692073, 109.834329),
        (0.473844, 105.023057),
        (0.556235, 103.711079),
        (1.230578, 103.414563),
        (2.507718, 101.501743),
        (8.201385, 95.594676),
        (8.362480, 94.036513),
        (8.109301, 88.687595),
        (5.453798, 81.408414),
        (5.453798, 79.966532),
        (7.210413, 76.710669),
        (11.203999, 75.152506),
        (15.614113, 73.408293),
        (18.230901, 72.896657),
        (18.579400, 72.829443),
        (18.787269, 72.851027),
        (18.94275, 72.8541945)
    ]
}

# Haversine formula to calculate the distance between two points on the Earth's surface
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Function to calculate the total distance for a list of points
def total_distance(points):
    total_dist = 0.0
    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]
        total_dist += haversine(lat1, lon1, lat2, lon2)
    return total_dist

# Calculate total distances for orange and blue routes
orange_total_distance = total_distance(routes['orange'])
blue_total_distance = total_distance(routes['blue'])

# print("Total distance for orange route: {:.2f} km".format(orange_total_distance))
# print("Total distance for blue route: {:.2f} km".format(blue_total_distance))

# Function to choose route based on initial port
def choose_route(initial_port):
    if initial_port.lower() == 'ningbo':
        return 'orange'
    elif initial_port.lower() == 'shenzhen':
        return 'blue'
    else:
        print("Invalid initial port.")
        return None

# Function to calculate the current position based on the fraction of distance traveled
def calculate_position(route, fraction):
    total_dist = total_distance(route)
    distance_traveled = fraction * total_dist
    
    accumulated_distance = 0.0
    for i in range(len(route) - 1):
        start_point = route[i]
        end_point = route[i + 1]
        segment_distance = haversine(start_point[0], start_point[1], end_point[0], end_point[1])
        
        if accumulated_distance + segment_distance >= distance_traveled:
            segment_fraction = (distance_traveled - accumulated_distance) / segment_distance
            current_lat = start_point[0] + (end_point[0] - start_point[0]) * segment_fraction
            current_lon = start_point[1] + (end_point[1] - start_point[1]) * segment_fraction
            return current_lat, current_lon
        
        accumulated_distance += segment_distance
    
    return route[-1]  # If we reach here, it means the travel covers the entire route

