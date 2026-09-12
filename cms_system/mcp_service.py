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

def execute_publish_website(args: dict, user: Optional[dict]) -> str:
    try:
        generator.build_all()
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
    {
        "name": "verify_mellgen_account",
        "description": "【账户身份核验】核验当前连接到美尔健官网后台的 WorkBuddy 账户与授权身份。返回当前登录操作人员的用户名、姓名、权限角色以及官网连接状态。",
        "inputSchema": {
            "type": "object",
            "title": "verify_mellgen_accountArguments",
            "properties": {}
        }
    },
    {
        "name": "list_all_products",
        "description": "获取美尔健官网当前所有产品的列表，包含产品ID、名称、分类、INCI及功效简介。",
        "inputSchema": {
            "type": "object",
            "title": "list_all_productsArguments",
            "properties": {}
        }
    },
    {
        "name": "get_product_detail",
        "description": "获取指定产品的完整详情，包括生物机理介绍、推荐应用场景及产品优势。\n:param product_id: 产品唯一标识ID（如 tpxldb, lzdt, 0xjydb 等）",
        "inputSchema": {
            "type": "object",
            "title": "get_product_detailArguments",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "audit_product_compliance",
        "description": "审核产品文案是否符合中国《广告法》、《化妆品监督管理条例》及《化妆品标签管理办法》。自动筛查涉医、疾病、消炎、杀菌、免疫力及绝对化极限词汇。\n:param text: 待审核的产品介绍、功效文案或宣传语",
        "inputSchema": {
            "type": "object",
            "title": "audit_product_complianceArguments",
            "properties": {
                "text": {"title": "Text", "type": "string"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "create_product_detail",
        "description": "由 WorkBuddy 直接在美尔健官网后台【制作并发布】全新产品详情页！自动生成高保真图文版式（产品介绍+应用场景+3大核心优势卡片），并生成静态HTML。",
        "inputSchema": {
            "type": "object",
            "title": "create_product_detailArguments",
            "properties": {
                "product_id": {"title": "Product Id", "type": "string"},
                "title": {"title": "Title", "type": "string"},
                "category": {"title": "Category", "type": "string"},
                "category_name": {"title": "Category Name", "type": "string"},
                "inci": {"title": "Inci", "type": "string"},
                "appearance": {"title": "Appearance", "type": "string"},
                "solubility": {"title": "Solubility", "type": "string"},
                "summary": {"title": "Summary", "type": "string"},
                "intro": {"title": "Intro", "type": "string"},
                "app_scenarios": {"title": "App Scenarios", "type": "string"},
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
        "name": "publish_website",
        "description": "一键触发全站重新编译与静态发布上线，同步所有产品与资讯页面。",
        "inputSchema": {
            "type": "object",
            "title": "publish_websiteArguments",
            "properties": {}
        }
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
    return None

TOOL_HANDLERS = {
    "verify_mellgen_account": execute_verify_mellgen_account,
    "list_all_products": execute_list_all_products,
    "get_product_detail": execute_get_product_detail,
    "audit_product_compliance": execute_audit_product_compliance,
    "create_product_detail": execute_create_product_detail,
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
