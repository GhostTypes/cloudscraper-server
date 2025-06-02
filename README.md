# 👻 cloudscraper-proxy

A simple local proxy server, powered by [cloudscraper](https://github.com/VeNoMouS/cloudscraper) library ☁️.
> 💡 This allows you to easily bypass Cloudflare "restrictions" in your project, without having to add additional code

---

## 👀 See it in Action!

**Before** (Standard request, 🧱 contents blocked by Cloudflare):
![image](https://github.com/user-attachments/assets/3ce7e244-8084-4e67-a904-e5a18d229899)

**After** (Using the local proxy ✅, contents accessed normally):
![image](https://github.com/user-attachments/assets/1b282213-6646-4011-abf0-5c19dc3de6d7)

---

## 🚀 Getting Started

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

That's it! 🎉 Your project can now make requests through the proxy.

---

## ⚙️ Configuration

Want to change the port? Easy!

Edit the `server.py` file at the bottom:
```python
if __name__ == "__main__":
    print('Starting Cloudflare bypass proxy server...')
    from waitress import serve
    # 👇 Change the port here
    serve(app, host="0.0.0.0", port=5000)
```

## 🐳 Docker & Make Commands
> 💡 The project includes several make commands to help manage the Docker container:
```
# 🏗️ Build the Docker image
make build

# ▶️ Run the Docker container (defaults to port 5000)
make run

# 🚀 Build and run in one go
make up

# 🛑 Stop and remove the container
make clean

# 📜 View container logs
make logs

# 🔄 Restart the container
make restart

# 📊 Check container status
make status
```
> 🔧 You can change the port and container settings by editing the variables at the top of the makefile.
