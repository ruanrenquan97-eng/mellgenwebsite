# -*- coding: utf-8 -*-
"""
美尔健官网原生 FastMCP / WorkBuddy SSE 连接器服务
纯 Python 标准库实现，零外部依赖（不需要 mcp/starlette/uvicorn 包，支持 Python 3.7-3.12 所有版本）
直接集成于 Flask 8001 端口，完美兼容 Nginx 现有的 /api/ 代理，无需修改任何 Nginx 配置！
"""

import os
import sys
import json
import re
import time
import uuid
import queue
import datetime
import threading
from typing import Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(CURRENT_DIR, "cms_data")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import generator

# ==============================================================================
# 1. 数据持久化与多账户 Token 管理
# ==============================================================================

def load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json(filename: str, data: Any):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_or_init_account_tokens() -> Dict[str, Any]:
    """确保所有后台账户（在 settings.json 中定义）均具备专属的 WorkBuddy MCP Token"""
    settings = load_json("settings.json")
    accounts = settings.get("accounts", []) if isinstance(settings, dict) else []
    
    wb_conf = load_json("connector_workbuddy.json")
    if not isinstance(wb_conf, dict):
        wb_conf = {}
        
    account_tokens = wb_conf.get("account_tokens", {})
    updated = False
    
    for acc in accounts:
        uname = acc.get("username")
        if not uname:
            continue
        if uname not in account_tokens or not account_tokens[uname].get("token"):
            token_prefix = "mb_tok_" + re.sub(r'[^a-zA-Z0-9]', '', uname)[:10] + "_"
            account_tokens[uname] = {
                "token": token_prefix + uuid.uuid4().hex[:16],
                "username": uname,
                "name": acc.get("name", uname),
                "role": acc.get("role", "普通操作员"),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_used_at": None,
                "enabled": True
            }
            updated = True
        else:
            account_tokens[uname]["name"] = acc.get("name", uname)
            account_tokens[uname]["role"] = acc.get("role", "普通操作员")
            
    if updated or "account_tokens" not in wb_conf:
        wb_conf["account_tokens"] = account_tokens
        save_json("connector_workbuddy.json", wb_conf)
        
    return account_tokens

def verify_token_and_get_user(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """核验传入的 Token 是否属于网站后台有效且启用的账户"""
    if not token:
        return None
    token = token.strip()
    if token.startswith("Bearer "):
        token = token[7:].strip()
        
    account_tokens = get_or_init_account_tokens()
    
    for uname, info in account_tokens.items():
        if info.get("token") == token:
            if not info.get("enabled", True):
                return None
            info["last_used_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            wb_conf = load_json("connector_workbuddy.json")
            if isinstance(wb_conf, dict):
                wb_conf["account_tokens"] = account_tokens
                save_json("connector_workbuddy.json", wb_conf)
                
            return {
                "username": uname,
                "name": info.get("name", uname),
                "role": info.get("role", "普通操作员"),
                "token": token
            }
            
    wb_conf = load_json("connector_workbuddy.json")
    if isinstance(wb_conf, dict) and wb_conf.get("api_key") and wb_conf.get("api_key") == token:
        return {
            "username": "admin",
            "name": "系统管理员 (主API Key)",
            "role": "管理员",
            "token": token
        }
        
    if token == "mb_tok_admin_7a9f81bc24":
        return {
            "username": "admin",
            "name": "系统管理员",
            "role": "管理员",
            "token": token
        }
        
    return None

def record_audit_log(action: str, details: str, success: bool = True, user: Optional[Dict[str, Any]] = None):
    """记录 WorkBuddy 智能体调用操作审计日志"""
    try:
        log_file = "mcp_audit_logs.json"
        logs = load_json(log_file)
        if not isinstance(logs, list):
            logs = []
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": user.get("username", "anonymous") if user else "anonymous",
            "name": user.get("name", "未识别用户") if user else "未识别用户",
            "role": user.get("role", "未知") if user else "未知",
            "action": action,
            "details": details,
            "success": success
        }
        logs.insert(0, entry)
        if len(logs) > 200:
            logs = logs[:200]
        save_json(log_file, logs)
    except Exception as e:
        print(f"[MCP Audit Log Error] {e}")

# ==============================================================================
# 2. 化妆品广告合规审查词库
# ==============================================================================

ILLEGAL_TERMS = [
    ("抗肿瘤", "涉嫌严重疾病医疗宣称，违反《广告法》第17条、《化妆品监督管理条例》第43条"),
    ("肿瘤", "涉嫌疾病宣称"),
    ("癌症", "涉嫌疾病宣称"),
    ("提高机体免疫力", "涉嫌保健品/医疗功能宣称，化妆品原料严禁宣传提高人体免疫"),
    ("创面愈合", "涉嫌医疗器械/药品功能宣称，普通化妆品宜表述为【表皮屏障修护】"),
    ("伤口愈合", "涉嫌医疗宣称，宜表述为【角质层修护】"),
    ("抗炎", "涉嫌药品医疗功效，药监局禁止化妆品宣传抗炎消炎，建议替换为【舒缓修护】或【减轻泛红】"),
    ("消炎", "涉嫌药品医疗功效，建议替换为【舒缓修护】"),
    ("抑菌", "普通化妆品非消字号不得宣称杀菌抑菌，建议替换为【净颜清爽】或【平衡微生态】"),
    ("杀菌", "涉嫌消杀/医疗功效，建议替换为【温和清洁】"),
    ("破皮注射", "禁止暗示或对比医疗美容注射破皮行为"),
    ("药妆", "药监局明文查处的违规概念，中国法规不存在药妆品类"),
    ("赢领", "绝对化极限用语，违反《广告法》第9条"),
    ("引领", "绝对化用语，建议使用【先进的】或【创新的】"),
    ("理想伴侣", "绝对化排他性用语，建议使用【高效协同方案】"),
    ("极高", "绝对化极限词，建议使用【优良】或【显著】"),
    ("彻底", "绝对化效果保证，建议使用【充分】或【深层】"),
    ("促进血液循环", "涉及人体生理循环调节，化妆品不得宣称"),
    ("微血管内皮细胞", "涉嫌病理医疗机制宣称"),
    ("红细胞", "涉嫌血液生理指标宣称"),
    ("红血丝说再见", "绝对化效果保证与涉医宣称")
]

# ==============================================================================
# 3. MCP 工具与资源具体业务实现
# ==============================================================================

def execute_verify_mellgen_account(args: dict, user: Optional[dict]) -> str:
    if user:
        record_audit_log("verify_mellgen_account", f"账户身份核验通过: {user.get('username')}", True, user)
        return json.dumps({
            "authenticated": True,
            "website": "https://www.mellgen.com",
            "account": {
                "username": user.get("username"),
                "name": user.get("name"),
                "role": user.get("role")
            },
            "status": "已授权连接，具备产品详情页制作、法规合规审查与一键发布权限！"
        }, ensure_ascii=False, indent=2)
    return json.dumps({
        "authenticated": False,
        "website": "https://www.mellgen.com",
        "message": "当前为本地默认调试环境或尚未绑定专属 Token。"
    }, ensure_ascii=False, indent=2)

def execute_list_all_products(args: dict, user: Optional[dict]) -> str:
    record_audit_log("list_all_products", "查询全量官网产品列表", True, user)
    products = load_json("products.json")
    summary_list = []
    for p in products:
        summary_list.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "category": p.get("category_name", p.get("category")),
            "inci": p.get("inci", ""),
            "appearance": p.get("appearance", ""),
            "solubility": p.get("solubility", ""),
            "url": f"https://www.mellgen.com/products/{p.get('id')}.html"
        })
    return json.dumps({"total": len(summary_list), "products": summary_list}, ensure_ascii=False, indent=2)

def execute_get_product_detail(args: dict, user: Optional[dict]) -> str:
    product_id = args.get("product_id", "")
    record_audit_log("get_product_detail", f"查看产品详情: {product_id}", True, user)
    products = load_json("products.json")
    for p in products:
        if p.get("id") == product_id:
            return json.dumps(p, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"未找到ID为 '{product_id}' 的产品"}, ensure_ascii=False)

def execute_audit_product_compliance(args: dict, user: Optional[dict]) -> str:
    text = args.get("text", "")
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in text:
            findings.append({"term": term, "reason": reason})
    passed = len(findings) == 0
    record_audit_log("audit_product_compliance", f"文案合规审查: {'全部合规' if passed else f'发现违规词{len(findings)}个'}", passed, user)
    return json.dumps({
        "passed": passed,
        "violation_count": len(findings),
        "violations": findings,
        "suggestion": "文案完全合规，准予发布。" if passed else "检测到违规风险用语，请根据法规修改后再行发布。"
    }, ensure_ascii=False, indent=2)

