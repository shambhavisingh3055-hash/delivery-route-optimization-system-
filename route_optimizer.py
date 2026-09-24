import pandas as pd
import math


# ==========================================
# CALCULATE DISTANCE BETWEEN TWO LOCATIONS
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):

    # Radius of Earth in kilometres
    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ==========================================
# FIND NEAREST DELIVERY
# ==========================================

def find_nearest(current_location, deliveries):

    current_lat, current_lon = current_location

    nearest_index = None
    shortest_distance = float("inf")

    for index, delivery in deliveries.iterrows():

        distance = calculate_distance(
            current_lat,
            current_lon,
            delivery["latitude"],
            delivery["longitude"]
        )

        if distance < shortest_distance:

            shortest_distance = distance
            nearest_index = index

    return nearest_index, shortest_distance


# ==========================================
# OPTIMIZE DELIVERY ROUTE
# ==========================================

def optimize_route(df):

    # Make a copy so original dataset isn't changed
    deliveries = df.copy()

    # Warehouse / starting point - SRMCEM, Lucknow
    warehouse_lat = 26.8467
    warehouse_lon = 80.9496

    current_location = (
        warehouse_lat,
        warehouse_lon
    )

    optimized_route = []

    total_distance = 0


    # ==========================================
    # VISIT NEAREST DELIVERY ONE BY ONE
    # ==========================================

    while len(deliveries) > 0:

        nearest_index, distance = find_nearest(
            current_location,
            deliveries
        )

        selected_delivery = deliveries.loc[
            nearest_index
        ].copy()

        selected_delivery["route_distance_km"] = round(
            distance,
            2
        )

        optimized_route.append(
            selected_delivery
        )

        total_distance += distance


        # Update current location
        current_location = (
            selected_delivery["latitude"],
            selected_delivery["longitude"]
        )


        # Remove delivered customer
        deliveries = deliveries.drop(
            nearest_index
        )


    # ==========================================
    # CREATE RESULT DATAFRAME
    # ==========================================

    route_df = pd.DataFrame(
        optimized_route
    ).reset_index(drop=True)


    # Add route order
    route_df.insert(
        0,
        "route_order",
        range(1, len(route_df) + 1)
    )


    return route_df, round(total_distance, 2)
# ==========================================
# TEST THE OPTIMIZER
# ==========================================

if __name__ == "__main__":

    # Load the delivery dataset
    df = pd.read_csv("dataset/delivery_data.csv")

    # Optimize the route
    route, total_distance = optimize_route(df)

    print("\n===================================")
    print("ROUTE OPTIMIZATION TEST")
    print("===================================")

    print("\nTotal deliveries:")
    print(len(route))

    print("\nTotal route distance:")
    print(total_distance, "km")

    print("\nFirst 10 stops:")

    print(
        route[
            [
                "route_order",
                "delivery_id",
                "customer",
                "route_distance_km"
            ]
        ].head(10)
    )

    print("\n===================================")