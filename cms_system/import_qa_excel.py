# -*- coding: utf-8 -*-
"""
美尔健客户咨询问答库 Excel 数据智能解析与导入工具
将《客户咨询问题话术汇总2026.9.12.xlsx》无缝导入客服问答数据库 (qa_database.json)
"""

import os
import re
import json
import pandas as pd
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
EXCEL_PATH = r"C:\Users\minicomputer\Desktop\客户咨询问题话术汇总2026.9.12.xlsx"
QA_FILE = os.path.join(DATA_DIR, "qa_database.json")

# 类别智能规则
CATEGORY_RULES = [
    ("透皮技术", ["透皮环肽", "透皮肽", "促透", "穿膜", "十肽", "环肽", "透皮"]),
    ("重组胶原蛋白", ["胶原蛋白", "5D胶原", "三型胶原", "重组三型", "0型胶原", "胶原"]),
    ("重组纤连蛋白", ["纤连蛋白", "TFN", "FN", "抗体", "活性单位"]),
    ("海洋仿生与特色蛋白", ["水母黏蛋白", "水母", "贻贝", "贻贝黏蛋白", "蜗牛", "Snailpro", "氧化还原酶", "海洋亮肤因子", "TXOD", "鹿茸多肽"]),
    ("配方工艺与稳定性", ["配方", "沉淀", "絮凝", "变色", "相容", "析出", "添加量", "禁配", "禁忌", "PH", "离子性", "酒精", "乙醇", "肤感"]),
    ("质检法规与报告", ["检测", "报告", "COA", "分子量", "农残", "毒理", "内毒素", "备案", "MA检测", "重金属", "菌种"]),
    ("商务合作与样品", ["样品", "拿样", "试样", "打样", "订单", "备货", "经销商", "发货", "流程", "买断", "服务", "收费", "1688", "进店"])
]

def detect_category(question, answer):
    text = (question + " " + answer).lower()
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw.lower() in text:
                return cat
    return "原料技术与应用"

def extract_keywords(question, answer):
    """自动提取高频技术与意图关键词"""
    candidates = [
        "透皮环肽", "透皮肽", "生物促透", "十肽", "环肽-161", "水母黏蛋白", "水母蛋白",
        "氧化还原酶", "透皮纤连蛋白", "纤连蛋白", "FN", "5D胶原", "胶原蛋白", "重组三型胶原",
        "重组胶原", "0型胶原", "分子量", "道尔顿", "130KD", "6000道尔顿", "起效量", "添加量",
        "配方禁忌", "酒精", "乙醇", "絮凝", "沉淀", "变色", "析出", "冻干粉", "打样收费",
        "益生抗敏因子", "长白山三宝", "灵芝", "人参", "松茸", "Snailpro", "蜗牛蛋白", "农残",
        "内毒素", "重金属", "洗发水", "精华液", "COA", "质检", "备案", "样品", "拿样",
        "起订量", "MOQ", "经销商", "备货", "肽维多", "环肽棒", "鹿茸多肽", "买断专利",
        "桃树脂", "TXOD", "海洋亮肤因子", "传明酸", "稳定性报告"
    ]
    kws = []
    text = question + " " + answer
    for c in candidates:
        if c in text and c not in kws:
            kws.append(c)
    # 若不足2个，拆分提问核心词
    if len(kws) < 2:
        words = re.findall(r'[\u4e00-\u9fa5]{2,6}', question)
        for w in words:
            if len(w) >= 2 and w not in kws and w not in ["我们", "可以", "怎么", "什么", "有没有", "一般", "需要"]:
                kws.append(w)
                if len(kws) >= 4:
                    break
    return kws[:6]

def clean_question(raw_q):
    q = str(raw_q).strip()
    # 清理行首形如 "1. " 或 "16." 的多余序号
    q = re.sub(r'^\d+[\.\、\s]+', '', q)
    return q

