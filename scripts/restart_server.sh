#!/bin/bash
# ==============================================================================
# 美尔健官网 (Mellgen) Linux 阿里云服务器 CMS 后台与 WorkBuddy MCP 重启脚本
# ==============================================================================

echo "========================================================"
echo "      Mellgen CMS & WorkBuddy MCP Server Restart        "
echo "========================================================"

WORKSPACE_DIR="/var/www/mellgenwebsite"
if [ -d "$WORKSPACE_DIR" ]; then
    cd "$WORKSPACE_DIR" || exit 1
else
    WORKSPACE_DIR=$(pwd)
    cd "$WORKSPACE_DIR" || exit 1
fi
echo "[*] Working Directory: $WORKSPACE_DIR"

echo "[1/4] Pulling latest code from GitHub..."
git pull origin main

echo "[2/4] Installing Python dependencies (Flask, FastMCP, Starlette, Uvicorn)..."
if command -v pip3 &>/dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &>/dev/null; then
    pip install -r requirements.txt
fi

echo "[2.5/4] Auto-configuring Nginx /mcp reverse proxy for WorkBuddy..."
if [ -f "scripts/auto_config_nginx.py" ]; then
    python3 scripts/auto_config_nginx.py || true
fi

echo "[3/4] Stopping existing processes on port 8001 (CMS) and port 8002 (MCP)..."
pkill -9 -f "server.py" 2>/dev/null || true
pkill -9 -f "mcp_server.py" 2>/dev/null || true
pkill -9 -f "run_cms.py" 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true
fuser -k 8002/tcp 2>/dev/null || true
sleep 1

echo "[4/4] Starting servers in background..."
export PYTHONPATH="$WORKSPACE_DIR"

# 1. Start Flask CMS Server on port 8001
nohup python3 cms_system/server.py > server.log 2>&1 &
echo "  -> CMS Backend Server started on port 8001."

# 2. Start WorkBuddy FastMCP SSE Server on port 8002
nohup python3 cms_system/mcp_server.py sse 8002 > mcp_server.log 2>&1 &
echo "  -> WorkBuddy FastMCP SSE Server started on port 8002."

sleep 2

echo ""
echo "Checking listening ports (8001 & 8002):"
if command -v ss &>/dev/null; then
    ss -tlpn | grep -E "8001|8002"
elif command -v netstat &>/dev/null; then
    netstat -tlpn | grep -E "8001|8002"
fi

echo ""
echo "Testing CMS API endpoint (8001):"
curl -s -I http://127.0.0.1:8001/api/ai_service/config | head -n 3

echo "Testing MCP SSE endpoint (8002):"
curl -s -I http://127.0.0.1:8002/mcp/sse | head -n 3

echo "========================================================"
echo "[OK] Both CMS and MCP Servers are up and running!"
echo "CMS Log: tail -f server.log"
echo "MCP Log: tail -f mcp_server.log"
echo "========================================================"
