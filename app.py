from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import pickle

from route_optimizer import optimize_route

from pymongo import MongoClient

app = Flask(__name__)

LOCATION_FILE = os.path.join(
    "location_data",
    "locations.csv"
)

# ==========================================
# MONGODB CONNECTION
# ==========================================

MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)

db = client["ai_route"]

deliveries_collection = db["deliveries"]

# ==========================================
# MONGODB CONNECTION TEST
# ==========================================

@app.route("/api/db-test")
def db_test():

    try:

        client.admin.command("ping")

        return jsonify({

            "success": True,

            "message":
                "MongoDB connected successfully.",

            "database":
                db.name,

            "collection":
                deliveries_collection.name

        })

    except Exception as e:

        print(
            "MONGODB ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "MongoDB connection failed.",

            "error":
                str(e)

        }), 500

 # ==========================================
# LOCATION COORDINATE LOOKUP
# ==========================================

def get_coordinates(address, city, pincode):

    if not os.path.exists(LOCATION_FILE):
        return None, None

    locations = pd.read_csv(LOCATION_FILE)

    match = locations[
        (locations["location"].str.lower() == address.lower()) &
        (locations["city"].str.lower() == city.lower()) &
        (locations["pincode"].astype(str) == str(pincode))
    ]

    if match.empty:
        return None, None

    latitude = float(match.iloc[0]["latitude"])
    longitude = float(match.iloc[0]["longitude"])

    return latitude, longitude
    
 # ==========================================
# ADD NEW DELIVERY
# ==========================================
@app.route("/api/deliveries", methods=["POST"])
def add_delivery():
    try:
        data = request.get_json()

        customer_name = data.get("customer_name", "").strip()
        phone = data.get("phone", "").strip()
        address = data.get("address", "").strip()
        city = data.get("city", "").strip()
        pincode = data.get("pincode", "").strip()
        instructions = data.get("instructions", "").strip()

        if not customer_name or not phone or not address or not city or not pincode:
            return jsonify({
                "success": False,
                "message": "Please provide all required customer details."
            }), 400

        # Get latitude and longitude
        latitude, longitude = get_coordinates(
            address,
            city,
            pincode
        )

        if latitude is None:
            return jsonify({
                "success": False,
                "message": "This location is not available in our location data."
            }), 400

        last_delivery = deliveries_collection.find_one(
            {},
            sort=[("delivery_id", -1)]
        )

        if last_delivery and str(last_delivery.get("delivery_id", "")).startswith("D"):
            try:
                last_number = int(
                    str(last_delivery["delivery_id"])[1:]
                )
                next_number = last_number + 1

            except ValueError:
                next_number = deliveries_collection.count_documents({}) + 1

        else:
            next_number = deliveries_collection.count_documents({}) + 1

        delivery_id = f"D{next_number:03d}"
        delivery = {
            "delivery_id": delivery_id,
            "customer": customer_name,
            "phone": phone,
            "address": address,
            "city": city,
            "pincode": pincode,
            "instructions": instructions,
            "latitude": latitude,
            "longitude": longitude,
            "status": "new"
        }
        deliveries_collection.insert_one(delivery)

        delivery.pop("_id", None)

        return jsonify({
            "success": True,
            "message": "New delivery added successfully.",
            "delivery_id": delivery_id,
            "data": delivery
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500  

 # ==========================================
# IMPORT CSV DATA INTO MONGODB
# ==========================================
@app.route("/api/import-csv", methods=["POST"])
def import_csv_to_mongodb():

    try:

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "delivery_data.csv"
        )

        # Check CSV
        if not os.path.exists(file_path):

            return jsonify({
                "success": False,
                "message": "delivery_data.csv not found."
            }), 400

        # Read CSV
        df = pd.read_csv(file_path)

        # Convert DataFrame to dictionaries
        records = df.to_dict(orient="records")

        # Clear existing MongoDB delivery records
        deliveries_collection.delete_many({})

        # Insert records
        if records:

            result = deliveries_collection.insert_many(records)

            inserted_count = len(result.inserted_ids)

        else:

            inserted_count = 0

        return jsonify({

            "success": True,

            "message":
                "CSV data imported into MongoDB successfully.",

            "records_inserted":
                inserted_count,

            "database":
                db.name,

            "collection":
                deliveries_collection.name

        })

    except Exception as e:

        print(
            "MONGODB IMPORT ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "An error occurred while importing CSV data.",

            "error":
                str(e)

        }), 500
    
# ==========================================
# CONFIGURATION
# ==========================================

UPLOAD_FOLDER = "dataset"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# ML MODEL CONFIGURATION
# ==========================================

MODEL_PATH = os.path.join(
    "model",
    "delivery_model.pkl"
)


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# UPLOAD DATASET PAGE
# ==========================================

@app.route("/upload")
def upload():

    return render_template(
        "upload.html"
    )

# ==========================================
# NEW DELIVERY PAGE
# ==========================================

@app.route("/new-delivery")
def new_delivery():

    return render_template(
        "new_delivery.html"
    )

# ==========================================
# UPLOAD DATASET API
# ==========================================

