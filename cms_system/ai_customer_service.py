# -*- coding: utf-8 -*-
"""
美尔健智能客服核心引擎 (AI Customer Service Engine)
实现：
1. 知识库检索与置信度匹配 (Q&A Database + Products Knowledge)
2. 双层防幻觉控制 (Grounded Retrieval + Strict System Prompt)
3. 优雅转人工兜底 (当AI回答不上来或用户索要人工时，自动输出电话与微信二维码)
4. 支持兼容 OpenAI 格式的大模型接入 (DeepSeek / 通义千问 / 智谱 / Kimi 等)
"""

import os
import json
import re
import datetime
import requests

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")

# 默认客服与兜底配置
DEFAULT_CONFIG = {
    "enabled": True,
    "service_name": "小美客服",
    "api_key": "",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "temperature": 0.2,
    "fallback_phone": "186-9197-8530 / 0755-82926499",
    "fallback_wechat_qrcode": "/resource/images/98118d91c8d74d289a05f86fc2519ad7_6.jpg",
    "wechat_name": "美尔健专属客户经理",
    "working_hours": "工作日 09:00 - 18:00",
    "welcome_message": "您好！我是美尔健生物科技官方AI顾问小美，专注为您解答生物透皮肽技术、高纯重组蛋白原料、资质质检(COA)、起订量及免费试样申请等业务。请问有什么可以帮您？",
    "preset_questions": [
        "重组胶原蛋白有哪些规格与型号？",
        "透皮纤连蛋白可以提供COA检测报告吗？",
        "起订量(MOQ)是多少？如何申领免费样品？",
        "你们拥有多少项核心发明专利？",
        "联系客户经理与技术支持"
    ],
    "strict_anti_hallucination": True
}

def load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default if default is not None else []
    return default if default is not None else []

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_ai_service_config():
    """获取智能客服系统配置"""
    settings = load_json("settings.json", {})
    cfg = settings.get("ai_customer_service", {})
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged

def save_ai_service_config(new_cfg):
    """保存智能客服系统配置"""
    settings = load_json("settings.json", {})
    current = settings.get("ai_customer_service", dict(DEFAULT_CONFIG))
    current.update(new_cfg)
    settings["ai_customer_service"] = current
    save_json("settings.json", settings)
    return current

def build_contact_card(config=None, title=None):
    """构建标准客户经理对接卡片数据"""
    if not config:
        config = get_ai_service_config()
    
    phone_raw = config.get("fallback_phone", DEFAULT_CONFIG["fallback_phone"])
    # 拆分多个电话以便一键拨号
    phones = [p.strip() for p in re.split(r'[/,，、|]', phone_raw) if p.strip()]
    if not phones:
        phones = ["186-9197-8530", "0755-82926499"]
        
    return {
        "title": title or "美尔健客户经理对接通道",
        "phones": phones,
        "phone_display": phone_raw,
        "wechat_qrcode": config.get("fallback_wechat_qrcode", DEFAULT_CONFIG["fallback_wechat_qrcode"]),
        "wechat_name": config.get("wechat_name", "美尔健专属客户经理"),
        "working_hours": config.get("working_hours", "工作日 09:00 - 18:00"),
        "tips": "资深研发工程师与客户经理将为您提供一对一原料选型指导、定制方案与商务试样支持"
    }

def log_visitor_question(question, answer, source, needs_human=False, session_id="", turn_count=1, client_ip="", user_agent="", matched_qa=None):
    """
    收集并记录前台访客咨询提问与AI答复，方便后台运营人员挖掘潜在需求、补全新知识
    """
    question = (question or "").strip()
    if not question:
        return None
    
    import uuid
    logs = load_json("visitor_questions.json", [])
    record = {
        "id": "vq_" + uuid.uuid4().hex[:8],
        "question": question,
        "answer": (answer or "").strip(),
        "source": source or "unknown",
        "needs_human": bool(needs_human),
        "matched_qa": matched_qa or "",
        "session_id": session_id or "",
        "turn_count": int(turn_count or 1),
        "client_ip": client_ip or "",
        "user_agent": user_agent or "",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_adopted": False
    }
    logs.insert(0, record)
    # 最多保留 5000 条访客历史咨询
    if len(logs) > 5000:
        logs = logs[:5000]
    save_json("visitor_questions.json", logs)
    return record