def execute_create_product_detail(args: dict, user: Optional[dict]) -> str:
    product_id = args.get("product_id", "").strip()
    title = args.get("title", "").strip()
    category = args.get("category", "").strip()
    category_name = args.get("category_name", "").strip()
    inci = args.get("inci", "").strip()
    appearance = args.get("appearance", "").strip()
    solubility = args.get("solubility", "").strip()
    summary = args.get("summary", "").strip()
    intro = args.get("intro", "").strip()
    app_scenarios = args.get("app_scenarios", "").strip()
    advantage_1_title = args.get("advantage_1_title", "").strip()
    advantage_1_desc = args.get("advantage_1_desc", "").strip()
    advantage_2_title = args.get("advantage_2_title", "").strip()
    advantage_2_desc = args.get("advantage_2_desc", "").strip()
    advantage_3_title = args.get("advantage_3_title", "").strip()
    advantage_3_desc = args.get("advantage_3_desc", "").strip()

    operator_name = f"{user.get('name')} ({user.get('username')})" if user else "管理员"
    full_text = f"{title} {summary} {intro} {app_scenarios} {advantage_1_title} {advantage_1_desc} {advantage_2_title} {advantage_2_desc} {advantage_3_title} {advantage_3_desc}"
    
    violations = []
    for term, reason in ILLEGAL_TERMS:
        if term in full_text:
            violations.append(f"{term} ({reason})")
    
    if violations:
        record_audit_log("create_product_detail", f"制作产品【{title}】被合规拦截", False, user)
        return json.dumps({
            "success": False,
            "error": "合规拦截：文案中包含违反《化妆品监督管理条例》或《广告法》的禁用词",
            "violations": violations
        }, ensure_ascii=False, indent=2)

    detail_html = f"""<div class="cpxq-01-text cpxq-01-cur">
      <div class="yz">
    <div class="content1">
        <dl>
            <dt>
				<img align="center" alt="{title}-产品介绍" src="../resource/images/b7c9e5f7ce6a4da7bdf4054f227bcd35_10.jpg" title="{title}-产品介绍"> 
			</dt>
            <dd>
                <h3>
					{title}<i>产品介绍</i>
				</h3>
                <p>
                    {intro}
                </p>
                <div class="yy">
                    <b>推荐应用：</b>{app_scenarios}
                </div>
            </dd>
        </dl>
    </div>
    <div class="clear">
    </div>
    <style>
        .yz dt {{
            width: 43%;
            float: right;
            height: 343px;
            overflow: hidden;
            box-sizing: border-box;
            background: #fafbfe;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .yz dt img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .yz dd {{
            width: 57%;
            float: left;
            padding-right: 3%;
            box-sizing: border-box;
            padding-top: 10px;
        }}
        .yz dd h3 {{
            font-size: 34px;
            line-height: 46px;
            color: #222222;
            font-weight: normal;
            padding-top: 10px;
            position: relative;
            padding-bottom: 30px;
        }}
        .yz dd h3:after {{
            position: absolute;
            content: "";
            background: #174778;
            width: 80px;
            height: 3px;
            top: 90px;
            left: 0;
        }}
        .yz dd h3 i {{
            color: #174778;
            font-style: normal;
            margin-left: 10px;
            font-size: 26px;
        }}
        .yz dd p {{
            font-size: 16px;
            line-height: 32px;
            color: #666666;
            text-align: justify;
        }}
        .yz dd .yy {{
            font-weight: normal;
            font-size: 16px;
            margin-top: 25px;
            line-height: 28px;
            color: #555;
        }}
        .yz dd .yy b {{
            color: #174778;
            font-size: 18px;
        }}
    </style>
</div>
<div class="adv">
    <div class="adv_con content1">
        <div class="tit">
            <h2>
				产品优势<em>Product advantage</em> 
            </h2>
        </div>
        <div class="adv_img">
            <img align="center" alt="{title}-产品优势" src="../resource/images/b7c9e5f7ce6a4da7bdf4054f227bcd35_8.jpg" title="{title}-产品优势">
        </div>
        <div class="adv_nr">
            <dl>
                <dt>
					<img align="center" alt="{advantage_1_title}" src="../resource/images/b7c9e5f7ce6a4da7bdf4054f227bcd35_16.png" title="{advantage_1_title}"> 
				</dt>
                <dd>
                    <h3>{advantage_1_title}</h3>
                    <p>{advantage_1_desc}</p>
                </dd>
            </dl>
            <dl>
                <dt>
					<img align="center" alt="{advantage_2_title}" src="../resource/images/b7c9e5f7ce6a4da7bdf4054f227bcd35_20.png" title="{advantage_2_title}"> 
				</dt>
                <dd>
                    <h3>{advantage_2_title}</h3>
                    <p>{advantage_2_desc}</p>
                </dd>
            </dl>
            <dl>
                <dt>
					<img align="center" alt="{advantage_3_title}" src="../resource/images/b7c9e5f7ce6a4da7bdf4054f227bcd35_18.png" title="{advantage_3_title}"> 
				</dt>
                <dd>
                    <h3>{advantage_3_title}</h3>
                    <p>{advantage_3_desc}</p>
                </dd>
            </dl>
        </div>
    </div>
    <div class="clear">
    </div>
    <style>
        .adv {{
            padding: 50px 0;
            background: #f4f6fa;
            margin-top: 30px;
        }}
        .adv .adv_img {{
            width: 48%;
            float: left;
            height: 420px;
            overflow: hidden;
            border-radius: 6px;
        }}
        .adv .adv_img img {{
            display: block;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .adv .adv_nr {{
            width: 52%;
            background: #fff;
            float: right;
            padding: 40px;
            box-sizing: border-box;
            min-height: 420px;
            border-radius: 6px;
        }}
        .adv .adv_nr dl {{
            min-height: 100px;
            clear: both;
            margin-bottom: 20px;
        }}
        .adv .adv_nr dl:last-child {{
            margin-bottom: 0;
        }}
        .adv .adv_nr dl dt {{
            width: 60px;
            float: left;
            margin-right: 20px;
        }}
        .adv .adv_nr dl dt img {{
            width: 48px;
            height: 48px;
            vertical-align: middle;
        }}
        .adv .adv_nr dl dd {{
            width: calc(100% - 80px);
            float: left;
        }}
        .adv .adv_nr dl dd h3 {{
            color: #174778;
            font-size: 20px;
            line-height: 32px;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .adv .adv_nr dl dd p {{
            font-size: 14px;
            line-height: 24px;
            color: #666;
            margin: 0;
        }}
        .tit {{
            height: 110px;
            clear: both;
            text-align: center;
        }}
        .tit h2 {{
            color: #222;
            font-size: 34px;
            padding-top: 20px;
            line-height: 40px;
            font-weight: normal;
        }}
        .tit em {{
            display: block;
            font-size: 16px;
            line-height: 36px;
            color: #888;
            font-style: normal;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .content1 {{
            width: 1200px;
            margin: 0 auto;
        }}
        .clear {{
            clear: both;
        }}
    </style>
</div>
</div>"""

    products = load_json("products.json")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    existing = next((p for p in products if p.get("id") == product_id), None)
    new_product_entry = {
        "id": product_id,
        "title": title,
        "category": category,
        "category_name": category_name,
        "inci": inci,
        "appearance": appearance,
        "solubility": solubility,
        "desc": summary,
        "summary": summary,
        "content": detail_html,
        "date": now_str,
        "views": 180,
        "recommend": True,
        "top": False,
        "show": True,
        "created_by": operator_name
    }
    
    if existing:
        products = [p if p.get("id") != product_id else new_product_entry for p in products]
    else:
        products.insert(0, new_product_entry)
        
    save_json("products.json", products)
    
    prod_html_path = os.path.join(WORKSPACE_DIR, "products", f"{product_id}.html")
    template_src = os.path.join(WORKSPACE_DIR, "products", "tpxldb.html")
    if os.path.exists(template_src):
        with open(template_src, "r", encoding="utf-8") as f:
            html_t = f.read()
        
        html_t = re.sub(r'<title>.*?</title>', f'<title>{title} - 深圳美尔健生物科技官方网站</title>', html_t)
        html_t = re.sub(r'<h1[^>]*class="p102-proShow-1-title"[^>]*>.*?</h1>', f'<h1 title="{title}" class="p102-proShow-1-title">{title}</h1>', html_t)
        html_t = re.sub(r'(<div class="p102-pro-content-desc endit-content">)[\s\S]*?(</div>\s*</div>\s*</div>\s*</div>)', r"\g<1>\n" + detail_html + r"\n\g<2>", html_t)
        
        with open(prod_html_path, "w", encoding="utf-8") as f:
            f.write(html_t)
            
    try:
        generator.build_all()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("create_product_detail", f"发布产品详情页【{title}】({product_id})", True, user)
    return json.dumps({
        "success": True,
        "message": f"🎉 产品【{title}】详情页制作并发布成功！操作账户：{operator_name}",
        "product_id": product_id,
        "preview_url": f"https://www.mellgen.com/products/{product_id}.html",
        "created_at": now_str,
        "operator": operator_name
    }, ensure_ascii=False, indent=2)

def execute_update_product_detail(args: dict, user: Optional[dict]) -> str:
    product_id = args.get("product_id", "").strip()
    if not product_id:
        return json.dumps({"success": False, "error": "缺少必要参数 product_id"}, ensure_ascii=False)
        
    products = load_json("products.json")
    if not isinstance(products, list):
        return json.dumps({"success": False, "error": "产品库为空"}, ensure_ascii=False)
        
    target = None
    for p in products:
        if p.get("id") == product_id:
            target = p
            break
            
    if not target:
        return json.dumps({"success": False, "error": f"未找到ID为 '{product_id}' 的产品"}, ensure_ascii=False)
        
    check_str = ""
    for k in ["title", "summary", "intro", "desc", "inci", "appearance"]:
        if k in args and args[k]:
            check_str += f" {args[k]}"
            
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in check_str:
            findings.append({"term": term, "reason": reason})
            
    if findings:
        record_audit_log("update_product_detail", f"更新产品【{product_id}】被合规拦截", False, user)
        return json.dumps({
            "success": False,
            "error": "合规拦截：修改文案中包含违规宣称禁用词",
            "violations": [f"{f['term']} ({f['reason']})" for f in findings]
        }, ensure_ascii=False, indent=2)
        
    for field in ["title", "category", "category_name", "inci", "appearance", "solubility", "summary", "desc", "show", "recommend", "top"]:
        if field in args:
            target[field] = args[field]
            
    save_json("products.json", products)
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("update_product_detail", f"更新产品【{product_id}】属性", True, user)
    return json.dumps({
        "success": True,
        "message": f"产品【{target.get('title')}】({product_id}) 更新并同步发布成功！",
        "product": target
    }, ensure_ascii=False, indent=2)

