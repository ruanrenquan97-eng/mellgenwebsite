#!/bin/bash
# ==============================================================================
# 美尔健官网 (Mellgen) Linux 阿里云服务器 CMS 后台重启与更新脚本
# ==============================================================================

echo "========================================================"
echo "          Mellgen CMS Production Server Restart          "
echo "========================================================"

WORKSPACE_DIR="/var/www/mellgenwebsite"
if [ -d "" ]; then
    cd "" || exit 1
else
    echo "[-] Directory  not found, using current directory."
    WORKSPACE_DIR=E:\私有云\我的AI管理系统\mellgen_website
fi

echo "[1/4] Pulling latest code from GitHub..."
git pull origin main

echo "[2/4] Checking and installing Python dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &>/dev/null; then
    pip install -r requirements.txt
fi

echo "[3/4] Stopping existing CMS Python process on port 8001..."
# Kill any process listening on port 8001 or matching server.py
pkill -9 -f "python.*server.py" 2>/dev/null || true
pkill -9 -f "python.*run_cms.py" 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true
sleep 1

echo "[4/4] Starting CMS Python server in background..."
export PYTHONPATH=""
nohup python3 cms_system/server.py > server.log 2>&1 &

sleep 2

# Verify that port 8001 is listening
if command -v ss &>/dev/null; then
    ss -tlpn | grep 8001
elif command -v netstat &>/dev/null; then
    netstat -tlpn | grep 8001
fi

echo "Testing API endpoint:"
curl -s -I http://127.0.0.1:8001/api/ai_service/config | head -n 5

echo "========================================================"
echo "[OK] CMS Server restarted successfully!"
echo "Server log can be checked via: tail -f server.log"
echo "========================================================"
