#!/bin/bash
# ==============================================================================
# 美尔健官网 (Mellgen) Linux 阿里云服务器 CMS 后台与 WorkBuddy MCP 一键重启脚本
# ==============================================================================

echo "========================================================"
echo "      Mellgen CMS & WorkBuddy MCP Server Restart        "
echo "========================================================"

# 智能获取项目根目录，无论从任何路径执行均能精准定位
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKSPACE_DIR="$( dirname "$SCRIPT_DIR" )"

if [ -d "$WORKSPACE_DIR" ] && [ -f "$WORKSPACE_DIR/cms_system/server.py" ]; then
    cd "$WORKSPACE_DIR" || exit 1
elif [ -d "/var/www/mellgenwebsite" ]; then
    cd "/var/www/mellgenwebsite" || exit 1
    WORKSPACE_DIR="/var/www/mellgenwebsite"
else
    WORKSPACE_DIR=$(pwd)
    cd "$WORKSPACE_DIR" || exit 1
fi
echo "[*] Working Directory: $WORKSPACE_DIR"

echo "[1/4] Pulling latest code from GitHub..."
git pull origin main

echo "[2/4] Checking Python dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install -r requirements.txt || true
elif command -v pip &>/dev/null; then
    pip install -r requirements.txt || true
fi

echo "[3/4] Stopping previous servers..."
pkill -9 -f "server.py" 2>/dev/null || true
pkill -9 -f "mcp_server.py" 2>/dev/null || true
pkill -9 -f "run_cms.py" 2>/dev/null || true
if command -v fuser &>/dev/null; then
    fuser -k 8001/tcp 2>/dev/null || true
    fuser -k 8002/tcp 2>/dev/null || true
fi
sleep 1

echo "[4/4] Starting Mellgen CMS & WorkBuddy Native MCP Server (Port 8001)..."
export PYTHONPATH="$WORKSPACE_DIR"

# 启动核心 Flask 服务（包含全站内容管理、AI 客服与原生 WorkBuddy MCP SSE）
nohup python3 cms_system/server.py > server.log 2>&1 &
echo "  -> CMS & WorkBuddy Native MCP Server started on port 8001."

# 尝试启动独立 FastMCP (端口 8002，若环境支持)
if python3 -c "import mcp" 2>/dev/null; then
    nohup python3 cms_system/mcp_server.py sse 8002 > mcp_server.log 2>&1 &
    echo "  -> Optional FastMCP Standalone Server started on port 8002."
fi

sleep 2

echo ""
echo "Checking running processes:"
ps aux | grep -E "server.py" | grep -v grep

echo ""
echo "Testing CMS API endpoint (8001):"
curl -s -I http://127.0.0.1:8001/api/ai_service/config | head -n 3

echo ""
echo "Testing Native WorkBuddy MCP SSE endpoint (8001):"
curl -s -I http://127.0.0.1:8001/api/mcp/sse | head -n 3

echo ""
echo "========================================================"
echo "[SUCCESS] 美尔健官网系统与 WorkBuddy MCP 连接器已成功启动！"
echo ""
echo "👉 WorkBuddy 直连端点 (零配置即连即通，推荐):"
echo "   https://www.mellgen.com/api/mcp/sse?token=您的Token"
echo ""
echo "👉 网站后台管理中心:"
echo "   https://www.mellgen.com/admin"
echo "========================================================"

