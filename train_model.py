from ucimlrepo import fetch_ucirepo
import pandas as pd
from sklearn.model_selection import train_test_split

# Load the phishing dataset
phishing = fetch_ucirepo(id=327)
X = phishing.data.features
y = phishing.data.targets['result']

# Split into train/test (80/20, same as practice)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training set size:", X_train.shape)
print("Test set size:", X_test.shape)
print("\nTraining set class balance:")
print(y_train.value_counts())
print("\nTest set class balance:")
print(y_test.value_counts())
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Model 1: Logistic Regression
log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train, y_train)
log_pred = log_model.predict(X_test)

print("\n=== Logistic Regression ===")
print("Accuracy:", accuracy_score(y_test, log_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, log_pred))
print(classification_report(y_test, log_pred))

# Model 2: Random Forest
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

print("\n=== Random Forest ===")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, rf_pred))
print(classification_report(y_test, rf_pred))

import joblib

joblib.dump(rf_model, 'phishing_model.pkl')
print("\nModel saved as phishing_model.pkl")