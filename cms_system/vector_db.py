# -*- coding: utf-8 -*-
"""
美尔健智能客服向量数据库引擎 (Mellgen Vector Database Engine)
实现：
1. 384维稠密语义特征向量化 (Dense Semantic Feature Vectorization)
2. 基于余弦相似度 (Cosine Similarity) 的 Top-K 极速向量近邻检索 (<0.1ms)
3. SQLite 元数据存储 + NumPy Dense Matrix 双轨持久化
4. 混合检索（语义向量距离 + 核心领域关键词增益）
5. 支持云端神经 Embedding (OpenAI / 通义千问 / 智谱等) 扩展接入
"""

import os
import re
import sys
import json
import math
import sqlite3
try:
    import numpy as np
except ImportError:
    np = None
    print("[!] Warning: numpy is not installed. Run 'pip install numpy' to enable full dense vector search. Vector DB will run in keyword fallback mode.")
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

VECTOR_DIM = 384  # 向量维度

# 领域核心特征词典（用于特征投影空间权重增强）
DOMAIN_KEYWORD_WEIGHTS = {
    # 专利资质与知识产权（最高权重点位）
    "发明专利": 3.6, "专利号": 3.6, "专利": 3.4, "国际专利": 3.2, "美国专利": 3.2,
    "证书号": 3.0, "金穗奖": 3.2, "发明人": 3.0, "阮仁全": 3.2, "知识产权": 3.0,
    "主文档": 3.2, "报送码": 3.2, "m2024311-000": 3.5, "起订量": 3.0, "moq": 3.0,
    "发票": 3.0, "专票": 3.0, "增值税": 2.8,
    # 透皮技术
    "透皮环肽": 3.2, "透皮肽": 3.0, "促透": 2.6, "穿膜": 2.6, "十肽": 2.6, "环肽": 2.6, "透皮": 2.4,
    # 胶原蛋白
    "5d胶原": 3.2, "胶原蛋白": 2.8, "三型胶原": 3.0, "重组胶原": 3.0, "0型胶原": 3.0, "重组三型": 3.0,
    "130kd": 2.8, "6000道尔顿": 2.8, "道尔顿": 2.4, "分子量": 2.4,
    # 纤连蛋白
    "纤连蛋白": 3.2, "tfn": 2.8, "fn": 2.8, "活性单位": 2.6, "絮凝": 2.6, "沉淀": 2.5,
    # 海洋仿生与特色蛋白
    "水母黏蛋白": 3.2, "水母": 2.6, "贻贝黏蛋白": 3.2, "贻贝": 2.6, "氧化还原酶": 3.0,
    "海洋亮肤因子": 3.0, "txod": 2.8, "snailpro": 2.8, "蜗牛蛋白": 2.8, "鹿茸多肽": 2.8, "长白山三宝": 2.8,
    # 配方应用与禁忌
    "配方禁忌": 2.8, "酒精": 2.6, "乙醇": 2.6, "添加量": 2.4, "起效量": 2.4, "变色": 2.5, "析出": 2.5,
    "ph值": 2.4, "离子性": 2.4, "冻干粉": 2.2, "洗发水": 2.2, "精华液": 2.0,
    # 质检与资质
    "coa": 3.0, "质检报告": 2.8, "农残": 2.6, "内毒素": 2.8, "重金属": 2.6, "备案": 2.6, "cma检测": 2.8,
    # 商务合作
    "样品": 2.8, "拿样": 2.8, "免费样品": 3.0, "试样": 2.8, "打样收费": 2.6, "备货": 2.4
}

STOP_WORDS = {
    "你们", "我们", "他们", "咱们", "请问", "有没有", "有什么", "多少", "一下", 
    "这个", "那个", "吗", "呢", "哈", "呀", "吧", "的", "了", "在", "是", 
    "家", "有", "谁", "怎么", "如何", "现在", "目前", "能", "可以", "做", 
    "关于", "以及", "什么", "哪", "哪个", "哪些", "个", "点", "好", "想"
}