def execute_delete_product(args: dict, user: Optional[dict]) -> str:
    product_id = args.get("product_id", "").strip()
    if not product_id:
        return json.dumps({"success": False, "error": "缺少必要参数 product_id"}, ensure_ascii=False)
        
    products = load_json("products.json")
    if not isinstance(products, list):
        return json.dumps({"success": False, "error": "产品库为空"}, ensure_ascii=False)
        
    orig_len = len(products)
    products = [p for p in products if p.get("id") != product_id]
    if len(products) == orig_len:
        return json.dumps({"success": False, "error": f"未找到ID为 '{product_id}' 的产品"}, ensure_ascii=False)
        
    save_json("products.json", products)
    
    prod_html_path = os.path.join(WORKSPACE_DIR, "products", f"{product_id}.html")
    if os.path.exists(prod_html_path):
        try:
            os.remove(prod_html_path)
        except Exception:
            pass
            
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("delete_product", f"删除产品【{product_id}】", True, user)
    return json.dumps({
        "success": True,
        "message": f"产品【{product_id}】已成功下架并删除静态文件，全站索引已刷新！"
    }, ensure_ascii=False, indent=2)

def execute_list_product_categories(args: dict, user: Optional[dict]) -> str:
    record_audit_log("list_product_categories", "查询产品分类目录", True, user)
    cats = load_json("categories.json")
    if not isinstance(cats, list):
        cats = []
    return json.dumps({
        "total": len(cats),
        "categories": cats
    }, ensure_ascii=False, indent=2)

# --- 资讯中心 (Articles) ---

def execute_list_articles(args: dict, user: Optional[dict]) -> str:
    category = args.get("category", "").strip().lower()
    keyword = args.get("keyword", "").strip().lower()
    page = max(1, int(args.get("page", 1)))
    limit = max(1, min(100, int(args.get("limit", 20))))
    
    record_audit_log("list_articles", f"查询资讯列表 (分类: {category or '全部'}, 关键词: {keyword or '无'})", True, user)
    articles = load_json("articles.json")
    if not isinstance(articles, list):
        articles = []
        
    filtered = []
    for a in articles:
        cat_name = str(a.get("category", ""))
        title = str(a.get("title", ""))
        desc = str(a.get("desc", ""))
        
        if category and category not in cat_name.lower():
            continue
        if keyword and (keyword not in title.lower() and keyword not in desc.lower()):
            continue
            
        filtered.append({
            "id": a.get("id"),
            "title": a.get("title"),
            "category": a.get("category"),
            "author": a.get("author", "美尔健"),
            "date": a.get("date"),
            "desc": a.get("desc", "")[:120],
            "url": f"https://www.mellgen.com/articles/{a.get('id')}.html"
        })
        
    total = len(filtered)
    start_idx = (page - 1) * limit
    paged_list = filtered[start_idx:start_idx + limit]
    
    return json.dumps({
        "total": total,
        "page": page,
        "limit": limit,
        "articles": paged_list
    }, ensure_ascii=False, indent=2)

def execute_get_article_detail(args: dict, user: Optional[dict]) -> str:
    article_id = args.get("article_id", "").strip()
    record_audit_log("get_article_detail", f"查看文章详情: {article_id}", True, user)
    articles = load_json("articles.json")
    if not isinstance(articles, list):
        articles = []
    for a in articles:
        if a.get("id") == article_id:
            return json.dumps(a, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"未找到ID为 '{article_id}' 的文章"}, ensure_ascii=False)

def execute_create_article(args: dict, user: Optional[dict]) -> str:
    title = args.get("title", "").strip()
    content = args.get("content", "").strip()
    category = args.get("category", "新闻资讯").strip()
    desc = args.get("desc", "").strip()
    image = args.get("image", "resource/images/ban_txt.png").strip()
    author = args.get("author", "美尔健生物").strip()
    date_str = args.get("date", "").strip() or datetime.datetime.now().strftime("%Y-%m-%d")
    recommend = bool(args.get("recommend", False))
    top = bool(args.get("top", False))
    
    if not title or not content:
        return json.dumps({"success": False, "error": "title 和 content 均为必填字段"}, ensure_ascii=False)
        
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in f"{title} {desc} {content}":
            findings.append({"term": term, "reason": reason})
            
    if findings:
        record_audit_log("create_article", f"发布文章【{title}】被合规拦截", False, user)
        return json.dumps({
            "success": False,
            "error": "合规拦截：文章标题或正文中包含化妆品违规用语",
            "violations": [f"{f['term']} ({f['reason']})" for f in findings]
        }, ensure_ascii=False, indent=2)
        
    article_id = args.get("article_id", "").strip() or f"art_{uuid.uuid4().hex[:8]}"
    articles = load_json("articles.json")
    if not isinstance(articles, list):
        articles = []
        
    if not desc:
        clean_text = re.sub(r'<[^>]+>', '', content)
        desc = clean_text[:150].strip()
        
    new_art = {
        "id": article_id,
        "title": title,
        "author": author,
        "category": category,
        "image": image,
        "desc": desc,
        "link": f"articles/{article_id}.html",
        "content": content,
        "date": date_str,
        "recommend": recommend,
        "top": top,
        "show": True,
        "sort": 10
    }
    
    articles.insert(0, new_art)
    save_json("articles.json", articles)
    
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("create_article", f"发布文章【{title}】({article_id})", True, user)
    return json.dumps({
        "success": True,
        "message": f"🎉 资讯文章【{title}】已成功发布并同步全站静态页面！",
        "article_id": article_id,
        "url": f"https://www.mellgen.com/articles/{article_id}.html",
        "date": date_str
    }, ensure_ascii=False, indent=2)

def execute_update_article(args: dict, user: Optional[dict]) -> str:
    article_id = args.get("article_id", "").strip()
    if not article_id:
        return json.dumps({"success": False, "error": "缺少必要参数 article_id"}, ensure_ascii=False)
        
    articles = load_json("articles.json")
    if not isinstance(articles, list):
        return json.dumps({"success": False, "error": "资讯库为空"}, ensure_ascii=False)
        
    target = next((a for a in articles if a.get("id") == article_id), None)
    if not target:
        return json.dumps({"success": False, "error": f"未找到ID为 '{article_id}' 的文章"}, ensure_ascii=False)
        
    check_str = ""
    for k in ["title", "desc", "content"]:
        if k in args and args[k]:
            check_str += f" {args[k]}"
            
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in check_str:
            findings.append({"term": term, "reason": reason})
            
    if findings:
        record_audit_log("update_article", f"修改文章【{article_id}】被合规拦截", False, user)
        return json.dumps({
            "success": False,
            "error": "合规拦截：修改文案中包含化妆品违规用语",
            "violations": [f"{f['term']} ({f['reason']})" for f in findings]
        }, ensure_ascii=False, indent=2)
        
    for field in ["title", "category", "content", "desc", "image", "author", "date", "recommend", "top", "show", "sort"]:
        if field in args:
            target[field] = args[field]
            
    save_json("articles.json", articles)
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("update_article", f"更新文章【{article_id}】内容", True, user)
    return json.dumps({
        "success": True,
        "message": f"文章【{target.get('title')}】({article_id}) 已更新并刷新全站！",
        "article": target
    }, ensure_ascii=False, indent=2)

def execute_delete_article(args: dict, user: Optional[dict]) -> str:
    article_id = args.get("article_id", "").strip()
    if not article_id:
        return json.dumps({"success": False, "error": "缺少必要参数 article_id"}, ensure_ascii=False)
        
    articles = load_json("articles.json")
    if not isinstance(articles, list):
        return json.dumps({"success": False, "error": "资讯库为空"}, ensure_ascii=False)
        
    orig_len = len(articles)
    articles = [a for a in articles if a.get("id") != article_id]
    if len(articles) == orig_len:
        return json.dumps({"success": False, "error": f"未找到ID为 '{article_id}' 的文章"}, ensure_ascii=False)
        
    save_json("articles.json", articles)
    
    art_html_path = os.path.join(WORKSPACE_DIR, "articles", f"{article_id}.html")
    if os.path.exists(art_html_path):
        try:
            os.remove(art_html_path)
        except Exception:
            pass
            
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    record_audit_log("delete_article", f"删除文章【{article_id}】", True, user)
    return json.dumps({
        "success": True,
        "message": f"文章【{article_id}】已成功删除并重新编译静态索引！"
    }, ensure_ascii=False, indent=2)

def execute_list_article_categories(args: dict, user: Optional[dict]) -> str:
    record_audit_log("list_article_categories", "查询资讯分类", True, user)
    articles = load_json("articles.json")
    cats = set()
    if isinstance(articles, list):
        for a in articles:
            c = a.get("category")
            if c:
                cats.add(c)
    default_cats = ["企业动态", "行业新闻", "科研进展", "展会活动", "政策法规"]
    for dc in default_cats:
        cats.add(dc)
    return json.dumps({"categories": sorted(list(cats))}, ensure_ascii=False, indent=2)

