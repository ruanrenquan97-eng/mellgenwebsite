# -*- coding: utf-8 -*-
"""
Channel, Component, and Subnav Polish across all English pages:
- Re-translates secondary navigation items (About, News, Product categories) into concise, idiomatic English.
- Upgrades common banner slogans into natural, punchy English.
- Upgrades breadcrumbs and category headers.
"""

import os
import glob
import re

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(ROOT_DIR)

REPLACEMENTS = [
    # Banner text
    ("Intelligent Full-Chain Manufacturing of BioactivityRaw Materials, Empowering Next-Gen Skincare",
     "Integrated Bioactive Manufacturing · Empowering Next-Gen Skincare"),
    ("Intelligent Full-Chain Manufacturing of BioactivityRaw Materials， Empowering Next-Gen Skincare",
     "Integrated Bioactive Manufacturing · Empowering Next-Gen Skincare"),
    ("National High-Tech Enterprise, Annual 30%R&D Investment Delivering Bio-Skincare Promises",
     "National High-Tech Enterprise · Advancing Cellular Bio-Skincare Science"),
    ("National High-Tech Enterprise， Annual 30%R&D Investment Delivering Bio-Skincare Promises",
     "National High-Tech Enterprise · Advancing Cellular Bio-Skincare Science"),
    ("From Ingredients to Formulations，Mellgen Biotechfor 200+brands with one-stop transdermal enhancement Solutions",
     "From Actives to Formulations: Turnkey CDMO Solutions for 200+ Global Brands"),
    ("From Ingredients to Formulations, Mellgen Biotechfor 200+brands with one-stop transdermal enhancement Solutions",
     "From Actives to Formulations: Turnkey CDMO Solutions for 200+ Global Brands"),
    ("Decoding Future Skincare: Defining the New Era of Transdermal Technology",
     "Next-Gen Transdermal Science: Overcoming the Cellular Absorption Barrier"),

    # Category and breadcrumb terms
    ("Cosmetic Raw Materials：", "Cosmetic Actives:"),
    ("Cosmetic Raw Materials:", "Cosmetic Actives:"),
    ("Cosmetic Raw Materials", "Cosmetic Actives"),
    ("Raw Material Center", "Product Catalog"),
    ("Raw Material Products", "Product Catalog"),
    ("Medical Raw Materials", "Biomedical Materials"),
    ("Food Nutrition Ingredients", "Nutraceutical Actives"),
    ("Raw Material OEM / Customization", "Custom CDMO"),
    ("Raw Material OEM/Customization", "Custom CDMO"),
    ("Transdermal Peptide Tech", "Transdermal Tech"),

    # Subcategory titles
    ("Transdermal Recombinant Protein/Peptides", "Transdermal Peptides & Proteins"),
    ("Recombinant Biomimetic Protein", "Biomimetic Recombinant Proteins"),
    ("Plant-Derived Actives", "Botanical Bio-Actives"),
    ("Marine-Derived Actives", "Marine Bio-Actives"),
    ("Infant Probiotic Fermentation Actives", "Probiotic Ferment Actives"),

    # Company subnav
    ("Founder Introduction", "Founder Profile"),
    ("Corporate Album", "Corporate Gallery"),
    ("Manufacturing Base", "Manufacturing Facility"),
    ("Honors & Certificates", "Honors & Awards"),
    ("Invention Patents", "Patents & IP"),
    ("Video Center", "Video Center"),

    # News subnav
    ("Technical Knowledge", "Technical Insights"),

    # Common Chinglish fragments
    ("Biological Transdermal Technology pioneer", "Pioneer in Transdermal Peptide Technology"),
    ("Global Pioneer in Biological Transdermal Technology", "Global Pioneer in Transdermal Peptide Technology"),
    ("Reshaping Youth · Locking In Skin Age", "Cellular Bio-Actives · Precision Delivery"),
    ("Reshaping Youth · Locking In Skin Age", "Cellular Bio-Actives · Precision Delivery"),
    ("Biotechnology · Global Pride", "Cellular Transdermal Science")
]

def polish_all_pages():
    files = glob.glob("en/**/*.html", recursive=True)
    active_files = [f for f in files if "backup_" not in f]

    updated_count = 0
    for fp in active_files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original = content
        for old_txt, new_txt in REPLACEMENTS:
            content = content.replace(old_txt, new_txt)

        if content != original:
            updated_count += 1
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"Updated channel & component copy in {updated_count} / {len(active_files)} English files.")

if __name__ == "__main__":
    polish_all_pages()
