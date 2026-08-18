import os
import sys
import subprocess
import time
import webbrowser
import signal

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

print("=========================================================")
print("          Mellgen Website Local CMS Workspace            ")
print("=========================================================")
print(f"[*] Base directory: {WORKSPACE_DIR}")

# Check if databases exist, if not, bootstrap them first!
db_check_path = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data", "products.json")
if not os.path.exists(db_check_path):
    print("[*] Databases not found. Bootstrapping initial database first...")
    try:
        bootstrap_script = os.path.join(WORKSPACE_DIR, "cms_system", "bootstrap_db.py")
        subprocess.run([sys.executable, bootstrap_script], check=True)
    except Exception as e:
        print(f"[-] Error bootstrapping database: {e}")
        sys.exit(1)

import socket

def get_lan_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip and not primary_ip.startswith("127."):
            ips.append(primary_ip)
    except Exception:
        pass
    try:
        host_name = socket.gethostname()
        for ip in socket.gethostbyname_ex(host_name)[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips

# Start 1: Front-end preview Web Server (port 8000)
print("[*] Launching Front-end Website Preview Server on port 8000...")
try:
    preview_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "-b", "0.0.0.0", "8000"],
        cwd=WORKSPACE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
except Exception as e:
    print(f"[-] Failed to launch preview server: {e}")
    sys.exit(1)

# Start 2: Flask CMS Server (port 8001)
print("[*] Launching CMS Backend Server on port 8001...")
server_script = os.path.join(WORKSPACE_DIR, "cms_system", "server.py")
try:
    # Set PYTHONPATH to root workspace folder so imports from cms_system work fine
    env = os.environ.copy()
    env["PYTHONPATH"] = WORKSPACE_DIR
    
    cms_process = subprocess.Popen(
        [sys.executable, server_script],
        cwd=os.path.join(WORKSPACE_DIR, "cms_system"),
        env=env
    )
except Exception as e:
    print(f"[-] Failed to launch CMS server: {e}")
    preview_process.kill()
    sys.exit(1)

# Wait a second for servers to boot up, then open browser
time.sleep(2)
print("\n[OK] Servers started successfully!")
print("  - 本地前台预览: http://localhost:8000")
print("  - 本地后台管理: http://localhost:8001")
print("  - 管理员账号密码: admin / admin888")

lan_ips = get_lan_ips()
if lan_ips:
    print("\n[局域网 LAN 访问地址]:")
    for ip in lan_ips:
        print(f"  - 网站前台: http://{ip}:8000")
        print(f"  - CMS后台:  http://{ip}:8001")
print("\n[提示] 如果局域网内其他设备打不开，请确认 Windows 防火墙已允许 Python 入站通信（或已开放 8000 / 8001 端口）。")
print("\n[*] Opening CMS Login page in your default browser...")

try:
    webbrowser.open("http://localhost:8001/login")
except Exception:
    pass

print("\n[!] Press Ctrl+C in this terminal to shut down both servers.")

# Keep running and wait for termination
try:
    while True:
        # Check if child processes are still alive
        if preview_process.poll() is not None:
            print("[-] Preview server stopped unexpectedly.")
            break
        if cms_process.poll() is not None:
            print("[-] CMS server stopped unexpectedly.")
            break
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[*] Shutting down servers gracefully...")
finally:
    # Terminate processes
    try:
        preview_process.terminate()
        cms_process.terminate()
        print("[OK] Stopped preview server (port 8000).")
        print("[OK] Stopped CMS server (port 8001).")
    except Exception:
        pass
    print("[*] Goodbye!")