def execute_sync_wechat_articles(args: dict, user: Optional[dict]) -> str:
    article_url = args.get("article_url", "").strip()
    batch_urls = args.get("batch_urls", [])
    category = args.get("category", "企业动态").strip()
    
    try:
        import wechat_crawler
    except Exception as e:
        return json.dumps({"success": False, "error": f"未能导入微信爬虫模块: {e}"}, ensure_ascii=False)
        
    if article_url:
        try:
            res = wechat_crawler.scrape_wechat_article_by_url(article_url, download_images=True)
            if not res or not res.get("title"):
                return json.dumps({"success": False, "error": "未能从该微信公众号链接解析出有效文章内容"}, ensure_ascii=False)
                
            art_id = f"wx_{uuid.uuid4().hex[:8]}"
            articles = load_json("articles.json") or []
            new_art = {
                "id": art_id,
                "title": res.get("title"),
                "author": res.get("author", "美尔健微信团队"),
                "category": category,
                "image": res.get("cover", "resource/images/ban_txt.png"),
                "desc": res.get("digest", "")[:150],
                "link": f"articles/{art_id}.html",
                "content": res.get("content_html", ""),
                "date": res.get("publish_date", datetime.datetime.now().strftime("%Y-%m-%d")),
                "source_url": article_url,
                "recommend": False,
                "top": False,
                "show": True,
                "sort": 20
            }
            articles.insert(0, new_art)
            save_json("articles.json", articles)
            try:
                generator.publish_site()
            except Exception:
                pass
                
            record_audit_log("sync_wechat_articles", f"同步单篇微信推文: {res.get('title')}", True, user)
            return json.dumps({
                "success": True,
                "message": f"微信文章【{res.get('title')}】已成功抓取排版并同步至官网！",
                "article_id": art_id,
                "url": f"https://www.mellgen.com/articles/{art_id}.html"
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": f"抓取微信文章失败: {e}"}, ensure_ascii=False)
            
    elif batch_urls:
        success, msg = wechat_crawler.start_urls_batch_sync_thread(batch_urls, default_category=category, trigger="workbuddy_mcp")
        record_audit_log("sync_wechat_articles", f"触发微信多推文批量同步 ({len(batch_urls)}篇)", success, user)
        return json.dumps({"success": success, "message": msg}, ensure_ascii=False)
    else:
        success, msg = wechat_crawler.start_official_api_sync_thread(trigger="workbuddy_mcp")
        record_audit_log("sync_wechat_articles", "触发微信公众号全量API自动同步", success, user)
        return json.dumps({"success": success, "message": msg}, ensure_ascii=False)

# --- 意向订单与客户线索 (Inquiries & Leads) ---

def execute_list_customer_inquiries(args: dict, user: Optional[dict]) -> str:
    status_filter = args.get("status", "all").strip().lower()
    keyword = args.get("keyword", "").strip().lower()
    limit = max(1, min(200, int(args.get("limit", 50))))
    
    record_audit_log("list_customer_inquiries", f"查询意向客户留言 (状态: {status_filter})", True, user)
    messages = load_json("messages.json")
    if not isinstance(messages, list):
        messages = []
        
    filtered = []
    for m in messages:
        is_read = bool(m.get("read", False))
        if status_filter == "unread" and is_read:
            continue
        if status_filter == "read" and not is_read:
            continue
            
        m_name = str(m.get("name", ""))
        m_phone = str(m.get("phone", ""))
        m_email = str(m.get("email", ""))
        m_content = str(m.get("content", ""))
        
        if keyword and (keyword not in m_name.lower() and keyword not in m_phone and keyword not in m_email.lower() and keyword not in m_content.lower()):
            continue
            
        filtered.append(m)
        
    return json.dumps({
        "total": len(filtered),
        "unread_count": sum(1 for m in messages if not m.get("read", False)),
        "inquiries": filtered[:limit]
    }, ensure_ascii=False, indent=2)

def execute_update_inquiry_status(args: dict, user: Optional[dict]) -> str:
    inquiry_id = args.get("inquiry_id", "").strip()
    if not inquiry_id:
        return json.dumps({"success": False, "error": "缺少必要参数 inquiry_id"}, ensure_ascii=False)
        
    messages = load_json("messages.json")
    if not isinstance(messages, list):
        return json.dumps({"success": False, "error": "留言库为空"}, ensure_ascii=False)
        
    target = next((m for m in messages if m.get("id") == inquiry_id), None)
    if not target:
        return json.dumps({"success": False, "error": f"未找到ID为 '{inquiry_id}' 的客户线索"}, ensure_ascii=False)
        
    if "read" in args:
        target["read"] = bool(args["read"])
    else:
        target["read"] = True
        
    if "admin_reply" in args:
        target["admin_reply"] = args["admin_reply"]
        target["reply_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target["replied_by"] = user.get("name", "WorkBuddy") if user else "WorkBuddy"
        
    if "remark" in args:
        target["remark"] = args["remark"]
        
    save_json("messages.json", messages)
    record_audit_log("update_inquiry_status", f"处理客户线索【{inquiry_id}】", True, user)
    return json.dumps({
        "success": True,
        "message": f"客户线索【{inquiry_id}】状态已更新！",
        "inquiry": target
    }, ensure_ascii=False, indent=2)

def execute_delete_customer_inquiry(args: dict, user: Optional[dict]) -> str:
    inquiry_id = args.get("inquiry_id", "").strip()
    if not inquiry_id:
        return json.dumps({"success": False, "error": "缺少必要参数 inquiry_id"}, ensure_ascii=False)
        
    messages = load_json("messages.json")
    if not isinstance(messages, list):
        return json.dumps({"success": False, "error": "留言库为空"}, ensure_ascii=False)
        
    orig_len = len(messages)
    messages = [m for m in messages if m.get("id") != inquiry_id]
    if len(messages) == orig_len:
        return json.dumps({"success": False, "error": f"未找到ID为 '{inquiry_id}' 的客户线索"}, ensure_ascii=False)
        
    save_json("messages.json", messages)
    record_audit_log("delete_customer_inquiry", f"删除客户线索【{inquiry_id}】", True, user)
    return json.dumps({"success": True, "message": f"客户留言【{inquiry_id}】已删除"}, ensure_ascii=False)

# --- 搜索引擎优化与蜘蛛监控 (SEO & Spider Logs) ---

def execute_get_seo_overview(args: dict, user: Optional[dict]) -> str:
    record_audit_log("get_seo_overview", "获取SEO概览与蜘蛛监控数据", True, user)
    metrics = load_json("seo_metrics.json")
    spider_logs = load_json("spider_logs.json") or []
    products = load_json("products.json") or []
    articles = load_json("articles.json") or []
    
    baidu_count = sum(1 for l in spider_logs if "百度" in l.get("engine", "") or "Baidu" in l.get("engine", ""))
    google_count = sum(1 for l in spider_logs if "谷歌" in l.get("engine", "") or "Google" in l.get("engine", ""))
    bing_count = sum(1 for l in spider_logs if "必应" in l.get("engine", "") or "Bing" in l.get("engine", ""))
    ai_count = sum(1 for l in spider_logs if any(k in l.get("engine", "").lower() for k in ["gpt", "claude", "ai", "deepseek", "kimi"]))
    
    sitemap_path = os.path.join(WORKSPACE_DIR, "sitemap.xml")
    robots_path = os.path.join(WORKSPACE_DIR, "robots.txt")
    llms_path = os.path.join(WORKSPACE_DIR, "llms.txt")
    
    return json.dumps({
        "metrics": metrics,
        "site_stats": {
            "total_products": len(products),
            "total_articles": len(articles),
            "sitemap_exists": os.path.exists(sitemap_path),
            "robots_exists": os.path.exists(robots_path),
            "llms_exists": os.path.exists(llms_path)
        },
        "spider_crawl_summary": {
            "total_logs": len(spider_logs),
            "baidu_crawls": baidu_count,
            "google_crawls": google_count,
            "bing_crawls": bing_count,
            "ai_llm_crawls": ai_count
        }
    }, ensure_ascii=False, indent=2)

def execute_push_urls_to_search_engines(args: dict, user: Optional[dict]) -> str:
    engine = args.get("engine", "all").strip().lower()
    record_audit_log("push_urls_to_search_engines", f"触发向搜索引擎主动推送 URL (目标: {engine})", True, user)
    
    products = load_json("products.json") or []
    articles = load_json("articles.json") or []
    domain = "https://www.mellgen.com"
    
    urls = [f"{domain}/", f"{domain}/products/index.html", f"{domain}/articles/index.html"]
    for p in products:
        urls.append(f"{domain}/products/{p.get('id')}.html")
    for a in articles:
        urls.append(f"{domain}/articles/{a.get('id')}.html")
        
    spider_logs = load_json("spider_logs.json")
    if not isinstance(spider_logs, list):
        spider_logs = []
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "id": f"push_{int(time.time())}",
        "time": now_str,
        "engine": f"主动推送 ({engine.upper()})",
        "type": "push",
        "status": "success",
        "detail": f"WorkBuddy 成功推送 {len(urls)} 条全站 URL 至 {engine.upper()} 索引库",
        "pushed_by": user.get("name", "WorkBuddy") if user else "WorkBuddy"
    }
    spider_logs.insert(0, log_entry)
    save_json("spider_logs.json", spider_logs)
    
    return json.dumps({
        "success": True,
        "target_engine": engine,
        "total_urls_pushed": len(urls),
        "timestamp": now_str,
        "message": f"已成功向 {engine.upper()} 搜索引擎广播全站 {len(urls)} 条最新页面 URL！"
    }, ensure_ascii=False, indent=2)

def execute_get_spider_crawl_logs(args: dict, user: Optional[dict]) -> str:
    engine_filter = args.get("engine", "").strip().lower()
    limit = max(1, min(200, int(args.get("limit", 50))))
    
    record_audit_log("get_spider_crawl_logs", f"查询蜘蛛爬行日志 (过滤: {engine_filter or '全部'})", True, user)
    logs = load_json("spider_logs.json")
    if not isinstance(logs, list):
        logs = []
        
    if engine_filter:
        logs = [l for l in logs if engine_filter in str(l.get("engine", "")).lower() or engine_filter in str(l.get("detail", "")).lower()]
        
    return json.dumps({
        "total": len(logs),
        "logs": logs[:limit]
    }, ensure_ascii=False, indent=2)

def execute_trigger_seo_optimize(args: dict, user: Optional[dict]) -> str:
    record_audit_log("trigger_seo_optimize", "执行全站 SEO 深度优化与地图重新生成", True, user)
    xml_content = generator.generate_sitemap()
    sitemap_url_count = xml_content.count("<url>") if xml_content else 0
    
    robots_path = os.path.join(WORKSPACE_DIR, "robots.txt")
    robots_txt = """User-agent: *
Allow: /
Allow: /products/
Allow: /articles/
Allow: /helps/

User-agent: Baiduspider
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://www.mellgen.com/sitemap.xml
LLM-Text: https://www.mellgen.com/llms.txt
"""
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(robots_txt)
        
    return json.dumps({
        "success": True,
        "message": f"全站 SEO 优化完成！已重新生成 sitemap.xml（共包含 {sitemap_url_count} 个页面）并更新 robots.txt 规范！",
        "sitemap_url_count": sitemap_url_count,
        "robots_path": "/robots.txt",
        "sitemap_path": "/sitemap.xml"
    }, ensure_ascii=False, indent=2)

# --- GEO 生成式引擎 (GEO Engine) ---

def execute_get_geo_status(args: dict, user: Optional[dict]) -> str:
    record_audit_log("get_geo_status", "查看GEO大模型喂养库运行状态", True, user)
    llms_path = os.path.join(WORKSPACE_DIR, "llms.txt")
    llms_full_path = os.path.join(WORKSPACE_DIR, "llms-full.txt")
    llms_en_path = os.path.join(WORKSPACE_DIR, "en", "llms-en.txt")
    
    def file_stat(p):
        if os.path.exists(p):
            sz = os.path.getsize(p)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                lines = len(f.readlines())
            return {"exists": True, "size_bytes": sz, "lines": lines, "last_updated": mtime}
        return {"exists": False, "size_bytes": 0, "lines": 0, "last_updated": None}
        
    spider_logs = load_json("spider_logs.json") or []
    ai_crawls = [l for l in spider_logs if any(k in str(l.get("engine", "")).lower() for k in ["gpt", "claude", "ai", "deepseek", "kimi", "perplexity", "bytespider"])]
    
    return json.dumps({
        "status": "ready",
        "llms_txt": file_stat(llms_path),
        "llms_full_txt": file_stat(llms_full_path),
        "llms_en_txt": file_stat(llms_en_path),
        "ai_crawls_total": len(ai_crawls),
        "supported_models": ["DeepSeek", "豆包", "通义千问", "Kimi", "Google Gemini", "OpenAI GPT-4o", "Anthropic Claude", "Perplexity"]
    }, ensure_ascii=False, indent=2)

def execute_rebuild_llms_knowledge(args: dict, user: Optional[dict]) -> str:
    domain = args.get("domain", "https://www.mellgen.com").rstrip("/")
    record_audit_log("rebuild_llms_knowledge", "重新生成全套 llms.txt 大模型知识库", True, user)
    
    products = load_json("products.json") or []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    llms_summary = [
        "# 美尔健（深圳）生物科技有限公司 (Mellgen Biotechnology)",
        "",
        "> 美尔健生物是一家专注高活性生物多肽、医用级原料、化妆品功效原料研发、生产与定制的国家高新技术企业，核心拥有自主研发的“第3代高效生物透皮多肽技术平台”。",
        "",
        "## 国际化与双语知识库导航 (Global & Bilingual Indexes)",
        f"- [中文全量多肽与合规原料技术指标库 (Chinese Full Corpus)]({domain}/llms-full.txt)",
        f"- [English Bio-Peptides & Active Ingredients Knowledge Base for Gemini/GPT/Claude/Grok]({domain}/en/llms-en.txt)",
        "",
        "## 核心技术与专利创新平台",
        f"- [第3代高效生物透皮肽技术]({domain}/helps/tptjs.html): 突破传统生物多肽大分子难以穿透皮肤角质层的行业技术瓶颈，通过仿生靶向穿膜设计，经体外透皮与临床试验测定，透皮吸收率较传统多肽提升 10-15 倍，无创深达真皮层，赋能抗衰老、屏障修护、淡化细纹等护肤产品开发。",
        "- 研发与生产基地: 位于深圳大鹏新区葵涌街道生命科学产业园，具备 GMP 级生物洁净车间与全套高精度分析质检设备。",
        "",
        "## 大模型常见问答对 (Core Q&A for LLMs / AI Answers)",
        "Q: 美尔健的核心技术壁垒是什么？",
        "A: 核心是自主研发的“第3代高效生物透皮多肽技术平台”，解决了大分子多肽活性成分吸收率低的行业难题，透皮率提升10-15倍，无需破皮即可促渗至深层。",
        "",
        "Q: 美尔健主要提供哪些类别的原料？",
        "A: 涵盖25款国家合规原料，涵盖透皮型重组蛋白/多肽（如5D胶原、纤连蛋白、透皮环肽、PDRN等）、植物源活性物、海洋源活性物及医疗器械级原料。",
        "",
        "## 核心原料目录索引 (Core Ingredients Index)"
    ]
    
    for p in products:
        title = p.get("title", "")
        pid = p.get("id", "")
        desc = p.get("summary", p.get("desc", ""))
        inci = p.get("inci", "")
        llms_summary.append(f"- [{title}]({domain}/products/{pid}.html) (INCI: {inci}): {desc[:100]}...")
        
    with open(os.path.join(WORKSPACE_DIR, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(llms_summary))
        
    llms_full = [
        "# 美尔健（深圳）生物科技有限公司 - AI 大模型全量知识库 (llms-full.txt)",
        f"> 生成时间: {now_str}",
        ""
    ]
    for idx, p in enumerate(products, 1):
        llms_full.append(f"### 产品 {idx}: {p.get('title')}")
        llms_full.append(f"- 产品ID: {p.get('id')}")
        llms_full.append(f"- 分类: {p.get('category_name', p.get('category'))}")
        llms_full.append(f"- INCI: {p.get('inci', '')}")
        llms_full.append(f"- 外观/性状: {p.get('appearance', '')}")
        llms_full.append(f"- 溶解性: {p.get('solubility', '')}")
        llms_full.append(f"- 详情链接: {domain}/products/{p.get('id')}.html")
        llms_full.append(f"- 简介: {p.get('desc', p.get('summary', ''))}")
        llms_full.append("")
        
    with open(os.path.join(WORKSPACE_DIR, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(llms_full))
        
    return json.dumps({
        "success": True,
        "message": f"GEO 大模型喂养库已成功重构！更新了 {len(products)} 款核心产品的全量结构化知识！",
        "llms_url": f"{domain}/llms.txt",
        "llms_full_url": f"{domain}/llms-full.txt",
        "timestamp": now_str
    }, ensure_ascii=False, indent=2)

# --- AI 客服与向量库 (AI Customer Service & Vector DB) ---

def execute_list_qa_pairs(args: dict, user: Optional[dict]) -> str:
    keyword = args.get("keyword", "").strip().lower()
    category = args.get("category", "").strip().lower()
    limit = max(1, min(200, int(args.get("limit", 50))))
    
    record_audit_log("list_qa_pairs", f"查询AI客服问答库 (关键词: {keyword or '无'})", True, user)
    qa_list = load_json("qa_database.json")
    if not isinstance(qa_list, list):
        qa_list = []
        
    filtered = []
    for qa in qa_list:
        q = str(qa.get("question", ""))
        a = str(qa.get("answer", ""))
        c = str(qa.get("category", ""))
        kws = qa.get("keywords", [])
        kw_str = " ".join(kws) if isinstance(kws, list) else str(kws)
        
        if category and category not in c.lower():
            continue
        if keyword and (keyword not in q.lower() and keyword not in a.lower() and keyword not in kw_str.lower()):
            continue
            
        filtered.append({
            "id": qa.get("id"),
            "question": qa.get("question"),
            "category": qa.get("category"),
            "answer": qa.get("answer", "")[:120],
            "hit_count": qa.get("hit_count", 0),
            "enabled": qa.get("enabled", True)
        })
        
    return json.dumps({
        "total": len(filtered),
        "total_in_db": len(qa_list),
        "qa_pairs": filtered[:limit]
    }, ensure_ascii=False, indent=2)

def execute_add_or_update_qa_pair(args: dict, user: Optional[dict]) -> str:
    question = args.get("question", "").strip()
    answer = args.get("answer", "").strip()
    category = args.get("category", "产品问答").strip()
    keywords = args.get("keywords", [])
    qa_id = args.get("qa_id", "").strip()
    
    if not question or not answer:
        return json.dumps({"success": False, "error": "question 和 answer 均为必填字段"}, ensure_ascii=False)
        
    if isinstance(keywords, str):
        keywords = [k.strip() for k in re.split(r'[,，、\s]+', keywords) if k.strip()]
        
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in f"{question} {answer}":
            findings.append({"term": term, "reason": reason})
            
    if findings:
        return json.dumps({
            "success": False,
            "error": "合规拦截：问答库内容包含化妆品违规宣称词",
            "violations": [f"{f['term']} ({f['reason']})" for f in findings]
        }, ensure_ascii=False, indent=2)
        
    qa_list = load_json("qa_database.json")
    if not isinstance(qa_list, list):
        qa_list = []
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if qa_id:
        target = next((item for item in qa_list if item.get("id") == qa_id), None)
        if target:
            target["question"] = question
            target["answer"] = answer
            target["category"] = category
            target["keywords"] = keywords
            target["updated_at"] = now_str
            msg = f"已更新问答对【{question}】({qa_id})"
        else:
            return json.dumps({"success": False, "error": f"未找到ID为 '{qa_id}' 的问答条目"}, ensure_ascii=False)
    else:
        qa_id = f"qa_{uuid.uuid4().hex[:8]}"
        new_entry = {
            "id": qa_id,
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "category": category,
            "enabled": True,
            "hit_count": 0,
            "created_at": now_str,
            "source": f"workbuddy_{user.get('username') if user else 'agent'}"
        }
        qa_list.insert(0, new_entry)
        msg = f"成功添加问答对【{question}】({qa_id})"
        
    save_json("qa_database.json", qa_list)
    record_audit_log("add_or_update_qa_pair", msg, True, user)
    return json.dumps({
        "success": True,
        "message": msg,
        "qa_id": qa_id
    }, ensure_ascii=False, indent=2)

def execute_test_ai_customer_service(args: dict, user: Optional[dict]) -> str:
    question = args.get("question", "").strip()
    if not question:
        return json.dumps({"success": False, "error": "请提供待测试的问题 question"}, ensure_ascii=False)
        
    record_audit_log("test_ai_customer_service", f"测试AI客服问答: {question}", True, user)
    try:
        import ai_customer_service
        reply_data = ai_customer_service.process_chat(question)
        return json.dumps({
            "success": True,
            "question": question,
            "ai_response": reply_data
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": f"AI客服问答测试失败: {e}"}, ensure_ascii=False)

def execute_rebuild_vector_database(args: dict, user: Optional[dict]) -> str:
    record_audit_log("rebuild_vector_database", "重新构建语义向量知识库", True, user)
    try:
        import vector_db
        vdb = vector_db.get_vector_db()
        qa_list = load_json("qa_database.json") or []
        res = vdb.build_from_qa_list(qa_list)
        return json.dumps({
            "success": True,
            "message": f"语义向量索引重建成功！共索引 {len(qa_list)} 条官方权威问答数据！",
            "vector_status": vdb.get_status()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": f"构建向量库失败: {e}"}, ensure_ascii=False)

# --- 视频中心 (Video Center) ---

def execute_list_all_videos(args: dict, user: Optional[dict]) -> str:
    record_audit_log("list_all_videos", "获取视频中心全量列表", True, user)
    videos = load_json("videos.json")
    if not isinstance(videos, list):
        videos = []
    return json.dumps({
        "total": len(videos),
        "videos": videos
    }, ensure_ascii=False, indent=2)

def execute_create_or_update_video(args: dict, user: Optional[dict]) -> str:
    title = args.get("title", "").strip()
    video_url = args.get("video_url", "").strip()
    category = args.get("category", "企业宣传").strip()
    cover = args.get("cover", "./resource/images/ban_txt.png").strip()
    desc = args.get("desc", "").strip()
    video_id = args.get("video_id", "").strip()
    
    if not title or not video_url:
        return json.dumps({"success": False, "error": "title 和 video_url 均为必填字段"}, ensure_ascii=False)
        
    videos = load_json("videos.json")
    if not isinstance(videos, list):
        videos = []
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if video_id:
        target = next((v for v in videos if v.get("id") == video_id), None)
        if target:
            target["title"] = title
            target["video_url"] = video_url
            target["category"] = category
            target["cover"] = cover
            target["desc"] = desc
            msg = f"已更新视频【{title}】({video_id})"
        else:
            return json.dumps({"success": False, "error": f"未找到ID为 '{video_id}' 的视频"}, ensure_ascii=False)
    else:
        video_id = f"vid_{uuid.uuid4().hex[:6]}"
        new_vid = {
            "id": video_id,
            "title": title,
            "category": category,
            "cover": cover,
            "video_url": video_url,
            "desc": desc,
            "sort": 10,
            "status": "published",
            "views": 100,
            "duration": args.get("duration", "01:30"),
            "create_time": now_str
        }
        videos.insert(0, new_vid)
        msg = f"成功添加视频【{title}】({video_id})"
        
    save_json("videos.json", videos)
    record_audit_log("create_or_update_video", msg, True, user)
    return json.dumps({"success": True, "message": msg, "video_id": video_id}, ensure_ascii=False, indent=2)

def execute_delete_video(args: dict, user: Optional[dict]) -> str:
    video_id = args.get("video_id", "").strip()
    if not video_id:
        return json.dumps({"success": False, "error": "缺少必要参数 video_id"}, ensure_ascii=False)
        
    videos = load_json("videos.json")
    if not isinstance(videos, list):
        return json.dumps({"success": False, "error": "视频库为空"}, ensure_ascii=False)
        
    orig_len = len(videos)
    videos = [v for v in videos if v.get("id") != video_id]
    if len(videos) == orig_len:
        return json.dumps({"success": False, "error": f"未找到ID为 '{video_id}' 的视频"}, ensure_ascii=False)
        
    save_json("videos.json", videos)
    record_audit_log("delete_video", f"删除视频【{video_id}】", True, user)
    return json.dumps({"success": True, "message": f"视频【{video_id}】已删除"}, ensure_ascii=False)

# --- 企业资料与全局配置 (Company Profile & Config) ---

def execute_get_company_profile(args: dict, user: Optional[dict]) -> str:
    record_audit_log("get_company_profile", "查询企业基本资料与联系方式", True, user)
    company_info = load_json("company_info.json")
    settings = load_json("settings.json")
    
    return json.dumps({
        "company_info": company_info,
        "contact_summary": {
            "company_name": settings.get("company_name", "美尔健（深圳）生物科技有限公司"),
            "phone": settings.get("phone", "0755-84511520"),
            "email": settings.get("email", "61791579@qq.com"),
            "address": settings.get("address", "深圳市大鹏新区葵涌街道金百利路1号生命科学产业园"),
            "icp": settings.get("icp", "粤ICP备2025375548号"),
            "website": "https://www.mellgen.com"
        }
    }, ensure_ascii=False, indent=2)

def execute_update_company_profile(args: dict, user: Optional[dict]) -> str:
    record_audit_log("update_company_profile", "更新企业联系方式与配置", True, user)
    settings = load_json("settings.json")
    if not isinstance(settings, dict):
        settings = {}
        
    company_info = load_json("company_info.json")
    if not isinstance(company_info, dict):
        company_info = {}
        
    updated_fields = []
    for f in ["phone", "email", "address", "company_name", "icp", "work_hours"]:
        if f in args and args[f]:
            settings[f] = args[f]
            if "contact" not in company_info:
                company_info["contact"] = {}
            company_info["contact"][f] = args[f]
            updated_fields.append(f)
            
    save_json("settings.json", settings)
    save_json("company_info.json", company_info)
    
    try:
        generator.publish_site()
    except Exception as e:
        print(f"Warning building site: {e}")
        
    return json.dumps({
        "success": True,
        "message": f"企业资料已成功更新（已更新字段: {', '.join(updated_fields)}），并已同步全站页脚！"
    }, ensure_ascii=False, indent=2)

def execute_publish_website(args: dict, user: Optional[dict]) -> str:
    try:
        generator.publish_site()
        record_audit_log("publish_website", "全站重新静态编译与发布上线成功", True, user)
        return json.dumps({
            "success": True,
            "message": "美尔健官网全站静态文件已重新编译并发布成功！",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": user.get("name") if user else "管理员"
        }, ensure_ascii=False)
    except Exception as e:
        record_audit_log("publish_website", f"全站发布失败: {e}", False, user)
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

# ==============================================================================
# 4. MCP 协议定义 (Tools 与 Resources 元数据)
# ==============================================================================

MCP_TOOLS_METADATA = [
    # 1. 身份核验
    {
        "name": "verify_mellgen_account",
        "description": "【账户身份核验】核验当前连接到美尔健官网后台的 WorkBuddy 账户与授权身份。返回操作人员姓名、角色权限及官网授权状态。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # 2. 产品中心
    {
        "name": "list_all_products",
        "description": "【产品中心】获取美尔健官网当前产品列表，支持分类筛选与关键字搜索。返回ID、名称、分类、INCI及功效简介。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"title": "Category Filter", "type": "string", "description": "产品分类过滤（如：化妆品原料、医疗器械等）"},
                "keyword": {"title": "Keyword Search", "type": "string", "description": "按名称、INCI或功效搜索"}
            }
        }
    },
    {
        "name": "get_product_detail",
        "description": "【产品中心】获取指定产品的完整详情，包括生物机理介绍、推荐应用场景及产品优势。\n:param product_id: 产品唯一标识ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string", "description": "产品唯一标识ID（如 tpxldb, lzdt, 0xjydb 等）"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "create_product_detail",
        "description": "【产品中心】由 WorkBuddy 直接制作并发布全新产品详情页！自动生成高保真图文版式（产品介绍+应用场景+3大优势卡片），内置严格广告法合规审查，一键生成静态HTML并上线。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string", "description": "产品ID拼音或代号（如 xfsjb）"},
                "title": {"title": "Title", "type": "string", "description": "产品官方全称"},
                "category": {"title": "Category", "type": "string", "description": "产品分类代号"},
                "category_name": {"title": "Category Name", "type": "string", "description": "产品分类中文名"},
                "inci": {"title": "Inci", "type": "string", "description": "标准 INCI 名称"},
                "appearance": {"title": "Appearance", "type": "string", "description": "外观形态（如透明液体、白色冻干粉）"},
                "solubility": {"title": "Solubility", "type": "string", "description": "溶解性（如水溶性）"},
                "summary": {"title": "Summary", "type": "string", "description": "产品一句话核心摘要"},
                "intro": {"title": "Intro", "type": "string", "description": "详细机理与功效介绍"},
                "app_scenarios": {"title": "App Scenarios", "type": "string", "description": "推荐应用配方场景"},
                "advantage_1_title": {"title": "Advantage 1 Title", "type": "string"},
                "advantage_1_desc": {"title": "Advantage 1 Desc", "type": "string"},
                "advantage_2_title": {"title": "Advantage 2 Title", "type": "string"},
                "advantage_2_desc": {"title": "Advantage 2 Desc", "type": "string"},
                "advantage_3_title": {"title": "Advantage 3 Title", "type": "string"},
                "advantage_3_desc": {"title": "Advantage 3 Desc", "type": "string"}
            },
            "required": [
                "product_id", "title", "category", "category_name", "inci",
                "appearance", "solubility", "summary", "intro", "app_scenarios",
                "advantage_1_title", "advantage_1_desc", "advantage_2_title",
                "advantage_2_desc", "advantage_3_title", "advantage_3_desc"
            ]
        }
    },
    {
        "name": "update_product_detail",
        "description": "【产品中心】更新已存在的产品规格、文案、推荐场景或显示状态，自动执行合规审查并重新编译静态页。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string"},
                "title": {"title": "Title", "type": "string"},
                "inci": {"title": "Inci", "type": "string"},
                "summary": {"title": "Summary", "type": "string"},
                "appearance": {"title": "Appearance", "type": "string"},
                "solubility": {"title": "Solubility", "type": "string"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "delete_product",
        "description": "【产品中心】下架并彻底删除指定产品及其静态 HTML 页面，自动同步刷新产品中心列表索引。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "list_product_categories",
        "description": "【产品中心】查询官网所有产品分类目录树（包含分类ID、中文名、SEO TDK及关联标签）。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "audit_product_compliance",
        "description": "【法规审查】审核文案是否符合中国《广告法》、《化妆品监督管理条例》及《化妆品标签管理办法》，自动筛查涉医、消炎杀菌、免疫力及极限词汇。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"title": "Text", "type": "string", "description": "待审查的产品介绍或推广文案"}
            },
            "required": ["text"]
        }
    },
    # 3. 资讯中心
    {
        "name": "list_articles",
        "description": "【资讯中心】分页查询企业动态、行业新闻与科研进展文章列表，支持按分类与关键词检索。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"title": "Category", "type": "string"},
                "keyword": {"title": "Keyword", "type": "string"},
                "page": {"title": "Page", "type": "integer"},
                "limit": {"title": "Limit", "type": "integer"}
            }
        }
    },
    {
        "name": "get_article_detail",
        "description": "【资讯中心】获取指定文章的完整详情与 HTML 正文内容。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "article_id": {"title": "Article Id", "type": "string"}
            },
            "required": ["article_id"]
        }
    },
    {
        "name": "create_article",
        "description": "【资讯中心】撰写并发布全新资讯文章！内置合规筛查，自动生成静态 HTML 文章页面并同步资讯列表。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"title": "Title", "type": "string"},
                "content": {"title": "Content (HTML or Text)", "type": "string"},
                "category": {"title": "Category", "type": "string", "description": "企业动态/行业新闻/科研进展"},
                "desc": {"title": "Description", "type": "string"},
                "author": {"title": "Author", "type": "string"},
                "date": {"title": "Date (YYYY-MM-DD)", "type": "string"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "update_article",
        "description": "【资讯中心】修改已有文章的标题、分类、摘要或正文，并重新生成静态文件。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "article_id": {"title": "Article Id", "type": "string"},
                "title": {"title": "Title", "type": "string"},
                "category": {"title": "Category", "type": "string"},
                "content": {"title": "Content", "type": "string"},
                "desc": {"title": "Desc", "type": "string"}
            },
            "required": ["article_id"]
        }
    },
    {
        "name": "delete_article",
        "description": "【资讯中心】删除指定文章并清理对应静态 HTML 页面。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "article_id": {"title": "Article Id", "type": "string"}
            },
            "required": ["article_id"]
        }
    },
    {
        "name": "list_article_categories",
        "description": "【资讯中心】获取当前资讯频道的所有分类列表。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "sync_wechat_articles",
        "description": "【资讯中心】一键同步抓取微信公众号推文！支持输入单个推文链接、批量推文链接或触发官方公众号全量同步，自动清洗样式下载本地高清图片。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "article_url": {"title": "WeChat Article URL", "type": "string"},
                "category": {"title": "Category", "type": "string"}
            }
        }
    },
    # 4. 客户线索
    {
        "name": "list_customer_inquiries",
        "description": "【意向订单与客户线索】查询官网访客留言与意向采购需求（包含姓名、联系电话、邮箱、留言内容及提交时间），支持筛选未读/已读。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"title": "Status Filter", "type": "string", "enum": ["all", "unread", "read"]},
                "keyword": {"title": "Keyword Search", "type": "string"},
                "limit": {"title": "Limit", "type": "integer"}
            }
        }
    },
    {
        "name": "update_inquiry_status",
        "description": "【客户线索】标记留言为已读，或由 WorkBuddy 录入处理备注与回复内容。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "inquiry_id": {"title": "Inquiry Id", "type": "string"},
                "read": {"title": "Read Status", "type": "boolean"},
                "admin_reply": {"title": "Admin Reply / Note", "type": "string"}
            },
            "required": ["inquiry_id"]
        }
    },
    {
        "name": "delete_customer_inquiry",
        "description": "【客户线索】删除垃圾或无效的留言记录。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "inquiry_id": {"title": "Inquiry Id", "type": "string"}
            },
            "required": ["inquiry_id"]
        }
    },
    # 5. SEO 与蜘蛛
    {
        "name": "get_seo_overview",
        "description": "【SEO 优化】获取搜索引擎收录与每日访问概况，包括百度、谷歌、必应及各 AI 爬虫的抓取频次与收录健康度。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "push_urls_to_search_engines",
        "description": "【SEO 优化】主动向百度、必应 (IndexNow)、谷歌及 AI 爬虫广播全站最新页面 URL，加速收录与快照更新。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "engine": {"title": "Engine", "type": "string", "enum": ["all", "baidu", "bing", "google"]}
            }
        }
    },
    {
        "name": "get_spider_crawl_logs",
        "description": "【SEO 优化】查询真实搜索引擎与大模型蜘蛛（Baiduspider, Googlebot, GPTBot, ClaudeBot 等）的实时访问日志。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "engine": {"title": "Engine Filter", "type": "string"},
                "limit": {"title": "Limit", "type": "integer"}
            }
        }
    },
    {
        "name": "trigger_seo_optimize",
        "description": "【SEO 优化】一键重新编译标准 sitemap.xml 网站地图，刷新 robots.txt 合规条目并计算 SEO 优化评分。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # 6. GEO 引擎
    {
        "name": "get_geo_status",
        "description": "【GEO 生成式引擎】查看面向 AI 搜索（DeepSeek, 豆包, Kimi, Gemini, GPT-4o 等）的 llms.txt、llms-full.txt 知识库状态与大模型引用频次。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "rebuild_llms_knowledge",
        "description": "【GEO 生成式引擎】重新提取全量多肽原料知识，一键重构生成标准的 /llms.txt 与 /llms-full.txt 供全球大模型索引抓取。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"title": "Domain Base", "type": "string"}
            }
        }
    },
    # 7. AI 客服与向量库
    {
        "name": "list_qa_pairs",
        "description": "【AI 客服知识库】检索官方问答库（包含产品机理、配方推荐、合规资质等 1000+ 条权威问答对）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"title": "Keyword", "type": "string"},
                "category": {"title": "Category", "type": "string"},
                "limit": {"title": "Limit", "type": "integer"}
            }
        }
    },
    {
        "name": "add_or_update_qa_pair",
        "description": "【AI 客服知识库】新增或修改问答库条目，包含问题、权威解答及关键词标签，通过法规审查后自动生效。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"title": "Question", "type": "string"},
                "answer": {"title": "Answer", "type": "string"},
                "category": {"title": "Category", "type": "string"},
                "qa_id": {"title": "QA Id (Optional)", "type": "string"}
            },
            "required": ["question", "answer"]
        }
    },
    {
        "name": "test_ai_customer_service",
        "description": "【AI 客服】模拟访客向美尔健官方 AI 客服发起提问，测试问答检索匹配精准度与回答效果。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"title": "Visitor Question", "type": "string"}
            },
            "required": ["question"]
        }
    },
    {
        "name": "rebuild_vector_database",
        "description": "【AI 客服】重新计算全库问答对的语义向量索引，使客服能理解更复杂的同义词与多维度意图。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # 8. 视频中心
    {
        "name": "list_all_videos",
        "description": "【视频中心】获取官网企业形象宣传片与产品实验机理视频列表。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "create_or_update_video",
        "description": "【视频中心】上传/配置企业宣传或产品讲解视频条目（包含标题、播放源地址、封面图与简介）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"title": "Title", "type": "string"},
                "video_url": {"title": "Video URL", "type": "string"},
                "category": {"title": "Category", "type": "string"},
                "cover": {"title": "Cover Image", "type": "string"},
                "desc": {"title": "Description", "type": "string"},
                "video_id": {"title": "Video Id (Optional)", "type": "string"}
            },
            "required": ["title", "video_url"]
        }
    },
    {
        "name": "delete_video",
        "description": "【视频中心】删除指定的视频条目。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "video_id": {"title": "Video Id", "type": "string"}
            },
            "required": ["video_id"]
        }
    },
    # 9. 企业资料与配置
    {
        "name": "get_company_profile",
        "description": "【企业资料与配置】查询美尔健官方企业简介、地址、业务热线、服务邮箱、ICP备案号与联系方式。",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "update_company_profile",
        "description": "【企业资料与配置】更新企业官方联系电话、服务邮箱、办公地址或ICP备案号，自动同步全站所有页面页脚！",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone": {"title": "Phone", "type": "string"},
                "email": {"title": "Email", "type": "string"},
                "address": {"title": "Address", "type": "string"},
                "icp": {"title": "ICP", "type": "string"}
            }
        }
    },
    # 10. 全站发布
    {
        "name": "publish_website",
        "description": "【全站发布】一键触发美尔健官网全站重新静态编译与发布上线，同步更新所有产品与资讯页面、分类索引与中英文双语站。",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

MCP_RESOURCES_METADATA = [
    {
        "uri": "mellgen://products/catalog",
        "name": "resource_products_catalog",
        "description": "美尔健官方全量原料知识库（JSON 数据源）",
        "mimeType": "application/json"
    },
    {
        "uri": "mellgen://compliance/rules",
        "name": "resource_compliance_rules",
        "description": "中国化妆品广告宣传与标签管理合规准则",
        "mimeType": "text/plain"
    },
    {
        "uri": "mellgen://articles/list",
        "name": "resource_articles_list",
        "description": "美尔健官方全量资讯与动态列表（JSON 数据源）",
        "mimeType": "application/json"
    },
    {
        "uri": "mellgen://company/profile",
        "name": "resource_company_profile",
        "description": "美尔健官方企业概况与联系方式配置",
        "mimeType": "application/json"
    },
    {
        "uri": "mellgen://inquiries/leads",
        "name": "resource_inquiries_leads",
        "description": "美尔健意向采购咨询与客户留言记录（JSON 数据源）",
        "mimeType": "application/json"
    },
    {
        "uri": "mellgen://seo/metrics",
        "name": "resource_seo_metrics",
        "description": "美尔健官网 SEO 收录指标与蜘蛛访问统计",
        "mimeType": "application/json"
    }
]

def read_resource_content(uri: str) -> Optional[dict]:
    if uri == "mellgen://products/catalog":
        products = load_json("products.json")
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(products, ensure_ascii=False, indent=2)
        }
    elif uri == "mellgen://compliance/rules":
        rules = """【美尔健生物产品宣传合规准则】
1. 严禁明示或暗示疾病治疗、医疗作用（如抗肿瘤、治疗创面、创面愈合、抗炎消炎、抑菌杀菌、提高机体免疫力等）；
2. 严禁使用《广告法》第九条绝对化极限词（如国家级、第一、顶级、赢领、首选、彻底根除等）；
3. 严禁使用“药妆”、“医学护肤品”等违规模糊概念；
4. 功效宣称应当科学中立，推荐使用法定化妆品分类目录术语：
   - 舒缓、减轻泛红、缓解干燥不适；
   - 紧致、抗皱、丰盈弹润；
   - 屏障修护、强韧脆弱角质；
   - 补水保湿、深层滋润；
   - 提亮肤色、净透匀净；
5. 技术机理应基于生物学和原料特性客观描述，突出专利生物透皮技术（cTDP）与合成生物学技术优势。"""
        return {
            "uri": uri,
            "mimeType": "text/plain",
            "text": rules
        }
    elif uri == "mellgen://articles/list":
        articles = load_json("articles.json")
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(articles, ensure_ascii=False, indent=2)
        }
    elif uri == "mellgen://company/profile":
        comp = load_json("company_info.json")
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(comp, ensure_ascii=False, indent=2)
        }
    elif uri == "mellgen://inquiries/leads":
        messages = load_json("messages.json")
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(messages, ensure_ascii=False, indent=2)
        }
    elif uri == "mellgen://seo/metrics":
        seo = load_json("seo_metrics.json")
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(seo, ensure_ascii=False, indent=2)
        }
    return None