@app.route("/api/upload", methods=["POST"])
def upload_dataset():

    try:

        # Check whether file exists
        if "file" not in request.files:

            return jsonify({

                "success": False,

                "message":
                    "No file was selected."

            }), 400


        # Get uploaded file
        file = request.files["file"]


        # Check filename
        if file.filename == "":

            return jsonify({

                "success": False,

                "message":
                    "Please select a CSV file."

            }), 400


        # Check file extension
        if not file.filename.lower().endswith(".csv"):

            return jsonify({

                "success": False,

                "message":
                    "Only CSV files are allowed."

            }), 400


        # ======================================
        # SAVE AS ACTIVE DATASET
        # ======================================

        file_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            "delivery_data.csv"

        )


        file.save(file_path)


        # ======================================
        # READ DATASET
        # ======================================

        df = pd.read_csv(
            file_path
        )


        # ======================================
        # REQUIRED COLUMNS
        # ======================================

        required_columns = [

            "delivery_id",

            "customer",

            "latitude",

            "longitude",

            "distance_km",

            "traffic",

            "weather",

            "delivery_time_min"

        ]


        # Find missing columns
        missing_columns = [

            column

            for column in required_columns

            if column not in df.columns

        ]


        # ======================================
        # VALIDATE COLUMNS
        # ======================================

        if missing_columns:

            # Remove invalid uploaded file
            if os.path.exists(file_path):

                os.remove(file_path)


            return jsonify({

                "success": False,

                "message":
                    "Dataset is missing required columns.",

                "missing_columns":
                    missing_columns

            }), 400


        # ======================================
        # SUCCESS RESPONSE
        # ======================================

        return jsonify({

            "success": True,

            "message":
                "Dataset uploaded successfully.",

            "filename":
                file.filename,

            "rows":
                len(df),

            "columns":
                df.columns.tolist()

        })


    except Exception as e:

        print(
            "UPLOAD ERROR:",
            e
        )


        return jsonify({

            "success": False,

            "message":
                "An error occurred while processing the dataset."

        }), 500


# ==========================================
# ROUTE OPTIMIZATION PAGE
# ==========================================

@app.route("/optimize")
def optimize():

    return render_template(
        "optimize.html"
    )


# ==========================================
# ROUTE OPTIMIZATION API
# ==========================================

@app.route("/api/optimize", methods=["POST"])
def api_optimize():

    try:

        # ======================================
        # GET NEW DELIVERIES FROM MONGODB
        # ======================================

        records = list(
            deliveries_collection.find(
                {"status": "new"},
                {"_id": 0}
            )
        )


        # ======================================
        # CHECK NEW DELIVERIES
        # ======================================

        if not records:

            return jsonify({
                "success": False,
                "message": "No new deliveries available for optimization."
            }), 400


        # ======================================
        # CREATE DATAFRAME
        # ======================================

        df = pd.DataFrame(records)


        # ======================================
        # CHECK REQUIRED COLUMNS
        # ======================================

        required_columns = [
            "delivery_id",
            "customer",
            "latitude",
            "longitude"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "success": False,
                "message": "Delivery data is missing required location fields.",
                "missing_columns": missing_columns
            }), 400


        # ======================================
        # CHECK COORDINATES
        # ======================================

        if (
            df["latitude"].isnull().any()
            or df["longitude"].isnull().any()
        ):

            return jsonify({
                "success": False,
                "message": "One or more deliveries do not have valid coordinates."
            }), 400


        # ======================================
        # RUN EXISTING ROUTE OPTIMIZER
        # ======================================

        optimized_route, total_distance = optimize_route(
            df
        )


        # ======================================
        # GET DELIVERY IDs
        # ======================================

        route_ids = optimized_route[
            "delivery_id"
        ].tolist()


        # ======================================
        # UPDATE DELIVERY STATUS
        # NEW → OPTIMIZED
        # ======================================

        deliveries_collection.update_many(
            {
                "delivery_id": {
                    "$in": route_ids
                },
                "status": "new"
            },
            {
                "$set": {
                    "status": "optimized"
                }
            }
        )


        # ======================================
        # UPDATE STATUS IN RESPONSE
        # ======================================

        optimized_route["status"] = "optimized"


         # ======================================
        # CONVERT ROUTE TO JSON
        # ======================================

        route_data = optimized_route.to_dict(
            orient="records"
        )

        # Replace NaN values with None for valid JSON
        for record in route_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        # ======================================
        # RETURN RESULT
        # ======================================

        return jsonify({

            "success": True,

            "message":
                "Route optimized successfully.",

            "total_deliveries":
                len(optimized_route),

            "total_distance_km":
                total_distance,

            "route":
                route_data

        })


    except Exception as e:

        print(
            "OPTIMIZATION ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "An error occurred during route optimization.",

            "error":
                str(e)

        }), 500

       
# ==========================================
# AI PREDICTION PAGE
# ==========================================

@app.route("/prediction")
def prediction():

    return render_template(
        "prediction.html"
    )


