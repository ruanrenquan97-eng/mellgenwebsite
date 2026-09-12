# -*- coding: utf-8 -*-
import os
import json
import re
import datetime
import uuid

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def build_video_html_block(video_list):
    html_chunks = []
    html_chunks.append(' <div class="zxlb-3n-ts-02-list g_splst f_cb"> \n')
    for v in video_list:
        title = v.get("title", "")
        cover = v.get("cover", "")
        video_url = v.get("video_url", "")
        html_chunks.append('   <dl> \n    <dt> \n     <i><img alt="' + title + '" src="' + cover + '" title="' + title + '"></i> \n     <video autoplay="autoplay" controls="" height="100%" muted preload="none" src="' + video_url + '" width="100%"></video> \n    </dt> \n    <dd> \n     <h4><b>' + title + '</b></h4> \n    </dd> \n   </dl> \n')
    html_chunks.append(' </div> \n <div class="clear"></div> \n')
    return "".join(html_chunks)

def sync_videos_to_html():
    videos = [v for v in load_videos() if v.get("status") == "published"]
    if not videos:
        return {"success": True, "message": "暂无已发布的视频"}
    
    page1_videos = videos[:12]
    page2_videos = videos[12:] if len(videos) > 12 else []
    
    grid_pattern = re.compile(r'<div class="zxlb-3n-ts-02-list g_splst f_cb">.*?<div class="clear"></div>', re.DOTALL)
    
    spzx_path = os.path.join(WORKSPACE_DIR, "help_spzx.html")
    if os.path.exists(spzx_path):
        with open(spzx_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_block = build_video_html_block(page1_videos)
        content = grid_pattern.sub(new_block, content, count=1)
        with open(spzx_path, "w", encoding="utf-8") as f:
            f.write(content)

    spzx2_path = os.path.join(WORKSPACE_DIR, "help_spzx_0002.html")
    if os.path.exists(spzx2_path) and page2_videos:
        with open(spzx2_path, "r", encoding="utf-8") as f:
            content2 = f.read()
        new_block2 = build_video_html_block(page2_videos)
        content2 = grid_pattern.sub(new_block2, content2, count=1)
        with open(spzx2_path, "w", encoding="utf-8") as f:
            f.write(content2)

    dydsp_videos = [v for v in videos if v.get("category") == "抖音短视频"]
    dydsp_path = os.path.join(WORKSPACE_DIR, "help_dydsp.html")
    if os.path.exists(dydsp_path) and dydsp_videos:
        with open(dydsp_path, "r", encoding="utf-8") as f:
            content_dy = f.read()
        new_block_dy = build_video_html_block(dydsp_videos[:12])
        content_dy = grid_pattern.sub(new_block_dy, content_dy, count=1)
        with open(dydsp_path, "w", encoding="utf-8") as f:
            f.write(content_dy)

    return {"success": True, "count": len(videos), "message": f"成功同步 {len(videos)} 部视频到前台视频中心！"}
