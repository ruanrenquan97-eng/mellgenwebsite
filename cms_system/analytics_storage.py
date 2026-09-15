# -*- coding: utf-8 -*-
"""
Mellgen CMS - Analytics, Traffic & Accounts Persistent Storage Engine (系统数据与账号持久化保险箱)
确保全站访客记录、今日流量、30天历史趋势、产品受访排行、受访页面以及【全部新增/修改的系统账号与权限】，
在任何代码更新、Git操作、分支切换或服务重启过程中【永不丢失】。
具备自动双向自愈合并、SQLite双重持久化与滚动快照备份机制。
"""

import os
import sys
import json
import sqlite3
import datetime
import threading
import shutil

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(CURRENT_DIR, "cms_data")
VAULT_DIR = os.path.join(DATA_DIR, "persistent")
BACKUP_DIR = os.path.join(DATA_DIR, "backups", "analytics")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

SQLITE_DB_PATH = os.path.join(VAULT_DIR, "analytics_vault.db")
PERSISTENT_SEO_VAULT = os.path.join(VAULT_DIR, "seo_metrics_vault.json")
PERSISTENT_VISITOR_VAULT = os.path.join(VAULT_DIR, "visitor_logs_vault.json")
PERSISTENT_ACCOUNTS_VAULT = os.path.join(VAULT_DIR, "accounts_vault.json")

_db_lock = threading.RLock()


def get_db_connection():
    """获取 SQLite 数据库连接并开启 WAL 模式以保障高并发读写与断电安全"""
    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=20.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_vault():
    """初始化持久化数据库表结构"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 每日流量历史总表 (支持无限年份存储，永不被覆盖)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_traffic (
                date TEXT PRIMARY KEY,
                pv INTEGER DEFAULT 0,
                uv INTEGER DEFAULT 0,
                ip INTEGER DEFAULT 0,
                pc_count INTEGER DEFAULT 0,
                mobile_count INTEGER DEFAULT 0,
                today_ips TEXT,
                extra_json TEXT,
                updated_at TEXT
            );
        """)

        # 2. 产品受访热度与行为统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_stats (
                product_id TEXT PRIMARY KEY,
                title TEXT,
                category TEXT,
                url TEXT,
                pv INTEGER DEFAULT 0,
                uv INTEGER DEFAULT 0,
                avg_duration_sec INTEGER DEFAULT 0,
                avg_duration_str TEXT,
                bounce_rate TEXT DEFAULT '0%',
                hot_pct INTEGER DEFAULT 0,
                last_visited TEXT
            );
        """)

        # 3. 重点页面受访统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_stats (
                url TEXT PRIMARY KEY,
                title TEXT,
                type TEXT,
                pv INTEGER DEFAULT 0,
                uv INTEGER DEFAULT 0,
                avg_duration_sec INTEGER DEFAULT 0,
                avg_duration_str TEXT,
                last_visited TEXT
            );
        """)

        # 4. 访客实时动态轨迹流水表 (按时间倒序保存所有历史会话)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitor_stream (
                id TEXT PRIMARY KEY,
                time TEXT,
                ip TEXT,
                region TEXT,
                title TEXT,
                url TEXT,
                type TEXT,
                duration_str TEXT,
                referrer TEXT,
                device TEXT,
                created_at TEXT
            );
        """)

        # 5. 全局指标与快照备份表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_snapshots (
                key TEXT PRIMARY KEY,
                data_json TEXT,
                updated_at TEXT
            );
        """)

        # 6. 系统账户持久化表 (管理员与操作员账户永久安全存储，不随代码更新而丢失)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_accounts (
                username TEXT PRIMARY KEY,
                password TEXT,
                name TEXT,
                role TEXT,
                permissions TEXT,
                disabled INTEGER DEFAULT 0,
                mobile TEXT,
                remark TEXT,
                created_at TEXT,
                updated_at TEXT
            );
        """)

        conn.commit()
        conn.close()


def atomic_save_json(filepath, data):
    """原子写入 JSON 文件（先写临时文件再重命名，防止进程崩溃导致文件损坏）"""
    tmp_path = filepath + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(tmp_path):
            os.replace(tmp_path, filepath)
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise e


def safe_load_json(filepath, default=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


# =========================================================================
# 账号持久化保险箱 (System Accounts Persistence & Protection)
# =========================================================================

def get_all_accounts():
    """获取所有持久化账户（以 SQLite 保险箱为主准，合并 accounts_vault.json 与 settings.json）"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_accounts ORDER BY rowid ASC")
        rows = cursor.fetchall()
        accounts_map = {}
        for r in rows:
            perms_raw = r["permissions"]
            try:
                perms = json.loads(perms_raw) if perms_raw else ["*"]
            except Exception:
                perms = ["*"]
            accounts_map[r["username"]] = {
                "username": r["username"],
                "password": r["password"],
                "name": r["name"] or r["username"],
                "role": r["role"] or "操作员",
                "permissions": perms,
                "disabled": bool(r["disabled"]),
                "mobile": r["mobile"] or "",
                "remark": r["remark"] or "",
                "created_at": r["created_at"] or "2026-09-01 00:00:00"
            }
        conn.close()

    # 兜底：如果 SQLite 为空，尝试从 accounts_vault.json 或 settings.json 导入
    if not accounts_map:
        vault_accounts = safe_load_json(PERSISTENT_ACCOUNTS_VAULT) or []
        if not vault_accounts:
            settings = safe_load_json(os.path.join(DATA_DIR, "settings.json")) or {}
            vault_accounts = settings.get("accounts", [])
        if not vault_accounts:
            vault_accounts = [
                {"username": "admin", "password": "admin123", "role": "管理员", "name": "系统管理员", "permissions": ["*"], "disabled": False, "created_at": "2026-09-01 00:00:00"},
                {"username": "kefu", "password": "kefu888", "role": "客服", "name": "在线客服", "permissions": ["overview", "orders", "tools"], "disabled": False, "created_at": "2026-09-01 00:00:00"}
            ]
        for acc in vault_accounts:
            save_account_to_vault(acc, sync_settings=False)
            accounts_map[acc["username"]] = acc

    # 确保 admin 始终存在
    if "admin" not in accounts_map:
        admin_acc = {"username": "admin", "password": "admin123", "role": "管理员", "name": "系统管理员", "permissions": ["*"], "disabled": False, "created_at": "2026-09-01 00:00:00"}
        save_account_to_vault(admin_acc, sync_settings=False)
        accounts_map["admin"] = admin_acc

    return list(accounts_map.values())


