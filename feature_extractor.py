import re
import ssl
import socket
import requests
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def having_ip_address(url):
    """Check if the hostname is an IP address."""
    hostname = urlparse(url).hostname or ""
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return -1 if re.match(ip_pattern, hostname) else 1

def url_length(url):
    """Classify based on URL length."""
    length = len(url)
    if length < 54:
        return 1
    elif length <= 75:
        return 0
    else:
        return -1

def shortining_service(url):
    """Check if URL uses a known shortening service."""
    shorteners = r"bit\.ly|goo\.gl|tinyurl|t\.co|ow\.ly|is\.gd|buff\.ly"
    return -1 if re.search(shorteners, url) else 1

def having_at_symbol(url):
    return -1 if '@' in url else 1

def double_slash_redirecting(url):
    """Check for // appearing after the protocol."""
    last_slash_pos = url.rfind('//')
    return -1 if last_slash_pos > 7 else 1

def prefix_suffix(url):
    domain = urlparse(url).netloc
    return -1 if '-' in domain else 1

def having_sub_domain(url):
    """Count dots in domain (excluding www and TLD)."""
    domain = urlparse(url).netloc
    domain = domain.replace('www.', '')
    dot_count = domain.count('.')
    if dot_count <= 1:
        return 1
    elif dot_count == 2:
        return 0
    else:
        return -1

def https_token(url):
    """Check if 'https' appears in the domain (not as protocol)."""
    domain = urlparse(url).netloc
    return -1 if 'https' in domain else 1

def port(url):
    """Check if URL specifies a non-standard port."""
    parsed = urlparse(url)
    if parsed.port and parsed.port not in [80, 443]:
        return -1
    return 1

def sslfinal_state(url):
    """Check SSL certificate validity."""
    parsed = urlparse(url)

    if parsed.scheme != 'https':
        return -1

    hostname = parsed.hostname
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        if expire_date < datetime.now():
            return -1

        return 1

    except (ssl.SSLError, ssl.SSLCertVerificationError):
        return -1
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError):
        return -1

def dnsrecord(url):
    """Check if domain has a valid DNS record."""
    hostname = urlparse(url).hostname
    try:
        socket.gethostbyname(hostname)
        return 1
    except (socket.gaierror, TypeError):
        return -1

