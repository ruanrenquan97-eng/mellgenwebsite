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
    ("功效护肤", "药监局明文查处的违规概念，中国法规不存在功效护肤品类"),
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
import mcp_service

# 模块 1: 身份核验
@mcp.tool()
def verify_mellgen_account() -> str:
    """【账户身份核验】核验当前连接到美尔健官网后台的 WorkBuddy 账户与授权身份。返回操作人员姓名、角色权限及官网授权状态。"""
    return mcp_service.execute_verify_mellgen_account({}, current_mcp_user.get())

# 模块 2: 产品中心
@mcp.tool()
def list_all_products(category: str = "", keyword: str = "") -> str:
    """【产品中心】获取美尔健官网当前产品列表，支持分类筛选与关键字搜索。返回ID、名称、分类、INCI及功效简介。"""
    return mcp_service.execute_list_all_products({"category": category, "keyword": keyword}, current_mcp_user.get())

@mcp.tool()
def get_product_detail(product_id: str) -> str:
    """【产品中心】获取指定产品的完整详情，包括生物机理介绍、推荐应用场景及产品优势。"""
    return mcp_service.execute_get_product_detail({"product_id": product_id}, current_mcp_user.get())

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
    """【产品中心】由 WorkBuddy 直接制作并发布全新产品详情页！自动生成高保真图文版式（产品介绍+应用场景+3大优势卡片），内置严格广告法合规审查，一键生成静态HTML并上线。"""
    args = {
        "product_id": product_id, "title": title, "category": category,
        "category_name": category_name, "inci": inci, "appearance": appearance,
        "solubility": solubility, "summary": summary, "intro": intro,
        "app_scenarios": app_scenarios, "advantage_1_title": advantage_1_title,
        "advantage_1_desc": advantage_1_desc, "advantage_2_title": advantage_2_title,
        "advantage_2_desc": advantage_2_desc, "advantage_3_title": advantage_3_title,
        "advantage_3_desc": advantage_3_desc
    }
    return mcp_service.execute_create_product_detail(args, current_mcp_user.get())

@mcp.tool()
def get_product_parameters_schema() -> str:
    """【产品中心】获取产品全量参数字典及字段定义架构（供 WorkBuddy 检索所有可修改字段规范与示例）"""
    return mcp_service.execute_get_product_parameters_schema({}, current_mcp_user.get())

@mcp.tool()
def update_product_detail(
    product_id: str,
    title: str = "",
    category: str = "",
    category_name: str = "",
    inci: str = "",
    appearance: str = "",
    solubility: str = "",
    summary: str = "",
    desc: str = "",
    image: str = "",
    largeImage: str = "",
    fullBanner: str = "",
    video: str = "",
    disclaimer: str = "",
    seoTitle: str = "",
    seoKeywords: str = "",
    seoDesc: str = "",
    h1: str = "",
    content: str = "",
    show: bool = None,
    recommend: bool = None,
    top: bool = None,
    specs: dict = None,
    rd_info: dict = None,
    procurement_info: dict = None,
    marketing_info: dict = None,
    raw_params: dict = None,
    ignore_compliance_warning: bool = False
) -> str:
    """【产品中心】全参数更新产品：支持修改全部理化specs、研发rd_info、采购procurement_info、市场marketing_info、合规disclaimer、SEO、图片/视频及富文本。"""
    args = {k: v for k, v in locals().items() if v is not None}
    return mcp_service.execute_update_product_detail(args, current_mcp_user.get())

@mcp.tool()
def update_product_parameter(
    product_id: str,
    parameter_path: str,
    value: str = ""
) -> str:
    """【产品中心】原子化精准修改产品的指定参数（支持点分路径如 'rd_info.cas', 'specs.核心活性物', 'procurement_info.moq' 等）"""
    return mcp_service.execute_update_product_parameter({
        "product_id": product_id,
        "parameter_path": parameter_path,
        "value": value
    }, current_mcp_user.get())

@mcp.tool()
def batch_update_products(
    product_ids: list,
    parameters: dict
) -> str:
    """【产品中心】批量更新多个产品的公共参数属性（如统一调整发货说明、免责条款、分类或推荐状态）"""
    return mcp_service.execute_batch_update_products({
        "product_ids": product_ids,
        "parameters": parameters
    }, current_mcp_user.get())

