## 2024-05-23 - Decoding Overhead in Proxy Servers
**Learning:** Accessing `response.text` in Python's `requests` library triggers automatic encoding detection and decoding, which is computationally expensive (measured 260x slower than `.content` for large payloads). For proxy servers, this is often unnecessary waste as the data just needs to be forwarded.
**Action:** When building proxies or pass-through services, always prefer raw bytes (`.content`) and forward the original `Content-Type` header to avoid double-transcoding (upstream -> unicode -> utf-8).
