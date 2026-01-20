import subprocess
import time
import requests
import sys
import pytest

SERVER_PORT = 5000
BASE_URL = f"http://localhost:{SERVER_PORT}"


def wait_for_server():
    retries = 30
    while retries > 0:
        try:
            # The root path 404s, but connection refused means it's not up
            requests.get(BASE_URL, timeout=1)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(0.5)
            retries -= 1
    return False


def test_ssrf():
    print("Starting server...")
    # Start server in background with different port
    env = {**subprocess.os.environ, 'PORT': str(SERVER_PORT)}
    process = subprocess.Popen(
        [sys.executable, "-c", f"import server; server.app.run(host='localhost', port={SERVER_PORT})"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if not wait_for_server():
            stdout, stderr = process.communicate()
            print(f"Server failed to start. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
            pytest.fail("Server failed to start within timeout")

        print("Server started. Running tests...")

        # Test 1: SSRF to localhost (should be blocked)
        print("Testing SSRF to localhost...")
        target_url = f"http://127.0.0.1:{SERVER_PORT}/"
        proxy_url = f"{BASE_URL}/api/proxy/{target_url}"

        resp = requests.get(proxy_url)
        print(f"SSRF Status: {resp.status_code}")
        print(f"SSRF Response: {resp.text}")

        # Should return 403 (Forbidden) for blocked requests
        assert resp.status_code == 403, f"Expected 403 for localhost, got {resp.status_code}"
        assert "forbidden" in resp.text.lower() or "private" in resp.text.lower(), "Expected blocking error message"

        # Test 2: SSRF to private IP (should be blocked)
        print("Testing SSRF to private IP...")
        resp = requests.get(f"{BASE_URL}/api/proxy/http://192.168.1.1/")
        print(f"Private IP Status: {resp.status_code}")
        assert resp.status_code == 403, f"Expected 403 for private IP, got {resp.status_code}"

        # Test 3: Valid external URL format (will fail to connect, but shouldn't be blocked by SSRF)
        print("Testing valid external URL format...")
        resp = requests.get(f"{BASE_URL}/api/proxy/http://example.com/")
        print(f"External URL Status: {resp.status_code}")
        # Should NOT return 403 - the SSRF check should pass
        assert resp.status_code != 403, "External URL should not be blocked by SSRF check"

    finally:
        print("Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    test_ssrf()