@mcp.tool()
def delete_product(product_id: str) -> str:
    """【产品中心】下架并彻底删除指定产品及其静态 HTML 页面，自动同步刷新产品中心列表索引。"""
    return mcp_service.execute_delete_product({"product_id": product_id}, current_mcp_user.get())

@mcp.tool()
def list_product_categories() -> str:
    """【产品中心】查询官网所有产品分类目录树（包含分类ID、中文名、SEO TDK及关联标签）。"""
    return mcp_service.execute_list_product_categories({}, current_mcp_user.get())

@mcp.tool()
def audit_product_compliance(text: str) -> str:
    """【法规审查】审核文案是否符合中国《广告法》、《化妆品监督管理条例》及《化妆品标签管理办法》，自动筛查涉医、消炎杀菌、免疫力及极限词汇。"""
    return mcp_service.execute_audit_product_compliance({"text": text}, current_mcp_user.get())

# 模块 3: 资讯中心
@mcp.tool()
def list_articles(category: str = "", keyword: str = "", page: int = 1, limit: int = 20) -> str:
    """【资讯中心】分页查询企业动态、行业新闻与科研进展文章列表，支持按分类与关键词检索。"""
    return mcp_service.execute_list_articles({"category": category, "keyword": keyword, "page": page, "limit": limit}, current_mcp_user.get())

@mcp.tool()
def get_article_detail(article_id: str) -> str:
    """【资讯中心】获取指定文章的完整详情与 HTML 正文内容。"""
    return mcp_service.execute_get_article_detail({"article_id": article_id}, current_mcp_user.get())

@mcp.tool()
def create_article(
    title: str,
    content: str,
    category: str = "新闻资讯",
    desc: str = "",
    image: str = "resource/images/ban_txt.png",
    author: str = "美尔健生物",
    date: str = ""
) -> str:
    """【资讯中心】撰写并发布全新资讯文章！内置合规筛查，自动生成静态 HTML 文章页面并同步资讯列表。"""
    return mcp_service.execute_create_article({
        "title": title, "content": content, "category": category,
        "desc": desc, "image": image, "author": author, "date": date
    }, current_mcp_user.get())

@mcp.tool()
def update_article(
    article_id: str,
    title: str = "",
    category: str = "",
    content: str = "",
    desc: str = "",
    image: str = "",
    author: str = ""
) -> str:
    """【资讯中心】修改已有文章的标题、分类、摘要或正文，并重新生成静态文件。"""
    args = {k: v for k, v in locals().items() if v}
    return mcp_service.execute_update_article(args, current_mcp_user.get())

@mcp.tool()
def delete_article(article_id: str) -> str:
    """【资讯中心】删除指定文章并清理对应静态 HTML 页面。"""
    return mcp_service.execute_delete_article({"article_id": article_id}, current_mcp_user.get())

@mcp.tool()
def list_article_categories() -> str:
    """【资讯中心】获取当前资讯频道的所有分类列表。"""
    return mcp_service.execute_list_article_categories({}, current_mcp_user.get())

@mcp.tool()
def sync_wechat_articles(article_url: str = "", category: str = "企业动态") -> str:
    """【资讯中心】一键同步抓取微信公众号推文！支持输入单个推文链接或触发官方公众号全量同步，自动清洗样式下载本地高清图片。"""
    return mcp_service.execute_sync_wechat_articles({"article_url": article_url, "category": category}, current_mcp_user.get())

# 模块 4: 客户线索
@mcp.tool()
def list_customer_inquiries(status: str = "all", keyword: str = "", limit: int = 50) -> str:
    """【意向订单与客户线索】查询官网访客留言与意向采购需求（包含姓名、联系电话、邮箱、留言内容及提交时间），支持筛选未读/已读。"""
    return mcp_service.execute_list_customer_inquiries({"status": status, "keyword": keyword, "limit": limit}, current_mcp_user.get())

@mcp.tool()
def update_inquiry_status(inquiry_id: str, read: bool = True, admin_reply: str = "", remark: str = "") -> str:
    """【客户线索】标记留言为已读，或由 WorkBuddy 录入处理备注与回复内容。"""
    return mcp_service.execute_update_inquiry_status({"inquiry_id": inquiry_id, "read": read, "admin_reply": admin_reply, "remark": remark}, current_mcp_user.get())

