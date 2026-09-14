# -*- coding: utf-8 -*-
"""
Fix English WeChat articles metadata & polish titles and headings,
plus fix legacy files missing banners and broken ftico icons.
"""

import os
import re

WX_TRANSLATIONS = {
    "wx_0321991b.html": {
        "title": "From the Deep Sea: Miracle Aurelia Jellyfish Mucin Protein",
        "desc": "JELFIPRO® Aurelia jellyfish mucin protein provides profound hydration, barrier repair, and antioxidant benefits powered by marine bio-actives."
    },
    "wx_0f91bf65.html": {
        "title": "In-Depth: Mellgen Biotech Pilot Scale-Up & Quality Assurance",
        "desc": "Explore how Mellgen Biotech bridges laboratory research and commercial manufacturing with rigorous pilot testing and GMP-grade quality control."
    },
    "wx_129dad60.html": {
        "title": "Cosmetic Ingredients Guide: In-Depth Technical Analysis",
        "desc": "A comprehensive deep dive into active cosmetic ingredients, penetration mechanisms, and efficacy evaluation for modern formulators."
    },
    "wx_1753f57d.html": {
        "title": "Next-Gen Skin Repair & Anti-Aging: Transdermal Fibronectin",
        "desc": "How Mellgen's transdermal recombinant fibronectin overcomes stratum corneum barriers to accelerate cellular regeneration and skin elasticity."
    },
    "wx_17e0362b.html": {
        "title": "Shenzhen Institute of Drug Control Delegation Visits Mellgen Biotech",
        "desc": "Vice President Wang Xiaowei of the Shenzhen Institute of Drug Control leads an expert inspection and academic exchange at Mellgen Biotech."
    },
    "wx_1fab9a78.html": {
        "title": "Mellgen Biotech Wins Three 2026 'Remarkable Chinese Raw Materials' Awards",
        "desc": "Recognized for breakthrough peptide and transdermal technologies, Mellgen Biotech secures three prestigious national industry honors."
    },
    "wx_25cd000c.html": {
        "title": "Mellgen Product Awarded 'Top 10 Innovative Raw Materials'",
        "desc": "Warmest congratulations to Mellgen Biotech on receiving the Top 10 Innovative Raw Materials Award for its pioneering transdermal active formulations."
    },
    "wx_2778f61a.html": {
        "title": "Dr. Ruan Renquan Honored with 'Outstanding Engineer' Award",
        "desc": "Founder and chief scientist Dr. Ruan Renquan receives the prestigious Outstanding Engineer award in recognition of his bio-transdermal inventions."
    },
    "wx_2b82c43a.html": {
        "title": "Congratulations to Mellgen Biotech on New Prestigious Honors",
        "desc": "Celebrating another milestone as Mellgen Biotech is commended for outstanding contributions to synthetic biology and transdermal drug/cosmetic delivery."
    },
    "wx_2efc34ad.html": {
        "title": "Mellgen Biotech Achieves ISO 9001 Quality Management Certification",
        "desc": "Mellgen successfully completes ISO 9001 certification, marking an elevated standard in international quality governance and customer satisfaction."
    },
    "wx_34304575.html": {
        "title": "Tech-Empowered Precision Anti-Aging: The Science of High Efficacy",
        "desc": "Discover how biophysical delivery mechanisms and targeted recombinant peptides empower high-performance, non-invasive anti-aging treatments."
    },
    "wx_482bf2d0.html": {
        "title": "Patented Transdermal Tech Activates Recombinant Human Type III Collagen",
        "desc": "Mellgen's patented delivery platform breaks through absorption bottlenecks to fully activate bioactive recombinant human Type III collagen."
    },
    "wx_4a7dddf2.html": {
        "title": "The Birth of Transdermal Fibronectin: New Horizons in Skin Health",
        "desc": "Unveiling how Mellgen's cell-penetrating transdermal fibronectin sets a new benchmark in tissue repair, wound healing, and cosmetic rejuvenation."
    },
    "wx_4ace9d1a.html": {
        "title": "Mellgen Biotech Receives Industry Innovation Accolades",
        "desc": "Another feather in the cap: Mellgen Biotech is celebrated by beauty tech and bio-industry associations for sustained R&D breakthroughs."
    },
    "wx_4c39b958.html": {
        "title": "Year-Round Skincare Innovation with Mellgen Biotechnology",
        "desc": "Dedicated to continuous scientific excellence, Mellgen's team delivers reliable transdermal solutions throughout every season."
    },
    "wx_4e8fce12.html": {
        "title": "Surging 94.74%: Mellgen Launches Cypress-Mushroom Clarity Factor",
        "desc": "Leading botanical extraction trends with high-purity phytochemical actives that deliver soothing, brightening, and anti-pollution defense."
    },
    "wx_4f564aac.html": {
        "title": "Grand Launch: Mellgen Probiotic Soothing Factor",
        "desc": "Derived from precision fermentation and natural peach gum polysaccharides, Mellgen launches its flagship soothing and anti-inflammatory complex."
    },
    "wx_5c64198b.html": {
        "title": "China High-Tech Fair: Mellgen Proprietary Actives in Spotlight",
        "desc": "At the China International High-Tech Fair, Mellgen's proprietary transdermal peptides and recombinant proteins draw widespread industry attention."
    },
    "wx_62ca942a.html": {
        "title": "Marine Collagen: Promising Biomaterial for Biomedical Applications",
        "desc": "Examining the biocompatibility, low immunogenicity, and wide therapeutic potential of marine-derived collagen in regenerative medicine and cosmetics."
    },
    "wx_643fc1dc.html": {
        "title": "PCHi 2023: Mellgen Biotech Ignites Industry Innovation",
        "desc": "Mellgen Biotech showcases breakthrough transdermal actives and customized OEM solutions at PCHi 2023 in Guangzhou."
    },
    "wx_664f0950.html": {
        "title": "Unlocking Fibronectin: Cutting-Edge Mechanism and Skin Efficacy",
        "desc": "An authoritative scientific overview of fibronectin's integrin-binding domains, cell adhesion, and matrix repair properties in human skin."
    },
    "wx_6a679498.html": {
        "title": "Mellgen Biotech Awarded New Chinese Invention Patent",
        "desc": "Continually strengthening intellectual property, Mellgen secures a major national patent for transdermal peptide carrier formulation."
    },
    "wx_6f765800.html": {
        "title": "5-Min Channel Opening, 30-Min Self-Closing: Transdermal Cyclic Peptides",
        "desc": "How Mellgen's proprietary cyclic peptide cTDP temporarily modulates tight junctions for safe, reversible macro-molecule delivery."
    },
    "wx_81fa03f0.html": {
        "title": "Patented Skin Secret: MEGCALM PSF Peach Gum Soothing & Antioxidant Power",
        "desc": "Investigating the biological mechanisms of MEGCALM PSF: nature's botanical polysaccharide shield against irritation and oxidative damage."
    },
    "wx_835f37a6.html": {
        "title": "Mellgen Biotech at PCHi 2023: Efficacy Skincare Actives Showcase",
        "desc": "Live from booth 1D22: Mellgen unveils new clinical data and formulation samples for global brand partners."
    },
    "wx_837d6b7f.html": {
        "title": "Biotech Research in Action: Cultivating Jellyfish for Active Ingredients",
        "desc": "A fascinating inside look at Mellgen's sustainable marine culture tanks and non-destructive enzyme extraction processes."
    },
    "wx_85e07069.html": {
        "title": "Company Profile - Mellgen Biotechnology",
        "desc": "Overview of Mellgen (Shenzhen) Biotechnology Co., Ltd., its pioneering transdermal peptide research, GMP facilities, and global partnerships."
    },
    "wx_860b7e6c.html": {
        "title": "Mellgen Biotech Wins 2023 China Cosmetics Summit Innovation Award",
        "desc": "Honoring excellence in green synthetic biology and commercialization of patented bio-active cosmetic ingredients."
    },
    "wx_86bb0747.html": {
        "title": "Inside Mellgen Synthetic Biology Applied Research Center",
        "desc": "Take a virtual tour of Mellgen's state-of-the-art synthetic biology laboratories, strain engineering pipelines, and analytical testing centers."
    },
    "wx_8a41aaa3.html": {
        "title": "Transdermal Cyclic Peptide: Multi-Layered Skin Defense",
        "desc": "Every single drop counts: explore the molecular mechanics of cyclic peptide transdermal delivery during dry and cold climate conditions."
    },
    "wx_9fc5707a.html": {
        "title": "Core Active: MELLPRO FN Transdermal Fibronectin",
        "desc": "High purity, enhanced penetration, and clinically proven barrier restoration: why MELLPRO FN is chosen by leading international skincare brands."
    },
    "wx_af53d8a4.html": {
        "title": "Formulating Anti-Wrinkle Products: Mellgen's Five Star Actives",
        "desc": "A technical roadmap for cosmetic formulators seeking synergistic anti-aging efficacy with peptides, collagen, and marine extracts."
    },
    "wx_b1c318d0.html": {
        "title": "Celebrating the Conclusion of 2024 Dermatology & Cosmetic Tech Forum",
        "desc": "Mellgen scientists share findings on transdermal macromolecule delivery at the international dermatology symposium."
    },
    "wx_b21386ea.html": {
        "title": "Founder Dr. Ruan Renquan Elected Fellow of the Royal Society of Biology",
        "desc": "Hearty congratulations to Dr. Ruan Renquan, founder of Mellgen Biotech, on being elected as a Fellow of the Royal Society of Biology (FRSB)."
    },
    "wx_b46e6ef9.html": {
        "title": "Photo Highlights & Milestones - Mellgen Biotechnology",
        "desc": "A curated photo gallery documenting corporate milestones, scientific congresses, laboratory expansions, and award ceremonies."
    },
    "wx_b83d9f7e.html": {
        "title": "Overcoming Raw Material Bottlenecks: Shenzhen's Beauty Valley",
        "desc": "Policy analysis and industry perspective on building a world-class biotechnology cluster for independent cosmetic raw materials in Shenzhen."
    },
    "wx_b90ac62e.html": {
        "title": "Innovative Cosmetic Formulations & Raw Materials",
        "desc": "Exploring how synthetic biology and cellular penetration peptides are reshaping the landscape of modern efficacy cosmetics."
    },
    "wx_c5dff9d3.html": {
        "title": "PCHi 2024: Mellgen Biotech Invites You to Connect",
        "desc": "Join Mellgen Biotech at PCHi 2024 to explore customized raw material solutions, one-stop OEM services, and clinical trial results."
    },
    "wx_cccca32e.html": {
        "title": "The 36th Nanjing International Beauty Expo: Mellgen Guide",
        "desc": "Complete visitor guide to Mellgen's exhibition highlights, active ingredient tastings, and technical consultation services at the expo."
    },
    "wx_cd1f6b92.html": {
        "title": "PCHi 2023 Wraps Up: Mellgen Empowers Synthetic Biology with Transdermal Tech",
        "desc": "Reflecting on four intense days of partnership discussions, technical presentations, and new contract signings at PCHi."
    },
    "wx_d217b6ce.html": {
        "title": "Brightening & Anti-Aging: Marine Brightening Factor Efficacy Report",
        "desc": "Independent 3rd-party clinical testing confirms significant melanin reduction, UV photodamage repair, and collagen stimulation."
    },
    "wx_d3247dda.html": {
        "title": "Dr. Ruan Renquan Attends Jiusan Society Pingshan Assembly",
        "desc": "Dr. Ruan Renquan contributes scientific perspectives on biomedical industry growth during the official regional plenary meeting."
    },
    "wx_de7a1800.html": {
        "title": "Mellgen Fibronectin Wins 2020 Ringier Technology Innovation Award",
        "desc": "Celebrating industry recognition for Mellgen's breakthrough in bioactive cellular fibronectin manufacturing and transdermal delivery."
    },
    "wx_e902186b.html": {
        "title": "Type 0 Collagen: The Truth Behind the Trendy Ingredient",
        "desc": "A scientific reality check comparing market claims against structural biology facts in collagen classification and skincare efficacy."
    },
    "wx_f292f0b0.html": {
        "title": "24th China High-Tech Fair: Mellgen's Core Bio-Tech Makes Headlines",
        "desc": "Highlighting Mellgen's innovative peptide chips and targeted cosmetic active delivery platforms at China's premier technology expo."
    },
    "wx_f4669797.html": {
        "title": "R&D and Smart Manufacturing Facility - Mellgen Biotech",
        "desc": "Detailed insight into Mellgen's GMP cleanrooms, computerized bioreactors, pilot testing labs, and high-throughput analytical suites."
    },
    "wx_f6984c2d.html": {
        "title": "Mellgen Biotech Awarded New Chinese Invention Patent",
        "desc": "Announcing the grant of a new national patent affirming Mellgen's technological leadership in bioactive carrier systems."
    },
    "wx_fa691f73.html": {
        "title": "From the Deep Sea: Miracle Aurelia Jellyfish Mucin Protein",
        "desc": "Marine biotechnology unlocks profound moisture-locking and cell-regenerating mucins from Aurelia aurita jellyfish."
    },
    "wx_fed12013.html": {
        "title": "Sensitive Skin Volunteer Clinical Trial Officially Launched",
        "desc": "Mellgen initiates ethical-board-approved clinical trials recruiting volunteers with sensitive and compromised skin barriers."
    },
    "wx_ffeb0d8b.html": {
        "title": "Marine Ingredients for Sensitive Skin: Market Overview & Potential",
        "desc": "Market trends, consumer sentiment, and scientific foundations for marine biomimetic compounds in sensitive skin formulations."
    }
}


