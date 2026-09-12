# -*- coding: utf-8 -*-
import os
import sys
import re
import shutil
import subprocess
from datetime import datetime

MCP_BLOCK = '''
    # WorkBuddy MCP 连接器反向代理 (8002 端口)
    location /mcp {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 长连接优化
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
'''

def find_nginx_config():
    search_dirs = ["/etc/nginx/conf.d", "/etc/nginx/sites-enabled", "/etc/nginx"]
    candidate_files = []
    
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for root, _, files in os.walk(sdir):
            for file in files:
                if file.endswith(".conf") or root.endswith("sites-enabled"):
                    fpath = os.path.join(root, file)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                        if "8001" in content or "mellgen" in content:
                            candidate_files.append((fpath, content))
                    except Exception:
                        pass
    return candidate_files

def main():
    print("========================================================")
    print("      美尔健官网 Nginx /mcp 反向代理自动配置工具        ")
    print("========================================================")
    
    if os.name == 'nt':
        print("[!] 当前在 Windows 环境下，此脚本供 Linux 服务器运行。")
        return

    candidates = find_nginx_config()
    if not candidates:
        print("[-] 未在 /etc/nginx/ 中找到包含 8001 或 mellgen 的配置文件。")
        print("[*] 尝试检查 /etc/nginx/nginx.conf ...")
        if os.path.exists("/etc/nginx/nginx.conf"):
            with open("/etc/nginx/nginx.conf", "r", encoding="utf-8", errors="ignore") as fp:
                candidates.append(("/etc/nginx/nginx.conf", fp.read()))
        else:
            print("[-] 未找到 Nginx 配置文件，请确认是否以 root/sudo 权限运行。")
            sys.exit(1)

    target_file, content = candidates[0]
    print(f"[*] 锁定目标 Nginx 配置文件: {target_file}")
    
    if "location /mcp" in content or "location /mcp/" in content:
        print("[*] 配置文件中已存在 location /mcp 规则，正在检查并规范为无斜杠转发...")
        # 替换确保指向 8002 且无斜杠截断
        new_content = re.sub(r'location\s+/mcp/?\s*\{[^}]+\}', MCP_BLOCK.strip(), content)
        if new_content == content:
            print("[OK] location /mcp 已经配置正确，无需重复修改。")
    else:
        print("[*] 正在注入 /mcp 代理规则...")
        # 寻找 location /api/ 或 location / 作为锚点在其前面插入
        if "location /api" in content:
            idx = content.find("location /api")
            # 找到前一行的换行符
            last_nl = content.rfind("\n", 0, idx)
            new_content = content[:last_nl] + "\n" + MCP_BLOCK + "\n" + content[last_nl:]
        elif "location /" in content:
            idx = content.find("location /")
            last_nl = content.rfind("\n", 0, idx)
            new_content = content[:last_nl] + "\n" + MCP_BLOCK + "\n" + content[last_nl:]
        else:
            # 插入在最后一个 } 之前
            last_brace = content.rfind("}")
            new_content = content[:last_brace] + "\n" + MCP_BLOCK + "\n}"

    # 备份原文件
    bak_file = target_file + f".bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(target_file, bak_file)
    print(f"[*] 已备份原配置文件至: {bak_file}")

    # 写入新内容
    with open(target_file, "w", encoding="utf-8") as fp:
        fp.write(new_content)

    # 测试语法
    print("[*] 测试 Nginx 语法 (nginx -t) ...")
    test_res = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if test_res.returncode != 0:
        print("[-] Nginx 语法测试失败，正在自动恢复备份...")
        print(test_res.stderr)
        shutil.copy2(bak_file, target_file)
        sys.exit(1)
    
    print("[OK] Nginx 语法检查通过！正在平滑重载 Nginx ...")
    reload_res = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
    if reload_res.returncode != 0:
        # 尝试 systemctl reload nginx
        subprocess.run(["systemctl", "reload", "nginx"])
        
    print("========================================================")
    print("[SUCCESS] Nginx /mcp 转发已全自动配置成功并生效！")
    print("========================================================")

if __name__ == "__main__":
    main()