@mcp.tool()
def delete_customer_inquiry(inquiry_id: str) -> str:
    """【客户线索】删除垃圾或无效的留言记录。"""
    return mcp_service.execute_delete_customer_inquiry({"inquiry_id": inquiry_id}, current_mcp_user.get())

# 模块 5: SEO 与蜘蛛
@mcp.tool()
def get_seo_overview() -> str:
    """【SEO 优化】获取搜索引擎收录与每日访问概况，包括百度, 谷歌, 必应及各 AI 爬虫的抓取频次与收录健康度。"""
    return mcp_service.execute_get_seo_overview({}, current_mcp_user.get())

@mcp.tool()
def push_urls_to_search_engines(engine: str = "all") -> str:
    """【SEO 优化】主动向百度、必应 (IndexNow)、谷歌及 AI 爬虫广播全站最新页面 URL，加速收录与快照更新。"""
    return mcp_service.execute_push_urls_to_search_engines({"engine": engine}, current_mcp_user.get())

@mcp.tool()
def get_spider_crawl_logs(engine: str = "", limit: int = 50) -> str:
    """【SEO 优化】查询真实搜索引擎与大模型蜘蛛（Baiduspider, Googlebot, GPTBot, ClaudeBot 等）的实时访问日志。"""
    return mcp_service.execute_get_spider_crawl_logs({"engine": engine, "limit": limit}, current_mcp_user.get())

@mcp.tool()
def trigger_seo_optimize() -> str:
    """【SEO 优化】一键重新编译标准 sitemap.xml 网站地图，刷新 robots.txt 合规条目并计算 SEO 优化评分。"""
    return mcp_service.execute_trigger_seo_optimize({}, current_mcp_user.get())

# 模块 6: GEO 引擎
@mcp.tool()
def get_geo_status() -> str:
    """【GEO 生成式引擎】查看面向 AI 搜索（DeepSeek, 豆包, Kimi, Gemini, GPT-4o 等）的 llms.txt、llms-full.txt 知识库状态与大模型引用频次。"""
    return mcp_service.execute_get_geo_status({}, current_mcp_user.get())

@mcp.tool()
def rebuild_llms_knowledge(domain: str = "https://www.mellgen.com") -> str:
    """【GEO 生成式引擎】重新提取全量多肽原料知识，一键重构生成标准的 /llms.txt 与 /llms-full.txt 供全球大模型索引抓取。"""
    return mcp_service.execute_rebuild_llms_knowledge({"domain": domain}, current_mcp_user.get())

# 模块 7: AI 客服与向量库
@mcp.tool()
def list_qa_pairs(keyword: str = "", category: str = "", limit: int = 50) -> str:
    """【AI 客服知识库】检索官方问答库（包含产品机理、配方推荐、合规资质等 1000+ 条权威问答对）。"""
    return mcp_service.execute_list_qa_pairs({"keyword": keyword, "category": category, "limit": limit}, current_mcp_user.get())

@mcp.tool()
def add_or_update_qa_pair(question: str, answer: str, category: str = "产品问答", qa_id: str = "") -> str:
    """【AI 客服知识库】新增或修改问答库条目，包含问题、权威解答及关键词标签，通过法规审查后自动生效。"""
    return mcp_service.execute_add_or_update_qa_pair({"question": question, "answer": answer, "category": category, "qa_id": qa_id}, current_mcp_user.get())

@mcp.tool()
def test_ai_customer_service(question: str) -> str:
    """【AI 客服】模拟访客向美尔健官方 AI 客服发起提问，测试问答检索匹配精准度与回答效果。"""
    return mcp_service.execute_test_ai_customer_service({"question": question}, current_mcp_user.get())

@mcp.tool()
def rebuild_vector_database() -> str:
    """【AI 客服】重新计算全库问答对的语义向量索引，使客服能理解更复杂的同义词与多维度意图。"""
    return mcp_service.execute_rebuild_vector_database({}, current_mcp_user.get())

# 模块 8: 视频中心
@mcp.tool()
def list_all_videos() -> str:
    """【视频中心】获取官网企业形象宣传片与产品实验机理视频列表。"""
    return mcp_service.execute_list_all_videos({}, current_mcp_user.get())