def save_account_to_vault(acc, sync_settings=True):
    """保存或更新单个账户到 SQLite 数据库与持久化镜像"""
    username = acc.get("username", "").strip()
    if not username:
        return
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    perms = acc.get("permissions", ["*"])
    perms_str = json.dumps(perms, ensure_ascii=False) if isinstance(perms, list) else json.dumps(["*"])

    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_accounts (username, password, name, role, permissions, disabled, mobile, remark, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password = excluded.password,
                name = excluded.name,
                role = excluded.role,
                permissions = excluded.permissions,
                disabled = excluded.disabled,
                mobile = excluded.mobile,
                remark = excluded.remark,
                updated_at = excluded.updated_at
        """, (
            username,
            acc.get("password", ""),
            acc.get("name", username),
            acc.get("role", "操作员"),
            perms_str,
            1 if acc.get("disabled") else 0,
            acc.get("mobile", ""),
            acc.get("remark", ""),
            acc.get("created_at") or now_str,
            now_str
        ))
        conn.commit()
        conn.close()

    # 同步更新持久化 JSON 文件
    all_accs = get_all_accounts()
    atomic_save_json(PERSISTENT_ACCOUNTS_VAULT, all_accs)

    if sync_settings:
        sync_accounts_to_settings(all_accs)


def delete_account_from_vault(username):
    """从 SQLite 与持久化镜像中彻底删除账户"""
    if username == "admin":
        return
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM system_accounts WHERE username = ?", (username,))
        conn.commit()
        conn.close()

    all_accs = get_all_accounts()
    atomic_save_json(PERSISTENT_ACCOUNTS_VAULT, all_accs)
    sync_accounts_to_settings(all_accs)


def sync_accounts_to_settings(accounts_list=None):
    """将账号列表写回 settings.json，保持完全兼容"""
    if accounts_list is None:
        accounts_list = get_all_accounts()
    settings_path = os.path.join(DATA_DIR, "settings.json")
    settings = safe_load_json(settings_path)
    if isinstance(settings, dict):
        settings["accounts"] = accounts_list
        atomic_save_json(settings_path, settings)


def heal_and_sync_settings_accounts(settings_data):
    """
    自愈保护：确保任意从文件读取到的 settings_data 始终包含 SQLite 保险箱中最新且最完整的账户列表！
    如果 settings.json 刚被 Git 拉取或代码更新覆盖，此函数会自动将保险箱中全部自定义账号合并恢复回来。
    """
    if not isinstance(settings_data, dict):
        return settings_data
    persisted_accs = get_all_accounts()
    persisted_unames = {a["username"] for a in persisted_accs}

    # 如果 settings_data 中有从外部新增的账户，录入 SQLite
    curr_accs = settings_data.get("accounts", [])
    if isinstance(curr_accs, list):
        for ca in curr_accs:
            if ca.get("username") and ca["username"] not in persisted_unames:
                save_account_to_vault(ca, sync_settings=False)

    # 强制将完整的持久化账户赋给 settings_data["accounts"]
    settings_data["accounts"] = get_all_accounts()
    return settings_data


# =========================================================================
# 流量与访客数据持久化同步与自愈机制 (Analytics Healing & Merging)
# =========================================================================

def sync_active_data_to_vault():
    """将当前 active 的 seo_metrics.json 与 visitor_logs.json 注入持久化 SQLite 数据库与保险箱"""
    seo_file = os.path.join(DATA_DIR, "seo_metrics.json")
    vlog_file = os.path.join(DATA_DIR, "visitor_logs.json")

    seo_data = safe_load_json(seo_file)
    vlog_data = safe_load_json(vlog_file)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 保存流量历史到 SQLite
        if seo_data and isinstance(seo_data, dict):
            traffic = seo_data.get("traffic", {})
            curr_date = traffic.get("current_date") or datetime.date.today().strftime("%Y-%m-%d")
            
            # 记录今日
            cursor.execute("""
                INSERT INTO daily_traffic (date, pv, uv, ip, pc_count, mobile_count, today_ips, extra_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    pv = MAX(daily_traffic.pv, excluded.pv),
                    uv = MAX(daily_traffic.uv, excluded.uv),
                    ip = MAX(daily_traffic.ip, excluded.ip),
                    pc_count = MAX(daily_traffic.pc_count, excluded.pc_count),
                    mobile_count = MAX(daily_traffic.mobile_count, excluded.mobile_count),
                    today_ips = excluded.today_ips,
                    extra_json = excluded.extra_json,
                    updated_at = excluded.updated_at
            """, (
                curr_date,
                traffic.get("pv", 0),
                traffic.get("uv", 0),
                traffic.get("ip", 0),
                traffic.get("devices", {}).get("pc", 0),
                traffic.get("devices", {}).get("mobile", 0),
                json.dumps(traffic.get("today_ips", []), ensure_ascii=False),
                json.dumps({
                    "pv_growth": traffic.get("pv_growth"),
                    "sources": traffic.get("sources", []),
                    "avg_duration": traffic.get("avg_duration")
                }, ensure_ascii=False),
                now_str
            ))

            # 记录 30 天 / 7 天历史
            for h in (traffic.get("history_30d") or []) + (traffic.get("history_7d") or []):
                h_date = h.get("full_date")
                if not h_date and h.get("date"):
                    year = datetime.date.today().year
                    h_date = f"{year}-{h.get('date')}"
                if h_date:
                    cursor.execute("""
                        INSERT INTO daily_traffic (date, pv, uv, ip, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(date) DO UPDATE SET
                            pv = MAX(daily_traffic.pv, excluded.pv),
                            uv = MAX(daily_traffic.uv, excluded.uv),
                            ip = MAX(daily_traffic.ip, excluded.ip),
                            updated_at = excluded.updated_at
                    """, (h_date, h.get("pv", 0), h.get("uv", 0), h.get("ip", 0), now_str))

            # 备份 SEO 全量快照到 Vault
            cursor.execute("""
                INSERT INTO system_snapshots (key, data_json, updated_at)
                VALUES ('seo_metrics', ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    data_json = excluded.data_json,
                    updated_at = excluded.updated_at
            """, (json.dumps(seo_data, ensure_ascii=False), now_str))

            atomic_save_json(PERSISTENT_SEO_VAULT, seo_data)

        # 2. 保存访客与受访页面到 SQLite
        if vlog_data and isinstance(vlog_data, dict):
            # 产品
            for prod in vlog_data.get("top_products", []):
                pid = prod.get("id") or prod.get("url", "").replace("products/", "").replace(".html", "")
                if pid:
                    cursor.execute("""
                        INSERT INTO product_stats (product_id, title, category, url, pv, uv, avg_duration_sec, avg_duration_str, bounce_rate, hot_pct, last_visited)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(product_id) DO UPDATE SET
                            pv = MAX(product_stats.pv, excluded.pv),
                            uv = MAX(product_stats.uv, excluded.uv),
                            title = excluded.title,
                            category = excluded.category,
                            url = excluded.url,
                            avg_duration_sec = MAX(product_stats.avg_duration_sec, excluded.avg_duration_sec),
                            avg_duration_str = excluded.avg_duration_str,
                            hot_pct = MAX(product_stats.hot_pct, excluded.hot_pct),
                            last_visited = excluded.last_visited
                    """, (
                        pid,
                        prod.get("title", ""),
                        prod.get("category", "核心原料"),
                        prod.get("url", f"products/{pid}.html"),
                        prod.get("pv", 0),
                        prod.get("uv", 0),
                        prod.get("avg_duration_sec", 0),
                        prod.get("avg_duration_str", "0秒"),
                        prod.get("bounce_rate", "0%"),
                        prod.get("hot_pct", 0),
                        now_str
                    ))

            # 页面
            for pg in vlog_data.get("top_pages", []):
                p_url = pg.get("url")
                if p_url:
                    cursor.execute("""
                        INSERT INTO page_stats (url, title, type, pv, uv, avg_duration_sec, avg_duration_str, last_visited)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(url) DO UPDATE SET
                            pv = MAX(page_stats.pv, excluded.pv),
                            uv = MAX(page_stats.uv, excluded.uv),
                            title = excluded.title,
                            type = excluded.type,
                            avg_duration_sec = MAX(page_stats.avg_duration_sec, excluded.avg_duration_sec),
                            avg_duration_str = excluded.avg_duration_str,
                            last_visited = excluded.last_visited
                    """, (
                        p_url,
                        pg.get("title", ""),
                        pg.get("type", "页面浏览"),
                        pg.get("pv", 0),
                        pg.get("uv", 0),
                        pg.get("avg_duration_sec", 0),
                        pg.get("avg_duration_str", "0秒"),
                        now_str
                    ))

            # 访客流水
            for stream_item in vlog_data.get("realtime_stream", []):
                sid = stream_item.get("id") or f"v-{int(datetime.datetime.now().timestamp())}"
                cursor.execute("""
                    INSERT OR IGNORE INTO visitor_stream (id, time, ip, region, title, url, type, duration_str, referrer, device, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid,
                    stream_item.get("time", ""),
                    stream_item.get("ip", ""),
                    stream_item.get("region", ""),
                    stream_item.get("title", ""),
                    stream_item.get("url", ""),
                    stream_item.get("type", "页面浏览"),
                    stream_item.get("duration_str", "刚刚进入"),
                    stream_item.get("referrer", "直接访问"),
                    stream_item.get("device", "电脑端"),
                    now_str
                ))

            # 备份 Visitor 全量快照到 Vault
            cursor.execute("""
                INSERT INTO system_snapshots (key, data_json, updated_at)
                VALUES ('visitor_logs', ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    data_json = excluded.data_json,
                    updated_at = excluded.updated_at
            """, (json.dumps(vlog_data, ensure_ascii=False), now_str))

            atomic_save_json(PERSISTENT_VISITOR_VAULT, vlog_data)

        conn.commit()
        conn.close()


def heal_and_get_seo_metrics(metrics_data):
    """
    自愈并合并 SEO & 流量数据：
    如果 metrics_data 的 PV/UV 为 0 或缺少历史，自动从 SQLite 保险箱恢复最大统计值和历史趋势！
    """
    if not metrics_data or not isinstance(metrics_data, dict) or "traffic" not in metrics_data:
        vault_data = safe_load_json(PERSISTENT_SEO_VAULT)
        if vault_data and isinstance(vault_data, dict):
            metrics_data = vault_data

    if not metrics_data or not isinstance(metrics_data, dict):
        return metrics_data

    traffic = metrics_data.get("traffic", {})
    today_full = datetime.date.today().strftime("%Y-%m-%d")

    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 恢复今日最高流量
        cursor.execute("SELECT * FROM daily_traffic WHERE date = ?", (today_full,))
        today_row = cursor.fetchone()
        if today_row:
            vault_pv = today_row["pv"] or 0
            vault_uv = today_row["uv"] or 0
            vault_ip = today_row["ip"] or 0
            vault_pc = today_row["pc_count"] or 0
            vault_mobile = today_row["mobile_count"] or 0

            traffic["pv"] = max(traffic.get("pv", 0), vault_pv)
            traffic["uv"] = max(traffic.get("uv", 0), vault_uv)
            traffic["ip"] = max(traffic.get("ip", 0), vault_ip)

            if "devices" not in traffic or not isinstance(traffic["devices"], dict):
                traffic["devices"] = {"pc": 0, "mobile": 0}
            traffic["devices"]["pc"] = max(traffic["devices"].get("pc", 0), vault_pc)
            traffic["devices"]["mobile"] = max(traffic["devices"].get("mobile", 0), vault_mobile)

            if today_row["today_ips"]:
                try:
                    db_ips = json.loads(today_row["today_ips"])
                    merged_ips = list(set(traffic.get("today_ips", []) + db_ips))
                    traffic["today_ips"] = merged_ips
                    traffic["uv"] = max(traffic["uv"], len(merged_ips))
                    traffic["ip"] = max(traffic["ip"], len(merged_ips))
                except Exception:
                    pass

        # 2. 从 SQLite 查询完整的最近 30 天流量历史
        cursor.execute("SELECT date, pv, uv, ip FROM daily_traffic ORDER BY date DESC LIMIT 60")
        all_db_history = {row["date"]: dict(row) for row in cursor.fetchall()}

        history_30d = []
        today_date = datetime.date.today()
        for i in range(29, -1, -1):
            d = today_date - datetime.timedelta(days=i)
            d_full = d.strftime("%Y-%m-%d")
            d_short = d.strftime("%m-%d")

            if i == 0:
                history_30d.append({
                    "date": d_short,
                    "full_date": d_full,
                    "pv": traffic.get("pv", 0),
                    "uv": traffic.get("uv", 0),
                    "ip": traffic.get("ip", 0)
                })
            else:
                db_item = all_db_history.get(d_full)
                if db_item:
                    history_30d.append({
                        "date": d_short,
                        "full_date": d_full,
                        "pv": db_item.get("pv", 0),
                        "uv": db_item.get("uv", 0),
                        "ip": db_item.get("ip", 0)
                    })
                else:
                    existing_h = next((h for h in traffic.get("history_30d", []) if h.get("full_date") == d_full or h.get("date") == d_short), None)
                    if existing_h:
                        history_30d.append({
                            "date": d_short,
                            "full_date": d_full,
                            "pv": existing_h.get("pv", 0),
                            "uv": existing_h.get("uv", 0),
                            "ip": existing_h.get("ip", 0)
                        })
                    else:
                        history_30d.append({
                            "date": d_short,
                            "full_date": d_full,
                            "pv": 0,
                            "uv": 0,
                            "ip": 0
                        })

        traffic["history_30d"] = history_30d
        traffic["history_7d"] = history_30d[-7:]
        metrics_data["traffic"] = traffic

        conn.close()

    return metrics_data


def heal_and_get_visitor_logs(logs_data):
    """
    自愈并合并访客与页面排行数据：
    如果 logs_data 为空或丢失产品访问量，自动从 SQLite 恢复全部数据！
    """
    if not logs_data or not isinstance(logs_data, dict):
        vault_logs = safe_load_json(PERSISTENT_VISITOR_VAULT)
        if vault_logs and isinstance(vault_logs, dict):
            logs_data = vault_logs
        else:
            logs_data = {"top_products": [], "top_pages": [], "realtime_stream": []}

    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 恢复与合并产品排行
        cursor.execute("SELECT * FROM product_stats ORDER BY pv DESC")
        db_prods = {row["product_id"]: dict(row) for row in cursor.fetchall()}

        curr_prods = logs_data.get("top_products", [])
        curr_prod_ids = {p.get("id"): p for p in curr_prods if p.get("id")}

        for pid, db_p in db_prods.items():
            if pid in curr_prod_ids:
                curr_p = curr_prod_ids[pid]
                curr_p["pv"] = max(curr_p.get("pv", 0), db_p.get("pv", 0))
                curr_p["uv"] = max(curr_p.get("uv", 0), db_p.get("uv", 0))
                curr_p["avg_duration_sec"] = max(curr_p.get("avg_duration_sec", 0), db_p.get("avg_duration_sec", 0))
                if not curr_p.get("avg_duration_str") or curr_p.get("avg_duration_str") == "0秒":
                    curr_p["avg_duration_str"] = db_p.get("avg_duration_str", "0秒")
            else:
                curr_prods.append({
                    "id": pid,
                    "title": db_p.get("title", pid),
                    "category": db_p.get("category", "核心原料"),
                    "url": db_p.get("url", f"products/{pid}.html"),
                    "pv": db_p.get("pv", 0),
                    "uv": db_p.get("uv", 0),
                    "avg_duration_sec": db_p.get("avg_duration_sec", 0),
                    "avg_duration_str": db_p.get("avg_duration_str", "0秒"),
                    "bounce_rate": db_p.get("bounce_rate", "0%"),
                    "hot_pct": db_p.get("hot_pct", 0)
                })

        curr_prods.sort(key=lambda x: x.get("pv", 0), reverse=True)
        logs_data["top_products"] = curr_prods

        # 2. 恢复与合并页面排行
        cursor.execute("SELECT * FROM page_stats ORDER BY pv DESC")
        db_pages = {row["url"]: dict(row) for row in cursor.fetchall()}
        curr_pages = logs_data.get("top_pages", [])
        curr_page_urls = {p.get("url"): p for p in curr_pages if p.get("url")}

        for p_url, db_pg in db_pages.items():
            if p_url in curr_page_urls:
                cp = curr_page_urls[p_url]
                cp["pv"] = max(cp.get("pv", 0), db_pg.get("pv", 0))
                cp["uv"] = max(cp.get("uv", 0), db_pg.get("uv", 0))
            else:
                curr_pages.append({
                    "title": db_pg.get("title", p_url),
                    "url": p_url,
                    "type": db_pg.get("type", "页面浏览"),
                    "pv": db_pg.get("pv", 0),
                    "uv": db_pg.get("uv", 0),
                    "avg_duration_sec": db_pg.get("avg_duration_sec", 0),
                    "avg_duration_str": db_pg.get("avg_duration_str", "0秒")
                })
        curr_pages.sort(key=lambda x: x.get("pv", 0), reverse=True)
        logs_data["top_pages"] = curr_pages

        # 3. 恢复实时访客轨迹流（保留最新的 30 条）
        if not logs_data.get("realtime_stream"):
            cursor.execute("SELECT * FROM visitor_stream ORDER BY rowid DESC LIMIT 30")
            stream_rows = cursor.fetchall()
            logs_data["realtime_stream"] = [
                {
                    "id": r["id"],
                    "time": r["time"],
                    "ip": r["ip"],
                    "region": r["region"],
                    "title": r["title"],
                    "url": r["url"],
                    "type": r["type"],
                    "duration_str": r["duration_str"],
                    "referrer": r["referrer"],
                    "device": r["device"]
                }
                for r in stream_rows
            ]

        conn.close()

    return logs_data


def create_periodic_snapshot():
    """创建滚动时间戳备份快照"""
    now = datetime.datetime.now()
    stamp = now.strftime("%Y%m%d_%H%M%S")
    snapshot_file = os.path.join(BACKUP_DIR, f"analytics_snapshot_{stamp}.json")

    seo_file = os.path.join(DATA_DIR, "seo_metrics.json")
    vlog_file = os.path.join(DATA_DIR, "visitor_logs.json")

    snapshot_data = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "accounts": get_all_accounts(),
        "seo_metrics": safe_load_json(seo_file),
        "visitor_logs": safe_load_json(vlog_file)
    }

    atomic_save_json(snapshot_file, snapshot_data)

    try:
        files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("analytics_snapshot_")])
        if len(files) > 60:
            for old_f in files[:-60]:
                os.remove(os.path.join(BACKUP_DIR, old_f))
    except Exception:
        pass