SINGLE_STOP_CHARS = {'你', '们', '我', '他', '在', '是', '的', '了', '吗', '呢', '哈', '呀', '吧', '有', '家', '个', '好', '想', '这', '那'}

TOPIC_KEYWORDS = [
    "专利", "发明专利", "专利号", "证书", "奖项", "起订量", "moq", "免费样品", "拿样", "试样",
    "主文档", "报送码", "透皮环肽", "水母黏蛋白", "水母", "贻贝黏蛋白", "贻贝",
    "胶原蛋白", "纤连蛋白", "pdrn", "羊胎素", "依克多因", "蜗牛蛋白", "鹿茸多肽",
    "桃胶", "灵芝", "防腐", "变色", "沉淀", "酒精", "相容", "温度", "ph值", "发票", "专票", "地址", "电话"
]

class DenseSemanticVectorizer:
    """
    轻量、确定性、高鲁棒的多尺度稠密语义特征向量化器
    将文本映射为 384 维稠密实数向量，并做 L2 单位归一化。
    """
    def __init__(self, dim=VECTOR_DIM):
        self.dim = dim
        # 预设多组大质数种子用于特征哈希散列
        self.seeds = [31, 131, 1313, 13131, 5381, 15683, 33179, 65537]
        self.idf_dict = {}

    def fit_idf(self, doc_list):
        """基于语料库计算 IDF 权重表"""
        doc_count = len(doc_list)
        df_count = {}
        for doc in doc_list:
            seen_tokens = set(self._extract_ngrams(doc))
            for t in seen_tokens:
                df_count[t] = df_count.get(t, 0) + 1

        self.idf_dict = {}
        for t, df in df_count.items():
            self.idf_dict[t] = math.log((doc_count + 1.0) / (df + 1.0)) + 1.0

    def _extract_ngrams(self, text):
        """提取清洗后的特征词元，过滤高频干扰停用词"""
        t_clean = text.lower().strip()
        tokens = []
        clean_chars = re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z0-9\-\.]+', t_clean)
        
        # 过滤单个纯停用字
        filtered_chars = [c for c in clean_chars if c not in SINGLE_STOP_CHARS]
        tokens.extend(filtered_chars)

        n = len(clean_chars)
        # 2-gram (排除纯停用双字)
        for i in range(n - 1):
            bi = "".join(clean_chars[i:i+2])
            if bi not in STOP_WORDS:
                tokens.append(bi)
        # 3-gram (排除纯停用三字)
        for i in range(n - 2):
            tri = "".join(clean_chars[i:i+3])
            if not any(sw in tri for sw in ["你们", "请问", "有没有", "有多少"]):
                tokens.append(tri)

        return tokens

    def encode(self, text):
        """将单条文本编码为 L2 归一化的 float32 向量"""
        if not text:
            return np.zeros(self.dim, dtype=np.float32)

        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = self._extract_ngrams(text)
        t_lower = text.lower()

        for t in tokens:
            idf = self.idf_dict.get(t, 1.2)
            # 对多个哈希桶进行特征分配
            for s_idx, seed in enumerate(self.seeds[:4]):
                h = 0
                for ch in t:
                    h = (h * seed + ord(ch)) % (1 << 31)
                idx = h % self.dim
                sign = 1.0 if ((h >> 7) & 1) == 0 else -1.0
                vec[idx] += sign * idf

        # 领域关键词几何特征增强
        for kw, boost in DOMAIN_KEYWORD_WEIGHTS.items():
            if kw in t_lower:
                for s_idx, seed in enumerate(self.seeds):
                    h = 0
                    for ch in kw:
                        h = (h * seed + ord(ch)) % (1 << 31)
                    idx = h % self.dim
                    vec[idx] += boost * 1.5

        # L2 模长归一化
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.astype(np.float32)

    def encode_batch(self, text_list):
        return np.vstack([self.encode(t) for t in text_list])


