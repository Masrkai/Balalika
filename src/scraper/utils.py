import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS_PREFIXES = ('utm_', 'refid', 'trackingid', 'position', 'pagenum', 'e_id')

def normalize_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query)
    filtered_params = [
        (k, v) for k, v in query_params
        if not k.lower().startswith(TRACKING_PARAMS_PREFIXES)
    ]
    new_query = urlencode(filtered_params)
    parsed = parsed._replace(query=new_query, fragment='')
    return urlunparse(parsed)

def parse_salary(salary_text):
    """
    Parse a LinkedIn salary string like "$80,000 - $120,000" into
    (min_amount, max_amount, currency). Returns None when unparseable.
    """
    if not salary_text:
        return None
    parts = [p.strip() for p in salary_text.split('-')]
    if len(parts) < 2:
        return None
    CURRENCY_SYMBOLS = {'$': 'USD', '€': 'EUR', '£': 'GBP', '₹': 'INR'}

    def _num(token):
        m = re.search(r'[\d,]+', token)
        return int(m.group().replace(',', '')) if m else None

    min_amount = _num(parts[0])
    max_amount = _num(parts[1])
    if min_amount is None or max_amount is None:
        return None
    symbol = parts[0][0] if parts[0] else ''
    currency = CURRENCY_SYMBOLS.get(symbol, 'USD')
    return {'min_amount': min_amount, 'max_amount': max_amount, 'currency': currency}