def export_full_backup_data():
    """全量导出备份数据字典"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM daily_traffic ORDER BY date DESC")
        daily_traffic = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM product_stats ORDER BY pv DESC")
        product_stats = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM page_stats ORDER BY pv DESC")
        page_stats = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM visitor_stream ORDER BY rowid DESC LIMIT 100")
        visitor_stream = [dict(r) for r in cursor.fetchall()]

        conn.close()

    return {
        "export_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "7.0",
        "accounts": get_all_accounts(),
        "daily_traffic": daily_traffic,
        "product_stats": product_stats,
        "page_stats": page_stats,
        "visitor_stream": visitor_stream,
        "seo_metrics": safe_load_json(os.path.join(DATA_DIR, "seo_metrics.json")),
        "visitor_logs": safe_load_json(os.path.join(DATA_DIR, "visitor_logs.json"))
    }


def get_vault_summary():
    """获取保险箱持久化状态统计"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), SUM(pv), SUM(uv) FROM daily_traffic")
        dt_res = cursor.fetchone()
        days_count = dt_res[0] or 0
        total_pv = dt_res[1] or 0
        total_uv = dt_res[2] or 0

        cursor.execute("SELECT COUNT(*) FROM product_stats")
        prod_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM visitor_stream")
        stream_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM system_accounts")
        accounts_count = cursor.fetchone()[0] or 0

        conn.close()

    db_size_kb = 0
    if os.path.exists(SQLITE_DB_PATH):
        db_size_kb = round(os.path.getsize(SQLITE_DB_PATH) / 1024, 1)

    backup_count = 0
    if os.path.exists(BACKUP_DIR):
        backup_count = len([f for f in os.listdir(BACKUP_DIR) if f.startswith("analytics_snapshot_")])

    return {
        "status": "active",
        "sqlite_db": SQLITE_DB_PATH,
        "db_size_kb": db_size_kb,
        "total_accounts_count": accounts_count,
        "recorded_days": days_count,
        "total_historical_pv": total_pv,
        "total_historical_uv": total_uv,
        "tracked_products_count": prod_count,
        "recorded_sessions_count": stream_count,
        "backup_snapshots_count": backup_count,
        "last_backup_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# 初始化启动
init_vault()
sync_active_data_to_vault()
# 自动把已有的账号同步到数据库保险箱中
get_all_accounts()
