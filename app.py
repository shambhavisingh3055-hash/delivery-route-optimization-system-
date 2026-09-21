from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import pickle

from route_optimizer import optimize_route


app = Flask(__name__)


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
        # DATASET PATH
        # ======================================

        file_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            "delivery_data.csv"

        )


        # ======================================
        # CHECK DATASET
        # ======================================

        if not os.path.exists(file_path):

            return jsonify({

                "success": False,

                "message":
                    "Please upload a delivery dataset first."

            }), 400


        # ======================================
        # READ DATASET
        # ======================================

        df = pd.read_csv(
            file_path
        )


        # ======================================
        # RUN ROUTE OPTIMIZATION
        # ======================================

        optimized_route, total_distance = optimize_route(
            df
        )


        # ======================================
        # CONVERT RESULT TO JSON
        # ======================================

        route_data = optimized_route.to_dict(
            orient="records"
        )


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
                "An error occurred during route optimization."

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

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "delivery_data.csv"
        )

        if not os.path.exists(file_path):

            return jsonify({
                "success": False,
                "message": "Dataset not found."
            }), 400

        df = pd.read_csv(file_path)

        total_deliveries = len(df)

        total_distance = df["distance_km"].sum()

        total_delivery_time = df["delivery_time_min"].sum()

        average_delivery_time = df["delivery_time_min"].mean()

        traffic_analysis = (
            df.groupby("traffic")["delivery_time_min"]
            .mean()
            .round(2)
            .to_dict()
        )

        return jsonify({

            "success": True,

            "total_deliveries": total_deliveries,

            "total_distance_km": round(
                total_distance, 2
            ),

            "total_delivery_time_min": round(
                total_delivery_time, 2
            ),

            "average_delivery_time_min": round(
                average_delivery_time, 2
            ),

            "traffic_analysis": traffic_analysis,

            "model_r2": 0.84

        })

    except Exception as e:

        print("REPORT ERROR:", e)

        return jsonify({

            "success": False,

            "message": "An error occurred while generating the report."

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