def get_visitor_questions_stats():
    """统计访客提问数据指标"""
    logs = load_json("visitor_questions.json", [])
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for x in logs if x.get("created_at", "").startswith(today_str))
    needs_human_count = sum(1 for x in logs if x.get("needs_human") or x.get("source") in ("fallback_human", "human_intent"))
    adopted_count = sum(1 for x in logs if x.get("is_adopted"))
    deepseek_count = sum(1 for x in logs if x.get("source") == "deepseek_reasoned")
    direct_qa_count = sum(1 for x in logs if x.get("source") == "qa_database_direct")
    
    return {
        "total": len(logs),
        "today_count": today_count,
        "needs_human_count": needs_human_count,
        "adopted_count": adopted_count,
        "deepseek_count": deepseek_count,
        "direct_qa_count": direct_qa_count
    }

def check_human_intent(query):
    """检查是否直接索取客户经理或联系方式"""
    human_keywords = [
        "客户经理", "人工", "真人", "转人工", "人工客服", "客服电话", "电话", "微信", "微信号", 
        "二维码", "扫码", "联系方式", "怎么联系", "找人", "找销售", "谈业务", "谈合作", 
        "经理", "销售经理", "多少钱", "价格", "报价", "折扣", "最低价", "代理", "商务合作", "投诉"
    ]
    q = query.strip().lower()
    for kw in human_keywords:
        if kw in q:
            return True
    return False

def clean_text(text):
    """去除中英文标点与空白，便于纯文本比对"""
    return re.sub(r'[\s\W_]+', '', (text or '').lower())

