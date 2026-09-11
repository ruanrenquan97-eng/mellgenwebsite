# -*- coding: utf-8 -*-
"""
Generate cms_system/cms_data/products_en.json with complete, high-quality,
biotech & regulatory compliant English information for all 25 products.
"""

import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "products.json")
DEST_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "products_en.json")

def build_products_en():
    with open(SRC_PATH, "r", encoding="utf-8") as f:
        prods = json.load(f)

    STANDARD_DISCLAIMER_EN = (
        "Regulatory & Professional Compliance Statement:\n"
        "1. The raw material characteristics and experimental data (including cytological studies, mechanism diagrams, and literature citations) presented on this webpage are intended exclusively for technical discussion and formulation R&D reference by cosmetic brand formulators, R&D engineers, product planners, and academic research institutions. They do not constitute finished consumer cosmetic efficacy claims or commercial warranties.\n"
        "2. Pursuant to the Regulations on the Supervision and Administration of Cosmetics, Standards for Cosmetic Efficacy Claim Evaluation, and relevant global cosmetic regulatory frameworks, cosmetic brand enterprises utilizing this raw material shall be solely responsible for the safety, stability, and efficacy claims of their finished consumer products, and shall independently complete efficacy evaluations and regulatory filings/registrations with the competent health authorities prior to commercial launch. Conclusions from in-vitro or cellular studies shall not be directly extrapolated as consumer claims.\n"
        "3. Mellgen Biotech assumes no joint or indirect liability for any claims or regulatory non-compliance arising from improper customer formulation, unauthorized off-label claims, or unverified applications."
    )

    # Translation dictionary for all 25 products
    EN_DATA = {
        "tptyts": {
            "title": "Placental Peptide Sheep Placenta",
            "category": "Cosmetic Raw Materials",
            "desc": "Mellgen high-purity directed enzymatic sheep placental peptide extract, rich in highly active oligopeptides, free amino acids, and trace micronutrients. Small molecules are readily absorbed, significantly activating dermal fibroblast viability and intensively ameliorating skin laxity, aging, and dull roughness.",
            "specs": {
                "INCI Name": "Aqua, Hydrolyzed Placenta Extract, Oligopeptide-1, Glycerin, Pentylene Glycol",
                "Core Actives": "Placental Small-Molecule Oligopeptides (<1000Da >85%)",
                "Appearance": "Light yellow clear transparent liquid",
                "Solubility": "Completely water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、水解胎盘（羊）提取物、寡肽-1、甘油、1,2-戊二醇",
                "inci_en": "Aqua, Hydrolyzed Placenta Extract, Oligopeptide-1, Glycerin, Pentylene Glycol",
                "cas": "91079-43-5 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Recommended to add below 45°C during cooling phase; avoid prolonged high-temperature homogenization",
                "appearance": "Light yellow clear transparent liquid with characteristic mild bio-active odor",
                "solubility": "Readily soluble in water phase, excellent compatibility with hydrophilic polymers",
                "compatibility": "Good compatibility with recombinant collagen, sodium hyaluronate, and peptides; avoid direct contact with strong oxidizers and high-concentration acids"
            },
            "procurement_info": {
                "nmpa_code": "008924-01822-6901",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/light-shielded drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store at 2-8°C, protected from light, dry and sealed under refrigeration",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample with formulation guidelines",
                "qualifications": "Batch COA, MSDS, TDS, Heavy Metal & Microbial Test Reports"
            },
            "marketing_info": {
                "mechanism": "Extracted from premium healthy ewe placental tissues using biomimetic gradient enzymatic cleavage to isolate high-activity oligopeptide clusters and growth factors. Deeply penetrates the basal layer (in-vitro studies indicate fibroblast activation), induces endogenous Type I & III collagen synthesis, and accelerates microcirculation and cellular turnover.",
                "claims": "Luxurious Firming & Anti-Wrinkle, Intensive Vitalizing & Radiant, Firm Elasticity Restoration, Smoothing Dry Roughness, Brightening Translucent Glow",
                "applications": "High-end anti-aging serums, placental restorative creams, intensive nourishment ampoules, luxury eye/neck creams",
                "patents": "Patented gradient targeted enzymatic cleavage and purification technology for sheep placental bioactive peptides"
            },
        },
        "pdrnht": {
            "title": "PDRN Cyclic Peptide Stick",
            "category": "Cosmetic Raw Materials",
            "desc": "Fusion of high-purity pharmaceutical-grade salmon DNA (PDRN) and patented transdermal cyclic peptide technology, providing bi-directional cellular revitalization, collagen network remodeling, rapid micro-inflammation soothing, and epidermal smoothing.",
            "specs": {
                "INCI Name": "Aqua, Sodium DNA, Acetyl Tetrapeptide-5, Butylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Salmon PDRN (Purity >98%) + Transdermal Cyclic Carrier Peptides",
                "Appearance": "Colorless to pale opalescent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 6.0%"
            },
            "rd_info": {
                "inci_cn": "水、脱氧核糖核酸钠、乙酰基四肽-5、丁二醇、1,2-己二醇",
                "inci_en": "Aqua, Sodium DNA, Acetyl Tetrapeptide-5, Butylene Glycol, 1,2-Hexanediol",
                "cas": "9007-49-2 / 82830-45-1",
                "dosage": "1.0% - 6.0% (Recommended 2.0% - 4.0%)",
                "ph_range": "6.0 - 7.5",
                "heat_tolerance": "Add below 40°C during final blending stage",
                "appearance": "Colorless to pale opalescent viscous liquid, odorless",
                "solubility": "Fully miscible in aqueous systems and essence bases",
                "compatibility": "Compatible with hyaluronic acid, peptides, and niacinamide; avoid high concentrations of polyvalent metal ions (e.g., Fe3+, Al3+)"
            },
            "procurement_info": {
                "nmpa_code": "009132-02411-8820",
                "packaging": "1kg/bottle, 5kg/drum, 20kg/sealed container",
                "moq": "1 kg (In Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store sealed at 2-8°C, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available upon request",
                "qualifications": "Batch COA, MSDS, TDS, HPLC Purity Certificate"
            },
            "marketing_info": {
                "mechanism": "Salmon polydeoxyribonucleotide (PDRN) combined with cyclic peptides acts as an adenosine A2A receptor agonist, initiating salvage pathways to supply nucleotides for cellular repair, reducing pro-inflammatory cytokines (IL-6, TNF-alpha), and boosting fibroblast VEGF and collagen secretion.",
                "claims": "Cellular Deep Repair, Barrier Fortification, Soothing Redness, Intensive Hydration, Smooth Texture Refinement",
                "applications": "Post-procedure soothing serums, barrier rescue creams, transdermal essence sticks, targeted micro-infusion liquids",
                "patents": "Patent-pending cyclic peptide delivery carrier for nucleic acid bioactive macromolecules"
            },
        },
        "mellpr8670": {
            "title": "MELLPRO 5Dcollagen 5D Collagen",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Targeting Type I, III, IV, VII, and XVII collagens with a 5-dimensional recombinant composite matrix, providing full-layer structural support and anchoring anti-aging across the epidermis, dermal-epidermal junction (DEJ), and deep dermis.",
            "specs": {
                "INCI Name": "Aqua, Soluble Collagen, Recombinant Collagen, Glycerin, 1,2-Hexanediol",
                "Core Actives": "5D Recombinant Collagen Peptide Complex (Purity >95%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "2.0% - 8.0%"
            },
            "rd_info": {
                "inci_cn": "水、可溶性胶原、重组胶原蛋白、甘油、1,2-己二醇",
                "inci_en": "Aqua, Soluble Collagen, Recombinant Collagen, Glycerin, 1,2-Hexanediol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "2.0% - 8.0% (Recommended 3.0% - 5.0%)",
                "ph_range": "5.5 - 6.8",
                "heat_tolerance": "Add below 40°C in cooling stage; avoid extreme shear",
                "appearance": "Colorless to pale yellow transparent liquid",
                "solubility": "Completely soluble in water, forming uniform transparent solutions",
                "compatibility": "Excellent compatibility with polyols, carbomer, and gentle emulsifiers"
            },
            "procurement_info": {
                "nmpa_code": "007812-03914-5501",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, tightly sealed, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available with formulation guides",
                "qualifications": "Batch COA, SDS, TDS, Endotoxin & Cytotoxicity Test Reports"
            },
            "marketing_info": {
                "mechanism": "Engineered with 5 distinct human-homologous collagen sequences to reconstruct the extracellular matrix (ECM) and the DEJ basement membrane, restoring youthful skin spring architecture and resistance to sagging.",
                "claims": "5D Multi-Layer Collagen Replenishment, DEJ Anchoring Support, Plumping & Elasticity, Fine Line Smoothing, Skin Density Enhancement",
                "applications": "Anti-aging firming serums, collagen plumping creams, facial sculpting masks, medical aesthetic aftercare",
                "patents": "Granted Chinese Invention Patent: Transdermal Multi-Type Recombinant Collagen Complex"
            },
        },
        "tpxldb": {
            "title": "Transdermal Fibronectin",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Humanized recombinant fibronectin overcoming biomacromolecular transdermal barriers, equipped with patented cell-penetrating peptide technology to deeply anchor integrin receptors, achieving rapid barrier emergency rescue and ECM network reconstruction.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Fibronectin, Butylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Humanized Recombinant Fibronectin (RGD sequence >98%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组纤连蛋白、丁二醇、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Fibronectin, Butylene Glycol, 1,2-Hexanediol",
                "cas": "86088-83-7 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "6.0 - 7.2",
                "heat_tolerance": "Add below 42°C during gentle mixing phase",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Easily miscible with aqueous phase and hydrogels",
                "compatibility": "Compatible with non-ionic polymers, hyaluronic acid, and ceramides; avoid strong cationic surfactants"
            },
            "procurement_info": {
                "nmpa_code": "008451-01932-7721",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample with formulation recommendations",
                "qualifications": "Batch COA, SDS, TDS, Cell Migration & Safety Reports"
            },
            "marketing_info": {
                "mechanism": "Contains authentic RGD cell-adhesion motifs that bind integrin alpha5beta1 on epidermal and dermal cells, triggering focal adhesion kinase (FAK) signaling to stimulate keratinocyte migration and rapid wound/barrier healing.",
                "claims": "Emergency Barrier Repair, Soothing Damaged Skin, Cell-Adhesion Network Rebuilding, Post-Sunburn Recovery, Redness Relief",
                "applications": "Barrier rescue ampoules, sensitive skin soothing lotions, post-procedure repair gels, micro-needling serums",
                "patents": "US and Chinese Invention Patents on Transdermal Recombinant Fibronectin Peptides"
            },
        },
        "qdjy": {
            "title": "Atelocollagen",
            "category": "Recombinant Biomimetic Protein",
            "desc": "High-purity atelocollagen with antigenic telopeptides removed through precision enzymatic cleavage, boasting exceptional biocompatibility, zero immunogenicity, and triple-helical structure retention for collagenous hydration.",
            "specs": {
                "INCI Name": "Aqua, Atelocollagen, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Medical-Grade Atelocollagen (>99% Triple Helix)",
                "Appearance": "Colorless to pale straw transparent viscous liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、去端肽胶原、甘油、1,2-己二醇",
                "inci_en": "Aqua, Atelocollagen, Glycerin, 1,2-Hexanediol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 4.0%)",
                "ph_range": "5.8 - 7.0",
                "heat_tolerance": "Must be added below 38°C to protect native triple-helix conformation",
                "appearance": "Colorless to light yellow viscous liquid",
                "solubility": "Completely soluble in aqueous phases",
                "compatibility": "Avoid high alcohol content (>15%) and strong acid/base environments"
            },
            "procurement_info": {
                "nmpa_code": "008129-02654-1190",
                "packaging": "1kg/bottle, 5kg/drum, 20kg/sealed drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, strictly sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available with application protocols",
                "qualifications": "Batch COA, SDS, TDS, CD Spectroscopy Report (Triple Helix Confirmation)"
            },
            "marketing_info": {
                "mechanism": "Preserves the native tertiary triple-helix collagen architecture without the immunogenic telopeptide ends, forming a biomimetic moisture-binding breathable film that supports tissue repair and cellular comfort.",
                "claims": "Medical-Grade Biocompatibility, Breathable Hydrating Membrane, Zero Irritation, Dermal Comfort Soothing, Intensive Moisture Lock",
                "applications": "Medical-grade barrier repair dressings, post-laser soothing masks, hypoallergenic sensitive skin creams, sterile eye serums",
                "patents": "Proprietary enzymatic telopeptide cleavage and purification process"
            },
        },
        "zbssb": {
            "title": "Changbai Mountain Three Treasures",
            "category": "Plant-Derived Actives",
            "desc": "Extracted from authentic Changbai Mountain Ginseng, Deer Antler, and Schisandra chinensis, concentrated with active ginsenosides, polypeptide factors, and lignans to impart robust antioxidant defense and revitalizing skin energy.",
            "specs": {
                "INCI Name": "Aqua, Panax Ginseng Root Extract, Cervus Elaphus Extract, Schisandra Chinensis Fruit Extract, Butylene Glycol",
                "Core Actives": "Total Ginsenosides >15%, Active Deer Antler Peptides, Schisandrin",
                "Appearance": "Golden-brown clear liquid with herbal fragrance",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、人参根提取物、鹿茸提取物、五味子果提取物、丁二醇",
                "inci_en": "Aqua, Panax Ginseng Root Extract, Cervus Elaphus Extract, Schisandra Chinensis Fruit Extract, Butylene Glycol",
                "cas": "90045-38-8 / 84603-62-3",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.0 - 6.5",
                "heat_tolerance": "Add below 50°C during cooling phase",
                "appearance": "Golden-brown transparent liquid with natural pleasant herbal scent",
                "solubility": "Readily soluble in water and hydroalcoholic systems",
                "compatibility": "Compatible with most botanical extracts, niacinamide, and amino acids"
            },
            "procurement_info": {
                "nmpa_code": "007693-01452-3310",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dry, dark place below 25°C",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Pesticide & Heavy Metal Screening Reports"
            },
            "marketing_info": {
                "mechanism": "Combines rare ginsenosides (Rb1, Rg1, Rh2) and bioactive antler peptides to activate cellular ATP synthesis, stimulate dermal microvascular circulation, and neutralize intracellular reactive oxygen species (ROS).",
                "claims": "Imperial Herbal Rejuvenation, Vitality Energy Infusion, Radiant Anti-Oxidant Glow, Firming Revitalization, Complexion Awakening",
                "applications": "High-end revitalizing toners, herbal nourishing creams, anti-fatigue serums, luxury facial oils",
                "patents": "Supercritical fluid extraction and ultrasonic cell-wall disruption technology"
            },
        },
        "megpep6245": {
            "title": "MEGPEP EXOs Yeast Exosome Peptide",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Biomimetic yeast-derived exosome peptide nanovesicles. Natural phospholipid bilayers encapsulate concentrated endogenous growth peptides and signaling molecules, achieving nanoscale gentle transdermal delivery to multi-dimensionally activate dermal stem cells.",
            "specs": {
                "INCI Name": "Aqua, Yeast Ferment Extract, Palmitoyl Tripeptide-5, Lecithin, 1,2-Hexanediol",
                "Core Actives": "Yeast Exosome Vesicles (>10^9 particles/mL), Palmitoyl Tripeptide-5",
                "Appearance": "Milky opalescent nano-dispersion liquid",
                "Solubility": "Water dispersible",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、酵母发酵产物提取物、棕榈酰三肽-5、卵磷脂、1,2-己二醇",
                "inci_en": "Aqua, Yeast Ferment Extract, Palmitoyl Tripeptide-5, Lecithin, 1,2-Hexanediol",
                "cas": "8013-01-2 / 623172-56-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 40°C during final step; avoid high-pressure homogenization",
                "appearance": "Milky opalescent liquid with bluish Tyndall effect",
                "solubility": "Dispersible in water phase forming a uniform stable emulsion",
                "compatibility": "Compatible with common emulsion and serum systems"
            },
            "procurement_info": {
                "nmpa_code": "008821-03104-6245",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 20kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, strictly sealed",
                "shelf_life": "18 Months",
                "sample_policy": "Complimentary 30g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, NTA Nanoparticle Tracking Analysis Report"
            },
            "marketing_info": {
                "mechanism": "Utilizes 50-150nm biomimetic lipid bilayer nanovesicles that fuse with cell membranes, delivering concentrated signaling peptides directly into recipient fibroblasts to switch on collagen and elastin expression cascades.",
                "claims": "Exosome Nano-Targeting, Cellular Messenger Activation, Dermal Deep Rebirth, Elastic Firming, Rapid Skin Smoothing",
                "applications": "Advanced regenerative serums, anti-wrinkle micro-emulsions, repair essence lotions, aesthetic post-care",
                "patents": "Proprietary bio-fermentation exosome isolation and purification platform"
            },
        },
        "megpep": {
            "title": "MEGPEP-13 Transdermal Enhancing Peptide",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Next-generation 13-amino-acid cell-penetrating carrier peptide, transiently reorganizing stratum corneum lipid bilayers to increase the transdermal delivery efficiency of macromolecular active ingredients by up to 5-10 times.",
            "specs": {
                "INCI Name": "Aqua, Oligopeptide-13, Pentylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Transdermal Carrier Peptide MEGPEP-13 (Purity >98%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 2.0%"
            },
            "rd_info": {
                "inci_cn": "水、寡肽-13、戊二醇、1,2-己二醇",
                "inci_en": "Aqua, Oligopeptide-13, Pentylene Glycol, 1,2-Hexanediol",
                "cas": "100085-39-0 / 7732-18-5",
                "dosage": "0.5% - 2.0% (Recommended 1.0%)",
                "ph_range": "5.0 - 7.5",
                "heat_tolerance": "Stable up to 60°C; add at any stage before cool-down",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Freely soluble in water and water/glycol mixtures",
                "compatibility": "Excellent compatibility with macromolecular proteins, hyaluronic acid, polysaccharides, and peptides"
            },
            "procurement_info": {
                "nmpa_code": "008319-01742-9905",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dry, dark place below 25°C or refrigerated at 2-8°C",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available with Franz cell penetration data",
                "qualifications": "Batch COA, SDS, TDS, Franz Cell Permeation Test Report"
            },
            "marketing_info": {
                "mechanism": "Interacts reversibly with stratum corneum intercellular lipids to create temporary micro-channels, acting as a molecular shuttle that pulls co-formulated proteins and peptides safely and reversibly across the skin barrier.",
                "claims": "5-Minute Reversible Skin Channel Opening, 5-10X Transdermal Booster, Molecular Chaperone Delivery, Needle-Free Penetration, Universal Booster",
                "applications": "High-efficacy booster primers, transdermal anti-aging serums, macromolecule-infused face masks, scalp penetration tonics",
                "patents": "Chinese and International Invention Patents on Transdermal Peptide Delivery Systems"
            },
        },
        "lzdt": {
            "title": "Ganoderma Polysaccharide",
            "category": "Food Nutrition Ingredients",
            "desc": "Extracted from authentic Changbai Mountain Ganoderma lucidum fruiting bodies, concentrated with high-purity beta-(1,3)(1,6)-D-glucan. Demonstrates robust macrophage activation, microcirculation support, and epidermal immunity enhancement.",
            "specs": {
                "INCI Name": "Aqua, Ganoderma Lucidum Extract, Butylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Ganoderma Beta-Glucans >65%, Ganoderic Triterpenes",
                "Appearance": "Amber clear transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、赤芝提取物、丁二醇、1,2-己二醇",
                "inci_en": "Aqua, Ganoderma Lucidum (Mushroom) Extract, Butylene Glycol, 1,2-Hexanediol",
                "cas": "223751-82-4 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.0 - 7.0",
                "heat_tolerance": "Heat stable up to 70°C",
                "appearance": "Amber to light brown clear liquid with natural mushroom aroma",
                "solubility": "Easily soluble in water phase",
                "compatibility": "Broad compatibility with hydrophilic thickeners, humectants, and botanical complexes"
            },
            "procurement_info": {
                "nmpa_code": "007945-02188-4310",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, ventilated, dry place below 25°C",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Food Grade / Cosmetic Grade Certification"
            },
            "marketing_info": {
                "mechanism": "Beta-glucan structures bind Dectin-1 and TLR-2 receptors on Langerhans and dendritic cells, modulating cutaneous immune balance, attenuating UV-induced immunosuppression, and supporting healthy barrier renewal.",
                "claims": "Cutaneous Immunity Fortification, Anti-Inflammatory Soothing, Free Radical Scavenging, Environmental Stress Defense, Radiant Barrier Support",
                "applications": "Immunity-defense essence lotions, soothing barrier rescue creams, anti-pollution sunscreens, oral dietary supplements",
                "patents": "Patented multi-stage gradient enzymolysis and membrane ultrafiltration purification"
            },
        },
        "mellpr205": {
            "title": "MELLPRO MAP Recombinant Mussel Adhesive Protein",
            "category": "Marine-Derived Actives",
            "desc": "Genetically engineered humanized mussel adhesive protein (MAP) rich in specific DOPA groups, providing super-strong wet surface adhesion, breathable barrier film formation, and instantaneous soothing of redness and sensitive irritation.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Mussel Adhesive Protein, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Recombinant Mussel Adhesive Protein (Purity >98%)",
                "Appearance": "Colorless to light yellow clear liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 3.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组贻贝粘蛋白、甘油、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Mussel Adhesive Protein, Glycerin, 1,2-Hexanediol",
                "cas": "103125-93-7 / 7732-18-5",
                "dosage": "0.5% - 3.0% (Recommended 1.0% - 2.0%)",
                "ph_range": "5.0 - 6.5",
                "heat_tolerance": "Add below 40°C during final formulation phase",
                "appearance": "Colorless to pale straw clear liquid",
                "solubility": "Readily soluble in water phase",
                "compatibility": "Avoid strong alkaline conditions (pH >7.5) to prevent DOPA auto-oxidation"
            },
            "procurement_info": {
                "nmpa_code": "008671-03099-2205",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 20kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample with application protocols",
                "qualifications": "Batch COA, SDS, TDS, Wet Surface Adhesion & Safety Reports"
            },
            "marketing_info": {
                "mechanism": "DOPA moieties undergo rapid coacervation on moist skin surfaces, creating a microscopic, flexible, bio-adhesive protective mesh that shields nerve endings, accelerates re-epithelialization, and quenches inflammatory cascades.",
                "claims": "Bio-Adhesive Barrier Shield, Immediate Redness Calming, Wet-Surface Protection, Post-Procedure Emergency Care, Hypoallergenic Comfort",
                "applications": "Medical aesthetic post-laser dressings, redness relief sprays, sensitive barrier rescue serums, anti-itch creams",
                "patents": "Granted Invention Patent on Recombinant Mussel Adhesive Protein Synthesis"
            },
        },
        "megzym": {
            "title": "MEGZYME mLyZ Marine Psychrophilic Lysozyme",
            "category": "Marine-Derived Actives",
            "desc": "Extracted from deep-sea psychrophilic microorganisms, this marine lysozyme exhibits 3-5 times higher catalytic activity at ambient temperature than conventional egg-white lysozyme, selectively hydrolyzing harmful Gram-positive bacterial cell walls to balance skin microecology.",
            "specs": {
                "INCI Name": "Aqua, Lysozyme, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Marine Psychrophilic Lysozyme (Specific Activity >40,000 U/mg)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 2.0%"
            },
            "rd_info": {
                "inci_cn": "水、溶菌酶、甘油、1,2-己二醇",
                "inci_en": "Aqua, Lysozyme, Glycerin, 1,2-Hexanediol",
                "cas": "9001-63-2 / 7732-18-5",
                "dosage": "0.5% - 2.0% (Recommended 1.0%)",
                "ph_range": "5.5 - 7.5",
                "heat_tolerance": "Add below 45°C during the cooling phase",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Completely soluble in aqueous solutions",
                "compatibility": "Compatible with most mild non-ionic and amphoteric surfactants; avoid strong anionic surfactants"
            },
            "procurement_info": {
                "nmpa_code": "008542-01994-3870",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Enzymatic Activity Assay Certificate"
            },
            "marketing_info": {
                "mechanism": "Selectively cleaves beta-1,4-glycosidic bonds between N-acetylmuramic acid and N-acetylglucosamine in peptidoglycan, inhibiting C. acnes and S. aureus without disrupting beneficial commensal microbiota.",
                "claims": "Microbiome Balancing, Targeted Blemish Defense, Gentle Anti-Microbial, Non-Antibiotic Purity, Sebum & Pore Clarity",
                "applications": "Acne-prone skin serums, clarifying cleansing foams, anti-dandruff scalp tonics, intimate hygiene gels",
                "patents": "Patent on Deep-Sea Psychrophilic Enzyme Fermentation & Stabilization"
            },
        },
        "mellpr": {
            "title": "MELLPRO 3Dcollagen 3D Collagen",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Targeted composite recombinant collagen specifically optimized for extracellular matrix (ECM) 3D meshwork remodeling. Precisely matches human Type I and Type III collagen core peptide sequences to erect an elastic structural scaffold supporting collapsing dermal architecture.",
            "specs": {
                "INCI Name": "Aqua, Soluble Collagen, Recombinant Collagen, 1,2-Hexanediol",
                "Core Actives": "3D Recombinant Type I & III Collagen Complex (>95%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.5% - 6.0%"
            },
            "rd_info": {
                "inci_cn": "水、可溶性胶原、重组胶原蛋白、1,2-己二醇",
                "inci_en": "Aqua, Soluble Collagen, Recombinant Collagen, 1,2-Hexanediol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "1.5% - 6.0% (Recommended 2.5% - 4.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 42°C in cooling stage",
                "appearance": "Colorless transparent viscous liquid",
                "solubility": "Easily miscible with aqueous solutions",
                "compatibility": "Compatible with common polyols, amino acids, and gentle rheology modifiers"
            },
            "procurement_info": {
                "nmpa_code": "007812-02844-3318",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available with formulation guides",
                "qualifications": "Batch COA, SDS, TDS, Amino Acid Composition Analysis"
            },
            "marketing_info": {
                "mechanism": "Combines human Type I (tensile strength) and Type III (suppleness) collagen domains at the golden ratio, providing immediate surface cushioning while signaling fibroblasts to upregulate neo-collagen synthesis.",
                "claims": "3D Matrix Remodeling, Plumping Elasticity, Golden Ratio Collagen, Supple Firming, Fine Line Softening",
                "applications": "Firming facial essences, anti-gravity lotions, contour lifting eye creams, hydrating night sleeping masks",
                "patents": "Granted Invention Patent on Recombinant Humanized Collagen Complex"
            },
        },
        "tysgdb": {
            "title": "Youth Hydrolight Protein",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Biomimetic bio-protein fusing poly-L-lactic acid (PLLA) bio-stimulatory pathways with recombinant human collagen. Imparts instantaneous dewy plumping hydration to the epidermis while continuously inducing endogenous collagen regeneration.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Collagen, Poly-L-Lactic Acid, Hyaluronic Acid, 1,2-Hexanediol",
                "Core Actives": "Nano-PLLA Bio-Stimulatory Dispersion + Recombinant Collagen",
                "Appearance": "Opalescent translucent liquid",
                "Solubility": "Water dispersible",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组胶原蛋白、聚左旋乳酸、透明质酸、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Collagen, Poly-L-Lactic Acid, Hyaluronic Acid, 1,2-Hexanediol",
                "cas": "9007-34-5 / 26100-51-6",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.5%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 40°C during final mixing phase",
                "appearance": "Opalescent translucent emulsion-liquid",
                "solubility": "Easily dispersible in essence bases and lotions",
                "compatibility": "Compatible with standard cosmetic thickeners and hydration actives"
            },
            "procurement_info": {
                "nmpa_code": "008719-02941-5582",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 20kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, strictly sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Biocompatibility & Safety Dossiers"
            },
            "marketing_info": {
                "mechanism": "Biodegradable nano-PLLA particles act as physical micro-scaffolds that stimulate macrophage sub-type polarization to M2 phenotype, promoting sustained fibroblast activation and endogenous collagen neo-genesis.",
                "claims": "Hydrolight Dewy Radiance, Sustained Neo-Collagenesis, Needle-Free Plumping, Volumetric Restructuring, Youthful Vitality",
                "applications": "Hydrolight plumping essences, volumizing day creams, glow ampoules, aesthetic clinic maintenance fluids",
                "patents": "Patent-pending nano-PLLA and recombinant collagen co-dispersion platform"
            },
        },
        "yskmyz": {
            "title": "Probiotic Soothing Factor / Peach Gum Polysaccharide",
            "category": "Plant-Derived Actives",
            "desc": "Highly branched acidic heteropolysaccharide extracted from authentic premium wild peach gum, rich in L-arabinose, D-galactose, and uronic acid. Forms a biomimetic second sebum film on the skin surface, fortifying sensitive barriers and locking in moisture.",
            "specs": {
                "INCI Name": "Aqua, Prunus Persica (Peach) Resin Extract, Bifida Ferment Lysate, Butylene Glycol",
                "Core Actives": "Peach Gum Heteropolysaccharides >70%, Probiotic Bio-Lysate",
                "Appearance": "Golden-yellow clear viscous liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、桃胶提取物、二裂酵母发酵产物溶胞物、丁二醇",
                "inci_en": "Aqua, Prunus Persica (Peach) Resin Extract, Bifida Ferment Lysate, Butylene Glycol",
                "cas": "90046-03-0 / 96507-89-0",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.0 - 6.8",
                "heat_tolerance": "Heat stable up to 65°C; broad processing compatibility",
                "appearance": "Golden-yellow transparent viscous liquid, neutral scent",
                "solubility": "Freely soluble in water",
                "compatibility": "High compatibility with anionic/non-ionic thickeners and sensitive skin active formulas"
            },
            "procurement_info": {
                "nmpa_code": "007551-01822-4490",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, ventilated place below 25°C",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available with formulation guides",
                "qualifications": "Batch COA, SDS, TDS, Skin Barrier Transepidermal Water Loss (TEWL) Report"
            },
            "marketing_info": {
                "mechanism": "Natural high-viscosity polysaccharides crosslink into an ultra-flexible hydrophilic biological shield, drastically reducing TEWL, blunting mechanical friction, and synergizing with probiotic lysates to re-stabilize microflora.",
                "claims": "Biomimetic Sebum Shield, Rapid Redness Soothing, TEWL Reduction, Sensitive Skin Calming, Long-Lasting Moisture Lock",
                "applications": "Sensitive barrier relief creams, calming gel balms, seasonal rescue lotions, soothing sleeping packs",
                "patents": "Invention Patent on High-Yield Peach Gum Polysaccharide Fermentation & Refining"
            },
        },
        "smndb": {
            "title": "Jellyfish Mucin Protein",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Specific ultra-high-molecular glycoprotein (Q-mucin) extracted from deep-sea jellyfish. Endowed with 3 times greater moisture-retention longevity than standard hyaluronic acid, plus innate dual defenses against bacterial adhesion and photo-oxidative stress.",
            "specs": {
                "INCI Name": "Aqua, Jellyfish Extract, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Deep-Sea Jellyfish Q-Mucin (Glycoprotein >90%)",
                "Appearance": "Colorless to pale straw transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 3.0%"
            },
            "rd_info": {
                "inci_cn": "水、水母提取物、甘油、1,2-己二醇",
                "inci_en": "Aqua, Jellyfish Extract, Glycerin, 1,2-Hexanediol",
                "cas": "91079-43-5 / 7732-18-5",
                "dosage": "0.5% - 3.0% (Recommended 1.0% - 2.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 45°C during the cooling phase",
                "appearance": "Colorless to pale straw transparent liquid",
                "solubility": "Completely miscible with water",
                "compatibility": "Compatible with hyaluronic acid, panthenol, and botanical antioxidants"
            },
            "procurement_info": {
                "nmpa_code": "008432-02104-9812",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 20kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Moisture Retention Comparative Test Report"
            },
            "marketing_info": {
                "mechanism": "The tandem repeat amino acid structure of Q-mucin holds abundant O-linked oligosaccharide chains, organizing a 3D water reservoir on keratinocytes while inhibiting bacterial surface adherence.",
                "claims": "Deep-Sea Moisture Matrix, 3X Hyaluronic Hydration Longevity, Anti-Adhesion Defense, Photo-Aging Cushion, Dewy Silkiness",
                "applications": "Hydrating jellyfish essence masks, all-day quench creams, anti-pollution setting sprays, dewy foundation primers",
                "patents": "Invention Patent on Deep-Sea Jellyfish Glycoprotein Extraction & Stabilization"
            },
        },
        "hylfyz": {
            "title": "Marine Brightening Factor",
            "category": "Marine-Derived Actives",
            "desc": "Derived from co-fermentation filtrates of deep-sea Pseudoalteromonas and marine microalgae, rich in small-molecule exopolysaccharides and tyrosinase-inhibiting bioactive peptides to intercept melanogenesis signal cascades.",
            "specs": {
                "INCI Name": "Aqua, Pseudoalteromonas Ferment Extract, Microalgae Extract, Butylene Glycol",
                "Core Actives": "Marine Bio-Peptides + Marine Oligosaccharides",
                "Appearance": "Pale yellow clear transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、交替假单胞菌发酵产物提取物、微藻提取物、丁二醇",
                "inci_en": "Aqua, Pseudoalteromonas Ferment Extract, Plankton Extract, Butylene Glycol",
                "cas": "100085-39-0 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 45°C during the cooling phase",
                "appearance": "Light amber transparent liquid, mild oceanic aroma",
                "solubility": "Easily miscible with aqueous phase",
                "compatibility": "Compatible with vitamin C derivatives, niacinamide, and arbutin"
            },
            "procurement_info": {
                "nmpa_code": "008291-01934-7714",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dry place at 2-8°C, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available with whitening test data",
                "qualifications": "Batch COA, SDS, TDS, Tyrosinase Inhibition Assay Report"
            },
            "marketing_info": {
                "mechanism": "Triple pathway intervention: competitively inhibits tyrosinase active centers, suppresses endothelin-1 melanocyte stimulation, and accelerates keratinocyte desquamation of surface dullness.",
                "claims": "Multi-Pathway Tone Brightening, Oceanic Radiance Awakening, Dark Spot Fading, Dull Complexion Clarifying, Uniform Luminosity",
                "applications": "Brightening treatment serums, spot correcting creams, radiant glow sheet masks, illuminating toners",
                "patents": "Deep-Sea Extreme Microbe Fermentation & Metabolite Fractionation Patent"
            },
        },
        "zzxldb": {
            "title": "Recombinant Fibronectin",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Full-length humanized recombinant fibronectin (FN) expressed via modern biosynthesis, containing authentic RGD cell-adhesion motifs to accelerate cell migration and ECM network reconstruction.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Fibronectin, Butylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Full-Length Recombinant Human Fibronectin (Purity >96%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组纤连蛋白、丁二醇、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Fibronectin, Butylene Glycol, 1,2-Hexanediol",
                "cas": "86088-83-7 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.0%)",
                "ph_range": "6.0 - 7.2",
                "heat_tolerance": "Add below 40°C during final gentle stirring step",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Water soluble",
                "compatibility": "Compatible with hyaluronic acid, glycerin, and non-ionic emulsifiers"
            },
            "procurement_info": {
                "nmpa_code": "008451-01932-8810",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, sealed and dark",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available with application guidelines",
                "qualifications": "Batch COA, SDS, TDS, Recombinant Purity Certificate"
            },
            "marketing_info": {
                "mechanism": "Provides essential anchoring points for cell migration through RGD motifs, activating intracellular survival kinases to accelerate re-epithelialization and thicken fragile compromised barriers.",
                "claims": "Emergency Barrier Rescue, Cellular Adhesion Network Rebuilding, Rapid Re-Epithelialization, Post-Procedure Care, Redness Calming",
                "applications": "Barrier rescue essences, intensive recovery creams, post-laser soothing gels, high-potency soothing ampoules",
                "patents": "Invention Patent on Industrialized Recombinant Fibronectin Biosynthesis"
            },
        },
        "zzjydb": {
            "title": "Recombinant Collagen Solution",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "High-purity humanized recombinant Type III collagen solution. Spatial structure is highly homologous to natural human collagen, ensuring high cell attachment and zero risk of animal-derived viral pathogens.",
            "specs": {
                "INCI Name": "Aqua, Soluble Collagen, 1,2-Hexanediol, Pentylene Glycol",
                "Core Actives": "Humanized Recombinant Type III Collagen (Purity >98%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "2.0% - 8.0%"
            },
            "rd_info": {
                "inci_cn": "水、可溶性胶原、1,2-己二醇、戊二醇",
                "inci_en": "Aqua, Soluble Collagen, 1,2-Hexanediol, Pentylene Glycol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "2.0% - 8.0% (Recommended 3.0% - 5.0%)",
                "ph_range": "5.5 - 6.8",
                "heat_tolerance": "Add below 40°C during cooling phase",
                "appearance": "Colorless transparent liquid, clear and odorless",
                "solubility": "Easily miscible with water in all proportions",
                "compatibility": "Compatible with standard formulation bases, peptides, and polyols"
            },
            "procurement_info": {
                "nmpa_code": "007812-01994-6623",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, protected from light",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, SEC-HPLC Purity & Endotoxin Reports"
            },
            "marketing_info": {
                "mechanism": "Engineered with the human Type III collagen core functional sequence, accelerating fibroblast proliferation and binding discoidin domain receptors (DDRs) to replenish baby-like skin suppleness.",
                "claims": "100% Human-Homologous Structure, Baby Collagen Replenishment, Dermal Elasticity Rebound, Fine Line Softening, Deep Hydration Plumpness",
                "applications": "Anti-aging collagen serums, firming bounce creams, hydrogel face masks, clinic-grade aesthetic post-care",
                "patents": "Granted Chinese Invention Patent on High-Density Yeast-Expressed Recombinant Collagen"
            },
        },
        "5djydb": {
            "title": "5D Collagen",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Integrates five essential active sequences of Type I, III, IV, VII, and XVII collagens, creating full-layer penetrating coverage from the dermal matrix and DEJ to the epidermal stem cell microenvironment.",
            "specs": {
                "INCI Name": "Aqua, Soluble Collagen, Recombinant Collagen, Glycerin, Butylene Glycol",
                "Core Actives": "5-Type Recombinant Collagen Matrix (Types I, III, IV, VII, XVII)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "2.0% - 8.0%"
            },
            "rd_info": {
                "inci_cn": "水、可溶性胶原、重组胶原蛋白、甘油、丁二醇",
                "inci_en": "Aqua, Soluble Collagen, Recombinant Collagen, Glycerin, Butylene Glycol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "2.0% - 8.0% (Recommended 3.0% - 5.0%)",
                "ph_range": "5.5 - 6.8",
                "heat_tolerance": "Add below 40°C in cooling stage",
                "appearance": "Colorless transparent viscous liquid",
                "solubility": "Water soluble",
                "compatibility": "Compatible with standard cosmetic thickeners, peptides, and humectants"
            },
            "procurement_info": {
                "nmpa_code": "007812-03914-8890",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Full Analytical Dossier"
            },
            "marketing_info": {
                "mechanism": "5-layer architectural repair: Type I/III replenish dermal volume, Type IV/VII re-anchor the DEJ basement membrane, and Type XVII prevents epidermal stem cell exhaustion and follicle thinning.",
                "claims": "5D Architectural Anti-Aging, DEJ Anchoring Support, Anti-Sagging Resilience, Dermal Density Restoration, Multi-Tiered Firming",
                "applications": "Comprehensive multi-depth anti-aging serums, lifting face sculpt creams, neck firming balms, sleeping treatment masks",
                "patents": "Chinese Invention Patent: Transdermal Multi-Type Recombinant Collagen Matrix"
            },
        },
        "twdvit": {
            "title": "Peptivida Vitaluxe",
            "category": "Food Nutrition Ingredients",
            "desc": "Comprehensive synergistic cellular nutrient complex combining functional peptides, full B-vitamin complex, and stabilized VC/VE precursors. Delivers one-stop nutritional fuel to energize cellular vitality and metabolic renewal.",
            "specs": {
                "INCI Name": "Aqua, Palmitoyl Pentapeptide-4, Niacinamide, Panthenol, Ascorbyl Glucoside, Tocopherol",
                "Core Actives": "Multi-Peptide Matrix + Multi-Vitamin Vital Complex",
                "Appearance": "Light golden transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、棕榈酰五肽-4、烟酰胺、泛醇、抗坏血酸葡糖苷、生育酚",
                "inci_en": "Aqua, Palmitoyl Pentapeptide-4, Niacinamide, Panthenol, Ascorbyl Glucoside, Tocopherol",
                "cas": "214047-00-4 / 98-92-0",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.5%)",
                "ph_range": "5.5 - 6.5",
                "heat_tolerance": "Add below 45°C during cooling stage",
                "appearance": "Light golden clear liquid",
                "solubility": "Water soluble",
                "compatibility": "Compatible with most cosmetic bases; avoid strong reducing/oxidizing agents"
            },
            "procurement_info": {
                "nmpa_code": "008104-02381-1150",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dry place protected from light below 25°C",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 30g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Nutritional Purity Analysis"
            },
            "marketing_info": {
                "mechanism": "Acts as an intracellular metabolic catalyst: peptides stimulate ECM synthesis while B-complex and antioxidant vitamins accelerate ATP generation and protect cellular membranes from lipid peroxidation.",
                "claims": "All-in-One Nutrient Infusion, Cellular Energy Recharging, Fatigue Resistance, Radiant Glow Awakening, Collagen Synthesis Synergy",
                "applications": "Multi-vitamin revitalization serums, radiant day lotions, anti-fatigue eye gels, wellness beauty supplements",
                "patents": "Synergistic peptide-vitamin co-stabilization micro-dispersion patent"
            },
        },
        "jnhtea": {
            "title": "Energy Cyclic Peptide EAC",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Multi-target cyclic peptide with closed-loop topological spatial locking, granting exceptional stability against proteolytic enzymatic degradation and activating dermal elastic fiber networks and fibrillin.",
            "specs": {
                "INCI Name": "Aqua, Cyclotetrapeptide-24 Aminocyclohexane Carboxylate, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Topologically Locked Cyclic Peptide EAC (Purity >98%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 2.5%"
            },
            "rd_info": {
                "inci_cn": "水、环己肽-24氨基环己烷羧酸酯、甘油、1,2-己二醇",
                "inci_en": "Aqua, Cyclotetrapeptide-24 Aminocyclohexane Carboxylate, Glycerin, 1,2-Hexanediol",
                "cas": "100085-39-0 / 7732-18-5",
                "dosage": "0.5% - 2.5% (Recommended 1.0% - 1.5%)",
                "ph_range": "5.0 - 7.5",
                "heat_tolerance": "Extremely heat stable up to 80°C",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Freely soluble in water",
                "compatibility": "Broad compatibility across diverse pH levels and emulsion matrices"
            },
            "procurement_info": {
                "nmpa_code": "008594-01822-7740",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dark, dry place below 25°C",
                "shelf_life": "36 Months",
                "sample_policy": "Complimentary 30g trial sample available with elasticity test reports",
                "qualifications": "Batch COA, SDS, TDS, HPLC Purity Certificate"
            },
            "marketing_info": {
                "mechanism": "The cyclic closed conformation protects peptide bonds from exopeptidases and endopeptidases, allowing extended receptor interaction to stimulate LOXL-1 and tropoelastin assembly into mature elastic fibers.",
                "claims": "Topological Enzymatic Resistance, Elastic Architecture Rebuilding, High-Potency Expression, Jawline Tightening, Resilient Bounce",
                "applications": "Firming bounce serums, jawline contouring essences, anti-gravity tightening creams, eye lifting treatments",
                "patents": "Granted Chinese and US Invention Patents on Cyclic Peptide Chemical Synthesis & Skin Penetration"
            },
        },
        "wndbzy": {
            "title": "Snail Mucin Protein",
            "category": "Recombinant Biomimetic Protein",
            "desc": "Humanized biomimetic recombinant snail secretion mucin, purified to remove allergenic impurities present in raw snail slime, rich in chondroitin, allantoin, small-molecule collagen, and defensive antimicrobial peptides.",
            "specs": {
                "INCI Name": "Aqua, Snail Secretion Filtrate, Recombinant Glycoprotein, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Recombinant Snail Mucin Glycoprotein (Purity >95%)",
                "Appearance": "Slightly viscous transparent liquid with silky feel",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.0% - 5.0%"
            },
            "rd_info": {
                "inci_cn": "水、蜗牛分泌物滤液、重组糖蛋白、甘油、1,2-己二醇",
                "inci_en": "Aqua, Snail Secretion Filtrate, Recombinant Glycoprotein, Glycerin, 1,2-Hexanediol",
                "cas": "91079-43-5 / 7732-18-5",
                "dosage": "1.0% - 5.0% (Recommended 2.0% - 3.5%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 45°C during cooling stage",
                "appearance": "Colorless to pale straw viscous liquid, elegant silky touch",
                "solubility": "Water soluble",
                "compatibility": "Compatible with standard cosmetic polymers, hyaluronic acid, and botanical extracts"
            },
            "procurement_info": {
                "nmpa_code": "008341-02914-5560",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, Skin Smoothing & Repair Clinical Reports"
            },
            "marketing_info": {
                "mechanism": "Natural chondroitin sulfate and mucopolysaccharides form a hydrating protective scaffold on micro-damaged skin, accelerating cell renewal and smoothing out rough irregular surface texture.",
                "claims": "Biomimetic Pure Snail Mucin, Rapid Texture Smoothing, Acne Scar Softening, Silky Protective Hydration, Calming Skin Irritation",
                "applications": "Texture-refining serums, blemish rescue creams, silky smoothing primers, post-acne repair gels",
                "patents": "Invention Patent on Biomimetic Recombinant Snail Mucin Protein Preparation"
            },
        },
        "fswnjy": {
            "title": "Biomimetic Snail Collagen",
            "category": "Recombinant Biomimetic Protein",
            "desc": "Biomimetic composite collagen merging the restorative smoothing prowess of snail mucin with the structural plumping benefits of recombinant human collagen, bi-directionally activating keratinocyte regeneration and ECM reconstruction.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Collagen, Snail Secretion Filtrate, Butylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Biomimetic Snail Glycoprotein + Recombinant Collagen Complex",
                "Appearance": "Colorless to pale yellow viscous liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.5% - 6.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组胶原蛋白、蜗牛分泌物滤液、丁二醇、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Collagen, Snail Secretion Filtrate, Butylene Glycol, 1,2-Hexanediol",
                "cas": "9007-34-5 / 91079-43-5",
                "dosage": "1.5% - 6.0% (Recommended 2.5% - 4.0%)",
                "ph_range": "5.5 - 7.0",
                "heat_tolerance": "Add below 42°C during final step",
                "appearance": "Clear to translucent viscous liquid",
                "solubility": "Water soluble",
                "compatibility": "Compatible with standard cosmetic bases, peptides, and humectants"
            },
            "procurement_info": {
                "nmpa_code": "008341-03120-7791",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, sealed and dark",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available with application guidelines",
                "qualifications": "Batch COA, SDS, TDS, Dermal Repair & Smoothing Reports"
            },
            "marketing_info": {
                "mechanism": "Dual-action bio-synergy: snail mucin accelerates epidermal barrier resurfacing while recombinant collagen refills dermal extracellular voids to flatten fine lines and roughness.",
                "claims": "Dual Bio-Regeneration, Blemish Mark Fading, Plump Elastic Restoration, Velvety Skin Smoothing, Intensive Barrier Restructuring",
                "applications": "Resurfacing night creams, acne pit repair essences, intensive recovery balms, hydrating sheet masks",
                "patents": "Patent on Snail Mucin and Recombinant Collagen Biomimetic Complex"
            },
        },
        "0xjydb": {
            "title": "Type 0 Collagen",
            "category": "Recombinant Biomimetic Protein",
            "desc": "Focusing on the foundational dermal-epidermal junction (DEJ) basement membrane, this 'Origin Type' collagen repairs the microscopic anchoring loops at the epidermal-dermal interface, reversing DEJ flattening and structural collapse.",
            "specs": {
                "INCI Name": "Aqua, Recombinant Collagen, Glycerin, 1,2-Hexanediol",
                "Core Actives": "Origin Type Recombinant Collagen (Type 0 / DEJ Homology >98%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "1.5% - 6.0%"
            },
            "rd_info": {
                "inci_cn": "水、重组胶原蛋白、甘油、1,2-己二醇",
                "inci_en": "Aqua, Recombinant Collagen, Glycerin, 1,2-Hexanediol",
                "cas": "9007-34-5 / 7732-18-5",
                "dosage": "1.5% - 6.0% (Recommended 2.0% - 4.0%)",
                "ph_range": "5.5 - 6.8",
                "heat_tolerance": "Add below 40°C in cooling stage",
                "appearance": "Colorless transparent liquid, odorless",
                "solubility": "Readily soluble in water",
                "compatibility": "Compatible with standard formulation systems, peptides, and polyols"
            },
            "procurement_info": {
                "nmpa_code": "007812-01994-0010",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store refrigerated at 2-8°C, dark and sealed",
                "shelf_life": "24 Months",
                "sample_policy": "Complimentary 50g trial sample available",
                "qualifications": "Batch COA, SDS, TDS, DEJ Anchoring Research Dossier"
            },
            "marketing_info": {
                "mechanism": "Specially designed to bind nidogen and laminin-332 in the basement membrane zone, reinforcing anchoring fibrils (Type VII collagen) and hemidesmosomes to prevent age-related epidermal detachment.",
                "claims": "Origin Type 0 Collagen, DEJ Basement Membrane Tightening, Anti-Slackening Anchor, Youthful Spring Scaffold, Resilient Facial Tone",
                "applications": "Structural lifting serums, anti-sagging facial contour creams, DEJ repairing eye balms, aesthetic clinic maintenance fluids",
                "patents": "Granted Invention Patent on Recombinant Basement Membrane Collagen Complex"
            },
        },
        "tphtct": {
            "title": "Transdermal Cyclic Peptide cTDP",
            "category": "Transdermal Recombinant Protein/Peptides",
            "desc": "Award-winning proprietary patented closed cyclic peptide penetration carrier, boasting exceptional proteolytic resistance and cell membrane fluidity modulation to safely transport macromolecular actives up to tens of kilodaltons across the skin barrier.",
            "specs": {
                "INCI Name": "Aqua, Cyclopeptide-1, Pentylene Glycol, 1,2-Hexanediol",
                "Core Actives": "Patented Transdermal Cyclic Peptide cTDP (Purity >99%)",
                "Appearance": "Colorless transparent liquid",
                "Solubility": "Water soluble",
                "Recommended Dosage": "0.5% - 2.0%"
            },
            "rd_info": {
                "inci_cn": "水、环肽-1、戊二醇、1,2-己二醇",
                "inci_en": "Aqua, Cyclopeptide-1, Pentylene Glycol, 1,2-Hexanediol",
                "cas": "100085-39-0 / 7732-18-5",
                "dosage": "0.5% - 2.0% (Recommended 1.0%)",
                "ph_range": "5.0 - 7.5",
                "heat_tolerance": "Heat stable up to 80°C",
                "appearance": "Clear colorless liquid, odorless",
                "solubility": "Completely miscible with water",
                "compatibility": "Broad compatibility across varied pH ranges, proteins, peptides, and botanical extracts"
            },
            "procurement_info": {
                "nmpa_code": "008319-01822-0099",
                "packaging": "1kg/fluorinated bottle, 5kg/drum, 25kg/drum",
                "moq": "1 kg (Ready Stock)",
                "lead_time": "Dispatched within 24-48 hours",
                "storage": "Store in a cool, dark, dry place below 25°C",
                "shelf_life": "36 Months",
                "sample_policy": "Complimentary 30g trial sample available with Franz cell penetration test data",
                "qualifications": "Batch COA, SDS, TDS, HPLC Purity, Franz Diffusion Cell Reports"
            },
            "marketing_info": {
                "mechanism": "Engineered cyclic peptide topology reversibly modulates stratum corneum lipid packaging, opening temporary 5-minute nano-channels that guide proteins, nucleic acids, and polysaccharides into deep cutaneous strata.",
                "claims": "Flagship Transdermal Cyclic Peptide, Universal Penetration Accelerator, 5-Minute Reversible Nano-Channel, Needle-Free Delivery, Maximum Bio-Availability",
                "applications": "High-potency transdermal booster essences, bio-active ampoules, post-procedure delivery serums, active-infused sheet masks",
                "patents": "Chinese and US Granted Invention Patents on Cyclic Transdermal Peptide Technology"
            },
        }
    }

    # Build the full products_en list
    products_en = []
    for p in prods:
        pid = p["id"]
        en_item = dict(p) # shallow copy
        if pid in EN_DATA:
            overrides = EN_DATA[pid]
            en_item["title"] = overrides["title"]
            en_item["category"] = overrides["category"]
            en_item["desc"] = overrides["desc"]
            en_item["specs"] = overrides["specs"]
            en_item["rd_info"] = overrides["rd_info"]
            en_item["procurement_info"] = overrides["procurement_info"]
            en_item["marketing_info"] = overrides["marketing_info"]
            en_item["disclaimer"] = STANDARD_DISCLAIMER_EN
        products_en.append(en_item)

    with open(DEST_PATH, "w", encoding="utf-8") as f:
        json.dump(products_en, f, ensure_ascii=False, indent=2)

    print(f"[OK] Successfully built {DEST_PATH} with {len(products_en)} products translated!")

if __name__ == "__main__":
    build_products_en()
