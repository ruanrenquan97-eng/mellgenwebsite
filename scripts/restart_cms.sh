#!/bin/bash
# ==============================================================================
# 美尔健 CMS 后台一键彻底重启与自检脚本 (Linux 生产服务器专用)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=========================================================="
echo "          美尔健 CMS 后台一键重启与环境诊断工具           "
echo "=========================================================="
echo "[*] 项目工作目录: $PROJECT_DIR"

# 1. 强力终止所有占用 8001 端口的旧进程
echo "[1/4] 正在清理 8001 端口历史旧进程..."
fuser -k 8001/tcp 2>/dev/null
PIDS=$(lsof -t -i:8001 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "  - 终止占用 8001 端口的 PID: $PIDS"
    kill -9 $PIDS 2>/dev/null
fi
pkill -9 -f "cms_system/server.py" 2>/dev/null
sleep 1
echo "  [OK] 8001 端口已彻底释放。"

# 2. 检查依赖
echo "[2/4] 检查运行依赖..."
python3 -c "import bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  - 正在安装缺失依赖..."
    pip3 install beautifulsoup4 || pip install beautifulsoup4
else
    echo "  [OK] 依赖正常。"
fi

# 3. 启动新版后端服务
echo "[3/4] 启动最新版 CMS 服务 (秒级监听)..."
export PYTHONPATH="$PROJECT_DIR"
nohup python3 "$PROJECT_DIR/cms_system/server.py" > "$PROJECT_DIR/cms_system/server_daemon.log" 2>&1 &
NEW_PID=$!
sleep 2

# 4. 接口连通性自检
echo "[4/4] 本地连通性探测..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/company-info)
echo "  - 探测结果 HTTP 状态码: $HTTP_CODE"

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 401 ] || [ "$HTTP_CODE" -eq 302 ]; then
    echo "  [SUCCESS] 8001 后台服务正常运行！(状态码: $HTTP_CODE)"
else
    echo "  [-] 警告：状态码 $HTTP_CODE，最新日志:"
    tail -n 15 "$PROJECT_DIR/cms_system/server_daemon.log"
fi

# 5. Nginx 重载
if which nginx >/dev/null 2>&1; then
    nginx -t >/dev/null 2>&1 && nginx -s reload 2>/dev/null
    echo "[*] Nginx 配置已重载。"
fi

echo "=========================================================="
echo "服务日志 (最新):"
tail -n 6 "$PROJECT_DIR/cms_system/server_daemon.log" 2>/dev/null
echo "=========================================================="
echo "  [完成] 请刷新浏览器后台测试！"
echo "=========================================================="