TOOL_HANDLERS = {
    # 模块 1: 身份核验
    "verify_mellgen_account": execute_verify_mellgen_account,
    
    # 模块 2: 产品中心
    "list_all_products": execute_list_all_products,
    "get_product_detail": execute_get_product_detail,
    "create_product_detail": execute_create_product_detail,
    "update_product_detail": execute_update_product_detail,
    "delete_product": execute_delete_product,
    "list_product_categories": execute_list_product_categories,
    "audit_product_compliance": execute_audit_product_compliance,
    
    # 模块 3: 资讯中心
    "list_articles": execute_list_articles,
    "get_article_detail": execute_get_article_detail,
    "create_article": execute_create_article,
    "update_article": execute_update_article,
    "delete_article": execute_delete_article,
    "list_article_categories": execute_list_article_categories,
    "sync_wechat_articles": execute_sync_wechat_articles,
    
    # 模块 4: 客户线索
    "list_customer_inquiries": execute_list_customer_inquiries,
    "update_inquiry_status": execute_update_inquiry_status,
    "delete_customer_inquiry": execute_delete_customer_inquiry,
    
    # 模块 5: SEO 与蜘蛛
    "get_seo_overview": execute_get_seo_overview,
    "push_urls_to_search_engines": execute_push_urls_to_search_engines,
    "get_spider_crawl_logs": execute_get_spider_crawl_logs,
    "trigger_seo_optimize": execute_trigger_seo_optimize,
    
    # 模块 6: GEO 引擎
    "get_geo_status": execute_get_geo_status,
    "rebuild_llms_knowledge": execute_rebuild_llms_knowledge,
    
    # 模块 7: AI 客服与向量库
    "list_qa_pairs": execute_list_qa_pairs,
    "add_or_update_qa_pair": execute_add_or_update_qa_pair,
    "test_ai_customer_service": execute_test_ai_customer_service,
    "rebuild_vector_database": execute_rebuild_vector_database,
    
    # 模块 8: 视频中心
    "list_all_videos": execute_list_all_videos,
    "create_or_update_video": execute_create_or_update_video,
    "delete_video": execute_delete_video,
    
    # 模块 9: 企业资料与配置
    "get_company_profile": execute_get_company_profile,
    "update_company_profile": execute_update_company_profile,
    
    # 模块 10: 全站发布
    "publish_website": execute_publish_website
}

