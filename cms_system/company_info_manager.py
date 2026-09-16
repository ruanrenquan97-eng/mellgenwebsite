# -*- coding: utf-8 -*-
"""
Company Info Manager (企业信息与资质中心管理器)
统一管理:
1. 关于美尔健 (about_company)
2. 创始人介绍 (founder)
3. 企业相册 (photos)
4. 生产基地 (production_bases)
5. 视频中心 (videos - 联动 videos.json)
6. 荣誉证书 (honors)
7. 公司资质 (qualifications)
8. 专利认证 (patents)
9. 联系我们 (contact)
10. 在线留言 (messages)
"""

import os
import re
import json
import uuid
from datetime import datetime
from bs4 import BeautifulSoup

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMS_DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
DATA_FILE = os.path.join(CMS_DATA_DIR, "company_info.json")

def get_data_file():
    os.makedirs(CMS_DATA_DIR, exist_ok=True)
    return DATA_FILE

def parse_grid_items_from_html(html_path):
    """从 k12-gl-gslb-3nf1-1-01-left 提取 dl 项"""
    if not os.path.exists(html_path):
        return []
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    container = soup.find("div", class_="k12-gl-gslb-3nf1-1-01-left")
    if not container:
        return []
    items = []
    for dl in container.find_all("dl"):
        img_tag = dl.find("img")
        img_src = img_tag.get("src", "") if img_tag else ""
        a_tag = dl.find("a", class_="p2imga")
        big_img = a_tag.get("href", "") if a_tag else img_src
        h4 = dl.find("h4")
        h4_a = h4.find("a") if h4 else None
        title = h4_a.get_text(strip=True) if h4_a else (img_tag.get("title", "") if img_tag else "")
        url = h4_a.get("href", "") if h4_a else ""
        if title or img_src:
            items.append({
                "id": f"item_{uuid.uuid4().hex[:8]}",
                "title": title,
                "title_en": "",
                "img": img_src,
                "big_img": big_img,
                "url": url,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return items

def bootstrap_company_info():
    """首次初始化：从前台 HTML 中提取全部数据并建立 company_info.json"""
    data = {
        "qualifications": [],
        "honors": [],
        "patents": [],
        "photos": [],
        "production_bases": [],
        "about_company": {
            "title": "走进美尔健生物",
            "subtitle": "开创生物修复美容新时代",
            "banner_img": "./resource/images/0ffdceeb65b346afb57542b0efb3fb79_2.jpg",
            "paragraphs": [
                "美尔健（深圳）生物科技有限公司坐落于粤港澳大湾区产业创新核心区域深圳国际生物谷，由中国科学技术大学教授和博士后团队成立的一家从事透皮技术孵化，提供皮肤准确修复抗衰老解决方案的国家高新技术企业。",
                "公司依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。围绕核心技术的开发与利用，我们专注“皮肤抗衰老分子”、“海洋蓝色分子”和“特色植物资源”的研究。",
                "以合成生物学基础，基因工程、发酵工程为技术手段，开发新一代透皮增强型生物活性分子，实现蛋白质多肽，植物多糖以及微生物发酵产物等特色功效性生物资源的绿色开发与产业化，提升功效性活性分子在皮肤修护与健康护理方面的有效利用。"
            ],
            "highlight_images": [
                "./resource/images/0ffdceeb65b346afb57542b0efb3fb79_8.jpg",
                "./resource/images/0ffdceeb65b346afb57542b0efb3fb79_10.jpg",
                "./resource/images/0ffdceeb65b346afb57542b0efb3fb79_12.jpg",
                "./resource/images/0ffdceeb65b346afb57542b0efb3fb79_14.jpg"
            ]
        },
        "founder": {
            "name": "夏总 / 研发团队",
            "title": "中国科学技术大学博士后团队领衔",
            "photo": "./resource/images/0214ae84e9dd44bfb0f554bd710097b6_4.png",
            "intro": "美尔健由中国科学技术大学教授与博士后领衔创办，拥有二十余年深耕生物透皮肽与合成生物学经验，牵头国家级和省市级重点科研课题多项。",
            "honors": [
                "科技部创新创业领军人才",
                "中国科学家论坛科技创新典范",
                "ICIC国际化妆品科技创新奖",
                "数十项生物透皮专利发明人"
            ]
        },
        "contact": {
            "company_name": "美尔健（深圳）生物科技有限公司",
            "phone": "186-9197-8530",
            "tel": "0755-82926499",
            "email": "61791579@qq.com",
            "qq": "61791579",
            "address": "广东省深圳市大鹏新区葵涌街道生命科学产业园A23栋 3楼",
            "address_en": "3rd Floor, Building A23, Life Science Industrial Park, Kuichong Street, Dapeng New District, Shenzhen, Guangdong, China",
            "work_hours": "周一至周五 09:00 - 18:00"
        },
        "messages": []
    }

    # 1. 公司资质 (help_gszz.html)
    gszz_items = parse_grid_items_from_html(os.path.join(WORKSPACE_DIR, "help_gszz.html"))
    gszz_en_items = parse_grid_items_from_html(os.path.join(WORKSPACE_DIR, "en", "help_gszz.html"))
    for i, it in enumerate(gszz_items):
        if i < len(gszz_en_items):
            it["title_en"] = gszz_en_items[i]["title"]
    data["qualifications"] = gszz_items

    # 2. 荣誉证书 (help_ryzs.html & 0002)
    ryzs_items = []
    ryzs_en_items = []
    for suffix in ["", "_0002"]:
        p_cn = os.path.join(WORKSPACE_DIR, f"help_ryzs{suffix}.html")
        p_en = os.path.join(WORKSPACE_DIR, "en", f"help_ryzs{suffix}.html")
        ryzs_items.extend(parse_grid_items_from_html(p_cn))
        ryzs_en_items.extend(parse_grid_items_from_html(p_en))
    for i, it in enumerate(ryzs_items):
        if i < len(ryzs_en_items):
            it["title_en"] = ryzs_en_items[i]["title"]
    data["honors"] = ryzs_items

    # 3. 专利认证 (help_fmzl.html & 0002 & 0003)
    fmzl_items = []
    fmzl_en_items = []
    for suffix in ["", "_0002", "_0003"]:
        p_cn = os.path.join(WORKSPACE_DIR, f"help_fmzl{suffix}.html")
        p_en = os.path.join(WORKSPACE_DIR, "en", f"help_fmzl{suffix}.html")
        fmzl_items.extend(parse_grid_items_from_html(p_cn))
        fmzl_en_items.extend(parse_grid_items_from_html(p_en))
    for i, it in enumerate(fmzl_items):
        if i < len(fmzl_en_items):
            it["title_en"] = fmzl_en_items[i]["title"]
    data["patents"] = fmzl_items

    # 4. 企业相册 (help_qyxc.html & 0002 & 0003)
    qyxc_items = []
    qyxc_en_items = []
    for suffix in ["", "_0002", "_0003"]:
        p_cn = os.path.join(WORKSPACE_DIR, f"help_qyxc{suffix}.html")
        p_en = os.path.join(WORKSPACE_DIR, "en", f"help_qyxc{suffix}.html")
        qyxc_items.extend(parse_grid_items_from_html(p_cn))
        qyxc_en_items.extend(parse_grid_items_from_html(p_en))
    for i, it in enumerate(qyxc_items):
        if i < len(qyxc_en_items):
            it["title_en"] = qyxc_en_items[i]["title"]
    data["photos"] = qyxc_items

    # 5. 生产基地 (help_scjd.html & 0002)
    scjd_items = []
    scjd_en_items = []
    for suffix in ["", "_0002"]:
        p_cn = os.path.join(WORKSPACE_DIR, f"help_scjd{suffix}.html")
        p_en = os.path.join(WORKSPACE_DIR, "en", f"help_scjd{suffix}.html")
        scjd_items.extend(parse_grid_items_from_html(p_cn))
        scjd_en_items.extend(parse_grid_items_from_html(p_en))
    for i, it in enumerate(scjd_items):
        if i < len(scjd_en_items):
            it["title_en"] = scjd_en_items[i]["title"]
    data["production_bases"] = scjd_items

    save_company_info(data)
    return data

def load_company_info():
    path = get_data_file()
    if not os.path.exists(path):
        return bootstrap_company_info()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 补齐默认板块
            for key in ["qualifications", "honors", "patents", "photos", "production_bases", "messages"]:
                if key not in data:
                    data[key] = []
            for key in ["about_company", "founder", "contact"]:
                if key not in data:
                    data[key] = {}
            return data
    except Exception as e:
        print(f"[company_info_manager] 读取数据失败，重新初始化: {e}")
        return bootstrap_company_info()

def save_company_info(data):
    path = get_data_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def build_grid_html_block(items, is_en=False):
    """
    生成标准网格卡片HTML:
    每 4 个 dl 生成一个 <div class="clear"></div>，保持排版稳健
    """
    html_parts = ['<div class="k12-gl-gslb-3nf1-1-01-left">\n']
    
    for i, item in enumerate(items):
        title = item.get("title_en", "") if (is_en and item.get("title_en")) else item.get("title", "")
        img = item.get("img", "")
        big_img = item.get("big_img", "") or img
        url = item.get("url", "") or "javascript:;"
        
        # 路径适配：如果是在英文站，资源相对路径处理
        if is_en and img.startswith("./resource/"):
            img_src = "../" + img[2:]
        elif is_en and not img.startswith("http") and not img.startswith("/") and not img.startswith("../"):
            img_src = "../" + img
        else:
            img_src = img

        dl_block = f"""    <dl> 
     <dt> 
      <a class="p2imga" href="{big_img}" rel="group" title="{title}"><img alt="{title}" src="{img_src}" title="{title}"></a> 
     </dt> 
     <dd> 
      <h4><a href="{url}" title="{title}"> {title} </a></h4> 
     </dd> 
    </dl>\n"""
        html_parts.append(dl_block)
        
        # 每 4 个加一次 clear
        if (i + 1) % 4 == 0:
            html_parts.append('    <div class="clear"></div>\n')
            
    # 如果最后一行不足 4 个，补齐 clear
    if len(items) % 4 != 0:
        html_parts.append('    <div class="clear"></div>\n')
        
    html_parts.append('   </div>')
    return "".join(html_parts)

def update_grid_page(html_path, items, is_en=False):
    """替换 html 页面中的 k12-gl-gslb-3nf1-1-01-left 区块"""
    if not os.path.exists(html_path):
        return False
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_block = build_grid_html_block(items, is_en=is_en)
    pattern = re.compile(r'<div class="k12-gl-gslb-3nf1-1-01-left">.*?</div>\s*(?=<div class="clear"></div>\s*</div>|\s*</div>\s*<div class="p102-pagination-blk">|\s*</div>\s*<div class="g_ft)', re.DOTALL)
    
    if pattern.search(content):
        updated_content = pattern.sub(new_block, content, count=1)
    else:
        # 宽容备选正则
        alt_pattern = re.compile(r'<div class="k12-gl-gslb-3nf1-1-01-left">.*?</div>', re.DOTALL)
        updated_content = alt_pattern.sub(new_block, content, count=1)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    return True

def sync_section_pages(section_key, data=None):
    """同步指定网格板块到前台（支持多页与英文站）"""
    if data is None:
        data = load_company_info()
        
    items = data.get(section_key, [])
    
    # 映射表: section_key -> 页面配置列表
    mapping = {
        "qualifications": [
            ("help_gszz.html", items[:12])
        ],
        "honors": [
            ("help_ryzs.html", items[:12]),
            ("help_ryzs_0002.html", items[12:24])
        ],
        "patents": [
            ("help_fmzl.html", items[:12]),
            ("help_fmzl_0002.html", items[12:24]),
            ("help_fmzl_0003.html", items[24:36])
        ],
        "photos": [
            ("help_qyxc.html", items[:12]),
            ("help_qyxc_0002.html", items[12:24]),
            ("help_qyxc_0003.html", items[24:36])
        ],
        "production_bases": [
            ("help_scjd.html", items[:12]),
            ("help_scjd_0002.html", items[12:24])
        ]
    }
    
    if section_key not in mapping:
        return False
        
    pages = mapping[section_key]
    for filename, page_items in pages:
        p_cn = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(p_cn):
            update_grid_page(p_cn, page_items, is_en=False)
            
        p_en = os.path.join(WORKSPACE_DIR, "en", filename)
        if os.path.exists(p_en):
            update_grid_page(p_en, page_items, is_en=True)
            
    return True

def sync_about_company(data=None):
    """同步关于美尔健图文内容到 helps/gymej.html 及英文版"""
    if data is None:
        data = load_company_info()
    about = data.get("about_company", {})
    if not about:
        return False

    cn_path = os.path.join(WORKSPACE_DIR, "helps", "gymej.html")
    if os.path.exists(cn_path):
        try:
            with open(cn_path, "r", encoding="utf-8") as f:
                content = f.read()
            if about.get("title"):
                content = re.sub(r'<h3>\s*<i>.*?</i>\s*</h3>', f'<h3><i>{about["title"]}</i></h3>', content)
            if about.get("subtitle"):
                content = re.sub(r'<em>开创生物修复美容新时代</em>', f'<em>{about["subtitle"]}</em>', content)
            if about.get("paragraphs"):
                p_html = "\n".join([f"                    <p>{p}</p>" for p in about["paragraphs"]])
                desc_pattern = re.compile(r'<div class="desc"[^>]*>.*?</div>', re.DOTALL)
                content = desc_pattern.sub(f'<div class="desc" deep="6">\n{p_html}\n                </div>', content)
            with open(cn_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[company_info_manager] 同步 helps/gymej.html 失败: {e}")

    return True

def sync_contact(data=None):
    """同步联系我们信息到 helps/lxwm.html 及英文版"""
    if data is None:
        data = load_company_info()
    contact = data.get("contact", {})
    if not contact:
        return False

    cn_path = os.path.join(WORKSPACE_DIR, "helps", "lxwm.html")
    if os.path.exists(cn_path):
        try:
            with open(cn_path, "r", encoding="utf-8") as f:
                content = f.read()
            if contact.get("phone"):
                content = re.sub(r'<span>186-9197-8530\s*</span>\s*<span>186-9197-8530</span>', 
                                 f'<span>{contact["phone"]}</span>', content)
            if contact.get("qq"):
                content = re.sub(r'<h3>\s*QQ\s*</h3>\s*<span>\d+</span>', 
                                 f'<h3>QQ</h3>\n                    <span>{contact["qq"]}</span>', content)
            if contact.get("email"):
                content = re.sub(r'<h3>\s*电子邮箱\s*</h3>\s*<span>[^<]+</span>', 
                                 f'<h3>电子邮箱</h3>\n                    <span>{contact["email"]}</span>', content)
            if contact.get("address"):
                content = re.sub(r'<h3>\s*公司地址\s*</h3>\s*<span>[^<]+</span>', 
                                 f'<h3>公司地址</h3>\n                    <span>{contact["address"]}</span>', content)
            with open(cn_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[company_info_manager] 同步 helps/lxwm.html 失败: {e}")

    en_path = os.path.join(WORKSPACE_DIR, "en", "helps", "lxwm.html")
    if os.path.exists(en_path):
        try:
            with open(en_path, "r", encoding="utf-8") as f:
                content = f.read()
            if contact.get("phone"):
                content = re.sub(r'<h3>\s*Phone\s*</h3>\s*<span>[^<]+</span>',
                                 f'<h3>Phone</h3>\n <span>{contact["phone"]}</span>', content)
            if contact.get("email"):
                content = re.sub(r'<h3>\s*Email\s*</h3>\s*<span>[^<]+</span>',
                                 f'<h3>Email</h3>\n <span>{contact["email"]}</span>', content)
            addr_en = contact.get("address_en") or "3rd Floor, Building A23, Life Science Industrial Park, Kuichong Street, Dapeng New District, Shenzhen, Guangdong, China"
            content = re.sub(r'<h3>\s*Company Address\s*</h3>\s*<span>[^<]+</span>',
                             f'<h3>Company Address</h3>\n <span>{addr_en}</span>', content)
            with open(en_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[company_info_manager] 同步 en/helps/lxwm.html 失败: {e}")

    # 同时更新 settings.json 保持全局联系方式同步
    settings_file = os.path.join(CMS_DATA_DIR, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                s = json.load(f)
            if "contact" not in s:
                s["contact"] = {}
            for k in ["phone", "tel", "email", "qq", "address", "company_name"]:
                if contact.get(k):
                    s["contact"][k] = contact[k]
            # 同步顶层字段供全站生成器使用
            phone_p = contact.get("phone", "").strip()
            phone_t = contact.get("tel", "").strip()
            if phone_t and phone_p:
                s["phone"] = f"{phone_t} / {phone_p}"
            elif phone_p:
                s["phone"] = phone_p
            elif phone_t:
                s["phone"] = phone_t
            if phone_p:
                s["mobile"] = phone_p
            if contact.get("email"):
                s["email"] = contact["email"]
            if contact.get("qq"):
                s["qq"] = contact["qq"]
            if contact.get("address"):
                s["address"] = contact["address"]
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(s, f, ensure_ascii=False, indent=2)

            # 触发全站页面联系方式即时同步
            try:
                import generator
                generator.sync_all_contact_to_site(s)
            except Exception as _g_err:
                print(f"[company_info_manager] 调用 generator.sync_all_contact_to_site 提示: {_g_err}")
        except Exception as e:
            print(f"[company_info_manager] 同步 settings.json 失败: {e}")

    return True

def sync_founder(data=None):
    """同步创始人介绍到 helps/csrjs.html 及英文版"""
    if data is None:
        data = load_company_info()
    founder = data.get("founder", {})
    if not founder:
        return False

    cn_path = os.path.join(WORKSPACE_DIR, "helps", "csrjs.html")
    if os.path.exists(cn_path):
        try:
            with open(cn_path, "r", encoding="utf-8") as f:
                content = f.read()
            name = founder.get("name", "阮仁全 博士")
            title = founder.get("title", "美尔健（深圳）生物科技有限公司创始人&总经理")
            content = re.sub(r'<h2 style="padding-top:20px;">\s*.*?<em>.*?</em>\s*</h2>',
                             f'<h2 style="padding-top:20px;">\n\t\t\t\t\t{name}<em>{title}</em> \n\t\t\t\t</h2>',
                             content, flags=re.DOTALL)
            if founder.get("photo"):
                photo = founder["photo"]
                if not photo.startswith("../") and not photo.startswith("http"):
                    photo = "../" + photo.lstrip("./")
                content = re.sub(r'<div class="fac_img">\s*<img[^>]*src="[^"]*"',
                                 f'<div class="fac_img">\n            <img align="middle" alt="{name}" src="{photo}"',
                                 content)
            # 组装正文与荣誉点
            items = []
            if founder.get("intro"):
                items.append(founder["intro"])
            for h in founder.get("honors", []):
                items.append(f"➤ {h}")
            if items:
                p_text = "<br> ".join(items)
                content = re.sub(r'<div class="fac_con">.*?<p>.*?</p>',
                                 f'<div class="fac_con">\n            <div class="tit">\n                <h2 style="padding-top:20px;">\n\t\t\t\t\t{name}<em>{title}</em> \n\t\t\t\t</h2>\n            </div>\n            <p>\n                {p_text}\n            </p>',
                                 content, flags=re.DOTALL)
            with open(cn_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[company_info_manager] 同步 helps/csrjs.html 失败: {e}")

    return True

def sync_all():
    """全量同步所有板块到前台页面"""
    data = load_company_info()
    for sec in ["qualifications", "honors", "patents", "photos", "production_bases"]:
        sync_section_pages(sec, data)
    sync_about_company(data)
    sync_contact(data)
    sync_founder(data)
    return {"success": True, "message": "全量企业信息已同步至前台双语网站！"}

def add_item(section, item_data):
    """添加新卡片项（资质/证书/专利/相册/基地）并自动同步前台页面"""
    data = load_company_info()
    if section not in data:
        data[section] = []
        
    item_id = item_data.get("id") or f"item_{uuid.uuid4().hex[:8]}"
    new_item = {
        "id": item_id,
        "title": item_data.get("title", "").strip(),
        "title_en": item_data.get("title_en", "").strip(),
        "img": item_data.get("img", "").strip(),
        "big_img": item_data.get("big_img", "").strip() or item_data.get("img", "").strip(),
        "url": item_data.get("url", "").strip() or "javascript:;",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # 默认插到最前面
    data[section].insert(0, new_item)
    save_company_info(data)
    sync_section_pages(section, data)
    return {"success": True, "item": new_item, "message": "添加成功并已同步到前台！"}

def update_item(section, item_id, item_data):
    """更新卡片项"""
    data = load_company_info()
    if section not in data:
        return {"success": False, "message": "板块不存在"}
        
    found = False
    for it in data[section]:
        if it.get("id") == item_id:
            if "title" in item_data: it["title"] = item_data["title"].strip()
            if "title_en" in item_data: it["title_en"] = item_data["title_en"].strip()
            if "img" in item_data: it["img"] = item_data["img"].strip()
            if "big_img" in item_data: it["big_img"] = item_data["big_img"].strip()
            if "url" in item_data: it["url"] = item_data["url"].strip()
            found = True
            break
            
    if not found:
        return {"success": False, "message": "找不到该项"}
        
    save_company_info(data)
    sync_section_pages(section, data)
    return {"success": True, "message": "更新成功并已同步到前台！"}

def delete_item(section, item_id):
    """删除卡片项并自动同步前台页面"""
    data = load_company_info()
    if section not in data:
        return {"success": False, "message": "板块不存在"}
        
    orig_len = len(data[section])
    data[section] = [it for it in data[section] if it.get("id") != item_id]
    
    if len(data[section]) == orig_len:
        return {"success": False, "message": "未找到要删除的项"}
        
    save_company_info(data)
    sync_section_pages(section, data)
    return {"success": True, "message": "已从数据及前台页面中成功删除！"}

def update_text_section(section, new_data):
    """更新文本类板块（关于美尔健/创始人/联系我们）"""
    data = load_company_info()
    if section not in data:
        data[section] = {}
        
    if isinstance(data[section], dict) and isinstance(new_data, dict):
        data[section].update(new_data)
    else:
        data[section] = new_data
        
    save_company_info(data)
    if section == "about_company":
        sync_about_company(data)
    elif section == "contact":
        sync_contact(data)
    elif section == "founder":
        sync_founder(data)
        
    return {"success": True, "message": f"{section} 内容更新成功并已同步！"}

def add_message(msg_data):
    """添加访客留言"""
    data = load_company_info()
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:8]}",
        "name": msg_data.get("name", "访客"),
        "phone": msg_data.get("phone", ""),
        "email": msg_data.get("email", ""),
        "content": msg_data.get("content", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending", # pending, processed
        "reply": ""
    }
    data["messages"].insert(0, msg)
    save_company_info(data)
    return {"success": True, "message": msg}

def delete_message(msg_id):
    data = load_company_info()
    data["messages"] = [m for m in data.get("messages", []) if m.get("id") != msg_id]
    save_company_info(data)
    return {"success": True}

def update_message_status(msg_id, status, reply=None):
    data = load_company_info()
    for m in data.get("messages", []):
        if m.get("id") == msg_id:
            m["status"] = status
            if reply is not None:
                m["reply"] = reply
            break
    save_company_info(data)
    return {"success": True}

