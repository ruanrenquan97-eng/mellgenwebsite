import os
import sys
import json
import uuid
import datetime
import threading
import urllib.request
import urllib.error
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename

# Ensure cms_system folder is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import the site generator
import generator

app = Flask(__name__)
app.secret_key = "mellgen_cms_secret_key_12938"

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
UPLOAD_FOLDER = os.path.join(WORKSPACE_DIR, "resource", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CORS Support
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

# Serve static files from workspace for dashboard preview
from flask import send_from_directory

@app.route("/resource/<path:filename>")
def serve_resource(filename):
    return send_from_directory(os.path.join(WORKSPACE_DIR, "resource"), filename)

@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(os.path.join(WORKSPACE_DIR, "images"), filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(WORKSPACE_DIR, "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(WORKSPACE_DIR, "js"), filename)

# Helper: load/save JSON data
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Authentication decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        settings_path = os.path.join(DATA_DIR, "settings.json")
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            accounts = settings.get("accounts", [])
        except Exception:
            accounts = [
                {"username": "admin", "password": "admin888", "role": "管理员", "name": "系统管理员"},
                {"username": "kefu", "password": "kefu888", "role": "客服", "name": "在线客服"}
            ]
        
        matched = None
        for acc in accounts:
            if acc.get("username") == username and acc.get("password") == password:
                matched = acc
                break
        
        if matched:
            session["logged_in"] = True
            session["username"] = matched.get("username")
            session["role"] = matched.get("role")
            session["name"] = matched.get("name")
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="用户名或密码错误")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
@app.route("/admin")
@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username", "admin"), role=session.get("role", "管理员"))

# --- API ENDPOINTS ---

# 1. Products API
@app.route("/api/products", methods=["GET"])
@login_required
def get_products():
    products = load_json("products.json")
    return jsonify(products)

@app.route("/api/products", methods=["POST"])
@login_required
def add_product():
    products = load_json("products.json")
    data = request.json
    
    product_id = data.get("id", "").strip() or str(uuid.uuid4())[:8]
    product_id = secure_filename(product_id).replace(".", "_")
    link = f"products/{product_id}.html"
    
    new_product = {
        "id": product_id,
        "title": data.get("title", "").strip(),
        "category": data.get("category", "化妆品原料"),
        "image": data.get("image", "images/ban_txt.png"),
        "largeImage": data.get("largeImage", "images/ban_txt.png"),
        "fullBanner": data.get("fullBanner", "").strip(),
        "video": data.get("video", "").strip(),
        "desc": data.get("desc", "").strip(),
        "link": link,
        "content": data.get("content", "").strip(),
        "specs": data.get("specs", {}),
        "seoTitle": data.get("seoTitle", "").strip(),
        "seoKeywords": data.get("seoKeywords", "").strip(),
        "seoDesc": data.get("seoDesc", "").strip(),
        "h1": data.get("h1", "").strip(),
        "recommend": bool(data.get("recommend", False)),
        "top": bool(data.get("top", False)),
        "show": bool(data.get("show", True)),
        "date": data.get("date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }
    
    if any(p["id"] == product_id for p in products):
        return jsonify({"success": False, "message": "产品 ID 已存在！"}), 400
        
    products.append(new_product)
    save_json("products.json", products)
    return jsonify({"success": True, "product": new_product})

@app.route("/api/products/<product_id>", methods=["PUT"])
@login_required
def edit_product(product_id):
    products = load_json("products.json")
    data = request.json
    
    for p in products:
        if p["id"] == product_id:
            p["title"] = data.get("title", p["title"]).strip()
            p["category"] = data.get("category", p["category"])
            p["image"] = data.get("image", p["image"])
            p["largeImage"] = data.get("largeImage", data.get("largeImage", p.get("largeImage", "images/ban_txt.png")))
            p["fullBanner"] = data.get("fullBanner", data.get("fullBanner", p.get("fullBanner", ""))).strip()
            p["video"] = data.get("video", data.get("video", p.get("video", ""))).strip()
            p["desc"] = data.get("desc", p["desc"]).strip()
            p["content"] = data.get("content", p["content"]).strip()
            p["specs"] = data.get("specs", p["specs"])
            p["seoTitle"] = data.get("seoTitle", data.get("seoTitle", p.get("seoTitle", ""))).strip()
            p["seoKeywords"] = data.get("seoKeywords", data.get("seoKeywords", p.get("seoKeywords", ""))).strip()
            p["seoDesc"] = data.get("seoDesc", data.get("seoDesc", p.get("seoDesc", ""))).strip()
            p["h1"] = data.get("h1", data.get("h1", p.get("h1", ""))).strip()
            p["recommend"] = bool(data.get("recommend", p.get("recommend", False)))
            p["top"] = bool(data.get("top", p.get("top", False)))
            p["show"] = bool(data.get("show", p.get("show", True)))
            p["date"] = data.get("date", p.get("date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            save_json("products.json", products)
            return jsonify({"success": True, "product": p})
            
    return jsonify({"success": False, "message": "产品未找到"}), 404

@app.route("/api/products/<product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):
    products = load_json("products.json")
    original_len = len(products)
    
    products = [p for p in products if p["id"] != product_id]
    if len(products) == original_len:
        return jsonify({"success": False, "message": "产品未找到"}), 404
        
    save_json("products.json", products)
    
    detail_path = os.path.join(WORKSPACE_DIR, "products", f"{product_id}.html")
    if os.path.exists(detail_path):
        try:
            os.remove(detail_path)
        except Exception:
            pass
            
    return jsonify({"success": True})

# 2. Articles API
@app.route("/api/articles", methods=["GET"])
@login_required
def get_articles():
    articles = load_json("articles.json")
    return jsonify(articles)

@app.route("/api/articles", methods=["POST"])
@login_required
def add_article():
    articles = load_json("articles.json")
    data = request.json
    
    article_id = data.get("id", "").strip() or str(uuid.uuid4())[:8]
    article_id = secure_filename(article_id).replace(".", "_")
    link = f"articles/{article_id}.html"
    
    new_article = {
        "id": article_id,
        "title": data.get("title", "").strip(),
        "category": data.get("category", "新闻资讯"),
        "image": data.get("image", "images/ban_txt.png"),
        "desc": data.get("desc", "").strip(),
        "link": link,
        "content": data.get("content", "").strip(),
        "date": data.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
        "recommend": bool(data.get("recommend", False)),
        "top": bool(data.get("top", False)),
        "show": bool(data.get("show", True)),
        "sort": int(data.get("sort", 50))
    }
    
    if any(a["id"] == article_id for a in articles):
        return jsonify({"success": False, "message": "文章 ID 已存在！"}), 400
        
    articles.append(new_article)
    save_json("articles.json", articles)
    return jsonify({"success": True, "article": new_article})

@app.route("/api/articles/<article_id>", methods=["PUT"])
@login_required
def edit_article(article_id):
    articles = load_json("articles.json")
    data = request.json
    
    for a in articles:
        if a["id"] == article_id:
            a["title"] = data.get("title", a["title"]).strip()
            a["category"] = data.get("category", a["category"])
            a["image"] = data.get("image", a["image"])
            a["desc"] = data.get("desc", a["desc"]).strip()
            a["content"] = data.get("content", a["content"]).strip()
            a["date"] = data.get("date", a["date"])
            a["recommend"] = bool(data.get("recommend", a.get("recommend", False)))
            a["top"] = bool(data.get("top", a.get("top", False)))
            a["show"] = bool(data.get("show", a.get("show", True)))
            a["sort"] = int(data.get("sort", a.get("sort", 50)))
            save_json("articles.json", articles)
            return jsonify({"success": True, "article": a})
            
    return jsonify({"success": False, "message": "文章未找到"}), 404

@app.route("/api/articles/<article_id>", methods=["DELETE"])
@login_required
def delete_article(article_id):
    articles = load_json("articles.json")
    original_len = len(articles)
    
    articles = [a for a in articles if a["id"] != article_id]
    if len(articles) == original_len:
        return jsonify({"success": False, "message": "文章未找到"}), 404
        
    save_json("articles.json", articles)
    
    detail_path = os.path.join(WORKSPACE_DIR, "articles", f"{article_id}.html")
    if os.path.exists(detail_path):
        try:
            os.remove(detail_path)
        except Exception:
            pass
            
    return jsonify({"success": True})

# 3. Settings API
@app.route("/api/settings", methods=["GET", "PUT"])
@login_required
def handle_settings():
    settings_path = os.path.join(DATA_DIR, "settings.json")
    if request.method == "PUT":
        data = request.json
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True, "settings": data})
        
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({})

# 4. Upload API
@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "没有上传文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "没有选择文件"}), 400
        
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(dest_path)
        relative_url = f"resource/images/{unique_filename}"
        return jsonify({"success": True, "url": relative_url})
    except Exception as e:
        return jsonify({"success": False, "message": f"保存文件失败: {e}"}), 500

# 5. Publish API (Rebuild Website HTMLs)
@app.route("/api/publish", methods=["POST"])
@login_required
def publish_site():
    try:
        generator.publish_site()
        return jsonify({"success": True, "message": "网站静态页面已成功更新！"})
    except Exception as e:
        return jsonify({"success": False, "message": f"发布网站失败: {e}"}), 500

# 6. Messages (Inquiries) API
@app.route("/api/submit_message", methods=["POST", "OPTIONS"])
def submit_message():
    if request.method == "OPTIONS":
        return jsonify({"success": True})
        
    data = request.json or {}
    messages = load_json("messages.json")
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
        
    new_msg = {
        "id": str(uuid.uuid4())[:8],
        "name": data.get("contactsName", "").strip() or "匿名用户",
        "phone": data.get("contactsPhone", "").strip() or data.get("phone", "").strip(),
        "email": data.get("contactsMail", "").strip() or data.get("email", "").strip(),
        "content": data.get("content", "").strip() or "在线咨询/留言反馈",
        "ip": client_ip,
        "time": now_str,
        "read": False
    }
    
    messages.insert(0, new_msg)
    save_json("messages.json", messages)
    # Trigger WorkBuddy Webhook Notification
    push_to_workbuddy("on_new_inquiry", new_msg)
    
    return jsonify({"success": True, "msg": "留言提交成功！我们将在2小时内给您回复。"})

@app.route("/api/messages", methods=["GET"])
@login_required
def get_messages():
    messages = load_json("messages.json")
    return jsonify(messages)

@app.route("/api/messages/<msg_id>/read", methods=["PUT"])
@login_required
def read_message(msg_id):
    messages = load_json("messages.json")
    for m in messages:
        if m["id"] == msg_id:
            m["read"] = True
            save_json("messages.json", messages)
            return jsonify({"success": True})
    return jsonify({"success": False, "message": "消息未找到"}), 404

@app.route("/api/messages/<msg_id>", methods=["DELETE"])
@login_required
def delete_message(msg_id):
    messages = load_json("messages.json")
    messages = [m for m in messages if m["id"] != msg_id]
    save_json("messages.json", messages)
    return jsonify({"success": True})

# 7. Friendship Links API
@app.route("/api/friendlinks", methods=["GET"])
@login_required
def get_friendlinks():
    friendlinks = load_json("friendlinks.json")
    if not friendlinks:
        friendlinks = [
            {"id": "1", "name": "单仁牛商", "url": "https://www.nsw88.com/", "show": True, "time": "2025-02-21 11:54:01"},
            {"id": "2", "name": "文思子牙", "url": "https://juzhenai.srnsjt.com", "show": True, "time": "2025-02-21 11:53:52"},
            {"id": "3", "name": "牛商学堂", "url": "http://kfb.nsw88.net.cn/", "show": True, "time": "2025-02-21 11:53:43"}
        ]
        save_json("friendlinks.json", friendlinks)
    return jsonify(friendlinks)

@app.route("/api/friendlinks", methods=["POST"])
@login_required
def add_friendlink():
    friendlinks = load_json("friendlinks.json")
    data = request.json
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_link = {
        "id": str(uuid.uuid4())[:8],
        "name": data.get("name", "").strip(),
        "url": data.get("url", "").strip(),
        "show": True,
        "time": now_str
    }
    
    friendlinks.append(new_link)
    save_json("friendlinks.json", friendlinks)
    return jsonify({"success": True, "link": new_link})

@app.route("/api/friendlinks/<link_id>", methods=["PUT"])
@login_required
def edit_friendlink(link_id):
    friendlinks = load_json("friendlinks.json")
    data = request.json
    
    for l in friendlinks:
        if l["id"] == link_id:
            l["name"] = data.get("name", l["name"]).strip()
            l["url"] = data.get("url", l["url"]).strip()
            l["show"] = data.get("show", l["show"])
            save_json("friendlinks.json", friendlinks)
            return jsonify({"success": True, "link": l})
            
    return jsonify({"success": False, "message": "链接未找到"}), 404

@app.route("/api/friendlinks/<link_id>", methods=["DELETE"])
@login_required
def delete_friendlink(link_id):
    friendlinks = load_json("friendlinks.json")
    friendlinks = [l for l in friendlinks if l["id"] != link_id]
    save_json("friendlinks.json", friendlinks)
    return jsonify({"success": True})

# 8. HTML Pages Listing API (for Page Edit feature)
@app.route("/api/pages", methods=["GET"])
@login_required
def get_pages():
    pages = []
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        if "cms_system" in root or ".git" in root or "resource" in root:
            continue
        for file in files:
            if file.endswith(".html") and not file.startswith("backend_shell"):
                rel_path = os.path.relpath(os.path.join(root, file), WORKSPACE_DIR).replace(os.sep, "/")
                pages.append({"path": rel_path, "name": file})
    return jsonify(pages)

# 9. HTML Page Content Get/Save API
@app.route("/api/pages/content", methods=["GET", "POST"])
@login_required
def handle_page_content():
    page_path = request.args.get("path")
    if not page_path:
        return jsonify({"success": False, "message": "缺少页面路径参数"}), 400
        
    abs_path = os.path.abspath(os.path.join(WORKSPACE_DIR, page_path.replace("/", os.sep)))
    if not abs_path.startswith(WORKSPACE_DIR):
        return jsonify({"success": False, "message": "越权路径访问拒绝"}), 403
        
    if request.method == "POST":
        data = request.json or {}
        content = data.get("content", "")
        try:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
            
    if os.path.exists(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                return jsonify({"success": True, "content": f.read()})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    return jsonify({"success": False, "message": "文件不存在"}), 404

# 10. Robots.txt Get/Save API
@app.route("/api/robots", methods=["GET", "POST"])
@login_required
def handle_robots():
    robots_path = os.path.join(WORKSPACE_DIR, "robots.txt")
    if request.method == "POST":
        data = request.json or {}
        content = data.get("content", "")
        try:
            with open(robots_path, "w", encoding="utf-8") as f:
                f.write(content)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
            
    content = "User-agent: *\nDisallow: /cms_system/\nSitemap: http://www.mellgen.com/sitemap.xml"
    if os.path.exists(robots_path):
        try:
            with open(robots_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            pass
    return jsonify({"success": True, "content": content})

# Sitemap XML REST API (GET & POST)
@app.route("/api/sitemap", methods=["GET", "POST"])
@login_required
def handle_sitemap():
    sitemap_path = os.path.join(WORKSPACE_DIR, "sitemap.xml")
    if request.method == "POST":
        data = request.json or {}
        content = data.get("content", "")
        try:
            with open(sitemap_path, "w", encoding="utf-8") as f:
                f.write(content)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
            
    content = ""
    if os.path.exists(sitemap_path):
        try:
            with open(sitemap_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            pass
    return jsonify({"success": True, "content": content})

# 11. Navigation Menu REST API (GET & PUT)
@app.route("/api/navigation", methods=["GET", "PUT"])
@login_required
def handle_navigation():
    if request.method == "PUT":
        data = request.json
        save_json("nav.json", data)
        return jsonify({"success": True})
        
    nav_data = load_json("nav.json")
    return jsonify(nav_data)

# 12. Product Categories REST API (GET, POST, PUT, DELETE)
@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    categories = load_json("categories.json")
    # If file doesn't exist or is empty, return empty list
    return jsonify(categories)

@app.route("/api/categories", methods=["POST"])
@login_required
def add_category():
    categories = load_json("categories.json")
    data = request.json or {}
    
    cat_name = data.get("name", "").strip()
    if not cat_name:
        return jsonify({"success": False, "message": "分类名称不能为空"}), 400
        
    cat_id = data.get("id", "").strip()
    if not cat_id:
        # Generate an ID based on name or secure random
        cat_id = "cat_" + str(uuid.uuid4())[:8]
    cat_id = secure_filename(cat_id).replace(".", "_")
    
    if any(c["id"] == cat_id for c in categories):
        return jsonify({"success": False, "message": "分类 ID 已存在！"}), 400
        
    # Get max sort number
    max_sort = max([c.get("sort", 0) for c in categories]) if categories else 0
    
    new_category = {
      "id": cat_id,
      "name": cat_name,
      "parent_id": data.get("parent_id", "").strip(),
      "page_url": data.get("page_url", "").strip() or cat_id,
      "seo_title": data.get("seo_title", "").strip(),
      "seo_keywords": data.get("seo_keywords", "").strip(),
      "seo_desc": data.get("seo_desc", "").strip(),
      "h1": data.get("h1", "").strip(),
      "associated_tag": data.get("associated_tag", "产品资讯").strip(),
      "thumbnail": data.get("thumbnail", "").strip() or "resource/images/ban_txt.png",
      "description": data.get("description", "").strip(),
      "list_description": bool(data.get("list_description", False)),
      "outer_link_mode": bool(data.get("outer_link_mode", False)),
      "recommend": bool(data.get("recommend", False)),
      "top": bool(data.get("top", False)),
      "show": bool(data.get("show", True)),
      "sort": int(data.get("sort", max_sort + 1)),
      "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    categories.append(new_category)
    # Sort categories to preserve sort order
    categories.sort(key=lambda x: x.get("sort", 999))
    save_json("categories.json", categories)
    return jsonify({"success": True, "category": new_category})

@app.route("/api/categories/<cat_id>", methods=["PUT"])
@login_required
def edit_category(cat_id):
    categories = load_json("categories.json")
    data = request.json or {}
    
    for c in categories:
        if c["id"] == cat_id:
            c["name"] = data.get("name", c["name"]).strip()
            c["parent_id"] = data.get("parent_id", c.get("parent_id", "")).strip()
            c["page_url"] = data.get("page_url", c.get("page_url", cat_id)).strip()
            c["seo_title"] = data.get("seo_title", c.get("seo_title", "")).strip()
            c["seo_keywords"] = data.get("seo_keywords", c.get("seo_keywords", "")).strip()
            c["seo_desc"] = data.get("seo_desc", c.get("seo_desc", "")).strip()
            c["h1"] = data.get("h1", c.get("h1", "")).strip()
            c["associated_tag"] = data.get("associated_tag", c.get("associated_tag", "产品资讯")).strip()
            c["thumbnail"] = data.get("thumbnail", c.get("thumbnail", "resource/images/ban_txt.png")).strip()
            c["description"] = data.get("description", c.get("description", "")).strip()
            c["list_description"] = bool(data.get("list_description", c.get("list_description", False)))
            c["outer_link_mode"] = bool(data.get("outer_link_mode", c.get("outer_link_mode", False)))
            c["recommend"] = bool(data.get("recommend", c.get("recommend", False)))
            c["top"] = bool(data.get("top", c.get("top", False)))
            c["show"] = bool(data.get("show", c.get("show", True)))
            c["sort"] = int(data.get("sort", c.get("sort", 999)))
            c["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            categories.sort(key=lambda x: x.get("sort", 999))
            save_json("categories.json", categories)
            return jsonify({"success": True, "category": c})
            
    return jsonify({"success": False, "message": "分类未找到"}), 404

@app.route("/api/categories/<cat_id>", methods=["DELETE"])
@login_required
def delete_category(cat_id):
    categories = load_json("categories.json")
    original_len = len(categories)
    
    categories = [c for c in categories if c["id"] != cat_id]
    if len(categories) == original_len:
        return jsonify({"success": False, "message": "分类未找到"}), 404
        
    save_json("categories.json", categories)
    return jsonify({"success": True})

@app.route("/api/categories/batch-delete", methods=["POST"])
@login_required
def batch_delete_categories():
    categories = load_json("categories.json")
    data = request.json or {}
    ids_to_delete = data.get("ids", [])
    
    if not ids_to_delete:
        return jsonify({"success": False, "message": "没有指定删除的分类ID"}), 400
        
    categories = [c for c in categories if c["id"] not in ids_to_delete]
    save_json("categories.json", categories)
    return jsonify({"success": True})



# ==========================================================
# WorkBuddy Connector Engine & APIs
# ==========================================================
def push_to_workbuddy(event_type, payload_data):
    """
    Asynchronously push event to WorkBuddy Webhook connector
    """
    def _worker():
        try:
            config = load_json("connector_workbuddy.json")
            if not config or not config.get("enabled"):
                return
            
            webhook_url = config.get("webhook_url", "").strip()
            if not webhook_url:
                return
                
            events = config.get("events", {})
            if not events.get(event_type, True):
                return
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if event_type == "on_new_inquiry":
                title = "【美尔健官网】有新的客户在线询盘/留言线索"
                content = f"### 🔔 {title}\n" \
                          f"- **客户姓名**: {payload_data.get('name', '未填写')}\n" \
                          f"- **联系电话**: {payload_data.get('phone', '未填写')}\n" \
                          f"- **电子邮箱**: {payload_data.get('email', '未填写')}\n" \
                          f"- **咨询内容**: {payload_data.get('content', '未填写')}\n" \
                          f"- **访客 IP**: {payload_data.get('ip', '未知')}\n" \
                          f"- **提交时间**: {timestamp}\n\n" \
                          f"> 请销售/客服人员及时跟进。"
                text_content = f"{title}\n姓名: {payload_data.get('name')}\n电话: {payload_data.get('phone')}\n内容: {payload_data.get('content')}"
            elif event_type == "on_product_update":
                title = "【美尔健官网】产品资料更新通知"
                content = f"### 📦 {title}\n" \
                          f"- **产品名称**: {payload_data.get('title', '未知产品')}\n" \
                          f"- **所属分类**: {payload_data.get('category_name', '通用分类')}\n" \
                          f"- **操作时间**: {timestamp}\n\n" \
                          f"> 官网知识库已同步更新。"
                text_content = f"{title}: {payload_data.get('title')}"
            else:
                title = f"【美尔健官网】业务事件通知: {event_type}"
                content = f"### 📢 {title}\n时间: {timestamp}"
                text_content = title
            
            body = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content,
                    "title": title,
                    "text": content
                },
                "text": {
                    "content": text_content
                },
                "event": event_type,
                "timestamp": timestamp,
                "data": payload_data
            }
            
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "Mellgen-CMS-WorkBuddy-Connector/1.0",
                    "X-Connector-Secret": config.get("secret_token", "")
                }
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                pass
        except Exception as e:
            print(f"[WorkBuddy Connector Async Error] {e}")
            
    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()


@app.route("/api/connector/workbuddy/config", methods=["GET"])
@login_required
def get_workbuddy_config():
    config = load_json("connector_workbuddy.json")
    if not config:
        config = {
            "enabled": False,
            "webhook_url": "",
            "secret_token": "",
            "api_key": "mb_sec_" + uuid.uuid4().hex[:16],
            "events": {"on_new_inquiry": True, "on_product_update": True, "on_article_publish": False},
            "last_tested_at": None,
            "last_status": "not_tested",
            "last_message": ""
        }
        save_json("connector_workbuddy.json", config)
    return jsonify(config)

@app.route("/api/connector/workbuddy/config", methods=["POST"])
@login_required
def save_workbuddy_config():
    data = request.json or {}
    config = load_json("connector_workbuddy.json") or {}
    config["enabled"] = bool(data.get("enabled", False))
    config["webhook_url"] = data.get("webhook_url", "").strip()
    config["secret_token"] = data.get("secret_token", "").strip()
    if not config.get("api_key"):
        config["api_key"] = "mb_sec_" + uuid.uuid4().hex[:16]
    config["events"] = data.get("events", {
        "on_new_inquiry": True,
        "on_product_update": True,
        "on_article_publish": False
    })
    save_json("connector_workbuddy.json", config)
    return jsonify({"success": True, "message": "WorkBuddy 连接器配置已保存！", "config": config})

@app.route("/api/connector/workbuddy/regenerate_key", methods=["POST"])
@login_required
def regenerate_workbuddy_key():
    config = load_json("connector_workbuddy.json") or {}
    config["api_key"] = "mb_sec_" + uuid.uuid4().hex[:16]
    save_json("connector_workbuddy.json", config)
    return jsonify({"success": True, "api_key": config["api_key"]})

@app.route("/api/connector/workbuddy/test", methods=["POST"])
@login_required
def test_workbuddy_webhook():
    data = request.json or {}
    webhook_url = data.get("webhook_url", "").strip()
    if not webhook_url:
        return jsonify({"success": False, "message": "请先填写 WorkBuddy Webhook 回调地址！"}), 400
    
    secret_token = data.get("secret_token", "").strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    test_title = "【测试】美尔健官网后台 ↔ WorkBuddy 连接器连通成功！"
    test_content = f"### 🚀 {test_title}\n" \
                   f"- **连通状态**: ✅ 通信正常 (200 OK)\n" \
                   f"- **测试来源**: 美尔健GEO智能官网管理后台\n" \
                   f"- **测试时间**: {now_str}\n" \
                   f"- **通知机制**: 访客提交留言/询盘时，将在此群实时推送线索卡片。\n\n" \
                   f"> 🎉 恭喜！您的官网后台与 WorkBuddy 连接器已就绪。"
    
    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": test_content,
            "title": test_title,
            "text": test_content
        },
        "text": {
            "content": f"{test_title}\n连通状态: 正常\n测试时间: {now_str}"
        },
        "event": "connector_test",
        "timestamp": now_str,
        "data": {
            "test": True,
            "system": "Mellgen CMS v7.0"
        }
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "Mellgen-CMS-WorkBuddy-Connector/1.0",
                "X-Connector-Secret": secret_token
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_code = resp.getcode()
            resp_body = resp.read().decode("utf-8", errors="ignore")[:300]
            
            config = load_json("connector_workbuddy.json") or {}
            config["last_tested_at"] = now_str
            config["last_status"] = "success"
            config["last_message"] = f"HTTP {resp_code}: {resp_body}"
            save_json("connector_workbuddy.json", config)
            
            return jsonify({
                "success": True, 
                "message": "测试消息已成功送达！请查看 WorkBuddy 接收端。",
                "status_code": resp_code,
                "response": resp_body
            })
    except urllib.error.HTTPError as e:
        err_msg = f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:200]}"
        return jsonify({"success": False, "message": f"连接 WorkBuddy 接口返回错误: {err_msg}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"连接失败，请检查 URL 是否正确或网络是否可达: {str(e)}"}), 400

# ---------------- OpenAPI for WorkBuddy AI Agents ----------------
def verify_workbuddy_api_key():
    config = load_json("connector_workbuddy.json") or {}
    expected_key = config.get("api_key", "").strip()
    provided_key = request.headers.get("X-API-Key", "") or request.args.get("api_key", "")
    return expected_key and (provided_key == expected_key)

@app.route("/api/connector/v1/products", methods=["GET"])
def connector_api_products():
    if not verify_workbuddy_api_key():
        return jsonify({"success": False, "message": "API Key 鉴权失败，请在请求头提供 X-API-Key 或 URL 参数携带 api_key"}), 401
    
    products = load_json("products.json")
    cleaned = []
    for p in products:
        cleaned.append({
            "id": p.get("id"),
            "name": p.get("title"),
            "category": p.get("category_name", p.get("category")),
            "inci": p.get("inci", ""),
            "appearance": p.get("appearance", ""),
            "solubility": p.get("solubility", ""),
            "description": p.get("desc", ""),
            "summary": p.get("summary", ""),
            "url": f"https://www.mellgen.com/products/{p.get('id')}.html"
        })
    return jsonify({
        "success": True,
        "total": len(cleaned),
        "data": cleaned,
        "source": "美尔健官方产品知识库",
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/connector/v1/articles", methods=["GET"])
def connector_api_articles():
    if not verify_workbuddy_api_key():
        return jsonify({"success": False, "message": "API Key 鉴权失败"}), 401
    
    articles = load_json("articles.json")
    cleaned = []
    for a in articles:
        cleaned.append({
            "id": a.get("id"),
            "title": a.get("title"),
            "date": a.get("date"),
            "author": a.get("author"),
            "summary": a.get("summary", ""),
            "url": f"https://www.mellgen.com/articles/{a.get('id')}.html"
        })
    return jsonify({
        "success": True,
        "total": len(cleaned),
        "data": cleaned,
        "source": "美尔健企业动态与新闻资讯",
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/connector/v1/inquiries", methods=["GET"])
def connector_api_inquiries():
    if not verify_workbuddy_api_key():
        return jsonify({"success": False, "message": "API Key 鉴权失败"}), 401
    
    messages = load_json("messages.json")
    return jsonify({
        "success": True,
        "total": len(messages),
        "data": messages
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False, use_reloader=False)

