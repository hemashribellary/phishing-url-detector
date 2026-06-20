from ucimlrepo import fetch_ucirepo
import pandas as pd
import joblib

# Load the dataset (for feature names) and the saved model
phishing = fetch_ucirepo(id=327)
X = phishing.data.features

model = joblib.load('phishing_model.pkl')

# Get feature importances
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': importances
}).sort_values('importance', ascending=False)

print(feature_importance_df.to_string(index=False))