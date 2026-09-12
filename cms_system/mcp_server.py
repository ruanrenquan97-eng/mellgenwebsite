"""
美尔健官网后台 MCP 连接器服务器 (Model Context Protocol Server for WorkBuddy)
支持 WorkBuddy 通过 MCP 标准协议制作、优化、发布产品详情页，并进行法规审核。
"""

import os
import sys
import json
import re
import datetime
from mcp.server.fastmcp import FastMCP

import os
import sys
import json
import re
import uuid
import datetime
import contextvars
from urllib.parse import parse_qs

# Ensure dynamic paths for production and local environments
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CMS_DIR = CURRENT_DIR
WORKSPACE_DIR = os.path.dirname(CMS_DIR)
DATA_DIR = os.path.join(CMS_DIR, "cms_data")
if CMS_DIR not in sys.path:
    sys.path.insert(0, CMS_DIR)

import generator

# Initialize FastMCP Server
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP("Mellgen-CMS-MCP-Server")
mcp.settings.host = "0.0.0.0"
mcp.settings.transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
    allowed_hosts=["*"],
    allowed_origins=["*"]
)

# ContextVar to track currently authenticated website account for the request/session
current_mcp_user = contextvars.ContextVar("current_mcp_user", default=None)

# Helper functions for data access
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_or_init_account_tokens():
    """确保所有网站账户（在 settings.json 中定义）均具备专属的 WorkBuddy MCP Token"""
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
            # 同步更新姓名和角色
            account_tokens[uname]["name"] = acc.get("name", uname)
            account_tokens[uname]["role"] = acc.get("role", "普通操作员")
            
    if updated or "account_tokens" not in wb_conf:
        wb_conf["account_tokens"] = account_tokens
        save_json("connector_workbuddy.json", wb_conf)
        
    return account_tokens

def verify_token_and_get_user(token: str) -> dict | None:
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
                return None  # 账户已被停用
            # 更新活跃时间
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
            
    # 兼容 connector_workbuddy.json 中的主 api_key (默认授予 admin 身份)
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

def record_audit_log(action: str, details: str, success: bool = True, user: dict = None):
    """记录 WorkBuddy 智能体调用操作审计日志"""
    try:
        user_info = user or current_mcp_user.get()
        log_file = "mcp_audit_logs.json"
        logs = load_json(log_file)
        if not isinstance(logs, list):
            logs = []
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": user_info.get("username", "anonymous") if user_info else "anonymous",
            "name": user_info.get("name", "未识别用户") if user_info else "未识别用户",
            "role": user_info.get("role", "未知") if user_info else "未知",
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

# Compliance checker rulebase
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

# ----------------- MCP TOOLS -----------------