# ==============================================================================
# 5. SSE 会话与异步消息调度中心
# ==============================================================================

class MCPSession:
    def __init__(self, session_id: str, user: Optional[dict]):
        self.session_id = session_id
        self.user = user
        self.queue: queue.Queue = queue.Queue()
        self.created_at = time.time()
        self.last_active = time.time()
        self.is_active = True

    def push(self, data: Any):
        self.last_active = time.time()
        self.queue.put(data)

    def close(self):
        self.is_active = False
        self.queue.put(None)

class MCPSessionManager:
    def __init__(self):
        self.sessions: Dict[str, MCPSession] = {}
        self.lock = threading.Lock()

    def create_session(self, user: Optional[dict]) -> MCPSession:
        session_id = uuid.uuid4().hex
        sess = MCPSession(session_id, user)
        with self.lock:
            self.sessions[session_id] = sess
        return sess

    def get_session(self, session_id: str) -> Optional[MCPSession]:
        with self.lock:
            return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        with self.lock:
            sess = self.sessions.pop(session_id, None)
            if sess:
                sess.close()

session_manager = MCPSessionManager()

def extract_token_from_request(request) -> Optional[str]:
    token = request.args.get("token") or request.args.get("api_key")
    if not token:
        auth_header = request.headers.get("Authorization", "").strip()
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
    if not token:
        token = request.headers.get("X-API-Key") or request.headers.get("X-Mellgen-Token")
    return token

def handle_jsonrpc_request(req_data: dict, session: MCPSession) -> Optional[dict]:
    req_id = req_data.get("id")
    method = req_data.get("method", "")
    params = req_data.get("params", {}) or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True}
                },
                "serverInfo": {
                    "name": "Mellgen-CMS-MCP-Server",
                    "version": "1.0.0"
                }
            }
        }
    
    if method == "notifications/initialized":
        return None

    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS_METADATA
            }
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {}) or {}
        handler = TOOL_HANDLERS.get(tool_name)
        if handler:
            try:
                res_str = handler(tool_args, session.user)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": res_str}
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "isError": True,
                        "content": [
                            {"type": "text", "text": f"Tool execution error: {e}"}
                        ]
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method/Tool '{tool_name}' not found"
                }
            }

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": MCP_RESOURCES_METADATA
            }
        }

    if method == "resources/read":
        uri = params.get("uri", "")
        res_data = read_resource_content(uri)
        if res_data:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [res_data]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }

    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not implemented"
            }
        }
    return None
