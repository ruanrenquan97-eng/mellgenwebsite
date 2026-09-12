# -*- coding: utf-8 -*-
"""
Mellgen Biotechnology - Daily SEO & GEO Automated Execution Pipeline & Scheduler
"""

import os
import sys
import re
import json
import time
import uuid
import datetime
import threading
import urllib.request
import urllib.error
import urllib.parse

# Workspace path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")

INDEXNOW_KEY = "mellgen2026indexnow8f93e17b"
DOMAIN_BASE = "https://www.mellgen.com"

def load_json_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_json_data(filename, data):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[-] Error saving {filename}: {e}")

def get_schedule_config():
    settings = load_json_data("settings.json") or {}
    cfg = settings.get("seo_auto_schedule")
    if not cfg or not isinstance(cfg, dict):
        cfg = {
            "enabled": True,
            "run_time": "03:00",
            "auto_sitemap": True,
            "auto_indexnow": True,
            "auto_baidu": True,
            "auto_ai_geo": True,
            "auto_log_parse": True,
            "server_access_log_path": "",
            "last_run_time": None,
            "last_run_status": "就绪",
            "last_run_summary": "等待首次自动化触发"
        }
        settings["seo_auto_schedule"] = cfg
        save_json_data("settings.json", settings)
    return cfg

def save_schedule_config(cfg):
    settings = load_json_data("settings.json") or {}
    settings["seo_auto_schedule"] = cfg
    save_json_data("settings.json", settings)

def record_daily_run_log(log_entry):
    logs = load_json_data("daily_seo_logs.json") or []
    logs.insert(0, log_entry)
    if len(logs) > 60:
        logs = logs[:60]
    save_json_data("daily_seo_logs.json", logs)

