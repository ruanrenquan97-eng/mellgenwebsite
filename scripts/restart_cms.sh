#!/bin/bash
# ==============================================================================
# 美尔健 CMS 后台一键彻底重启与自检脚本 (Linux 生产服务器专用)
# 功能：
# 1. 强行终止所有占用 8001 端口的旧 Python 进程
# 2. 检查并自动安装依赖环境 (beautifulsoup4 等)
# 3. 重新启动最新版本的 server.py
# 4. 自动发起本地接口自检测试，验证 /api/company-info 状态
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=========================================================="
echo "          美尔健 CMS 后台一键重启与环境诊断工具           "
echo "=========================================================="
echo "[*] 项目工作目录: $PROJECT_DIR"

# 1. 查找并结束旧的 Python CMS 进程
echo "[1/4] 正在排查并终止历史旧进程..."
if command -v fuser &>/dev/null; then
    fuser -k 8001/tcp 2>/dev/null || true
    fuser -k 8002/tcp 2>/dev/null || true
fi

PIDS=$(lsof -t -i:8001 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "  - 发现占用 8001 端口的旧进程 PID: $PIDS，正在终止..."
    kill -9 $PIDS 2>/dev/null
    sleep 1
fi

PGREP_PIDS=$(pgrep -f "cms_system/server.py")
if [ -n "$PGREP_PIDS" ]; then
    echo "  - 发现匹配 server.py 的进程 PID: $PGREP_PIDS，正在终止..."
    kill -9 $PGREP_PIDS 2>/dev/null
    sleep 1
fi
echo "  [OK] 旧进程清理完毕。"

# 2. 检查依赖与 Python 版本
echo "[2/4] 检查 Python 运行环境与依赖..."
if command -v python3.11 &>/dev/null; then
    PYTHON_CMD="python3.11"
    PIP_CMD="pip3.11"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi
echo "  - 选用 Python 环境: $PYTHON_CMD ($($PYTHON_CMD -V 2>&1))"

$PYTHON_CMD -c "import bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  - 正在安装缺少的基础依赖 (beautifulsoup4)..."
    $PIP_CMD install beautifulsoup4 || pip install beautifulsoup4
else
    echo "  [OK] 依赖环境正常。"
fi

# 3. 启动新版后端服务
echo "[3/4] 正在启动最新版 CMS 后端守护进程..."
export PYTHONPATH="$PROJECT_DIR"
nohup $PYTHON_CMD "$PROJECT_DIR/cms_system/server.py" > "$PROJECT_DIR/cms_system/server_daemon.log" 2>&1 &
NEW_PID=$!
sleep 2

if ps -p $NEW_PID > /dev/null; then
    echo "  [OK] 后端服务启动成功！新进程 PID: $NEW_PID"
else
    echo "  [-] 警告：进程未能成功启动，请查看错误日志:"
    tail -n 20 "$PROJECT_DIR/cms_system/server_daemon.log"
    exit 1
fi

# 4. 接口连通性自检
echo "[4/4] 正在对 /api/company-info 发起本地连通性探测..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/company-info)
echo "  - 本地探测结果 HTTP 状态码: $HTTP_CODE"

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 401 ] || [ "$HTTP_CODE" -eq 302 ]; then
    echo "  [SUCCESS] 接口路由已成功注册并正常响应！(状态码 $HTTP_CODE 表示接口存活)"
else
    echo "  [-] 异常状态码: $HTTP_CODE，最新日志片段:"
    tail -n 15 "$PROJECT_DIR/cms_system/server_daemon.log"
fi

# 5. Nginx 快速检查提示
if which nginx >/dev/null 2>&1; then
    nginx -t >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        nginx -s reload 2>/dev/null
        echo "[*] Nginx 配置重载完成。"
    fi
fi

echo "=========================================================="
echo "          重启完成！请在浏览器刷新后台面板测试            "
echo "=========================================================="
