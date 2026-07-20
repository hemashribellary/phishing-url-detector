from ucimlrepo import fetch_ucirepo
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

print("Starting model training...")

# Load dataset
phishing = fetch_ucirepo(id=327)
X_full = phishing.data.features
y = phishing.data.targets['result']

# Keep only the 22 computable features
keep_features = [
    'sslfinal_state', 'url_of_anchor', 'having_sub_domain', 'links_in_tags',
    'prefix_suffix', 'sfh', 'request_url', 'having_ip_address', 'dnsrecord',
    'url_length', 'https_token', 'having_at_symbol', 'redirect',
    'submitting_to_email', 'popupwindow', 'shortining_service', 'favicon',
    'on_mouseover', 'double_slash_redirecting', 'port', 'iframe', 'rightclick'
]

X = X_full[keep_features]

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

# Save
os.makedirs('model', exist_ok=True)
joblib.dump(rf_model, 'model/phishing_model_v2.pkl')

print(f"Model trained and saved. Accuracy: {rf_model.score(X_test, y_test):.4f}")