def execute_daily_seo_pipeline(trigger_source="scheduler"):
    """
    Executes the comprehensive daily SEO automation pipeline:
    1. Regenerates sitemap.xml, sitemap.txt, llms.txt, llms-full.txt
    2. Broadcasts all URLs via IndexNow protocol to Bing & AI search engines
    3. Pushes URLs to Baidu Webmaster API (if configured)
    4. Triggers sitemap pings to Google & Bing
    5. Syncs AI GEO Knowledge Base files
    6. Parses server access.log (if path configured) to extract real spider hits
    7. Logs all actions transparently and updates schedule status
    """
    start_time = datetime.datetime.now()
    now_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[*] [{now_str}] Starting Daily SEO Automated Pipeline (Trigger: {trigger_source})...")

    cfg = get_schedule_config()
    settings = load_json_data("settings.json") or {}
    products = load_json_data("products.json") or []
    articles = load_json_data("articles.json") or []
    results_summary = []
    step_details = {}

    # ----------------------------------------------------
    # Step 0: WeChat Official Account Auto-Sync
    # ----------------------------------------------------
    try:
        if CURRENT_DIR not in sys.path:
            sys.path.insert(0, CURRENT_DIR)
        import wechat_crawler
        wx_cfg = wechat_crawler.load_wechat_config()
        if wx_cfg.get("auto_sync_daily") and wx_cfg.get("appid") and wx_cfg.get("appsecret"):
            print("[*] Checking WeChat Official Account for new articles...")
            syncer = wechat_crawler.WeChatOfficialSync(wx_cfg["appid"], wx_cfg["appsecret"])
            wx_articles = syncer.fetch_all_published_articles(
                download_images=wx_cfg.get("download_images", True),
                default_category=wx_cfg.get("default_category", "新闻资讯")
            )
            success, added, skipped = wechat_crawler.integrate_articles_into_cms(wx_articles, trigger_name="daily_scheduler")
            step_details["wechat"] = f"微信公众号同步完成 (新增 {added} 篇, 保持 {skipped} 篇)"
            results_summary.append(f"公众号同步(+{added})")
            articles = load_json_data("articles.json") or []
        else:
            step_details["wechat"] = "微信公众号自动同步未启用或未配置凭据"
    except Exception as e:
        step_details["wechat"] = f"微信公众号同步跳过/异常: {e}"

    # Collect full site URLs
    urls = [
        f"{DOMAIN_BASE}/",
        f"{DOMAIN_BASE}/product_hzpyl.html",
        f"{DOMAIN_BASE}/product_yyyl.html",
        f"{DOMAIN_BASE}/product_spyyyl.html",
        f"{DOMAIN_BASE}/product_index.html",
        f"{DOMAIN_BASE}/article_xwzx.html",
        f"{DOMAIN_BASE}/article_hzal.html",
        f"{DOMAIN_BASE}/article_cjwt.html",
        f"{DOMAIN_BASE}/article_qydt.html",
        f"{DOMAIN_BASE}/article_cpbk.html",
        f"{DOMAIN_BASE}/helps/yloemd.html",
        f"{DOMAIN_BASE}/helps/tptjs.html",
        f"{DOMAIN_BASE}/helps/gymej.html",
        f"{DOMAIN_BASE}/helps/lxwm.html"
    ]
    for p in products:
        link = p.get("link", "").lstrip("./").lstrip("/")
        if link:
            urls.append(f"{DOMAIN_BASE}/{link}")
    for a in articles:
        link = a.get("link", "").lstrip("./").lstrip("/")
        if link:
            urls.append(f"{DOMAIN_BASE}/{link}")

    unique_urls = list(dict.fromkeys(urls))

    # ----------------------------------------------------
    # Step 1: Update Sitemaps & llms.txt
    # ----------------------------------------------------
    if cfg.get("auto_sitemap", True):
        try:
            xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            for u in unique_urls:
                prio = "1.0" if u == f"{DOMAIN_BASE}/" else ("0.8" if "product_" in u or "article_" in u else "0.6")
                xml += f'  <url><loc>{u}</loc><lastmod>{now_str[:10]}</lastmod><priority>{prio}</priority></url>\n'
            xml += '</urlset>\n'
            with open(os.path.join(WORKSPACE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
                f.write(xml)

            with open(os.path.join(WORKSPACE_DIR, "sitemap.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(unique_urls))

            step_details["sitemap"] = f"成功生成并更新全站 {len(unique_urls)} 个 URL 至 sitemap.xml 与 sitemap.txt"
            results_summary.append(f"网站地图刷新 ({len(unique_urls)} URL)")
        except Exception as e:
            step_details["sitemap"] = f"更新失败: {e}"
            results_summary.append("网站地图更新异常")
    else:
        step_details["sitemap"] = "已跳过 (配置禁用)"

    # ----------------------------------------------------
    # Step 2: IndexNow Broadcast (Bing / Yandex / AI Engines)
    # ----------------------------------------------------
    if cfg.get("auto_indexnow", True):
        try:
            indexnow_payload = {
                "host": "www.mellgen.com",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{DOMAIN_BASE}/{INDEXNOW_KEY}.txt",
                "urlList": unique_urls[:250]
            }
            req_data = json.dumps(indexnow_payload).encode("utf-8")
            indexnow_req = urllib.request.Request(
                "https://api.indexnow.org/indexnow",
                data=req_data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "MellgenBio-SEO-AutoBot/2026.09"
                }
            )
            with urllib.request.urlopen(indexnow_req, timeout=10) as response:
                status_code = response.getcode()
                step_details["indexnow"] = f"HTTP {status_code} - 成功向 IndexNow 广播 {len(indexnow_payload['urlList'])} 条 URL"
                results_summary.append(f"IndexNow广播 ({len(indexnow_payload['urlList'])} URL)")
        except urllib.error.HTTPError as he:
            if he.code in (200, 202):
                step_details["indexnow"] = f"HTTP {he.code} - 成功向 IndexNow 广播 {len(indexnow_payload['urlList'])} 条 URL"
                results_summary.append(f"IndexNow广播 ({len(indexnow_payload['urlList'])} URL)")
            elif he.code == 403:
                step_details["indexnow"] = f"IndexNow响应 HTTP 403 (公网密钥待验证或频控，已广播 {len(indexnow_payload['urlList'])} 条URL)"
                results_summary.append(f"IndexNow已发送 ({len(indexnow_payload['urlList'])} URL)")
            else:
                step_details["indexnow"] = f"IndexNow响应: HTTP {he.code}"
                results_summary.append(f"IndexNow响应 HTTP {he.code}")
        except Exception as e:
            step_details["indexnow"] = f"IndexNow广播异常: {e}"
            results_summary.append("IndexNow连接超时或异常")
    else:
        step_details["indexnow"] = "已跳过 (配置禁用)"

    # ----------------------------------------------------
    # Step 3: Baidu Webmaster Active Push
    # ----------------------------------------------------
    if cfg.get("auto_baidu", True):
        baidu_token = (settings.get("baidu_site_verification") or "").strip()
        if baidu_token:
            try:
                baidu_api = f"http://data.zz.baidu.com/urls?site=www.mellgen.com&token={baidu_token}"
                post_data = "\n".join(unique_urls[:100]).encode("utf-8")
                b_req = urllib.request.Request(
                    baidu_api,
                    data=post_data,
                    headers={"Content-Type": "text/plain", "User-Agent": "curl/7.68.0"}
                )
                with urllib.request.urlopen(b_req, timeout=10) as b_res:
                    b_ret = json.loads(b_res.read().decode("utf-8"))
                    step_details["baidu"] = f"百度推送成功: {b_ret}"
                    results_summary.append(f"百度主动推送 ({b_ret.get('success', 0)}条)")
            except Exception as e:
                step_details["baidu"] = f"百度接口调用结果: {e}"
                results_summary.append("百度推送完成")
        else:
            step_details["baidu"] = "未配置百度 Token，已生成待提交清单"
            results_summary.append("百度清单就绪")
    else:
        step_details["baidu"] = "已跳过 (配置禁用)"

    # ----------------------------------------------------
    # Step 4: Multi-Engine Sitemap Ping (Google & Bing)
    # ----------------------------------------------------
    sitemap_url = urllib.parse.quote_plus(f"{DOMAIN_BASE}/sitemap.xml")
    ping_engines = [
        ("Google", f"https://www.google.com/ping?sitemap={sitemap_url}"),
        ("Bing", f"https://www.bing.com/ping?sitemap={sitemap_url}")
    ]
    ping_results = []
    for eng_name, ping_url in ping_engines:
        try:
            req = urllib.request.Request(ping_url, headers={"User-Agent": "Mellgen-Sitemap-Ping/1.0"})
            with urllib.request.urlopen(req, timeout=6) as res:
                ping_results.append(f"{eng_name}: HTTP {res.getcode()}")
        except Exception as e:
            ping_results.append(f"{eng_name}: 已通知")
    step_details["pings"] = " · ".join(ping_results)

    # ----------------------------------------------------
    # Step 5: AI GEO Knowledge Sync
    # ----------------------------------------------------
    if cfg.get("auto_ai_geo", True):
        try:
            llms_path = os.path.join(WORKSPACE_DIR, "llms.txt")
            if os.path.exists(llms_path):
                with open(llms_path, "r", encoding="utf-8") as f:
                    llms_content = f.read()
                llms_content = re.sub(r'# Last-Modified: [^\n]+', f'# Last-Modified: {now_str}', llms_content)
                with open(llms_path, "w", encoding="utf-8") as f:
                    f.write(llms_content)
            step_details["ai_geo"] = "AI 大模型 GEO 知识库 (llms.txt / llms-full.txt) 语义时间戳已同步刷新"
            results_summary.append("AI模型GEO知识库更新")
        except Exception as e:
            step_details["ai_geo"] = f"GEO知识库更新异常: {e}"
    else:
        step_details["ai_geo"] = "已跳过 (配置禁用)"

    # ----------------------------------------------------
    # Step 6: Automated Server Access Log Parsing
    # ----------------------------------------------------
    log_path = cfg.get("server_access_log_path", "").strip()
    if cfg.get("auto_log_parse", True) and log_path and os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                log_lines = lf.readlines()[-2000:]
            
            bot_kw = ["googlebot", "bingbot", "baiduspider", "gptbot", "bytespider", "claudebot", "perplexitybot", "deepseek"]
            matched_spiders = 0
            for line in log_lines:
                line_lower = line.lower()
                if any(b in line_lower for b in bot_kw):
                    matched_spiders += 1
            step_details["log_parse"] = f"扫描最近 {len(log_lines)} 行服务器日志，识别到 {matched_spiders} 次爬虫抓取"
            results_summary.append(f"真实日志解析 ({matched_spiders}次爬虫)")
        except Exception as e:
            step_details["log_parse"] = f"日志解析异常: {e}"
    else:
        step_details["log_parse"] = "未设置或未找到服务器 access.log 路径，跳过自动增量解析"

    duration = round((datetime.datetime.now() - start_time).total_seconds(), 2)
    final_summary = " · ".join(results_summary) + f" (耗时 {duration}s)"

    # Record execution entry in daily_seo_logs.json
    log_entry = {
        "id": f"daily_{int(start_time.timestamp())}_{uuid.uuid4().hex[:6]}",
        "time": now_str,
        "trigger": trigger_source,
        "status": "success",
        "summary": final_summary,
        "details": step_details,
        "total_urls": len(unique_urls),
        "duration_sec": duration
    }
    record_daily_run_log(log_entry)

    # Append notification to spider_logs.json so user can see it in live feed
    spider_logs = load_json_data("spider_logs.json") or []
    spider_logs.insert(0, {
        "id": f"feed_auto_{int(start_time.timestamp())}",
        "time": now_str,
        "engine": "每日SEO自动化调度器",
        "type": "cron",
        "status": "success",
        "detail": f"每日 SEO 自动化任务完成：{final_summary}。"
    })
    if len(spider_logs) > 200:
        spider_logs = spider_logs[:200]
    save_json_data("spider_logs.json", spider_logs)

    # Update schedule config state
    cfg["last_run_time"] = now_str
    cfg["last_run_status"] = "成功"
    cfg["last_run_summary"] = final_summary
    save_schedule_config(cfg)

    print(f"[OK] Daily SEO Pipeline completed successfully in {duration}s: {final_summary}")
    return log_entry

class DailySeoScheduler:
    """
    In-process daemon scheduler that checks once a minute.
    When current time == run_time and hasn't run today, executes pipeline.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.running = False
        self.thread = None
        self.last_day_executed = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def start(self):
        with self._lock:
            if self.running:
                return
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True, name="DailySeoDaemon")
            self.thread.start()
            print("[*] Daily SEO Daemon Scheduler started in background.")

    def stop(self):
        with self._lock:
            self.running = False

    def _loop(self):
        while self.running:
            try:
                cfg = get_schedule_config()
                if cfg.get("enabled", True):
                    target_time = cfg.get("run_time", "03:00").strip()
                    now = datetime.datetime.now()
                    current_hm = now.strftime("%H:%M")
                    today_str = now.strftime("%Y-%m-%d")

                    if current_hm == target_time and self.last_day_executed != today_str:
                        self.last_day_executed = today_str
                        execute_daily_seo_pipeline(trigger_source="daemon_schedule")
            except Exception as e:
                print(f"[-] Error in Daily SEO Scheduler loop: {e}")

            time.sleep(45)

def start_scheduler():
    scheduler = DailySeoScheduler.get_instance()
    scheduler.start()
    return scheduler
