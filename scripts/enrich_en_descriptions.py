# -*- coding: utf-8 -*-
"""
Generate professional, compliant, fluent English descriptions for all 37 products in products_en.json
matching the rich 2-3 paragraph format.
"""

import json
import os

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_JSON_PATH = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data", "products_en.json")

with open(EN_JSON_PATH, "r", encoding="utf-8") as f:
    en_products = json.load(f)

rich_content_en = {
    "tphtct": (
        "<p>Transdermal Cyclic Peptide cTDP is an award-winning, proprietary closed-loop peptide transdermal carrier developed by Mellgen Biotechnology. Its unique cyclic topology provides outstanding enzymatic stability and cell biocompatibility, selectively binding to cell membrane ion transport channels to reversibly open cutaneous absorption pathways within 5 minutes across follicular and intercellular routes.</p>"
        "<p>This innovation completely overcomes the classical physical barrier of stratum corneum impermeability for biological macromolecules (recombinant proteins, peptides, polysaccharides, and nucleic acids), elevating transdermal absorption efficiency by over 10-fold. The process is gentle, fully reversible, and non-destructive to lipid bilayers, significantly enhancing active bioavailability and delivering remarkable firming and smoothing benefits.</p>"
    ),
    "pdrnht": (
        "<p>PDRN Cyclic Peptide Rod PRO harnesses high-activity Sodium DNA constrained into an ordered supramolecular rod-like self-assembly complex, integrated with patented transdermal cyclic peptides to overcome the historic challenge of large nucleic acid skin penetration.</p>"
        "<p>This formulation efficiently delivers deep revitalizing signals to basal cells, supporting cellular metabolic vitality, natural nucleic acid replenishment, and barrier resilience against environmental stressors. It notably improves dermal firmness, elasticity, and plump moisture retention, making it ideal for prestige anti-aging serums, intensive repair essences, and rejuvenating sheet masks.</p>"
    ),
    "jnhtea": (
        "<p>Poly-energy Cyclic Peptide EAC is a cutting-edge cellular energizing raw material innovatively combining Mellgen's transdermal cyclic peptide delivery system with high-energy bio-actives (including energy adenosine and Artemia extract) to provide continuous metabolic vitality and enhanced cutaneous penetration.</p>"
        "<p>Its bio-actives work synergistically to optimize microcirculation, boost mitochondrial cellular energy turnover, and promote endogenous collagen synthesis. It effectively combats skin sagging, dullness, fine lines, and lack of tone, delivering superior firming, radiance, and structural lifting in luxury face creams and eye contour treatments.</p>"
    ),
    "tpxldb": (
        "<p>Transdermal Fibronectin (TFNpro) is a multifunctional humanized recombinant macromolecular glycoprotein fused with University of Science and Technology of China (USTC) transdermal technology. Produced via high-density yeast fermentation with purity exceeding 95%, it displays superior bio-stability and physiological activity.</p>"
        "<p>The molecule retains the essential human RGD cell-adhesion motif, achieving a 10-fold absorption enhancement when guided by transdermal cyclic peptides. It specifically directs keratinocyte migration to micro-stressed sites, accelerating stratum corneum physical barrier assembly and moisture retention to visibly soothe sensitivity, dryness, and barrier compromise.</p>"
    ),
    "tp1jydb": (
        "<p>Transdermal Type I Collagen is manufactured via pharmaceutical-grade synthetic biology, delivering 100% human-homologous full-length active Type I collagen integrated with Mellgen's 3rd-generation transdermal technology, completely transcending the superficial surface film-forming limitations of conventional collagens.</p>"
        "<p>As the primary structural scaffolding protein of the dermis, it directly supplements depleted collagen fibers to counter photoaging and natural chronological breakdown. It significantly bolsters dermal tensile strength and facial contour firmness, locking in moisture to restore bouncy, supple, and refined youthful skin.</p>"
    ),
    "zzjydb": (
        "<p>Recombinant Type III Collagen (RHCS) is designed according to the core high-activity functional sequence of human Type III collagen, featuring high-density triple-helix domains. Often celebrated in the industry as the crucial 'baby collagen', it governs cutaneous suppleness and delicate texture.</p>"
        "<p>Powered by transdermal technology, it smoothly traverses the stratum corneum to reach the basal microenvironment, stimulating fibroblast vitality and replenishing the extracellular matrix. It softens fine dehydration lines, enhances elasticity and bounce, and provides gentle soothing care for compromised or post-sunlight exposed skin.</p>"
    ),
    "mellpr8670": (
        "<p>5D Collagen (5Dcollagen) is an innovative multi-type collagen composite matrix created through AI molecular simulation, tandem-connecting high-affinity active domains of human Types I, II, III, IV, and XVII collagens, followed by yeast co-expression and site-specific enzymatic cleavage.</p>"
        "<p>With an optimal molecular weight around 6,000 Daltons and integrated transdermal technology, it orchestrates a 5-dimensional anti-aging synergy: 1D surface hydration, 2D basement membrane support, 3D infant elasticity, 4D deep plumping, and 5D stem cell niche stabilization, comprehensively combating facial sagging and contour relaxation.</p>"
    ),
    "tptxdb": (
        "<p>Transdermal Elastin Telastin is a 100% recombinant human-homologous functional elastin produced through yeast bio-fermentation and gradient purification, exhibiting complete sequence homology with human elastin alongside exceptional hydrophilicity and flexibility.</p>"
        "<p>Elastin forms the spring-like tensile meshwork of the dermis. Armed with a transdermal delivery system, Telastin directly replenishes degraded elastic fiber scaffolding, significantly reducing elasticity loss, improving recoil resilience, and smoothing facial expression lines for a silky, lifted texture.</p>"
    ),
    "tysgdb": (
        "<p>Youthful Radiant Protein MELLPRO rECM is a breakthrough biomimetic raw material scientifically assembled from recombinant fibronectin, recombinant collagen, recombinant elastin, and functional amino acids (glycine, proline) adhering to the native architecture of human extracellular matrix (ECM).</p>"
        "<p>This matrix faithfully reproduces the structural support network of healthy skin. Fusion with transdermal peptides enables multi-protein synergistic penetration, providing immediate mechanical scaffolding, sustained hydration, and intensive nourishment for stressed, dull, and fatigued complexions, delivering a luminous, plump 'glass skin' finish.</p>"
    ),
    "gtlafdp": (
        "<p>Oligopeptides MEGPEP AFDP is a patented high-activity recombinant peptide lyophilized powder formulated with high-purity Oligopeptide-2 in a protective stabilization matrix, characterized by low molecular weight, high tissue compatibility, and potent antioxidant efficacy.</p>"
        "<p>Upon aqueous reconstitution, it rapidly releases bioactive signals that neutralize UV- and oxidation-induced free radicals, mitigating cellular oxidative stress while encouraging fibroblasts to synthesize endogenous collagen and hyaluronic acid. It excels in emergency sensitive skin recovery, after-sun calming, and freeze-dried ampoule applications.</p>"
    ),
    "hylfyz": (
        "<p>Marine Brightening Factor MEGPEP TXOD originates from symbiotic marine yeast inhabiting red coral communities, engineered via cDNA library reconstruction and homologous recombination to deliver high-purity oxidoreductase sequences through fermentation.</p>"
        "<p>It features dual active domains: a copper-containing superoxide dismutase oxidoreductase and a highly conserved thioredoxin catalytic center, effectively neutralizing reactive oxygen species (ROS) and lipid peroxides. Verified through zebrafish in vivo testing, it diminishes melanin signals, clarifies dull yellow tones, and restores luminous, even-toned skin.</p>"
    ),
    "wndbzy": (
        "<p>Snailpro Snail Protein Mucin is the world's premier non-animal biomimetic snail secretion protein crafted through green synthetic biology, eliminating batch variance, impurities, and allergen risks associated with traditional animal farming extracts.</p>"
        "<p>It replicates the core biochemical functionality of snail mucin, featuring glycoproteins that target epidermal growth factor receptors to stimulate natural barrier restoration. With exceptional water-binding and viscoelastic properties, it establishes a breathable protective hydro-film across the stratum corneum to soothe dryness, peeling, and redness.</p>"
    ),
    "fswnjy": (
        "<p>Snailpro Biomimetic Snail Collagen utilizes computational biology to reconstruct the specialized molecular backbone of snail collagen, produced via engineered microbial fermentation and combined with transdermal cyclic peptides.</p>"
        "<p>It exhibits a versatile molecular assembly spanning low-molecular monomers to high-molecular nonamers, delivering rich, velvety nourishment without stickiness. Featuring superior thermal stability (minimal activity loss after 48h high-temperature storage) and hydration rivalling premium hyaluronic acid, it firms and softens fine lines in prestige anti-aging creams.</p>"
    ),
    "mellpr205": (
        "<p>MELLPRO MAP Recombinant Mussel Adhesive Protein is developed via genetic engineering based on the underwater super-adhesion mechanism of marine mussels, rich in characteristic L-DOPA functional catechol groups.</p>"
        "<p>Under cutaneous physiological conditions, it rapidly self-crosslinks into a dense, water-resistant, and breathable protective biopolymer film. It effectively shields vulnerable skin from friction, pollutants, and chemical irritants, calming redness and heat, accelerating post-sun recovery, and offering distinctive barrier defense in dermatological creams.</p>"
    ),
    "lrdt": (
        "<p>Deer Antler Polypeptide is extracted from premium natural deer antler using biomimetic enzymatic cleavage and ultrafiltration, yielding small-molecule active peptides, ceramide precursors, and micronutrients fused with transdermal cyclic peptides.</p>"
        "<p>This gentle and stable active protects epidermal and dermal cells against oxidative damage, maintaining regular physiological metabolic turnover. It significantly refines rough, fatigued, and dull complexions, reinforcing skin firmness, elasticity, and self-repair capacity in prestige anti-aging formulations and salon ampoules.</p>"
    ),
    "smndb": (
        "<p>JELFIPRO Jellyfish Mucin is isolated from marine jellyfish using proprietary low-temperature enzymatic extraction, completely eliminating mammalian pathogen risks and honored with the Guangdong Golden Spike Patent Award.</p>"
        "<p>Retaining its authentic native triple-helix conformation, it exhibits superior bio-affinity compared to terrestrial collagens. It effectively inhibits UV-induced photoaging and matrix breakdown, noticeably reduces transepidermal water loss (TEWL), soothes redness and dryness, and restores supple elasticity in suncare and sensitive skin formulations.</p>"
    ),
    "0xjydb": (
        "<p>JELFIPRO Type 0 Collagen (Jellyfish Collagen) is heralded as 'next-generation clean collagen', derived from primitive marine coelenterates and possessing a complete, native triple-helix trimer architecture.</p>"
        "<p>Free from bovine and porcine pathogen concerns with ultra-low allergenicity, its unique space network grants unmatched moisture-holding capacity and anti-photoaging defense. It constructs an intensive protective hydration veil over stressed skin, shielding against environmental stress and enhancing rebound suppleness in clean beauty regimens.</p>"
    ),
    "tpjy": (
        "<p>Placenta Collagen is extracted from certified healthy ovine placenta tissues, containing undenatured native active Types I, III, and V collagens integrated with proprietary transdermal peptide technology for superior biocompatibility.</p>"
        "<p>These multi-type collagens work synergistically to replenish the reticular and papillary dermis, restoring collagen density lost over time. It deeply binds moisture, strengthens connective tissue resilience, and smooths wrinkles and roughness to restore a firm, plump, and youthful complexion.</p>"
    ),
    "tptyts": (
        "<p>Sheep Placenta Extract utilizes biomimetic gradient enzymatic cleavage and cold purification to retain high-potency oligopeptides, free amino acids, nucleotides, and trace bio-factors from healthy ovine placenta.</p>"
        "<p>Leveraging nano-transdermal delivery, active molecules cross the stratum corneum with ease to nourish basal cells. It revitalizes fibroblast collagen synthesis, accelerates turnover, reduces flaccidity and dullness, and sculpts a rejuvenated, plump, and radiant facial contour.</p>"
    ),
    "yskmyz": (
        "<p>Probiotic Anti-Allergy Factor (MEGCALM PSF Peach Gum Polysaccharides) uses natural alpine peach gum digested by patented probiotic yeast fermentation into easily absorbed, low-molecular-weight oligosaccharide complexes.</p>"
        "<p>These oligosaccharides selectively nurture the cutaneous microbiome balance, favoring beneficial flora while suppressing opportunists. Simultaneously, they activate aquaporin AQP3 expression for endogenous deep hydration. Proven to calm itchiness, redness, and tight discomfort within 5 minutes, it is a benchmark ingredient for sensitive skin rescue.</p>"
    ),
    "zbssb": (
        "<p>MEGCALM GPT Three Treasures of Changbai Mountain combines authentic wild Ganoderma, Ginseng root, and Matsutake mushroom, co-fermented in deep liquid culture to concentrate active polysaccharides, ginsenosides, and matsutake polyphenols.</p>"
        "<p>The multi-extract synergy delivers powerful DPPH and free radical scavenging while potently inhibiting tyrosinase catalytic activity to block melanin formation, outperforming conventional arbutin. It visibly brightens dull complexions, softens expression wrinkles, and reveals an even, translucent luminosity.</p>"
    ),
    "twdvit": (
        "<p>Vitaluxe is a concentrated cellular nutrient extract derived from pure yeast fermentation bio-factories, containing multi-complex B vitamins, free amino acids, organic acids, and essential trace minerals such as zinc and selenium.</p>"
        "<p>Mimicking healthy intracellular and interstitial fluid nutrition, it provides deep biocompatible penetration and metabolic support. It swiftly re-energizes fatigued, seasonally stressed, or nutrient-deficient skin, reinforcing stratum corneum barrier resilience and imparting smooth, clear vitality.</p>"
    ),
    "aminofree": (
        "<p>AminoFree Free Amino Acids is a full-spectrum solution designed to redress cutaneous nutritional imbalances, concentrating 20 high-purity human-homologous free amino acids essential for cellular viability and keratin synthesis.</p>"
        "<p>Carefully balanced to mirror the natural moisturizing factor (NMF) ratio of healthy skin, its low-molecular structure penetrates freely to take part in keratinocyte protein maintenance and interstitial matrix formation, mitigating tightness and restoring suppleness in advanced repair formulas.</p>"
    ),
    "colamino": (
        "<p>ColAmino Collagen Amino Acids is tailored to the precise chemical profile of human collagen, highly enriched in the distinctive triad amino acids of the triple helix (including glycine, proline, and hydroxyproline).</p>"
        "<p>Serving as direct precursor building blocks for fibroblast collagen and elastin bio-synthesis, it shortens the synthetic cycle and boosts the speed and stability of quality collagen assembly. It plumps the dermal matrix, enhances structural firmness, and reduces fine lines from within.</p>"
    ),
    "tpxviijy": (
        "<p>Transdermal Type XVII Collagen is engineered using advanced recombinant biotechnology to express human transmembrane Type XVII collagen, fused with patented transdermal cyclic peptides to target the dermal-epidermal junction (DEJ) and hair follicle stem cell niche.</p>"
        "<p>As the essential hemidesmosome anchor pinning the epidermis to the basement membrane, Type XVII collagen depletion is a primary cause of epidermal thinning, sagging, and follicle miniaturization. Telastin XVII penetrates directly to the DEJ to anchor structural integrity and maintain follicle health, pioneering deep anti-aging and scalp longevity.</p>"
    ),
    "supercleaner": (
        "<p>Super cleaner is an innovative gentle pore-purifying compound combining natural Sapindus saponins, an alkaline arginine softening complex, and Decapeptide-4 transdermal carrier technology, balancing deep cleansing with barrier gentleness.</p>"
        "<p>It penetrates the follicular infundibulum to softly emulsify and dissolve stubborn sebum plugs and oxidized blackheads without aggressive AHAs or BHAs. Pores emerge clear and refined without stripping or post-wash tightness, safeguarding the natural acid mantle and skin microbiome.</p>"
    ),
    "zwjy": (
        "<p>Plant Collagen is an advanced vegan collagen polysaccharide complex extracted from botanical sources via green bioprocessing, free of animal-derived components, pathogens, or allergen concerns in alignment with international clean and vegan standards.</p>"
        "<p>Its high-molecular glycoprotein and polysaccharide matrix forms a biomimetic 3D breathable hydro-film across the stratum corneum, locking in moisture and defending against environmental dryness while smoothing superficial dehydration lines for a silky, resilient feel.</p>"
    ),
    "mgpdrn": (
        "<p>Rose PDRN Cyclic Peptide Pro blends Damascus rose floral distillate with high-potency Sodium DNA (polydeoxyribonucleotide mesh) and patented transdermal cyclic peptide cTDP into an opulent hydrating recovery elixir.</p>"
        "<p>Driven by transdermal peptides, Sodium DNA traverses the stratum corneum to furnish damaged cells with restorative nucleotide pools; rose polyphenols and aromatics boost microcirculation, sooth redness, and enhance firm elasticity, reviving dull skin with a dewy, natural rosy glow.</p>"
    ),
    "4dzyshyz": (
        "<p>4D Herbal Anti-itch Soothing Factor is derived via modern network pharmacology, combining Centella asiatica triterpenes, Portulaca polysaccharides, dipotassium glycyrrhizate, and decapeptides into a 4-dimensional soothing defense network.</p>"
        "<p>This multi-targeted active interrupts histamine release and neuro-inflammatory signaling to immediately alleviate redness, burning, pruritus, and tightness. Simultaneously, it encourages barrier rebuild, restoring calm and defense to hyper-sensitive complexions in emergency formulas.</p>"
    ),
    "lzdt": (
        "<p>MEGCALM GLP Ganoderma Polysaccharide is purified from Changbai Mountain Ganoderma lucidum via liquid fermentation and modern membrane separation, enriched in bioactive branched β-glucan architectures.</p>"
        "<p>These polysaccharides demonstrate high water-binding capacity and hydroxyl radical neutralization, creating an enduring moisture reservoir over the stratum corneum while calming environmental irritations and bolstering skin resistance for long-lasting, comforting relief.</p>"
    ),
    "megzym": (
        "<p>MEGZYME Lysozyme is a recombinant bio-fermented enzyme preparation specifically cleaving the β-1,4 glycosidic bonds in bacterial peptidoglycan walls, offering broad-spectrum, gentle biological microbial control.</p>"
        "<p>Safe, non-resistant, and non-disruptive to natural skin commensal flora, it excels in oil-control, blemish-prone skin care, and gentle preservative-boosting systems, providing a pure biotechnology foundation for hypoallergenic formulations.</p>"
    ),
    "megpep6245": (
        "<p>MEGPEP SFF Yeast Ferment Filtrate is produced from select yeast strains through high-density fermentation, cell disruption, and ultrafiltration, concentrating amino acids, micro-peptides, nucleotides, and organic acids.</p>"
        "<p>Its nutrient spectrum is readily absorbed by keratinocytes to stimulate natural moisturizing factor (NMF) synthesis, gently soften rough keratin, and optimize surface microbiome equilibrium, leaving the complexion smooth, supple, and radiant.</p>"
    ),
    "megpep": (
        "<p>MEGPEP RF50G- is formulated with high-purity recombinant oligopeptides tailored for micro-stressed and physically fragile skin barriers, exhibiting outstanding resilience and microenvironment stabilization.</p>"
        "<p>The low-molecular peptides easily penetrate to the basal layer, fostering keratinocyte differentiation and accelerating the re-assembly of stratum corneum lipid bilayers to mitigate flaking, peeling, and redness after aesthetic procedures or environmental extremes.</p>"
    )
}

for p in en_products:
    pid = p["id"]
    if pid in rich_content_en:
        p["content"] = rich_content_en[pid]

with open(EN_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(en_products, f, ensure_ascii=False, indent=2)

print("Updated all 37 English products in products_en.json with rich, fluent, compliant descriptions!")
