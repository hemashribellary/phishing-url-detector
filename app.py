from flask import Flask, render_template, request
import joblib
import pandas as pd
from feature_extractor import extract_features

app = Flask(__name__)

# Load the model once when the app starts
model = joblib.load('model/phishing_model_v2.pkl')

FEATURE_ORDER = [
    'sslfinal_state', 'url_of_anchor', 'having_sub_domain', 'links_in_tags',
    'prefix_suffix', 'sfh', 'request_url', 'having_ip_address', 'dnsrecord',
    'url_length', 'https_token', 'having_at_symbol', 'redirect',
    'submitting_to_email', 'popupwindow', 'shortining_service', 'favicon',
    'on_mouseover', 'double_slash_redirecting', 'port', 'iframe', 'rightclick'
]

FEATURE_EXPLANATIONS = {
    'sslfinal_state': 'Invalid or missing SSL certificate',
    'url_of_anchor': 'Links on the page point to unrelated or broken destinations',
    'having_sub_domain': 'Unusually high number of subdomains',
    'links_in_tags': 'Page resources (scripts, styles) loaded from external domains',
    'prefix_suffix': 'Domain name contains a hyphen (often mimics brand names)',
    'sfh': 'Login form submits data to a suspicious or empty destination',
    'request_url': 'Images and media loaded from unrelated external domains',
    'having_ip_address': 'URL uses a raw IP address instead of a domain name',
    'dnsrecord': 'Domain has no valid DNS record',
    'url_length': 'Unusually long URL',
    'https_token': '"https" used misleadingly within the domain name',
    'having_at_symbol': 'URL contains an "@" symbol (can hide the real destination)',
    'redirect': 'Page redirects multiple times before loading',
    'submitting_to_email': 'Form submits data directly via email instead of a server',
    'popupwindow': 'Page uses pop-up windows',
    'shortining_service': 'URL uses a link-shortening service',
    'favicon': 'Site icon loaded from a different domain',
    'on_mouseover': 'Page changes link behavior when hovered (can disguise destinations)',
    'double_slash_redirecting': 'Suspicious "//" redirect pattern in the URL path',
    'port': 'URL uses a non-standard network port',
    'iframe': 'Page contains hidden iframes',
    'rightclick': 'Page disables right-click (often used to block inspection)',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form.get('url', '').strip()

    if not url:
        return render_template('index.html', error="Please enter a URL.")

    # Add http:// if missing
    if not url.startswith('http'):
        url = 'http://' + url

    # Extract features
    features = extract_features(url)

    # Convert to dataframe in correct order
    df = pd.DataFrame([features])[FEATURE_ORDER]

    # Predict
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]

    is_phishing = prediction == -1
    confidence = round(max(probability) * 100, 1)

    # Find risk factors (features that came back as -1)
    risk_factors = [FEATURE_EXPLANATIONS.get(k, k) for k, v in features.items() if v == -1]

    return render_template('result.html',
                           url=url,
                           is_phishing=is_phishing,
                           confidence=confidence,
                           risk_factors=risk_factors)

if __name__ == '__main__':
    app.run(debug=True)