from flask import Flask, render_template

app = Flask(__name__)


# --------------------------
# Dashboard
# --------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------
# Upload Dataset
# --------------------------
@app.route("/upload")
def upload():
    return render_template("upload.html")


# --------------------------
# Route Optimization
# --------------------------
@app.route("/optimize")
def optimize():
    return render_template("optimize.html")


# --------------------------
# AI Prediction
# --------------------------
@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


# --------------------------
# Reports
# --------------------------
@app.route("/report")
def report():
    return render_template("report.html")


# --------------------------
# Run Application
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)