def search_qa_database(query):
    """
    优先使用向量数据库 (Vector Database) 进行高维语义近邻检索与混合打分
    """
    try:
        try:
            import vector_db
        except ImportError:
            from cms_system import vector_db
        vdb = vector_db.get_vector_db()
        # 向量检索 Top-6
        v_results = vdb.search(query, top_k=6, min_similarity=0.25)
        formatted = []
        for r in v_results:
            # 缩放至百分为量纲 (0.0 - 1.0 -> 0 - 100)
            scaled_score = r["score"] * 100.0
            formatted.append({
                "item": {
                    "id": r["id"],
                    "question": r["question"],
                    "answer": r["answer"],
                    "category": r["category"],
                    "keywords": r.get("keywords", [])
                },
                "score": scaled_score,
                "vector_similarity": r.get("vector_similarity", 0.0)
            })
        if formatted:
            return formatted
    except Exception as e:
        print(f"[AIChat] 向量检索降级执行: {e}")

    # 兜底：传统纯字面比对
    qa_list = load_json("qa_database.json", [])
    if not qa_list:
        return []

    q_lower = query.strip().lower()
    q_clean = clean_text(q_lower)
    results = []

    for item in qa_list:
        if not item.get("enabled", True):
            continue
        
        score = 0.0
        standard_q = item.get("question", "").lower()
        std_clean = clean_text(standard_q)
        keywords = item.get("keywords", [])

        if q_clean == std_clean:
            score += 95.0
        elif q_clean in std_clean:
            score += 65.0
        elif std_clean in q_clean:
            score += 60.0

        for kw in keywords:
            kw_c = clean_text(kw)
            if kw_c and kw_c in q_clean:
                score += 25.0

        if score >= 30.0:
            results.append({
                "item": item,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def search_product_knowledge(query):
    """从官网产品库检索相关产品知识作为补充上下文"""
    products = load_json("products.json", [])
    q_lower = query.strip().lower()
    matched_products = []

    for p in products:
        p_title = p.get("title", "").lower()
        p_cat = p.get("category", "").lower()
        
        # 匹配标题或关键特征
        if p_title in q_lower or any(part in q_lower for part in p_title.split() if len(part) >= 2):
            matched_products.append(p)
        elif any(kw in q_lower for kw in [p_title[:4], p_cat]) and len(p_title) >= 3:
            matched_products.append(p)

    return matched_products[:3]

def call_llm_api(config, user_query, context_text, history=None, reach_10_turns=False):
    """
    调用外部大模型 API (DeepSeek / 通义千问等)，让 AI 深度理解语境、“过下大脑”后再妥善回答：
    1. 结合官方权威知识库 RAG 上下文做逻辑提炼与条理输出；
    2. 严格遵循广告法与化妆品合规条例；
    3. 统一使用“美尔健专属客户经理”；
    4. 满 10 轮主动引导联系专属客户经理；
    5. 保护商业机密与合作方隐私。
    """
    api_key = config.get("api_key", "").strip()
    api_base = config.get("api_base", "").strip().rstrip("/")
    model = config.get("model", "deepseek-chat")
    temperature = float(config.get("temperature", 0.3))

    if not api_key:
        return None

    system_prompt = f"""你叫“小美”，是美尔健（深圳）生物科技有限公司的官方AI技术与商务顾问。

【核心工作准则：必须先深度研读并学习下方美尔健官方问答库，再结合客户提问过脑妥善作答】：
在回答客户任何问题前，你必须严格履行以下三大工作流程：
1. 【第一步：深度研读学习官方问答库】：下方【美尔健官方权威问答库与技术资料】是美尔健研发工程师与法规团队审定的唯一权威知识来源。你必须先仔细阅读、学习并彻底消化这些标准问答中提供的精准数据指标、产品规格型号、研发机理、批次出厂质检（COA）、法规备案号与服务政策。
2. 【第二步：深度过大脑与基准对齐】：认真剖析客户提问的核心意图。若问答库中有直接对应的标准问答，你的作答必须【严格对标】官方问答库中的标准答案与基准事实，绝不脱离问答库核心要点；若涉及多项技术，请在充分理解后融会贯通、条理阐述。
3. 【第三步：妥善、合规、有温度地输出】：以小美顾问亲切、严谨、得体的专业语言作答，条理清晰、层次分明。

【严格合规纪律（广告法与化妆品条例）】：
1. 恪守广告法与化妆品法规：严禁使用“最高、第一、顶级、绝对、绝无、唯一”等极限词；严禁宣称任何医疗疗效或药品功能（如“治疗”、“除疤”、“根治”、“消炎”、“药用”等）。美尔健所有原料均为高纯度化妆品及日用化学品活性成分，功效陈述严格限定于保湿滋润、舒缓修护、抗皱紧致、弹性饱满、改善暗沉等化妆品合规表述。
2. 外用涂抹技术定位：美尔健拥有的透皮环肽、透皮纤连蛋白等透皮技术，均为涂抹式外用促渗吸收技术，绝非医疗注射或医美水光注射，严禁提及注射。
3. 商业机密与隐私保护：严禁透露任何非公开客户项目代号或保密合作品牌（如可肤贝、独特艾琳、BLY-MM01、COLTRIO等），恪守商业秘密。
4. 统一服务称谓：涉及人工咨询、深度技术选型、商务报价、大宗订购或索样跟进时，统一指引联系【美尔健专属客户经理】（坚决严禁使用“人工客服”或“人工客户”字样）。
5. 价格与商业条款：因原料规格及采购批量不同，价格与梯度政策请建议客户联系专属客户经理获取官方报价单。
{"6. 【特别指引】：当前客户已深度连续咨询超过10个问题，请在专业作答完毕后，真诚温馨地建议客户直接与我们专属客户经理一对一深入沟通，并在回答末尾附带固定暗号：[NEED_MANAGER]。" if reach_10_turns else "6. 当客户问题完全超出参考资料且无法确切回答时，请坦诚告知用户“抱歉，这个问题小美暂时无法准确回答”，并指引联系美尔健专属客户经理获取进一步支持，并在回答末尾附带固定暗号：[NEED_MANAGER]。"}

【美尔健官方权威问答库与技术资料（供学习与基准对齐）】：
{context_text}
"""

    messages = [{"role": "system", "content": system_prompt}]

    # 加入最近 2-4 轮对话上下文，保障多轮问答逻辑连贯
    if history and isinstance(history, list):
        for msg in history[-4:]:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_query})

    endpoint = f"{api_base}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 800
    }

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=18)
        if resp.status_code == 200:
            res_json = resp.json()
            reply = res_json["choices"][0]["message"]["content"].strip()
            return reply
        else:
            print(f"[DeepSeek] API返回异常: HTTP {resp.status_code} - {resp.text[:120]}")
            return None
    except Exception as e:
        print(f"[DeepSeek] API调用失败: {e}")
        return None

