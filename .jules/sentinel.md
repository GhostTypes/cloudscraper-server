## 2024-05-22 - SSRF in Proxy Endpoint
**Vulnerability:** The `/api/proxy/<path:url>` endpoint accepted and requested any URL provided by the user, including `localhost` and private IP ranges. This allowed potential access to internal network services or the proxy server itself.
**Learning:** Proxy applications are inherently vulnerable to SSRF. Relying on "it's just a local tool" is insufficient as it might be deployed in containers or environments with access to other services.
**Prevention:** Implemented strict URL validation (`is_safe_url`) that resolves the hostname and checks if the IP belongs to private/loopback blocks before making the request. Also added timeouts and generic error messages to prevent DoS and info leakage.
