import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv(r"C:\Users\moksh\OneDrive\Documents\Projects\Techsophy project\Cancer-Screening-Reminder-and-Risk-Stratification-System\Model Training\cancer_prediction_dataset.csv")


X = df.drop(columns=["Cancer"])
y = df["Cancer"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

joblib.dump(model, "model.pkl")
print("Model trained and saved.")