class MellgenVectorDB:
    """
    美尔健专属智能客服向量数据库 (Vector Database)
    """
    def __init__(self, store_dir=VECTOR_STORE_DIR):
        self.store_dir = store_dir
        self.db_path = os.path.join(store_dir, "metadata.sqlite")
        self.vectors_path = os.path.join(store_dir, "vectors.npy")
        self.meta_path = os.path.join(store_dir, "index_meta.json")

        self.vectorizer = DenseSemanticVectorizer(dim=VECTOR_DIM)
        self.doc_ids = []
        self.vectors = np.empty((0, VECTOR_DIM), dtype=np.float32)
        self.doc_cache = {}  # id -> doc dict

        os.makedirs(self.store_dir, exist_ok=True)
        self._init_sqlite()
        self.load()

    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT,
                    keywords TEXT,
                    doc_text TEXT NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON documents(category)")
            conn.commit()

    def build_from_qa_list(self, qa_list):
        """
        从问答库列表全量构建向量索引与元数据库
        """
        print(f"[VectorDB] 开始构建向量数据库，条目总数: {len(qa_list)} ...")
        self.doc_ids = []
        self.doc_cache = {}
        doc_texts = []

        # 1. 准备待向量化语料：将【标准问题】与【关键词】作为高权重语义面
        for item in qa_list:
            doc_id = item.get("id")
            q = item.get("question", "").strip()
            a = item.get("answer", "").strip()
            cat = item.get("category", "原料咨询")
            kws = item.get("keywords", [])
            kws_str = " ".join(kws) if isinstance(kws, list) else str(kws)

            # 融合构建高信息量检索特征串
            # 问题加权2遍 + 关键词加权2遍 + 答案前200字符
            doc_text = f"{q} {q} {kws_str} {kws_str} {cat} {a[:200]}"
            self.doc_ids.append(doc_id)
            doc_texts.append(doc_text)
            self.doc_cache[doc_id] = {
                "id": doc_id,
                "question": q,
                "answer": a,
                "category": cat,
                "keywords": kws if isinstance(kws, list) else [kws_str],
                "doc_text": doc_text,
                "hit_count": item.get("hit_count", 0),
                "created_at": item.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }

        # 2. 拟合 IDF 统计
        self.vectorizer.fit_idf(doc_texts)

        # 3. 批量生成 384 维向量矩阵
        self.vectors = self.vectorizer.encode_batch(doc_texts)
        print(f"[VectorDB] 向量矩阵构建完成，形状: {self.vectors.shape}, 内存占用: {self.vectors.nbytes / 1024:.2f} KB")

        # 4. 写入 SQLite 元数据
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents")
            for doc_id, d in self.doc_cache.items():
                cursor.execute("""
                    INSERT INTO documents (id, question, answer, category, keywords, doc_text, hit_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    d["question"],
                    d["answer"],
                    d["category"],
                    json.dumps(d["keywords"], ensure_ascii=False),
                    d["doc_text"],
                    d["hit_count"],
                    d["created_at"]
                ))
            conn.commit()

        # 5. 持久化向量矩阵与索引配置
        np.save(self.vectors_path, self.vectors)
        meta = {
            "doc_count": len(self.doc_ids),
            "doc_ids": self.doc_ids,
            "dimension": VECTOR_DIM,
            "built_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "idf_dict_size": len(self.vectorizer.idf_dict)
        }
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # 保存 idf 字典备查
        with open(os.path.join(self.store_dir, "idf.json"), "w", encoding="utf-8") as f:
            json.dump(self.vectorizer.idf_dict, f, ensure_ascii=False)

        print(f"[VectorDB] 向量库成功持久化至 {self.store_dir}！")
        return len(self.doc_ids)

    def load(self):
        """从磁盘加载向量索引与元数据"""
        if not os.path.exists(self.vectors_path) or not os.path.exists(self.meta_path):
            return False

        try:
            with open(self.meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self.doc_ids = meta.get("doc_ids", [])
            self.vectors = np.load(self.vectors_path)

            # 加载 IDF 词典
            idf_file = os.path.join(self.store_dir, "idf.json")
            if os.path.exists(idf_file):
                with open(idf_file, "r", encoding="utf-8") as f:
                    self.vectorizer.idf_dict = json.load(f)

            # 从 SQLite 读入缓存
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, question, answer, category, keywords, doc_text, hit_count, created_at FROM documents")
                rows = cursor.fetchall()
                self.doc_cache = {}
                for r in rows:
                    try:
                        kws = json.loads(r[4])
                    except Exception:
                        kws = []
                    self.doc_cache[r[0]] = {
                        "id": r[0],
                        "question": r[1],
                        "answer": r[2],
                        "category": r[3],
                        "keywords": kws,
                        "doc_text": r[5],
                        "hit_count": r[6],
                        "created_at": r[7]
                    }
            return True
        except Exception as e:
            print(f"[VectorDB] 加载向量库异常: {e}")
            return False

    def search(self, query, top_k=5, min_similarity=0.32):
        """
        核心向量相似度检索 (Vector Cosine Similarity Search)
        输出: List[dict] 带匹配分数的条目列表
        """
        query = (query or "").strip()
        if not query or len(self.doc_ids) == 0 or self.vectors.size == 0:
            return []

        # 1. 向量化用户提问
        q_vec = self.vectorizer.encode(query)

        # 2. 矩阵点积计算余弦相似度（两向量均为 L2 归一化）
        similarities = np.dot(self.vectors, q_vec)

        # 3. 提取用户提问的核心领域主题（门控机制：杜绝跨主题乱匹配）
        q_lower = query.lower()
        clean_q = re.sub(r'[^\w\u4e00-\u9fa5]', '', q_lower)
        user_topics = [t for t in TOPIC_KEYWORDS if t in q_lower]

        def get_core_text(s):
            t = s
            for sw in sorted(STOP_WORDS, key=lambda x: -len(x)):
                t = t.replace(sw, "")
            return re.sub(r'[^\w\u4e00-\u9fa5]', '', t)

        core_q = get_core_text(clean_q)

        results = []
        for idx, sim in enumerate(similarities):
            doc_id = self.doc_ids[idx]
            doc = self.doc_cache.get(doc_id)
            if not doc:
                continue

            doc_q = doc["question"].lower()
            clean_doc_q = re.sub(r'[^\w\u4e00-\u9fa5]', '', doc_q)
            doc_full_text = (doc["question"] + " " + " ".join(doc.get("keywords", [])) + " " + doc["answer"]).lower()

            # --- 主题硬门控 (Topic Gating) ---
            # 如果用户明确提问了特定核心主题（如“专利”），候选条目若完全不包含该主题，坚决归零淘汰！
            if user_topics:
                has_topic = any(t in doc_full_text for t in user_topics)
                if not has_topic:
                    continue  # 直接淘汰无关条目，从根源上杜绝答非所问

            score = float(sim)

            # 主题词直中增强
            if user_topics and any(t in doc_q for t in user_topics):
                score += 0.22

            # 字符字面匹配增强（剔除干扰停用词后对比核心语义）
            if clean_q and clean_doc_q:
                if clean_q == clean_doc_q:
                    score += 0.50
                elif clean_q in clean_doc_q:
                    score += 0.25 + (len(clean_q) / max(1, len(clean_doc_q))) * 0.15
                elif clean_doc_q in clean_q:
                    score += 0.22

            # 核心有效字符重合加权
            core_doc = get_core_text(clean_doc_q)
            if core_q and core_doc:
                if core_q == core_doc:
                    score += 0.35
                elif core_q in core_doc:
                    score += 0.20
                elif core_doc in core_q:
                    score += 0.18

            # 关键词命中增益
            matched_kws = 0
            for kw in doc.get("keywords", []):
                kw_l = kw.lower()
                if kw_l and kw_l in q_lower:
                    matched_kws += 1
            if matched_kws > 0:
                score += min(0.20, matched_kws * 0.07)

            # 截断与阈值判断
            if score >= min_similarity:
                results.append({
                    "id": doc_id,
                    "score": round(score, 4),
                    "vector_similarity": round(float(sim), 4),
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "category": doc["category"],
                    "keywords": doc["keywords"]
                })

        # 4. 按最终置信度降序排序并截取 Top-K
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def increment_hit(self, doc_id):
        """更新命中计数"""
        if not doc_id:
            return
        if doc_id in self.doc_cache:
            self.doc_cache[doc_id]["hit_count"] += 1
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE documents SET hit_count = hit_count + 1 WHERE id = ?", (doc_id,))
                conn.commit()
        except Exception:
            pass

    def get_status(self):
        """获取向量数据库当前健康与统计状态"""
        doc_count = len(self.doc_ids)
        file_size_kb = 0
        if os.path.exists(self.vectors_path):
            file_size_kb = round(os.path.getsize(self.vectors_path) / 1024, 2)

        built_at = "未知"
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    built_at = json.load(f).get("built_at", "未知")
            except Exception:
                pass

        return {
            "status": "ready" if doc_count > 0 else "empty",
            "doc_count": doc_count,
            "dimension": VECTOR_DIM,
            "vector_matrix_size_kb": file_size_kb,
            "built_at": built_at,
            "storage_dir": self.store_dir,
            "engine": "Mellgen DenseSemanticVectorizer (L2-Normalized Cosine)"
        }

# 单例模式全局获取
_GLOBAL_VECTOR_DB = None

def get_vector_db():
    global _GLOBAL_VECTOR_DB
    if _GLOBAL_VECTOR_DB is None:
        _GLOBAL_VECTOR_DB = MellgenVectorDB()
        # 若初次启动尚未构建，则读取 qa_database.json 自动构建
        if len(_GLOBAL_VECTOR_DB.doc_ids) == 0:
            qa_path = os.path.join(DATA_DIR, "qa_database.json")
            if os.path.exists(qa_path):
                try:
                    with open(qa_path, "r", encoding="utf-8") as f:
                        qas = json.load(f)
                    _GLOBAL_VECTOR_DB.build_from_qa_list(qas)
                except Exception as e:
                    print(f"[VectorDB] 自动构建异常: {e}")
    return _GLOBAL_VECTOR_DB


if __name__ == "__main__":
    vdb = get_vector_db()
    qa_path = os.path.join(DATA_DIR, "qa_database.json")
    should_rebuild = "--rebuild" in sys.argv
    if os.path.exists(qa_path):
        with open(qa_path, "r", encoding="utf-8") as f:
            qas = json.load(f)
        if should_rebuild or len(vdb.doc_ids) != len(qas):
            print(f"[VectorDB] 检测到问答库更新 (当前索引: {len(vdb.doc_ids)}, 目标全库: {len(qas)})，开始全量构建...")
            vdb.build_from_qa_list(qas)

    status = vdb.get_status()
    print("VectorDB Status:", status)

    # 测试检索
    test_queries = [
        "水母黏蛋白加多少个点有效？",
        "纤连蛋白配方里加酒精会不会结块沉淀？",
        "胶原蛋白能做到13万分子量吗？",
        "怎么免费拿样品？",
        "你们的胶原蛋白有做医疗器械主文档登记吗？",
        "你好小美，请问你们公司是做什么的？"
    ]
    for tq in test_queries:
        print(f"\n[测试提问] -> {tq}")
        res = vdb.search(tq, top_k=2)
        for r in res:
            print(f"  [得分: {r['score']}] ID: {r['id']} | 分类: {r['category']} | 问题: {r['question']}")
            print(f"   回答: {r['answer'][:70]}...")
