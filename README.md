<div align="center">
  <h1>cloudscraper-proxy</h1>
  <p>A simple local proxy server, powered by <a href="https://github.com/VeNoMouS/cloudscraper">cloudscraper</a> library</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/github/v/release/GhostTypes/cloudscraper-server?style=for-the-badge">
  <img src="https://img.shields.io/badge/docker-ready-blue?style=for-the-badge&logo=docker&logoColor=white">
</p>

<div align="center">
  <p>This allows you to easily bypass Cloudflare "restrictions" in your project, without having to add additional code</p>
</div>

---

<div align="center">
  <h2>Getting Started</h2>
</div>

1.  **Modify Your Requests:**

    Instead of directly requesting a URL like:
    ```
    https://www.google.com
    ```
    Point it to your local proxy server:
    ```
    http://localhost:5000/api/proxy/https://www.google.com
    ```
    *(Replace `5000` if you change the default port)*

2.  **Start the Proxy Server:**

    Run the Python server:
    ```bash
    python server.py
    ```

That's it! Your project can now make requests through the proxy.

---

<div align="center">
  <h2>Configuration</h2>
</div>

Want to change the port? Easy!

Edit the `server.py` file at the bottom:
```python
if __name__ == "__main__":
    print('Starting Cloudflare bypass proxy server...')
    from waitress import serve
    # Change the port here
    serve(app, host="0.0.0.0", port=5000)
```

---

<div align="center">
  <h2>Docker & Make Commands</h2>
</div>

<div align="center">
  <p>The project includes several make commands to help manage the Docker container</p>
</div>

<div align="center">
<table>
  <tr>
    <th>Command</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>make build</code></td>
    <td>Build the Docker image</td>
  </tr>
  <tr>
    <td><code>make run</code></td>
    <td>Run the Docker container (defaults to port 5000)</td>
  </tr>
  <tr>
    <td><code>make up</code></td>
    <td>Build and run in one go</td>
  </tr>
  <tr>
    <td><code>make clean</code></td>
    <td>Stop and remove the container</td>
  </tr>
  <tr>
    <td><code>make logs</code></td>
    <td>View container logs</td>
  </tr>
  <tr>
    <td><code>make restart</code></td>
    <td>Restart the container</td>
  </tr>
  <tr>
    <td><code>make status</code></td>
    <td>Check container status</td>
  </tr>
</table>
</div>

<div align="center">
  <p>You can change the port and container settings by editing the variables at the top of the makefile.</p>
</div>