def fetch_page(url):
    """Fetch the page once; return (response, soup) or (None, None) on failure."""
    try:
        response = requests.get(url, timeout=5, allow_redirects=True,
                                 headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        return response, soup
    except requests.exceptions.RequestException:
        return None, None

def redirect(response):
    """Count redirects."""
    if response is None:
        return -1
    num_redirects = len(response.history)
    if num_redirects == 0:
        return 1
    elif num_redirects <= 2:
        return 0
    else:
        return -1

def request_url(soup, base_url):
    """% of images/scripts/etc. loaded from external domains."""
    if soup is None:
        return -1
    base_domain = urlparse(base_url).netloc
    total = 0
    external = 0
    for tag in soup.find_all(['img', 'script', 'video', 'audio', 'source']):
        src = tag.get('src')
        if src:
            total += 1
            src_domain = urlparse(src).netloc
            if src_domain and src_domain != base_domain:
                external += 1
    if total == 0:
        return 1
    pct = external / total
    if pct < 0.22:
        return 1
    elif pct <= 0.61:
        return 0
    else:
        return -1

def url_of_anchor(soup, base_url):
    """% of <a> tags pointing elsewhere or nowhere."""
    if soup is None:
        return -1
    base_domain = urlparse(base_url).netloc
    total = 0
    suspicious = 0
    for tag in soup.find_all('a'):
        href = tag.get('href')
        total += 1
        if not href or href.startswith('#') or href.lower().startswith('javascript:'):
            suspicious += 1
        else:
            href_domain = urlparse(href).netloc
            if href_domain and href_domain != base_domain:
                suspicious += 1
    if total == 0:
        return 1
    pct = suspicious / total
    if pct < 0.31:
        return 1
    elif pct <= 0.67:
        return 0
    else:
        return -1

def links_in_tags(soup, base_url):
    """% of <meta>/<script>/<link> referencing external domains."""
    if soup is None:
        return -1
    base_domain = urlparse(base_url).netloc
    total = 0
    external = 0
    for tag in soup.find_all(['meta', 'script', 'link']):
        src = tag.get('src') or tag.get('href')
        if src:
            total += 1
            src_domain = urlparse(src).netloc
            if src_domain and src_domain != base_domain:
                external += 1
    if total == 0:
        return 1
    pct = external / total
    if pct < 0.17:
        return 1
    elif pct <= 0.81:
        return 0
    else:
        return -1

def sfh(soup, base_url):
    """Check form action (Server Form Handler)."""
    if soup is None:
        return -1
    base_domain = urlparse(base_url).netloc
    forms = soup.find_all('form')
    if not forms:
        return 1
    for form in forms:
        action = form.get('action', '')
        if action == '' or action.lower() == 'about:blank':
            return -1
        action_domain = urlparse(action).netloc
        if action_domain and action_domain != base_domain:
            return 0
    return 1

def submitting_to_email(soup):
    """Check if any form submits via mailto:."""
    if soup is None:
        return 1
    for form in soup.find_all('form'):
        action = form.get('action', '')
        if 'mailto:' in action.lower():
            return -1
    return 1

def on_mouseover(soup):
    """Check for onmouseover JS event."""
    if soup is None:
        return 1
    html_str = str(soup).lower()
    return -1 if 'onmouseover' in html_str else 1

def popupwindow(soup):
    """Check for window.open (popups)."""
    if soup is None:
        return 1
    html_str = str(soup).lower()
    return -1 if 'window.open' in html_str else 1

def iframe(soup):
    """Check for iframe tags."""
    if soup is None:
        return 1
    return -1 if soup.find('iframe') else 1

def rightclick(soup):
    """Check for right-click disabling."""
    if soup is None:
        return 1
    html_str = str(soup).lower()
    return -1 if 'event.button==2' in html_str or 'contextmenu' in html_str else 1

def favicon(soup, base_url):
    """Check if favicon is loaded from same domain."""
    if soup is None:
        return 1
    base_domain = urlparse(base_url).netloc
    icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    if icon_link is None:
        return 1
    href = icon_link.get('href', '')
    if not href:
        return 1
    icon_domain = urlparse(href).netloc
    if icon_domain and icon_domain != base_domain:
        return -1
    return 1


def extract_features(url):
    """Extract all 22 features from a URL, in the order the model expects."""
    response, soup = fetch_page(url)

    features = {
        'sslfinal_state': sslfinal_state(url),
        'url_of_anchor': url_of_anchor(soup, url),
        'having_sub_domain': having_sub_domain(url),
        'links_in_tags': links_in_tags(soup, url),
        'prefix_suffix': prefix_suffix(url),
        'sfh': sfh(soup, url),
        'request_url': request_url(soup, url),
        'having_ip_address': having_ip_address(url),
        'dnsrecord': dnsrecord(url),
        'url_length': url_length(url),
        'https_token': https_token(url),
        'having_at_symbol': having_at_symbol(url),
        'redirect': redirect(response),
        'submitting_to_email': submitting_to_email(soup),
        'popupwindow': popupwindow(soup),
        'shortining_service': shortining_service(url),
        'favicon': favicon(soup, url),
        'on_mouseover': on_mouseover(soup),
        'double_slash_redirecting': double_slash_redirecting(url),
        'port': port(url),
        'iframe': iframe(soup),
        'rightclick': rightclick(soup),
    }

    return features


if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login",
        "http://paypal-secure-login.fake-site.com/account@verify",
    ]

    for url in test_urls:
        print(f"\nURL: {url}")
        print("  having_ip_address:", having_ip_address(url))
        print("  url_length:", url_length(url))
        print("  shortining_service:", shortining_service(url))
        print("  having_at_symbol:", having_at_symbol(url))
        print("  double_slash_redirecting:", double_slash_redirecting(url))
        print("  prefix_suffix:", prefix_suffix(url))
        print("  having_sub_domain:", having_sub_domain(url))
        print("  https_token:", https_token(url))
        print("  port:", port(url))

    print("\n--- SSL Check ---")
    for url in test_urls:
        print(f"{url}: sslfinal_state = {sslfinal_state(url)}")

    print("\n--- DNS Check ---")
    for url in test_urls:
        print(f"{url}: dnsrecord = {dnsrecord(url)}")

    print("\n--- HTML-based Features ---")
    for url in test_urls:
        print(f"\nURL: {url}")
        response, soup = fetch_page(url)
        print("  redirect:", redirect(response))
        print("  request_url:", request_url(soup, url))
        print("  url_of_anchor:", url_of_anchor(soup, url))
        print("  links_in_tags:", links_in_tags(soup, url))
        print("  sfh:", sfh(soup, url))
        print("  submitting_to_email:", submitting_to_email(soup))
        print("  on_mouseover:", on_mouseover(soup))
        print("  popupwindow:", popupwindow(soup))
        print("  iframe:", iframe(soup))
        print("  rightclick:", rightclick(soup))
        print("  favicon:", favicon(soup, url))

    print("\n--- Combined extract_features() ---")
    for url in test_urls:
        print(f"\nURL: {url}")
        feats = extract_features(url)
        for k, v in feats.items():
            print(f"  {k}: {v}")