def search_local_kb_files(query):
    """
    当向量问答库未高置信命中时，从 10 大卷私有技术知识库 (kb_files) 中检索权威档案
    """
    kb_dir = os.path.join(DATA_DIR, "kb_files")
    if not os.path.exists(kb_dir):
        return None

    try:
        try:
            import vector_db
        except ImportError:
            from cms_system import vector_db
        topic_kws = getattr(vector_db, "TOPIC_KEYWORDS", [])
    except Exception:
        topic_kws = ["专利", "发明专利", "胶原蛋白", "纤连蛋白", "透皮环肽", "水母", "贻贝", "pdrn", "主文档", "报送码", "起订量", "样品"]

    q_lower = query.lower()
    matched_topics = [t for t in topic_kws if t in q_lower]
    if not matched_topics:
        return None

    best_section = None
    best_score = 0

    for fname in os.listdir(kb_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(kb_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        sections = re.split(r'\n(?=#{1,3}\s+)', content)
        for sec in sections:
            sec_l = sec.lower()
            sc = sum(sec_l.count(t) * 3 for t in matched_topics)
            if sc > best_score:
                best_score = sc
                best_section = sec.strip()

    if best_section and best_score >= 3:
        # 清理前缀与过长文本，提取前 600 字精华
        lines = [l for l in best_section.split("\n") if l.strip()]
        clean_text = "\n".join(lines[:12])
        if len(clean_text) > 550:
            clean_text = clean_text[:550] + "..."
        return f"根据美尔健官方技术知识档案：\n\n{clean_text}"
    return None

def process_chat(user_query, history=None, question_count=None):
    """
    智能客服主处理流程：
    1. 会话轮次统计：若客户每次问答累计达到或超过10条，贴心引导联系专属客户经理
    2. 意图检测：若直接询问客户经理/人工/电话/微信 -> 直接输出客户经理联系卡片
    3. 全域RAG资料检索：向量检索Top-4问答对 + 官网产品库匹配 + 10卷私有技术档案
    4. DeepSeek“过大脑”思考与专业作答：
       - 若配置了 DeepSeek API Key，将 RAG 知识送入大模型，由 DeepSeek 深度思考、条理提炼、礼貌作答
       - 遵守广告法与化妆品条例，自称小美，指引联系客户经理
    5. 降级容灾：若大模型未配置或调用超时/失败，自动秒级平滑降级至本地问答库与私有技术库直出
    6. 客户经理关怀：满10条主动推荐客户经理，并附带电话与微信二维码名片
    """
    user_query = (user_query or "").strip()
    if not user_query:
        return {
            "status": "success",
            "reply": "您好！我是小美，美尔健官方AI顾问。请问有什么关于生物透皮肽、重组蛋白原料或配方应用的问题可以帮您？",
            "needs_human": False
        }

    config = get_ai_service_config()

    # 统计用户在该会话中的累计提问轮次
    history_user_msgs = [m for m in (history or []) if m.get("role") == "user"]
    turn_count = max(len(history_user_msgs) + 1, int(question_count or 0))
    reach_10_turns = (turn_count >= 10)

    # 1. 意图检测：直接要客户经理/人工或联系方式
    if check_human_intent(user_query):
        contact_card = build_contact_card(config, title="美尔健专属客户经理")
        return {
            "status": "success",
            "reply": f"您好！已为您连接美尔健官方专属客户经理对接通道。您可以直接拨打热线电话，或扫描下方微信二维码添加专属客户经理微信，我们将第一时间为您服务：",
            "needs_human": True,
            "contact": contact_card,
            "source": "human_intent",
            "suggest_manager": True,
            "turn_count": turn_count
        }

    # 2. 全域 RAG 知识检索
    # 2.1 问答数据库向量检索
    qa_results = search_qa_database(user_query)
    
    # 2.2 官网产品库匹配
    matched_products = search_product_knowledge(user_query)

    # 2.3 私有技术知识库匹配
    kb_text = search_local_kb_files(user_query)

    # 构建统一的 RAG 参考资料上下文（供 DeepSeek 深度研读学习）
    context_chunks = []

    # 2.1 注入企业基本档案与核心研发资质（基础学习资料）
    company_core_facts = (
        "【美尔健企业基本档案与核心资质总览（基础学习背景）】：\n"
        "- 公司全称：美尔健（深圳）生物科技有限公司\n"
        "- 创始人背景：由阮仁全高级工程师带队创立的国家高新技术企业，专注生物活性多肽与重组蛋白原料的源头研发与精益制造\n"
        "- 原创透皮技术：自主研发第3代高效生物透皮多肽技术平台（cTDP），攻克大分子活性原料难穿透角质层的世界级技术瓶颈。透皮深度实测超700μm，吸收率提升10-15倍，均为外用涂抹级促渗活性技术（绝非医疗注射，严禁宣称注射）\n"
        "- 8大授权发明专利：持有透皮环肽专利（ZL 2024 1 1708075.5，证书号7741928，第一发明人：阮仁全）、重组三型胶原蛋白专利、重组胶原水凝胶专利、桃胶发酵多糖专利、重组仿生蜗牛蛋白专利、水母胶原面膜专利、长白山灵芝提取专利、重组人纤连蛋白美国发明专利，并荣获中国化妆品金穗奖·专利金奖\n"
        "- 权威资质备案：持有国家器审中心械字号医用级生物原料主文档登记备案（CMDE.NMPA 登记号：M2024311-000），全系列原料具备国家药监局NMPA报送码，随批随货出具CMA/CNAS认证出厂COA质检报告\n"
        "- 样品与商务规则：支持企业与机构免费申领5g-50g研发打样装；采购报价、阶梯折扣或大宗订购请指引联系【美尔健专属客户经理】"
    )
    context_chunks.append(company_core_facts)

    # 2.2 注入官方标准问答库条目（重点对标 + 关联参考）
    if qa_results:
        top_res = qa_results[0]
        top_item = top_res["item"]
        top_score = top_res["score"]
        if top_score >= 45.0:
            context_chunks.append(
                f"【核心对标官方标准问答（与客户提问高度吻合，请优先深度对齐学习）】：\n"
                f"官方标准问题：{top_item.get('question')}\n"
                f"官方权威解答：{top_item.get('answer')}"
            )
            for res in qa_results[1:6]:
                it = res["item"]
                context_chunks.append(f"【关联参考问答】：\n问题：{it.get('question')}\n解答：{it.get('answer')}")
        else:
            for res in qa_results[:6]:
                it = res["item"]
                context_chunks.append(f"【官方参考问答】：\n问题：{it.get('question')}\n解答：{it.get('answer')}")

    # 2.3 注入官网在售产品技术规格
    for p in matched_products:
        p_desc = f"【官网在售产品技术规格与建议】产品名称：{p.get('title')}，所属分类：{p.get('category')}。"
        if p.get("rd_info"):
            rd = p["rd_info"]
            p_desc += f" 建议添加量：{rd.get('dosage', '见配方指南')}，INCI中文名：{rd.get('inci_cn', '')}。"
        context_chunks.append(p_desc)

    # 2.4 注入私有技术研发档案
    if kb_text:
        context_chunks.append(f"【美尔健私有技术研发档案】：\n{kb_text}")

    context_text = "\n\n".join(context_chunks)

    reply_text = None
    source_type = None
    matched_qa_id = None
    matched_q = None
    needs_human = False

    # 3. 核心：优先让 DeepSeek“过下大脑”，结合 RAG 参考资料妥善回答
    if config.get("api_key") and context_text:
        ai_reply = call_llm_api(config, user_query, context_text, history=history, reach_10_turns=reach_10_turns)
        if ai_reply:
            reply_text = ai_reply
            source_type = "deepseek_reasoned"
            if "[NEED_MANAGER]" in reply_text or "[NEED_HUMAN]" in reply_text:
                needs_human = True
                reply_text = reply_text.replace("[NEED_MANAGER]", "").replace("[NEED_HUMAN]", "").strip()
            
            # 记录高相关问答的命中次数
            if qa_results and qa_results[0]["score"] >= 40.0:
                top_qa = qa_results[0]["item"]
                matched_qa_id = top_qa.get("id")
                matched_q = top_qa.get("question")
                _increment_qa_hit(matched_qa_id)

    # 4. 容灾平滑降级（若 DeepSeek 未开启或调用异常，使用本地高置信规则秒级直出）
    if not reply_text:
        if qa_results and qa_results[0]["score"] >= 55.0:
            top_qa = qa_results[0]["item"]
            matched_qa_id = top_qa.get("id")
            matched_q = top_qa.get("question")
            reply_text = top_qa.get("answer", "")
            source_type = "qa_database_direct"
            _increment_qa_hit(matched_qa_id)
        elif kb_text:
            reply_text = kb_text
            source_type = "kb_files_direct"
        else:
            # 兜底：无法确定时诚实引导联系客户经理，坚决不瞎编乱造
            reply_text = (
                "抱歉，这个问题小美暂时无法准确回答。\n\n"
                "为了避免给您带来误导，并确保向您提供最专业、准确的解答与技术支持，建议您直接与美尔健官方**专属客户经理**联系交流："
            )
            needs_human = True
            source_type = "fallback_human"

    # 5. 【核心规则】：如果客户提问达到或超过 10 条，贴心引导联系专属客户经理
    contact_data = None
    if reach_10_turns:
        manager_tip = (
            "\n\n💬 **小美贴心建议**：检测到您在本轮交谈中已深度咨询超过 10 个专业问题。"
            "为了让您的产品配方开发、技术选型或商务采购获得最精准、高效的一对一专业支持，"
            "建议您直接联系美尔健**专属客户经理**为您服务！"
        )
        if "已深度咨询超过" not in reply_text and "客户经理" not in reply_text[-80:]:
            reply_text += manager_tip
        needs_human = True
        contact_data = build_contact_card(config, title="美尔健专属客户经理")
    elif needs_human or "186-9197-8530" in reply_text or "微信" in reply_text:
        needs_human = True
        contact_data = build_contact_card(config, title="美尔健专属客户经理")

    return {
        "status": "success",
        "reply": reply_text,
        "needs_human": needs_human,
        "contact": contact_data,
        "source": source_type,
        "matched_question": matched_q,
        "turn_count": turn_count,
        "suggest_manager": reach_10_turns
    }

def _increment_qa_hit(qa_id):
    """更新问答命中次数"""
    if not qa_id:
        return
    try:
        qa_list = load_json("qa_database.json", [])
        for item in qa_list:
            if item.get("id") == qa_id:
                item["hit_count"] = item.get("hit_count", 0) + 1
                break
        save_json("qa_database.json", qa_list)
    except Exception:
        pass
