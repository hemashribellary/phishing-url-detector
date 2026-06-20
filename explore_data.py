from ucimlrepo import fetch_ucirepo
import pandas as pd

# Fetch dataset (id=327 is the original Phishing Websites dataset)
phishing = fetch_ucirepo(id=327)

X = phishing.data.features
y = phishing.data.targets

print("Shape of X:", X.shape)
print("Shape of y:", y.shape)
print("\nFirst 5 rows of X:")
print(X.head())
print("\nFirst 5 values of y:")
print(y.head())
print("\nColumn names:")
print(X.columns.tolist())
print("\nMissing values per column:")
print(X.isnull().sum().sum())  # total missing values across all columns

print("\nClass balance (result column):")
print(y['result'].value_counts())