def fix_wechat_articles():
    base_dir = "en/articles"
    count = 0
    for filename, info in WX_TRANSLATIONS.items():
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        title_en = info["title"]
        desc_en = info["desc"]

        # Fix <title>
        full_title = f"{title_en} - News & Insights - Mellgen Biotechnology"
        content = re.sub(
            r"<title>.*?</title>",
            f"<title>{full_title}</title>",
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Fix <meta name="description" ...>
        content = re.sub(
            r'<meta\s+name="description"\s+content="[^"]*"',
            f'<meta name="description" content="{desc_en}"',
            content,
            flags=re.IGNORECASE
        )

        # Fix og:title and twitter:title
        content = re.sub(
            r'<meta\s+property="og:title"\s+content="[^"]*"',
            f'<meta property="og:title" content="{title_en} - Mellgen Biotechnology"',
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'<meta\s+name="twitter:title"\s+content="[^"]*"',
            f'<meta name="twitter:title" content="{title_en} - Mellgen Biotechnology"',
            content,
            flags=re.IGNORECASE
        )

        # Fix og:description and twitter:description
        content = re.sub(
            r'<meta\s+property="og:description"\s+content="[^"]*"',
            f'<meta property="og:description" content="{desc_en}"',
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'<meta\s+name="twitter:description"\s+content="[^"]*"',
            f'<meta name="twitter:description" content="{desc_en}"',
            content,
            flags=re.IGNORECASE
        )

        # Fix JSON-LD headline & description
        content = re.sub(
            r'("headline"\s*:\s*)"[^"]*"',
            f'\\1"{title_en}"',
            content
        )

        # Fix <h1 class="p102-info-blk-title">...</h1>
        h1_replacement = f'<h1 class="p102-info-blk-title" title="{title_en}">{title_en}</h1>'
        content = re.sub(
            r'<h1[^>]*class="p102-info-blk-title"[^>]*>.*?</h1>',
            h1_replacement,
            content,
            flags=re.DOTALL
        )
        # Also try reverse attribute order:
        content = re.sub(
            r'<h1[^>]*title="[^"]*"[^>]*class="p102-info-blk-title"[^>]*>.*?</h1>',
            h1_replacement,
            content,
            flags=re.DOTALL
        )

        # Ensure WeChat articles have a clean English introduction summary box
        if '<div class="article-en-lead"' not in content:
            lead_html = f'''<div class="article-en-lead" style="margin: 20px 0 26px 0; padding: 18px 22px; background: #f0f7ff; border-left: 4px solid #0056b3; border-radius: 4px; font-size: 15px; line-height: 1.7; color: #1e3a8a;">
  <strong>Article Overview:</strong> {desc_en}
</div>'''
            content = re.sub(
                r'(<div class="p102-info-content\s+endit-content">)',
                f'\\1\n{lead_html}',
                content
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

    print(f"Successfully polished {count} WeChat articles in {base_dir}!")


def fix_legacy_files():
    legacy_fixes = [
        (
            "en/help_ryzs_0002.html",
            "../resource/images/afd7203e032747ddb72c31d760ceea03_32.jpg",
            "../resource/images/en_banner_about.jpg"
        ),
        (
            "en/product_hzpyl_0003.html",
            "../resource/images/afd7203e032747ddb72c31d760ceea03_26.jpg",
            "../resource/images/en_banner_products.jpg"
        ),
        (
            "en/product_tpxzzd_0002.html",
            "../resource/images/afd7203e032747ddb72c31d760ceea03_26.jpg",
            "../resource/images/en_banner_products.jpg"
        )
    ]

    for rel_path, old_img, new_img in legacy_fixes:
        if not os.path.exists(rel_path):
            continue
        with open(rel_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        content = content.replace(old_img, new_img)

        # Remove broken ftico img tags: <em><img src="../images/ftico1.png"></em>
        content = re.sub(r'<em>\s*<img\s+src="\.\./images/ftico\d+\.png">\s*</em>', '', content)

        with open(rel_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed legacy file: {rel_path}")


if __name__ == "__main__":
    fix_wechat_articles()
    fix_legacy_files()