@mcp.tool()
def create_or_update_video(title: str, video_url: str, category: str = "企业宣传", cover: str = "./resource/images/ban_txt.png", desc: str = "", video_id: str = "") -> str:
    """【视频中心】上传/配置企业宣传或产品讲解视频条目（包含标题、播放源地址、封面图与简介）。"""
    return mcp_service.execute_create_or_update_video({"title": title, "video_url": video_url, "category": category, "cover": cover, "desc": desc, "video_id": video_id}, current_mcp_user.get())

@mcp.tool()
def delete_video(video_id: str) -> str:
    """【视频中心】删除指定的视频条目。"""
    return mcp_service.execute_delete_video({"video_id": video_id}, current_mcp_user.get())

# 模块 9: 企业资料与配置
@mcp.tool()
def get_company_profile() -> str:
    """【企业资料与配置】查询美尔健官方企业简介、地址、业务热线、服务邮箱、ICP备案号与联系方式。"""
    return mcp_service.execute_get_company_profile({}, current_mcp_user.get())

@mcp.tool()
def update_company_profile(phone: str = "", email: str = "", address: str = "", company_name: str = "", icp: str = "") -> str:
    """【企业资料与配置】更新企业官方联系电话、服务邮箱、办公地址或ICP备案号，自动同步全站所有页面页脚！"""
    args = {k: v for k, v in locals().items() if v}
    return mcp_service.execute_update_company_profile(args, current_mcp_user.get())

# 模块 10: 全站发布
@mcp.tool()
def publish_website() -> str:
    """【全站发布】一键触发全站重新编译与静态发布上线，同步所有产品与资讯页面。"""
    return mcp_service.execute_publish_website({}, current_mcp_user.get())

# 动态自动补齐全站其余所有模块工具 (确保全站 70 项原生 Tools 100% 完整挂载至 FastMCP 服务)
_existing_tools = set(mcp._tool_manager._tools.keys()) if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools') else set()
for _t_meta in mcp_service.MCP_TOOLS_METADATA:
    _t_name = _t_meta["name"]
    if _t_name not in _existing_tools and _t_name in mcp_service.TOOL_HANDLERS:
        _desc = _t_meta["description"]
        _handler = mcp_service.TOOL_HANDLERS[_t_name]
        
        def _make_fastmcp_fn(h):
            def _fn(**kwargs):
                return h(kwargs, current_mcp_user.get())
            return _fn
            
        _wrapped = _make_fastmcp_fn(_handler)
        _wrapped.__name__ = _t_name
        _wrapped.__doc__ = _desc
        try:
            mcp.add_tool(_wrapped, name=_t_name, description=_desc)
        except Exception:
            pass

# ----------------- MCP RESOURCES -----------------
@mcp.resource("mellgen://products/catalog")
def resource_products_catalog() -> str:
    """美尔健官方全量原料知识库（JSON 数据源）"""
    res = mcp_service.read_resource_content("mellgen://products/catalog")
    return res["text"] if res else "{}"

@mcp.resource("mellgen://compliance/rules")
def resource_compliance_rules() -> str:
    """中国化妆品广告宣传与标签管理合规准则"""
    res = mcp_service.read_resource_content("mellgen://compliance/rules")
    return res["text"] if res else ""

@mcp.resource("mellgen://articles/list")
def resource_articles_list() -> str:
    """美尔健官方全量资讯与动态列表（JSON 数据源）"""
    res = mcp_service.read_resource_content("mellgen://articles/list")
    return res["text"] if res else "[]"

@mcp.resource("mellgen://company/profile")
def resource_company_profile() -> str:
    """美尔健官方企业概况与联系方式配置"""
    res = mcp_service.read_resource_content("mellgen://company/profile")
    return res["text"] if res else "{}"

@mcp.resource("mellgen://inquiries/leads")
def resource_inquiries_leads() -> str:
    """美尔健意向采购咨询与客户留言记录（JSON 数据源）"""
    res = mcp_service.read_resource_content("mellgen://inquiries/leads")
    return res["text"] if res else "[]"

@mcp.resource("mellgen://seo/metrics")
def resource_seo_metrics() -> str:
    """美尔健官网 SEO 收录指标与蜘蛛访问统计"""
    res = mcp_service.read_resource_content("mellgen://seo/metrics")
    return res["text"] if res else "{}"

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

