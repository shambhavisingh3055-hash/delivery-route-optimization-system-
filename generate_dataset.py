import pandas as pd
import numpy as np
import os
import math


# ==========================================
# SETTINGS
# ==========================================

NUMBER_OF_DELIVERIES = 150

# Create dataset folder if it doesn't exist
os.makedirs("dataset", exist_ok=True)


# ==========================================
# RANDOM DATA GENERATION
# ==========================================

np.random.seed(42)


# ==========================================
# DELIVERY LOCATIONS
# ==========================================

# Central point representing the warehouse
base_latitude = 20.0000
base_longitude = 77.0000

latitudes = np.random.uniform(
    base_latitude - 0.05,
    base_latitude + 0.05,
    NUMBER_OF_DELIVERIES
)

longitudes = np.random.uniform(
    base_longitude - 0.05,
    base_longitude + 0.05,
    NUMBER_OF_DELIVERIES
)


# ==========================================
# TRAFFIC CONDITIONS
# ==========================================

traffic_conditions = np.random.choice(
    ["Low", "Medium", "High"],
    NUMBER_OF_DELIVERIES,
    p=[0.40, 0.40, 0.20]
)


# ==========================================
# WEATHER CONDITIONS
# ==========================================

weather_conditions = np.random.choice(
    ["Clear", "Cloudy", "Rain"],
    NUMBER_OF_DELIVERIES,
    p=[0.50, 0.30, 0.20]
)


# ==========================================
# DISTANCE CALCULATION
# ==========================================

warehouse_lat = base_latitude
warehouse_lon = base_longitude


def haversine_distance(lat1, lon1, lat2, lon2):

    radius = 6371  # Earth radius in kilometres

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radius * c


distances = []

for lat, lon in zip(latitudes, longitudes):

    distance = haversine_distance(
        warehouse_lat,
        warehouse_lon,
        lat,
        lon
    )

    distances.append(round(distance, 2))


# ==========================================
# DELIVERY TIME GENERATION
# ==========================================

delivery_times = []

for distance, traffic, weather in zip(
    distances,
    traffic_conditions,
    weather_conditions
):

    # Base delivery time
    time = 8 + (distance * 4)

    # Traffic effect
    if traffic == "Low":
        time += 2

    elif traffic == "Medium":
        time += 8

    else:
        time += 15

    # Weather effect
    if weather == "Clear":
        time += 0

    elif weather == "Cloudy":
        time += 3

    else:
        time += 8

    # Small random variation
    time += np.random.normal(0, 3)

    # Prevent negative/unrealistic values
    time = max(time, 5)

    delivery_times.append(round(time, 2))


# ==========================================
# CREATE DATAFRAME
# ==========================================

data = pd.DataFrame({

    "delivery_id": [
        f"D{i:03d}"
        for i in range(1, NUMBER_OF_DELIVERIES + 1)
    ],

    "customer": [
        f"Customer {i}"
        for i in range(1, NUMBER_OF_DELIVERIES + 1)
    ],

    "latitude": np.round(latitudes, 6),

    "longitude": np.round(longitudes, 6),

    "distance_km": distances,

    "traffic": traffic_conditions,

    "weather": weather_conditions,

    "delivery_time_min": delivery_times

})


# ==========================================
# SAVE DATASET
# ==========================================

file_path = "dataset/delivery_data.csv"

data.to_csv(
    file_path,
    index=False
)


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n===================================")
print("Dataset created successfully!")
print("===================================")

print(f"\nFile: {file_path}")

print(f"Total deliveries: {len(data)}")

print("\nColumns:")

for column in data.columns:
    print("-", column)

print("\nFirst 5 records:")
print(data.head())

print("\n===================================")