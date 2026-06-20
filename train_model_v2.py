from ucimlrepo import fetch_ucirepo
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load full dataset
phishing = fetch_ucirepo(id=327)
X_full = phishing.data.features
y = phishing.data.targets['result']

# Keep only our 22 reliably-computable features
keep_features = [
    'sslfinal_state', 'url_of_anchor', 'having_sub_domain', 'links_in_tags',
    'prefix_suffix', 'sfh', 'request_url', 'having_ip_address', 'dnsrecord',
    'url_length', 'https_token', 'having_at_symbol', 'redirect',
    'submitting_to_email', 'popupwindow', 'shortining_service', 'favicon',
    'on_mouseover', 'double_slash_redirecting', 'port', 'iframe', 'rightclick'
]

X = X_full[keep_features]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Logistic Regression
log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train, y_train)
log_pred = log_model.predict(X_test)
print("=== Logistic Regression (22 features) ===")
print("Accuracy:", accuracy_score(y_test, log_pred))
print(confusion_matrix(y_test, log_pred))
print(classification_report(y_test, log_pred))

# Train Random Forest
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
print("\n=== Random Forest (22 features) ===")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print(confusion_matrix(y_test, rf_pred))
print(classification_report(y_test, rf_pred))

# Save the better model (Random Forest, based on Phase 3 results)
joblib.dump(rf_model, 'phishing_model_v2.pkl')
print("\nModel saved as phishing_model_v2.pkl")