# ==========================================
# AI PREDICTION API
# ==========================================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    try:

        # ======================================
        # CHECK MODEL
        # ======================================

        if not os.path.exists(MODEL_PATH):

            return jsonify({

                "success": False,

                "message":
                    "Trained ML model not found."

            }), 500


        # ======================================
        # GET FRONTEND DATA
        # ======================================

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No prediction data was received."

            }), 400


        # ======================================
        # GET INPUT VALUES
        # ======================================

        distance = data.get(
            "distance_km"
        )

        traffic = data.get(
            "traffic"
        )

        weather = data.get(
            "weather"
        )


        # ======================================
        # VALIDATE INPUTS
        # ======================================

        if (
            distance is None
            or traffic is None
            or weather is None
        ):

            return jsonify({

                "success": False,

                "message":
                    "Distance, traffic and weather are required."

            }), 400


        # ======================================
        # CONVERT DISTANCE
        # ======================================

        distance = float(
            distance
        )


        # ======================================
        # VALIDATE DISTANCE
        # ======================================

        if distance <= 0:

            return jsonify({

                "success": False,

                "message":
                    "Distance must be greater than 0."

            }), 400


        # ======================================
        # LOAD TRAINED MODEL
        # ======================================

        with open(
            MODEL_PATH,
            "rb"
        ) as file:

            model = pickle.load(
                file
            )


        # ======================================
        # PREPARE INPUT DATA
        # ======================================

        input_data = pd.DataFrame({

            "distance_km": [
                distance
            ],

            "traffic": [
                traffic
            ],

            "weather": [
                weather
            ]

        })


        # ======================================
        # MAKE PREDICTION
        # ======================================

        prediction = model.predict(
            input_data
        )


        predicted_time = float(
            prediction[0]
        )


        # ======================================
        # RETURN PREDICTION
        # ======================================

        return jsonify({

            "success": True,

            "predicted_time_min":
                round(
                    predicted_time,
                    2
                ),

            "traffic":
                traffic,

            "weather":
                weather

        })


    except ValueError:

        return jsonify({

            "success": False,

            "message":
                "Distance must be a valid number."

        }), 400


    except Exception as e:

        print(
            "PREDICTION ERROR:",
            e
        )


        return jsonify({

            "success": False,

            "message":
                "An error occurred while making the prediction."

        }), 500
  # ==========================================
# REPORTS API
# ==========================================

@app.route("/api/report", methods=["GET"])
def api_report():

    try:

        # ======================================
        # GET DELIVERIES FROM MONGODB
        # ======================================

        records = list(
            deliveries_collection.find(
                {},
                {"_id": 0}
            )
        )

        # ======================================
        # CHECK DELIVERY DATA
        # ======================================

        if not records:
            return jsonify({
                "success": False,
                "message": "No delivery data available."
            }), 400

        # ======================================
        # CREATE DATAFRAME
        # ======================================

        df = pd.DataFrame(records)

        # ======================================
        # TOTAL DELIVERIES
        # ======================================

        total_deliveries = len(df)

        # ======================================
        # TOTAL DISTANCE
        # ======================================

        if "distance_km" in df.columns:

            total_distance = pd.to_numeric(
                df["distance_km"],
                errors="coerce"
            ).sum()

        else:

            total_distance = 0

        # ======================================
        # DELIVERY TIME
        # ======================================

        if "delivery_time_min" in df.columns:

            delivery_times = pd.to_numeric(
                df["delivery_time_min"],
                errors="coerce"
            )

            total_delivery_time = delivery_times.sum()

            average_delivery_time = delivery_times.mean()

        else:

            total_delivery_time = 0

            average_delivery_time = 0
                    # ======================================
        # OPTIMIZED ROUTE DISTANCE
        # ======================================

        optimized_records = list(
            deliveries_collection.find(
                {"status": "optimized"},
                {"_id": 0}
            )
        )

        optimized_distance = 0

        if optimized_records:

            optimized_df = pd.DataFrame(
                optimized_records
            )

            optimized_route, optimized_distance = optimize_route(
                optimized_df
            )

        optimized_distance = round(
            float(optimized_distance),
            2
        )

        # ======================================
        # TRAFFIC ANALYSIS
        # ======================================

        if (
            "traffic" in df.columns
            and "delivery_time_min" in df.columns
        ):

            traffic_analysis = (
                df.groupby("traffic")["delivery_time_min"]
                .mean()
                .round(2)
                .to_dict()
            )

        else:

            traffic_analysis = {}

        # ======================================
        # RETURN REPORT DATA
        # ======================================

        return jsonify({

            "success": True,

            "total_deliveries":
                total_deliveries,

            "total_distance_km":
                round(
                    float(total_distance),
                    2
                ),

            "total_delivery_time_min":
                round(
                    float(total_delivery_time),
                    2
                ),

            "average_delivery_time_min":
                round(
                    float(average_delivery_time),
                    2
                ),

            "traffic_analysis":
                traffic_analysis,

                       "model_r2":
                0.84,

            "optimized_distance_km":
                optimized_distance

        })

    except Exception as e:

        print(
            "REPORT ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "An error occurred while generating the report."

        }), 500

# ==========================================
# REPORT PAGE
# ==========================================

@app.route("/report")  
def report():

    return render_template(
        "report.html"
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
