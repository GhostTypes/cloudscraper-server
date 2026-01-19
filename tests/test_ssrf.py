import subprocess
import time
import requests
import sys
import os

SERVER_PORT = 5000
BASE_URL = f"http://localhost:{SERVER_PORT}"

def wait_for_server():
    retries = 30
    while retries > 0:
        try:
            # The root path 404s, but connection refused means it's not up
            requests.get(BASE_URL)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            retries -= 1
    return False

def test_ssrf():
    print("Starting server...")
    # Start server in background
    # We use sys.executable to ensure we use the same python interpreter
    process = subprocess.Popen([sys.executable, "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        if not wait_for_server():
            print("Server failed to start")
            sys.exit(1)

        print("Server started. Running tests...")

        # Test 1: Proxy to google.com (Valid)
        # We might not have internet access in some sandboxes, but let's assume we do or handle it.
        # If we don't have internet, this might fail with connection error, but the status code won't be 400 from our validation.
        print("Testing valid external URL...")
        try:
            resp = requests.get(f"{BASE_URL}/api/proxy/http://example.com")
            print(f"External URL Status: {resp.status_code}")
            # It might be 200 or 500 depending on network, but we are looking for behavior.
        except Exception as e:
            print(f"External URL Request failed: {e}")

        # Test 2: SSRF to localhost (Vulnerability)
        # We try to proxy to the server itself.
        # Since the server has no root route, accessing http://127.0.0.1:5000/ should return 404.
        # If the proxy works, it will return that 404 (or 500 if recursive blowup).
        # If blocked, it should return 400 (or whatever we decide).
        print("Testing SSRF to localhost...")
        target_url = f"http://127.0.0.1:{SERVER_PORT}/"
        proxy_url = f"{BASE_URL}/api/proxy/{target_url}"

        resp = requests.get(proxy_url)
        print(f"SSRF Status: {resp.status_code}")

        # In the vulnerable state, we expect the code to execute the request.
        # Since 127.0.0.1:5000/ returns 404, the proxy will return 404.
        if resp.status_code == 404:
            print("VULNERABILITY CONFIRMED: Proxied request to localhost (received 404 from internal).")
        elif resp.status_code == 200:
             print("VULNERABILITY CONFIRMED: Proxied request to localhost (received 200).")
        elif resp.status_code == 500:
            # 500 could mean it tried and failed (e.g. max retries), which still means it tried.
            print("VULNERABILITY CONFIRMED: Proxied request to localhost (received 500).")
        elif resp.status_code == 400 or resp.status_code == 403:
            print("SECURE: Request to localhost blocked.")
        else:
            print(f"Unexpected status: {resp.status_code}")

    finally:
        print("Stopping server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_ssrf()
