# -*- coding: utf-8 -*-
import os
import json
import re
import datetime
import uuid

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if '\ufffd' in WORKSPACE_DIR or not os.path.exists(WORKSPACE_DIR) or not os.path.exists(os.path.join(WORKSPACE_DIR, "cms_system")):
    WORKSPACE_DIR = os.path.abspath(os.path.normpath('E:/\u79c1\u6709\u4e91/\u6211\u7684AI\u7ba1\u7406\u7cfb\u7edf/mellgen_website'))
VIDEOS_FILE = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data", "videos.json")

def load_videos():
    if not os.path.exists(VIDEOS_FILE):
        return []
    try:
        with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
            videos = json.load(f)
            videos.sort(key=lambda x: (int(x.get("sort", 999)), x.get("create_time", "")), reverse=False)
            return videos
    except Exception as e:
        print(f"Error loading videos: {e}")
        return []

def save_videos(videos):
    os.makedirs(os.path.dirname(VIDEOS_FILE), exist_ok=True)
    with open(VIDEOS_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

def add_video(data):
    videos = load_videos()
    new_id = "vid_" + uuid.uuid4().hex[:8]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_video = {
        "id": new_id,
        "title": data.get("title", "").strip(),
        "category": data.get("category", "原料介绍").strip(),
        "cover": data.get("cover", "./resource/images/821127c2e5274f2b86ef7d57489dbe99_24.jpg").strip(),
        "video_url": data.get("video_url", "").strip(),
        "desc": data.get("desc", "").strip(),
        "sort": int(data.get("sort", 1)),
        "status": data.get("status", "published"),
        "views": int(data.get("views", 100)),
        "duration": data.get("duration", "01:30").strip(),
        "create_time": now_str
    }
    
    videos.append(new_video)
    videos.sort(key=lambda x: (int(x.get("sort", 999)), x.get("create_time", "")), reverse=False)
    save_videos(videos)
    return new_video

def update_video(video_id, data):
    videos = load_videos()
    found = False
    for v in videos:
        if v.get("id") == video_id:
            if "title" in data: v["title"] = data["title"].strip()
            if "category" in data: v["category"] = data["category"].strip()
            if "cover" in data: v["cover"] = data["cover"].strip()
            if "video_url" in data: v["video_url"] = data["video_url"].strip()
            if "desc" in data: v["desc"] = data["desc"].strip()
            if "sort" in data: v["sort"] = int(data["sort"])
            if "status" in data: v["status"] = data["status"]
            if "views" in data: v["views"] = int(data["views"])
            if "duration" in data: v["duration"] = data["duration"].strip()
            found = True
            break
    if found:
        videos.sort(key=lambda x: (int(x.get("sort", 999)), x.get("create_time", "")), reverse=False)
        save_videos(videos)
        return True
    return False

def delete_video(video_id):
    videos = load_videos()
    original_len = len(videos)
    videos = [v for v in videos if v.get("id") != video_id]
    if len(videos) < original_len:
        save_videos(videos)
        return True
    return False

def batch_set_video_status(status="offline", video_ids=None):
    videos = load_videos()
    count = 0
    for v in videos:
        if video_ids is None or v.get("id") in video_ids:
            v["status"] = status
            count += 1
    save_videos(videos)
    sync_videos_to_html()
    return count

def toggle_video_status(video_id):
    videos = load_videos()
    new_status = None
    for v in videos:
        if v.get("id") == video_id:
            v["status"] = "offline" if v.get("status") == "published" else "published"
            new_status = v["status"]
            break
    if new_status is not None:
        save_videos(videos)
        sync_videos_to_html()
    return new_status

VIDEO_TITLE_TRANSLATIONS = {
    "工厂介绍": "Factory Introduction",
    "5D胶原蛋白": "5D Collagen",
    "PDRN环肽棒": "PDRN Cyclic Peptide Stick",
    "海洋亮肤因子": "Marine Brightening Factor",
    "聚能环肽EAC": "Poly-Energy Cyclic Peptide EAC",
    "重组Ⅲ型胶原": "Recombinant Type III Collagen",
    "肽维多": "Peptide Multi-Nutrient",
    "cTDP环肽": "cTDP Transdermal Cyclic Peptide",
    "小分子水解胶原蛋白": "Low Molecular Weight Hydrolyzed Collagen",
    "微乳包裹": "Microemulsion Encapsulation",
    "依克多因": "Ectoin Active Solution",
    "cTDP环肽-讲解": "Transdermal Cyclic Peptide - Presentation",
    "未来美妆战场，创新定制原料成为品牌核心竞争力！": "Future Beauty Battlefield: Custom Innovative Raw Materials as Core Competitiveness!",
    "皮肤护理做不好？这里有高科技方案": "Suboptimal Skincare Results? High-Tech Bio Solutions Here",
    "你还在用没效果的护肤品？看这里": "Still Using Ineffective Skincare? Discover Transdermal Science",
    "美尔健生物给您拜年啦": "Mellgen Biotech Season's Greetings",
    "2025护肤品市场千亿预热！！！": "2025 Skincare Market: 100-Billion Surge Brewing!",
    "“中国芯”原料定制，成美妆爆款新密码！": "'China-Core' Raw Material Customization: New Secret to Beauty Blockbusters!"
}

def build_video_html_block(video_list, is_en=False):
    html_chunks = []
    html_chunks.append(' <div class="zxlb-3n-ts-02-list g_splst f_cb"> \n')
    if not video_list:
        msg = "No video resources published currently." if is_en else "暂无已发布的视频资料"
        html_chunks.append(f'   <div style="width:100%;text-align:center;padding:40px 0;color:#94a3b8;font-size:14px;">{msg}</div> \n')
    else:
        for v in video_list:
            title_cn = v.get("title", "")
            title = VIDEO_TITLE_TRANSLATIONS.get(title_cn, title_cn) if is_en else title_cn
            cover = v.get("cover", "")
            if is_en:
                if cover.startswith("./"):
                    cover = "." + cover  # ./resource/ -> ../resource/
                elif not cover.startswith("http") and not cover.startswith("../"):
                    cover = "../" + cover.lstrip("/")
            video_url = v.get("video_url", "")
            html_chunks.append(f'   <dl> \n    <dt> \n     <i><img alt="{title}" src="{cover}" title="{title}"></i> \n     <video autoplay="autoplay" controls="" height="100%" muted preload="none" src="{video_url}" width="100%"></video> \n    </dt> \n    <dd> \n     <h4><b>{title}</b></h4> \n    </dd> \n   </dl> \n')
    html_chunks.append(' </div> \n <div class="clear"></div> \n')
    return "".join(html_chunks)

def update_single_video_page(file_rel_path, video_list, is_en=False, pagination_html=None):
    path = os.path.join(WORKSPACE_DIR, file_rel_path)
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Clean up obsolete nodata block if present
        content = re.sub(r'<div class="n-nodata">.*?</div>\s*', '', content, flags=re.DOTALL)

        grid_pattern = re.compile(r'<div class="zxlb-3n-ts-02-list g_splst f_cb">.*?<div class="clear"></div>', re.DOTALL)
        new_grid = build_video_html_block(video_list, is_en=is_en)
        content = grid_pattern.sub(new_grid, content, count=1)

        if pagination_html is not None:
            pag_pattern = re.compile(r'(<div class="p102-pagination-1-main">)(.*?)(</div>)', re.DOTALL)
            content = pag_pattern.sub(r'\1 ' + pagination_html + r' \3', content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"[-] Error updating {file_rel_path}: {e}")

def sync_videos_to_html():
    """
    全量同步视频至前台页面：
    已下架视频（status != 'published' 或 show == False）前台全面清除不予显示。
    同时更新全量视频列表、分页、以及分类子页面（工厂介绍、原料介绍、技术介绍、科研团队介绍、抖音短视频）。
    中英文版同步刷新。
    """
    videos = [v for v in load_videos() if v.get("status") == "published" and v.get("show", True) is not False]
    
    page1_videos = videos[:12]
    page2_videos = videos[12:24] if len(videos) > 12 else []

    # Pagination HTML for all-videos index pages
    if len(videos) > 12:
        cn_pag_p1 = '<a class="page_curr">1</a><a href="./help_spzx_0002.html">2</a><a class="page_next" href="./help_spzx_0002.html">下一页</a><a class="page_last" href="./help_spzx_0002.html">末页</a>'
        cn_pag_p2 = '<a class="page_prev" href="./help_spzx.html">上一页</a><a href="./help_spzx.html">1</a><a class="page_curr">2</a>'
        en_pag_p1 = '<a class="page_curr">1</a><a href="./help_spzx_0002.html">2</a><a class="page_next" href="./help_spzx_0002.html">Next</a><a class="page_last" href="./help_spzx_0002.html">Last</a>'
        en_pag_p2 = '<a class="page_prev" href="./help_spzx.html">Prev</a><a href="./help_spzx.html">1</a><a class="page_curr">2</a>'
    else:
        cn_pag_p1 = ''
        cn_pag_p2 = ''
        en_pag_p1 = ''
        en_pag_p2 = ''

    # Category video filters
    gcjs_videos = [v for v in videos if v.get("category") == "工厂介绍"]
    yljs_videos = [v for v in videos if v.get("category") in ["原料介绍", "产品演示"]]
    jsjs_videos = [v for v in videos if v.get("category") == "技术介绍"]
    kytdjs_videos = [v for v in videos if v.get("category") == "科研团队介绍"]
    dydsp_videos = [v for v in videos if v.get("category") == "抖音短视频"]

    # 1. Update Chinese pages
    update_single_video_page("help_spzx.html", page1_videos, is_en=False, pagination_html=cn_pag_p1)
    update_single_video_page("help_spzx_0002.html", page2_videos, is_en=False, pagination_html=cn_pag_p2)
    update_single_video_page("help_gcjs.html", gcjs_videos, is_en=False, pagination_html='')
    update_single_video_page("help_yljs.html", yljs_videos, is_en=False, pagination_html='')
    update_single_video_page("help_jsjs.html", jsjs_videos, is_en=False, pagination_html='')
    update_single_video_page("help_kytdjs.html", kytdjs_videos, is_en=False, pagination_html='')
    update_single_video_page("help_dydsp.html", dydsp_videos, is_en=False, pagination_html='')

    # 2. Update English pages
    update_single_video_page(os.path.join("en", "help_spzx.html"), page1_videos, is_en=True, pagination_html=en_pag_p1)
    update_single_video_page(os.path.join("en", "help_spzx_0002.html"), page2_videos, is_en=True, pagination_html=en_pag_p2)
    update_single_video_page(os.path.join("en", "help_gcjs.html"), gcjs_videos, is_en=True, pagination_html='')
    update_single_video_page(os.path.join("en", "help_yljs.html"), yljs_videos, is_en=True, pagination_html='')
    update_single_video_page(os.path.join("en", "help_jsjs.html"), jsjs_videos, is_en=True, pagination_html='')
    update_single_video_page(os.path.join("en", "help_kytdjs.html"), kytdjs_videos, is_en=True, pagination_html='')
    update_single_video_page(os.path.join("en", "help_dydsp.html"), dydsp_videos, is_en=True, pagination_html='')

    return {"success": True, "count": len(videos), "message": f"成功同步 {len(videos)} 部上架视频至前台全站（中文与英文版）！"}
