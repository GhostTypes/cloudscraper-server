import cloudscraper
import time

from urllib.parse import unquote
from flask import Flask, request, Response

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=1,
    allow_brotli=True
)


def set_user_agent(headers):
    # this needs to match Sec-Ch-Ua (cloudflare will flag as a bot seeing two different user agents)
    # make sure to change it accordingly if you change this
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/120.0.0.0 Safari/537.36'
    return headers


def set_security_headers(headers):
    headers['Sec-Ch-Ua'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
    headers['Sec-Ch-Ua-Mobile'] = '?0'
    headers['Sec-Ch-Ua-Platform'] = '"Windows"'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-origin'
    return headers


def set_origin_and_ref(headers, origin, ref):
    headers['Origin'] = origin
    headers['Referer'] = ref
    return headers


def generate_origin_and_ref(url, headers):
    data = url.split('/')
    first = data[0]
    base = data[2]
    c_url = f"{first}//{base}/"
    headers = set_origin_and_ref(headers, c_url, c_url)
    return headers


app = Flask(__name__)

HOP_BY_HOP_HEADERS = {
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade',
}


def clean_headers(response):
    headers = {}
    for name, value in response.headers.items():
        if name.lower() not in HOP_BY_HOP_HEADERS:
            headers[name] = value
    headers.pop('content-encoding', None)
    headers.pop('content-length', None)
    return headers


def generate_proxy_response(response) -> Response:
    content_type = response.headers.get('content-type', '')

    # OPTIMIZATION: Use .content (bytes) to avoid decoding overhead
    # This provides significant performance improvement and avoids potential transcoding issues.
    content = response.content

    headers = clean_headers(response)

    # For JSON content
    if 'application/json' in content_type:
        return Response(content, status=response.status_code, content_type='application/json')

    # For HTML content
    if 'text/html' in content_type:
        # Use the original content type to ensure charset matches the raw bytes
        return Response(content, status=response.status_code, content_type=content_type)

    # For all other content types
    return Response(
        content,
        status=response.status_code,
        headers=headers
    )


def get_headers():
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    headers = set_user_agent(headers)
    headers = set_security_headers(headers)
    return headers


def get_proxy_request_url(req, url):
    full_url = unquote(url.strip('"'))
    if req.query_string:
        full_url = f"{full_url}?{req.query_string.decode('utf-8')}"
    return full_url


def get_proxy_request_headers(req, url):
    headers = get_headers()
    headers['Accept-Encoding'] = 'gzip, deflate, br'

    for header in req.headers:
        if header[0].lower() not in ['host', 'connection', 'content-length']:
            headers[header[0]] = header[1]
    headers = generate_origin_and_ref(url, headers)
    return headers


# Cloudflare bypassed request
@app.route("/api/proxy/<path:url>", methods=["GET"])
def handle_proxy(url):
    if request.method == 'GET':
        full_url = get_proxy_request_url(request, url)  # parse request url
        headers = get_proxy_request_headers(request, url)  # generate headers for the request

        try:
            start = time.time()
            response = scraper.get(full_url, headers=headers)
            end = time.time()
            elapsed = end - start
            print(f"Proxied request for {full_url.split('?')[0]} in {elapsed:.6f} seconds")
            response.raise_for_status()

            return generate_proxy_response(response)

        except Exception as e:
            print(f"Proxy Request Error: {str(e)}")
            return {'error': str(e)}, 500


if __name__ == "__main__":
    print('Starting cloudflare bypass proxy server')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