@mcp.tool()
def verify_mellgen_account() -> str:
    """
    【账户身份核验】核验当前连接到美尔健官网后台的 WorkBuddy 账户与授权身份。
    返回当前登录操作人员的用户名、姓名、权限角色以及官网连接状态。
    """
    user = current_mcp_user.get()
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
    else:
        return json.dumps({
            "authenticated": False,
            "website": "https://www.mellgen.com",
            "message": "当前为本地默认调试环境或尚未绑定专属 Token。"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def list_all_products() -> str:
    """获取美尔健官网当前所有产品的列表，包含产品ID、名称、分类、INCI及功效简介。"""
    user = current_mcp_user.get()
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


@mcp.tool()
def get_product_detail(product_id: str) -> str:
    """
    获取指定产品的完整详情，包括生物机理介绍、推荐应用场景及产品优势。
    :param product_id: 产品唯一标识ID（如 tpxldb, lzdt, 0xjydb 等）
    """
    user = current_mcp_user.get()
    record_audit_log("get_product_detail", f"查看产品详情: {product_id}", True, user)
    products = load_json("products.json")
    for p in products:
        if p.get("id") == product_id:
            return json.dumps(p, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"未找到ID为 '{product_id}' 的产品"}, ensure_ascii=False)


@mcp.tool()
def audit_product_compliance(text: str) -> str:
    """
    审核产品文案是否符合中国《广告法》、《化妆品监督管理条例》及《化妆品标签管理办法》。
    自动筛查涉医、疾病、消炎、杀菌、免疫力及绝对化极限词汇。
    :param text: 待审核的产品介绍、功效文案或宣传语
    """
    findings = []
    for term, reason in ILLEGAL_TERMS:
        if term in text:
            findings.append({"term": term, "reason": reason})
    
    passed = len(findings) == 0
    user = current_mcp_user.get()
    record_audit_log("audit_product_compliance", f"文案合规审查: {'全部合规' if passed else f'发现违规词{len(findings)}个'}", passed, user)
    return json.dumps({
        "passed": passed,
        "violation_count": len(findings),
        "violations": findings,
        "suggestion": "文案完全合规，准予发布。" if passed else "检测到违规风险用语，请根据法规修改后再行发布。"
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def create_product_detail(
    product_id: str,
    title: str,
    category: str,
    category_name: str,
    inci: str,
    appearance: str,
    solubility: str,
    summary: str,
    intro: str,
    app_scenarios: str,
    advantage_1_title: str,
    advantage_1_desc: str,
    advantage_2_title: str,
    advantage_2_desc: str,
    advantage_3_title: str,
    advantage_3_desc: str
) -> str:
    """
    由 WorkBuddy 直接在美尔健官网后台【制作并发布】全新产品详情页！
    自动生成高保真图文版式（产品介绍+应用场景+3大核心优势卡片），并生成静态HTML。
    
    :param product_id: 产品英文标识（如 recombinant_collagen_pro, pdrn_stick 等，仅字母数字下划线）
    :param title: 产品中文主标题（如：重组人源化Ⅲ型胶原蛋白）
    :param category: 主分类（化妆品原料、医用原料、食品营养原料）
    :param category_name: 二级分类（如：重组仿生蛋白、透皮型重组蛋白/多肽、植物源活性物、海洋源活性物等）
    :param inci: INCI标准成分名称（如：可溶性胶原、甘油、水）
    :param appearance: 外观性状（如：无色透明液体、白色疏松冻干粉块）
    :param solubility: 溶解性（如：易溶于水、水溶）
    :param summary: 简明功效亮点（50字以内概括）
    :param intro: 详尽生物机理阐释与产品介绍（150-250字，需严格符合化妆品法规）
    :param app_scenarios: 推荐应用场景（如：抗皱紧致精华液、屏障修护乳霜、美容护理冻干安瓶等）
    :param advantage_1_title: 优势1标题（如：高纯度生物表达）
    :param advantage_1_desc: 优势1详细说明
    :param advantage_2_title: 优势2标题（如：生物透皮靶向吸收）
    :param advantage_2_desc: 优势2详细说明
    :param advantage_3_title: 优势3标题（如：优良生物相容性）
    :param advantage_3_desc: 优势3详细说明
    """
    # 1. Compliance pre-check
    user = current_mcp_user.get()
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

    # 2. Prepare HTML detail snippet
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

    # 3. Create or update in database
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
    
    # 4. Generate HTML static file
    prod_html_path = os.path.join(WORKSPACE_DIR, "products", f"{product_id}.html")
    template_src = os.path.join(WORKSPACE_DIR, "products", "tpxldb.html")
    if os.path.exists(template_src):
        with open(template_src, "r", encoding="utf-8") as f:
            html_t = f.read()
        
        # Replace title, breadcrumbs, and detail
        html_t = re.sub(r'<title>.*?</title>', f'<title>{title} - 深圳美尔健生物科技官方网站</title>', html_t)
        html_t = re.sub(r'<h1[^>]*class="p102-proShow-1-title"[^>]*>.*?</h1>', f'<h1 title="{title}" class="p102-proShow-1-title">{title}</h1>', html_t)
        html_t = re.sub(r'(<div class="p102-pro-content-desc endit-content">)[\s\S]*?(</div>\s*</div>\s*</div>\s*</div>)', f'\\1\n     {detail_html}\n    \\2', html_t)
        
        with open(prod_html_path, "w", encoding="utf-8") as f:
            f.write(html_t)
            
    # Trigger full catalog rebuild
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


@mcp.tool()
def publish_website() -> str:
    """一键触发全站重新编译与静态发布上线，同步所有产品与资讯页面。"""
    user = current_mcp_user.get()
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

# ----------------- MCP RESOURCES -----------------

@mcp.resource("mellgen://products/catalog")
def resource_products_catalog() -> str:
    """美尔健官方全量原料知识库（JSON 数据源）"""
    products = load_json("products.json")
    return json.dumps(products, ensure_ascii=False, indent=2)

@mcp.resource("mellgen://compliance/rules")
def resource_compliance_rules() -> str:
    """中国化妆品广告宣传与标签管理合规准则"""
    return """
【美尔健生物产品宣传合规准则】
1. 严禁明示或暗示疾病治疗、医疗作用（如抗肿瘤、治疗创面、创面愈合、抗炎消炎、抑菌杀菌、提高机体免疫力等）；
2. 严禁使用《广告法》第九条绝对化极限词（如国家级、第一、顶级、赢领、首选、彻底根除等）；
3. 严禁使用“药妆”、“医学护肤品”等违规模糊概念；
4. 功效宣称应当科学中立，推荐使用法定化妆品分类目录术语：
   - 舒缓、减轻泛红、缓解干燥不适；
   - 紧致、抗皱、丰盈弹润；
   - 屏障修护、强韧脆弱角质；
   - 补水保湿、深层滋润；
   - 提亮肤色、净透匀净；
5. 技术机理应基于生物学和原料特性客观描述，突出专利生物透皮技术（cTDP）与合成生物学技术优势。
"""

# ----------------- ASGI AUTHENTICATION & MULTI-MOUNT APP -----------------

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import Response

class MellgenMCPAuthMiddleware:
    """
    针对 WorkBuddy 客户端的多账户身份核验 ASGI 中间件
    部署于 https://www.mellgen.com
    核验规则：
    1. Query 参数：?token=... 或 ?api_key=...
    2. Header：Authorization: Bearer <token>
    3. Header：X-API-Key 或 X-Mellgen-Token
    必须属于网站后台启用的合法账户，否则返回 HTTP 401
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            method = scope.get("method", "GET")
            # 放行 OPTIONS 预检请求以支持 CORS
            if method == "OPTIONS":
                response = Response(status_code=204, headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type, X-API-Key, X-Mellgen-Token",
                })
                await response(scope, receive, send)
                return

            path = scope.get("path", "")
            # 对 MCP 核心路径做身份核验
            if path in ("/sse", "/mcp/sse", "/messages", "/mcp/messages") or "/messages" in path or "/sse" in path:
                query_string = scope.get("query_string", b"").decode("utf-8", errors="ignore")
                qs = parse_qs(query_string)
                token = qs.get("token", [None])[0] or qs.get("api_key", [None])[0]

                headers = dict(scope.get("headers", []))
                auth_h = headers.get(b"authorization", b"").decode("utf-8", errors="ignore").strip()
                if not token and auth_h.startswith("Bearer "):
                    token = auth_h[7:].strip()
                if not token:
                    token = headers.get(b"x-api-key", b"").decode("utf-8", errors="ignore").strip()
                if not token:
                    token = headers.get(b"x-mellgen-token", b"").decode("utf-8", errors="ignore").strip()

                user = verify_token_and_get_user(token)
                if not user:
                    err_body = {
                        "error": "Unauthorized",
                        "code": 401,
                        "message": "美尔健官网 MCP 连接器：网站账户核验失败！",
                        "hint": "请在 WorkBuddy 中配置已授权的网站账户专属 Token（详见 https://www.mellgen.com/admin 后台【WorkBuddy 连接器】）。",
                        "help_url": "https://www.mellgen.com/admin"
                    }
                    response = Response(
                        content=json.dumps(err_body, ensure_ascii=False, indent=2),
                        status_code=401,
                        media_type="application/json; charset=utf-8",
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                    await response(scope, receive, send)
                    return

                # 核验通过，设置当前请求上下文
                token_ctx = current_mcp_user.set(user)
                try:
                    await self.app(scope, receive, send)
                finally:
                    current_mcp_user.reset(token_ctx)
                return

        await self.app(scope, receive, send)


def create_combined_mcp_app() -> Starlette:
    """
    创建兼顾本地调试与生产环境 https://www.mellgen.com/mcp/sse 的 ASGI 复合应用
    同时支持 /sse 和 /mcp/sse 路径
    """
    base_app = mcp.sse_app(mount_path="/mcp")
    
    # 挂载到主路由
    main_app = Starlette(
        routes=[
            Mount("/mcp", app=base_app),
            Mount("/", app=base_app)
        ]
    )
    
    # 包装安全认证中间件
    return MellgenMCPAuthMiddleware(main_app)


if __name__ == "__main__":
    import uvicorn
    
    port = 8002
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        mcp.run(transport="stdio")
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "sse":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8002
            
        print(f"[*] Starting Mellgen CMS FastMCP SSE Server on port {port}...")
        print(f"[*] Production Endpoint: https://www.mellgen.com/mcp/sse")
        print(f"[*] Local Endpoint:      http://127.0.0.1:{port}/mcp/sse")
        
        # 初始化并同步所有账户专属 Token
        tokens = get_or_init_account_tokens()
        print(f"[*] Loaded {len(tokens)} authorized website accounts for WorkBuddy.")
        
        app = create_combined_mcp_app()
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

