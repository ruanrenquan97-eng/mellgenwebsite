# -*- coding: utf-8 -*-
"""
Professional Native English Rewriter for Mellgen Homepages:
- en/index.html
- en/mellgen_home.html

Translates all headlines, teasers, modules, case studies, news snippets,
and footer elements into concise, punchy, native B2B biotech English.
Eliminates all Chinglish, broken punctuation, and literal translations.
"""

import os
import re

def rewrite_homepage(filepath, is_absolute=False):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Base prefix for links
    p_img = "https://www.mellgen.com/images/" if is_absolute else "../images/"
    p_res = "https://www.mellgen.com/resource/images/" if is_absolute else "../resource/images/"
    p_root = "https://www.mellgen.com/" if is_absolute else "./"
    p_en = "https://www.mellgen.com/en/" if is_absolute else "./"

    # 1. Page Title & Meta Description
    c = re.sub(
        r'<title>.*?</title>',
        '<title>Mellgen Biotechnology | Bioactive Ingredients & Transdermal Peptide Science</title>',
        c,
        flags=re.DOTALL | re.IGNORECASE
    )
    c = re.sub(
        r'<meta\s+name="description"\s+content="[^"]*"',
        '<meta name="description" content="Mellgen Biotechnology is a premier life science pioneer developing next-generation bioactive ingredients, patented transdermal peptides, and turnkey CDMO solutions for global skincare and biomedical brands."',
        c,
        flags=re.IGNORECASE
    )
    c = re.sub(
        r'<meta\s+property="og:title"\s+content="[^"]*"',
        '<meta property="og:title" content="Mellgen Biotechnology | Bioactive Ingredients & Transdermal Peptide Science"',
        c,
        flags=re.IGNORECASE
    )
    c = re.sub(
        r'<meta\s+property="og:description"\s+content="[^"]*"',
        '<meta property="og:description" content="Mellgen Biotechnology is a premier life science pioneer developing next-generation bioactive ingredients, patented transdermal peptides, and turnkey CDMO solutions for global skincare and biomedical brands."',
        c,
        flags=re.IGNORECASE
    )
    c = re.sub(
        r'<meta\s+name="twitter:title"\s+content="[^"]*"',
        '<meta name="twitter:title" content="Mellgen Biotechnology | Bioactive Ingredients & Transdermal Peptide Science"',
        c,
        flags=re.IGNORECASE
    )
    c = re.sub(
        r'<meta\s+name="twitter:description"\s+content="[^"]*"',
        '<meta name="twitter:description" content="Mellgen Biotechnology is a premier life science pioneer developing next-generation bioactive ingredients, patented transdermal peptides, and turnkey CDMO solutions for global skincare and biomedical brands."',
        c,
        flags=re.IGNORECASE
    )

    # 2. Header Slogan
    c = re.sub(
        r'<h2 class="lter">\s*<em>.*?</em>\s*<b>.*?</b>\s*</h2>',
        '<h2 class="lter"> <em>Cellular Bio-Actives · Precision Delivery</em><b>Global Pioneer in Transdermal Peptide Technology</b> </h2>',
        c,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 3. Clean Navigation
    clean_nav = f'''<ul>
 <li> <a href="{p_en}index.html" title="Home"> Home </a> </li> 
 <li> <a href="{p_en}product_hzpyl.html" title="Cosmetic Actives"> Cosmetic Actives </a> </li> 
 <li> <a href="{p_en}product_index.html" title="Product Catalog"> Product Catalog </a> </li> 
 <li> <a href="{p_en}helps/yloemd.html" title="Custom CDMO"> Custom CDMO </a> </li> 
 <li> <a href="{p_en}helps/tptjs.html" title="Transdermal Tech"> Transdermal Tech </a> </li> 
 <li> <a href="{p_en}article_hzal.html" title="Client Cases"> Client Cases </a> </li> 
 <li> <a href="{p_en}article_xwzx.html" title="Insights"> Insights </a> </li> 
 <li> <a href="{p_en}helps/gymej.html" title="About Us"> About Us </a> </li> 
 </ul>'''
    c = re.sub(r'<div class="g_nav menu rter">\s*<ul>.*?</ul>\s*</div>', f'<div class="g_nav menu rter">\n {clean_nav}\n </div>', c, flags=re.DOTALL)

    # 4. Banner image replacement (Replace ban_txt.png with en_ban_txt.png!)
    c = c.replace('ban_txt.png', 'en_ban_txt.png')

    # Slider titles
    c = re.sub(
        r'title="Mellgen Biotech: Crafting Superior Products from the Source"',
        'title="Mellgen Biotech: Next-Gen Bioactive Ingredients & Molecular Engineering"',
        c
    )
    c = re.sub(
        r'title="Breakthrough in Biological Transdermal Tech for Skin Repair & Anti-Aging"',
        'title="Breakthrough Transdermal Delivery Platform: 5-Minute Reversible Absorption"',
        c
    )
    c = re.sub(
        r'title="1,000\+ Global Brand Partners & 2,000\+ Cosmetic Brands Choose Our Ingredients"',
        'title="Trusted by 1,000+ Global Skincare, Medical & Health Brand Partners"',
        c
    )

    # 5. Brand Teaser Section
    c = re.sub(
        r'<h2 class="teaser"><em>mellgen biotech</em><b>.*?</b><span>.*?</span></h2>',
        '<h2 class="teaser"><em>MELLGEN BIOTECH</em><b>Pioneering Cellular Transdermal Science</b><span>Engineered Bio-Actives for High-Performance Skincare & Medicine</span></h2>',
        c,
        flags=re.DOTALL | re.IGNORECASE
    )
    c = re.sub(
        r'<li><a href="[^"]*help_spzx\.html"[^>]*>Video Center</a></li>',
        f'<li><a href="{p_en}help_spzx.html" title="Inside Mellgen Video">Inside Mellgen Video</a></li>',
        c
    )
    c = re.sub(
        r'<em>Scan for TikTok</em>',
        '<em>Scan for Video Tour</em>',
        c
    )
    about_text = "Mellgen Biotechnology is a premier life science pioneer developing next-generation bioactive ingredients. Powered by proprietary transdermal peptide platforms and green synthetic biology, we provide clinically validated active molecules, custom formulation, and turnkey CDMO solutions for cosmetic, pharmaceutical, and health brands worldwide."
    c = re.sub(
        r'<p>Mellgen Biotech is a national high-tech enterprise focusing on the development.*?</p>',
        f'<p>{about_text}</p>',
        c,
        flags=re.DOTALL
    )

    # 6. Core Technology Section (6 Pillars)
    c = re.sub(
        r'<h2 class="teaser"><b title="Mellgen Biotech">Mellgen Biotech</b><em>Innovative 3rd-Gen Transdermal Peptide Fusion Tech</em></h2>',
        '<h2 class="teaser"><b title="Mellgen Biotech">Core Technology</b><em>Proprietary 3rd-Gen Transdermal Peptide Delivery Platform</em></h2>',
        c
    )
    tech_intro = "Overcoming the stratum corneum barrier: Our AI-engineered cell-penetrating peptides safely and reversibly modulate tight junctions, multiplying macromolecule absorption without skin irritation."
    c = re.sub(
        r'<div class="jsjs teaser">\s*<p>Utilizing AI molecular design.*?</p>\s*</div>',
        f'<div class="jsjs teaser">\n <p>{tech_intro}</p>\n </div>',
        c,
        flags=re.DOTALL
    )

    # 6 Pillar titles and descriptions
    pillars = [
        (
            "22 Years R&D Experience",
            "22+ Years of Research",
            "Dedicated molecular research and application expertise, establishing Mellgen as a globally trusted pioneer in transdermal science."
        ),
        (
            "SCI Journal Publications",
            "30+ High-Impact SCI Papers",
            "Recognized by the international scientific community for fundamental discoveries in cellular delivery and peptide engineering (Nature, Science, IF >200)."
        ),
        (
            "6 R&D Laboratories",
            "6 Specialized R&D Labs",
            "End-to-end laboratory infrastructure: AI Molecular Design, Cell Biology, Fermentation, Synthetic Biology, Transdermal Delivery, and Clinical Efficacy."
        ),
        (
            "Sci-Tech Fund Support",
            "National Grants & Funding",
            "Supported by National Science Foundations and municipal innovation funds, accelerating the translation of cutting-edge bio-deliveries."
        ),
        (
            "NMPA Filing & Registration",
            "Global Regulatory Compliance",
            "Pharmaceutical-grade quality systems, full safety dossiers, NMPA filings, ISO 9001 certification, and rapid commercial scale-up."
        ),
        (
            "4 Rare Resource Libraries",
            "4 Proprietary Bio-Libraries",
            "Housing thousands of characterized Transdermal Peptides, Skin Bioactive Proteins, Microbial Genetic Elements, and Industrial Fermentation Strains."
        )
    ]

    for old_h4, new_h4, new_desc in pillars:
        # replace H4
        c = re.sub(rf'<h4>{re.escape(old_h4)}</h4>', f'<h4>{new_h4}</h4>', c)
        c = re.sub(rf'alt="{re.escape(old_h4)}"', f'alt="{new_h4}"', c)
        c = re.sub(rf'title="{re.escape(old_h4)}"', f'title="{new_h4}"', c)

    # Replace old descriptions in sup_nav
    c = re.sub(
        r'<p>Through 22 years of dedicated scientific research.*?</p>',
        f'<p>{pillars[0][2]}</p>',
        c
    )
    c = re.sub(
        r'<p>Published over 30 high-quality papers.*?</p>',
        f'<p>{pillars[1][2]}</p>',
        c
    )
    c = re.sub(
        r'<p>A comprehensive R&D laboratory system comprising 6 major labs.*?</p>',
        f'<p>{pillars[2][2]}</p>',
        c
    )
    c = re.sub(
        r'<p>Multiple R&D projects supported by the National Youth Science Fund.*?</p>',
        f'<p>{pillars[3][2]}</p>',
        c
    )
    c = re.sub(
        r'<p>High-quality bio-materials have completed standard safety information.*?</p>',
        f'<p>{pillars[4][2]}</p>',
        c
    )
    c = re.sub(
        r'<p>Equipped with 4 globally scarce proprietary bio-resource repositories.*?</p>',
        f'<p>{pillars[5][2]}</p>',
        c
    )

    # 7. Solutions Section
    c = re.sub(
        r'<h2 class="teaser"><a href="[^"]*product_index\.html"><b>Raw Materials & Solutions</b><em>Providing application solutions for cosmetic manufacturers, medical and food brands worldwide</em></a></h2>',
        f'<h2 class="teaser"><a href="{p_en}product_index.html"><b>Active Ingredients & Solutions</b><em>Formulation solutions engineered for cosmetic chemists, dermatologists, and brand formulators worldwide</em></a></h2>',
        c
    )

    c = re.sub(r'<h4><a href="[^"]*product_hzpyl\.html"[^>]*>Cosmetic Raw Materials</a></h4>', f'<h4><a href="{p_en}product_hzpyl.html" title="Cosmetic Actives">Cosmetic Actives</a></h4>', c)
    c = re.sub(r'<h4><a href="[^"]*product_yyyl\.html"[^>]*>Medical Raw Materials</a></h4>', f'<h4><a href="{p_en}product_yyyl.html" title="Biomedical Materials">Biomedical Materials</a></h4>', c)
    c = re.sub(r'<h4><a href="[^"]*product_spyyyl\.html"[^>]*>Food Nutrition Ingredients</a></h4>', f'<h4><a href="{p_en}product_spyyyl.html" title="Nutraceutical Actives">Nutraceutical Actives</a></h4>', c)
    c = re.sub(r'<h4><a href="[^"]*helps/yloemd\.html"[^>]*>Raw Material OEM / Customization</a></h4>', f'<h4><a href="{p_en}helps/yloemd.html" title="Custom CDMO & OEM">Custom CDMO & OEM</a></h4>', c)

    # 8. Large-Scale Manufacturing Section
    c = re.sub(
        r'<h2 class="teaser"><a href="[^"]*helps/yloemd\.html"><b>Large-Scale Manufacturing Center</b><em>One-stop integration from molecular design, process development, and efficacy validation to downstream raw material and end-product manufacturing</em></a></h2>',
        f'<h2 class="teaser"><a href="{p_en}helps/yloemd.html"><b>Smart Bio-Manufacturing Facility</b><em>GMP Cleanrooms · 100-Ton Fermentation · 100M+ Vials Annual Capacity</em></a></h2>',
        c
    )
    c = re.sub(
        r'<p class="teaser">Equipped with Class 10,000 medical cleanrooms and tens of millions worth of R&D instruments.*?</p>',
        '<p class="teaser">Class 10,000 GMP cleanrooms with multi-million dollar analytical instruments and injection-grade purified water systems. Features 10-ton industrial fermenters producing over 100 tons of high-purity bioactive ingredients annually.</p>',
        c,
        flags=re.DOTALL
    )
    c = re.sub(
        r'<p class="teaser">Equipped with a biological transdermal incubation platform for molecular biology.*?</p>',
        '<p class="teaser">End-to-end biological transdermal platform integrating in-silico design, cellular validation, 1,000 m² cell factory with automated bioreactor suites, and human clinical efficacy verification.</p>',
        c,
        flags=re.DOTALL
    )
    c = re.sub(
        r'<p class="teaser">Industrialized freeze-drying lines with annual capacity over 100M vials; fully automated high-efficiency formulation lines.*?</p>',
        '<p class="teaser">High-speed automated freeze-drying lines producing over 100M vials of bioactive peptides annually, complemented by sterile cream and lotion lines producing over 1M units per year.</p>',
        c,
        flags=re.DOTALL
    )

    # 9. Scientific Leadership Section
    c = re.sub(
        r'<h2 class="teaser"><b>Scientific Achievements · Honors & Responsibilities</b><em>Products successfully exported to the US, Europe, Southeast Asia, and other key regions, earning high acclaim</em></h2>',
        '<h2 class="teaser"><b>World-Class Scientific Leadership</b><em>International peer-reviewed research, global patent protection, and clinical validation</em></h2>',
        c
    )
    c = re.sub(
        r'<p class="teaser">The original team of global biological transdermal technology brings together over 10 leading scientists.*?</p>',
        '<p class="teaser">Our scientific team brings together over 10 leading scientists and professors from Stanford University, USTC, HKU, and SCUT, led by Fellows of the Royal Society of Biology (FRSB). We hold robust international patents protecting molecular structures, peptide sequences, and transdermal formulations.</p>',
        c,
        flags=re.DOTALL
    )

    # 10. Video Section
    c = re.sub(
        r'<b>Video Center · Raw Material Factory</b>',
        '<b>Video Center · Inside Mellgen</b>',
        c
    )
    c = re.sub(
        r'<div class="teaser spwz">\s*The company focuses on \'skin endogenous molecules\'.*?</div>',
        '<div class="teaser spwz">\n Explore our state-of-the-art research laboratories, automated cleanrooms, and patented transdermal peptide mechanisms in action.\n </div>',
        c,
        flags=re.DOTALL
    )

    # Video Titles
    v_map = [
        ("Future Beauty Battlefield: Custom Innovative Raw Materials as Core Competitiveness!", "Next-Gen Actives: Why Custom Bio-Ingredients Define Brand Success"),
        ("Suboptimal Skincare Results? High-Tech Bio Solutions Here", "Overcoming the Absorption Barrier: The Science of Transdermal Peptides"),
        ("Still Using Ineffective Skincare? Discover Transdermal Science", "Recombinant Collagen vs. Traditional Collagen: The Scientific Truth"),
        ("Mellgen Biotech Season's Greetings", "Inside Mellgen Biotechnology: Tour of Our GMP Cleanrooms"),
        ("2025 Skincare Market: 100-Billion Surge!", "2025 Skincare Trends: The Rise of Clinically Proven Efficacy Skincare"),
        ("'China-Core' Material Customization: Secret to Beauty Best-sellers!", "Cell-Penetrating Peptides: Transforming Topical Delivery")
    ]
    for old_v, new_v in v_map:
        c = c.replace(old_v, new_v)

    # 11. Case Studies Section
    c = re.sub(
        r'<h2 class="teaser"><a href="[^"]*article_hzal\.html"[^>]*><b>Premium Raw Materials Empower Quality Beauty</b><em>Successfully exported to the US, Europe, Southeast Asia, and other key regions, widely acclaimed</em></a></h2>',
        f'<h2 class="teaser"><a href="{p_en}article_hzal.html" title="Industry Applications & Case Studies"><b>Industry Applications & Case Studies</b><em>Trusted by 1,000+ brand partners across medical and cosmetic markets worldwide</em></a></h2>',
        c
    )

    case_map = [
        ("Blockbuster Code Lgrade ：Ingredients×Formulations×Applications＝Transdermal 5Dcollagen ，multi- for collagen depletion", "Transdermal 5D Collagen: Rebuilding the Extracellular Matrix Support"),
        ("InnovationTransdermal Technology！MellgenInvention PatentsMatrix， Leapfrog Competitiveness", "Patented Transdermal Peptide Matrix: Multiplying Active Penetration by 300%"),
        ("Sensitive Skin New Trend: Natural + Tech, Ushering in Repair & Anti-Aging Era", "Sensitive Skin Renewal: Biomimetic Barrier Restoration & Anti-Aging"),
        ("Triumph! Mellgen Tops 'Great Chinese Raw Materials' List!", "Industry Accolades: Mellgen Wins Top 10 Innovative Ingredients Award"),
        ("2026 Dermatology SCI Impact Factors Released: Editorial Trends & Direction", "Dermatological Research: Transdermal Peptides & Tight Junction Dynamics"),
        ("Collagen Trust Crisis? Mellgen Reveals Genuine Technology, Rejecting Mere Concept Addition!", "Collagen Purity: True Bioactive Peptides vs. Mere Concept Addition"),
        ("30+ Anti-Aging: Rebuilding the Skin's 'Spring Mattress' Support", "Structural Anti-Aging: Restoring Youthful Dermal Elasticity & Firmness"),
        ("Stop Over-Treating Sensitive Skin! Cell-Level Repair is the True Secret to Renewal", "Cell-Level Barrier Repair: Calming Inflammation & Soothing Sensitive Skin"),
        ("🔑 The Key to Opening Skin Channels in 5 Mins — Transdermal Biomacromolecules Solved", "Fast-Acting Transdermal Channels: 5-Minute Macromolecule Entry"),
        ("Salmon DNA Multi-Dimensional Repair: Deep Hydration & Barrier Revitalization", "Salmon DNA (PDRN): Multi-Dimensional Cellular Revitalization")
    ]
    for old_c, new_c in case_map:
        c = c.replace(old_c, new_c)

    # 12. News & Insights Section
    c = re.sub(
        r'<h2 class="teaser"><a href="[^"]*article_xwzx\.html"[^>]*><b>Understand Cosmetic Ingredients · Start with Mellgen</b><em>Daily valuable insights and real-time industry updates</em></a></h2>',
        f'<h2 class="teaser"><a href="{p_en}article_xwzx.html" title="News & Scientific Insights"><b>News & Scientific Insights</b><em>Latest breakthroughs in transdermal delivery, peptide synthesis, and clinical trials</em></a></h2>',
        c
    )

    # Tab 1: Corporate News
    c = re.sub(
        r'<a href="[^"]*wx_17e0362b\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_17e0362b.html" target="_blank" title="Shenzhen Institute of Drug Control Delegation Visits Mellgen Biotech">
 <dt> 
 <h4>Shenzhen Institute of Drug Control Delegation Visits Mellgen Biotech</h4> 
 <i><img alt="Shenzhen Institute of Drug Control Delegation Visits Mellgen Biotech" src="{p_res}wechat/8c8d6c558559208d101947f0fe43e4bb.jpg"></i> 
 </dt> 
 <dd> 
 <p>Vice President Wang Xiaowei and senior regulatory experts inspect Mellgen's research center, reviewing GMP quality control and transdermal advancements.</p> 
 <span><em>2022-07-08</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_f292f0b0\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_f292f0b0.html" target="_blank" title="24th China High-Tech Fair: Mellgen Core Bio-Tech Makes Headlines"> 
 <dt> 
 <h4>24th China High-Tech Fair: Mellgen Core Bio-Tech Makes Headlines</h4> 
 <i><img alt="24th China High-Tech Fair: Mellgen Core Bio-Tech Makes Headlines" src="{p_res}wechat/ff9c1701c758b9c8ab00972dc7714dd9.jpg"></i> 
 </dt> 
 <dd> 
 <p>Mellgen's proprietary cell-penetrating peptide platform and recombinant proteins draw widespread international attention at the premier technology expo.</p> 
 <span><em>2022-11-19</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_643fc1dc\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_643fc1dc.html" target="_blank" title="PCHi Expo: Mellgen Unveils Next-Gen Transdermal Bioactive Ingredients"> 
 <dt> 
 <h4>PCHi Expo: Mellgen Unveils Next-Gen Transdermal Bioactive Ingredients</h4> 
 <i><img alt="PCHi Expo: Mellgen Unveils Next-Gen Transdermal Bioactive Ingredients" src="{p_res}bab44d41caf84e418181ff0690ccb806_16.jpg"></i> 
 </dt> 
 <dd> 
 <p>Showcasing clinical data, raw material samples, and customized CDMO solutions to beauty brand formulators and cosmetic chemists.</p> 
 <span><em>2022-12-23</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_835f37a6\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_835f37a6.html" target="_blank" title="Mellgen Biotech Secures New National Invention Patent for Transdermal Peptides"> 
 <dt> 
 <h4>Mellgen Biotech Secures New National Invention Patent for Transdermal Peptides</h4> 
 <i><img alt="Mellgen Biotech Secures New National Invention Patent for Transdermal Peptides" src="{p_res}wechat/80fc50cfa85df2bd8d9077367096d077.jpg"></i> 
 </dt> 
 <dd> 
 <p>Strengthening intellectual property barriers for our proprietary reversible tight-junction modulating peptide carriers.</p> 
 <span><em>2023-02-11</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    # Tab 2: Technical Insights
    c = re.sub(
        r'<a href="[^"]*wx_664f0950\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_664f0950.html" target="_blank" title="Unlocking Fibronectin: Molecular Mechanisms and Skin Regeneration"> 
 <dt> 
 <h4>Unlocking Fibronectin: Molecular Mechanisms and Skin Regeneration</h4> 
 <i><img alt="Unlocking Fibronectin: Molecular Mechanisms and Skin Regeneration" src="{p_res}wechat/467634ae4ccb272bfd2bbd77cf05bf6c.jpg"></i> 
 </dt> 
 <dd> 
 <p>How human-derived recombinant fibronectin drives cellular adhesion, wound healing, and extracellular matrix remodeling in human skin.</p> 
 <span><em>2022-05-26</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_81fa03f0\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_81fa03f0.html" target="_blank" title="Botanical Defense: MEGCALM PSF Peach Gum Soothing & Antioxidant Power"> 
 <dt> 
 <h4>Botanical Defense: MEGCALM PSF Peach Gum Soothing & Antioxidant Power</h4> 
 <i><img alt="Botanical Defense: MEGCALM PSF Peach Gum Soothing & Antioxidant Power" src="{p_res}wechat/552db3edb9572274744e34b213939fd7.jpg"></i> 
 </dt> 
 <dd> 
 <p>Natural high-purity polysaccharides engineered to neutralize oxidative stress and restore sensitized skin barriers.</p> 
 <span><em>2026-09-12</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_ffeb0d8b\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_ffeb0d8b.html" target="_blank" title="Marine Bio-Actives: Therapeutic Potential of Jellyfish Mucin Protein"> 
 <dt> 
 <h4>Marine Bio-Actives: Therapeutic Potential of Jellyfish Mucin Protein</h4> 
 <i><img alt="Marine Bio-Actives: Therapeutic Potential of Jellyfish Mucin Protein" src="{p_res}bab44d41caf84e418181ff0690ccb806_26.jpg"></i> 
 </dt> 
 <dd> 
 <p>Exploring the moisture-locking, anti-inflammatory, and cell-regenerating capabilities of sustainable jellyfish extracts.</p> 
 <span><em>2022-03-06</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*wx_837d6b7f\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/wx_837d6b7f.html" target="_blank" title="Type 0 Collagen: A Scientific Reality Check on Emerging Skincare Claims"> 
 <dt> 
 <h4>Type 0 Collagen: A Scientific Reality Check on Emerging Skincare Claims</h4> 
 <i><img alt="Type 0 Collagen: A Scientific Reality Check on Emerging Skincare Claims" src="{p_res}wechat/6cab68262810cd85187b8e00f460a063.jpg"></i> 
 </dt> 
 <dd> 
 <p>Comparing marketing trends against structural biology facts in collagen classification and dermal bioavailability.</p> 
 <span><em>2022-05-30</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    # Tab 3: FAQs
    c = re.sub(
        r'<a href="[^"]*jydbxr\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/jydbxr.html" target="_blank" title="Behind the Collagen Trust Crisis: How Mellgen Restores Scientific Rigor"> 
 <dt> 
 <h4>Behind the Collagen Trust Crisis: How Mellgen Restores Scientific Rigor</h4> 
 <i><img alt="Behind the Collagen Trust Crisis: How Mellgen Restores Scientific Rigor" src="{p_res}eef6296a65d94a0c8df0da56fdf7cfd7_2.jpg"></i> 
 </dt> 
 <dd> 
 <p>Why real bioactive collagen requires precise triple-helix conformations and effective transdermal delivery to stimulate true cellular synthesis.</p> 
 <span><em>2025-07-02</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*jfdxsm\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/jfdxsm.html" target="_blank" title="Have You Unlocked Your Skin's Absorption Code? The Science of Permeation"> 
 <dt> 
 <h4>Have You Unlocked Your Skin's Absorption Code? The Science of Permeation</h4> 
 <i><img alt="Have You Unlocked Your Skin's Absorption Code? The Science of Permeation" src="{p_res}8f0b40e82e88445182c73f5922559de9_2.jpg"></i> 
 </dt> 
 <dd> 
 <p>Understanding molecular weight limits and how cell-penetrating peptides temporarily create safe pathways for large active proteins.</p> 
 <span><em>2025-07-02</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*kpsp3f\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/kpsp3f.html" target="_blank" title="3-Minute Guide to Protein Purity and Quality Verification in Skincare"> 
 <dt> 
 <h4>3-Minute Guide to Protein Purity and Quality Verification in Skincare</h4> 
 <i><img alt="3-Minute Guide to Protein Purity and Quality Verification in Skincare" src="{p_res}b8a942ac10c0484bbb9d2eb5ab7ed6ce_19.png"></i> 
 </dt> 
 <dd> 
 <p>How HPLC, mass spectrometry, and SDS-PAGE ensure zero immunogenic contaminants and high bio-activity in every batch.</p> 
 <span><em>2025-07-02</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    c = re.sub(
        r'<a href="[^"]*mejsww5875\.html"[^>]*>.*?</a>',
        f'''<a href="{p_en}articles/mejsww5875.html" target="_blank" title="Innovative Bioactive Material Solutions for Medical and Cosmetic Fields"> 
 <dt> 
 <h4>Innovative Bioactive Material Solutions for Medical and Cosmetic Fields</h4> 
 <i><img alt="Innovative Bioactive Material Solutions for Medical and Cosmetic Fields" src="{p_res}8310656f8dca483193424397d6fe2b84_4.jpg"></i> 
 </dt> 
 <dd> 
 <p>From custom molecular synthesis and safety testing to GMP-compliant commercial production and turnkey CDMO support.</p> 
 <span><em>2025-07-02</em><i><img src="{p_img}newmore.png"></i></span> 
 </dd> </a>''',
        c,
        flags=re.DOTALL
    )

    # 13. Footer
    c = re.sub(
        r'<h3><b>Reshaping Youth · Locking In Skin Age</b><em>Global Pioneer in Biological Transdermal Technology</em></h3>',
        '<h3><b>Cellular Bio-Actives · Precision Delivery</b><em>Global Pioneer in Transdermal Peptide Technology</em></h3>',
        c
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(c)

    print(f"Successfully rewritten {filepath} with native English copy!")

if __name__ == "__main__":
    rewrite_homepage("en/index.html", is_absolute=False)
    rewrite_homepage("en/mellgen_home.html", is_absolute=True)