def format_answer(row_ans, row_sup, question):
    ans = str(row_ans).strip() if pd.notna(row_ans) else ""
    sup = str(row_sup).strip() if pd.notna(row_sup) else ""

    # 特殊话术标准化处理（例如商务流程与话术，调整为专业得体的客服指引）
    if "1688客户进店咨询流程" in question or "公域流量一定要导到私域" in sup:
        return (
            "您好！美尔健生物提供全方位的原料供应、成品贴牌打样及定制开发服务：\n"
            "1. **精准需求对接**：请告知您是品牌方、代工生产厂、研发机构或原料贸易商，我们将为您匹配专属产品经理；\n"
            "2. **全套资料获取**：您可以直接提供您的联系方式或添加我们的官方客服微信，我们将为您发送完整的原料技术资料、配方应用手册及最新价格表；\n"
            "3. **免费索样支持**：常规原料提供 5g-50g 研发测试打样装，通常 1-2 个工作日内安排顺丰寄出。"
        )

    if ans == "nan":
        ans = ""
    if sup == "nan":
        sup = ""

    # 简单的确认词不作为补充
    if sup.lower() in ["ok", "好的", "没问题", "可", "赞同"]:
        sup = ""

    if ans and sup and ans != sup:
        if len(sup) > 10:
            return f"{ans}\n\n💡【专家研发机理与技术补充】：\n{sup}"
        else:
            return f"{ans}（{sup}）"
    elif ans:
        return ans
    elif sup:
        return sup
    else:
        return "该问题已收录，美尔健研发工程师正为您准备最权威的解答，欢迎直接联系专属技术专家咨询。"

def import_excel_qa():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Excel文件未找到: {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH)
    print(f"读取到 Excel 数据: {len(df)} 行")

    # 读取原问答库以保留核心条目
    existing_qas = []
    if os.path.exists(QA_FILE):
        try:
            with open(QA_FILE, "r", encoding="utf-8") as f:
                existing_qas = json.load(f)
        except Exception:
            existing_qas = []

    # 建立已有 question 的集合以防重复
    seen_questions = set()
    cleaned_qas = []

    # 保留原有的 qa_001 - qa_010
    for item in existing_qas:
        if item.get("id", "").startswith("qa_") and not item.get("id", "").startswith("qa_xl_"):
            q_clean = clean_question(item.get("question", ""))
            seen_questions.add(q_clean)
            cleaned_qas.append(item)

    print(f"保留原有系统基础问答: {len(cleaned_qas)} 条")

    # 遍历 Excel 导入新条目
    added_count = 0
    supplement_count = 0

    for idx, row in df.iterrows():
        raw_q = row.get("客户问题", "")
        if pd.isna(raw_q) or not str(raw_q).strip():
            continue

        q = clean_question(raw_q)
        if not q or q in seen_questions:
            continue

        raw_a = row.get("回答", "")
        raw_sup = row.get("阮总补充", "")

        if pd.notna(raw_sup) and str(raw_sup).strip() and str(raw_sup).strip() not in ["ok", "好的", "nan"]:
            supplement_count += 1

        final_answer = format_answer(raw_a, raw_sup, q)
        category = detect_category(q, final_answer)
        keywords = extract_keywords(q, final_answer)

        item = {
            "id": f"qa_xl_{added_count + 1:03d}",
            "question": q,
            "keywords": keywords,
            "answer": final_answer,
            "category": category,
            "enabled": True,
            "hit_count": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        cleaned_qas.append(item)
        seen_questions.add(q)
        added_count += 1

    # 保存至 qa_database.json
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(QA_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_qas, f, ensure_ascii=False, indent=2)

    print(f"=== 导入成功 ===")
    print(f"新增 Excel 问答: {added_count} 条")
    print(f"融合阮总技术补充: {supplement_count} 处")
    print(f"当前问答库总条数: {len(cleaned_qas)} 条")
    return cleaned_qas

if __name__ == "__main__":
    import_excel_qa()
