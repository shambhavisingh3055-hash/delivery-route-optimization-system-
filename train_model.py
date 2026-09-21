import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pickle


# ==========================================
# LOAD DATASET
# ==========================================

dataset_path = os.path.join(
    "dataset",
    "delivery_data.csv"
)

df = pd.read_csv(dataset_path)

print("Dataset loaded successfully.")
print("Total records:", len(df))


# ==========================================
# INPUT FEATURES AND TARGET
# ==========================================

X = df[
    [
        "distance_km",
        "traffic",
        "weather"
    ]
]

y = df["delivery_time_min"]


# ==========================================
# CATEGORICAL FEATURES
# ==========================================

categorical_features = [
    "traffic",
    "weather"
]

numeric_features = [
    "distance_km"
]


# ==========================================
# PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),

        (
            "numeric",
            "passthrough",
            numeric_features
        )

    ]
)


# ==========================================
# MACHINE LEARNING MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ==========================================
# CREATE ML PIPELINE
# ==========================================

pipeline = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )

    ]

)


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42

)


print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# TRAIN MODEL
# ==========================================

print("\nTraining ML model...")

pipeline.fit(
    X_train,
    y_train
)

print("Model training completed.")


# ==========================================
# MAKE PREDICTIONS
# ==========================================

y_pred = pipeline.predict(
    X_test
)


# ==========================================
# MODEL EVALUATION
# ==========================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n========== MODEL PERFORMANCE ==========")

print(
    "Mean Absolute Error:",
    round(mae, 2),
    "minutes"
)

print(
    "Root Mean Squared Error:",
    round(rmse, 2),
    "minutes"
)

print(
    "R² Score:",
    round(r2, 2)
)


# ==========================================
# CREATE MODEL DIRECTORY
# ==========================================

model_directory = "model"

os.makedirs(
    model_directory,
    exist_ok=True
)


# ==========================================
# SAVE TRAINED MODEL
# ==========================================

model_path = os.path.join(
    model_directory,
    "delivery_model.pkl"
)

with open(
    model_path,
    "wb"
) as file:

    pickle.dump(
        pipeline,
        file
    )


print("\nModel saved successfully.")

print(
    "Model location:",
    model_path
)